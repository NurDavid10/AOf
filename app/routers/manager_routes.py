"""
Manager routes for user, course, and queue management.

This module provides endpoints for managers to perform administrative tasks.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.models.expense import ExpenseCategory
from app.models.maintenance_task import TaskPriority, TaskStatus
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService
from app.services.expense_service import ExpenseService
from app.services.maintenance_service import MaintenanceService
from app.services.financial_report_service import FinancialReportService

# Set up templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Create router
router = APIRouter(prefix="/manager", tags=["manager"])


def require_manager(user: User):
    """Helper function to ensure user is a manager."""
    if user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Access denied. Manager role required.")
    return user


# ============================================================================
# USER MANAGEMENT ROUTES
# ============================================================================

@router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display list of all users."""
    try:
        require_manager(current_user)
        users = UserService.get_all_users(db)

        return templates.TemplateResponse(
            "manager/users.html",
            {
                "request": request,
                "user": current_user,
                "users": users
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/users/create", response_class=HTMLResponse)
async def create_user_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display user creation form."""
    try:
        require_manager(current_user)

        # Get list of parents for student creation
        parents = UserService.get_users_by_role(UserRole.PARENT, db)

        # Get any error/success messages from session
        error = request.session.pop("error", None)
        success = request.session.pop("success", None)

        return templates.TemplateResponse(
            "manager/create_user.html",
            {
                "request": request,
                "user": current_user,
                "parents": parents,
                "error": error,
                "success": success
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/users/create")
async def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    role: str = Form(...),
    # Manager fields
    department: Optional[str] = Form(None),
    access_level: Optional[int] = Form(1),
    # Teacher fields
    subject_specialization: Optional[str] = Form(None),
    teacher_hire_date: Optional[str] = Form(None),
    salary: Optional[str] = Form(None),
    # Student fields
    student_enrollment_date: Optional[str] = Form(None),
    grade_level: Optional[str] = Form(None),
    parent_id: Optional[str] = Form(None),  # Changed to str to handle empty strings
    # Parent fields
    phone_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    # Worker fields
    job_title: Optional[str] = Form(None),
    worker_hire_date: Optional[str] = Form(None),
    hourly_rate: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process user creation form."""
    try:
        require_manager(current_user)

        # Convert role string to enum
        user_role = UserRole(role)

        # Normalize parent_id: convert empty string to None, then to int if not None
        parent_id_normalized = None
        if parent_id and parent_id.strip():
            try:
                parent_id_normalized = int(parent_id)
            except ValueError:
                request.session["error"] = "Invalid parent ID format."
                return RedirectResponse(url="/manager/users/create", status_code=302)

        # Build profile data based on role
        profile_data = {}

        if user_role == UserRole.MANAGER:
            profile_data = {
                'department': department,
                'access_level': access_level or 1
            }
        elif user_role == UserRole.TEACHER:
            profile_data = {
                'subject_specialization': subject_specialization,
                'hire_date': datetime.strptime(teacher_hire_date, '%Y-%m-%d').date() if teacher_hire_date else None,
                'salary': Decimal(salary) if salary else None
            }
        elif user_role == UserRole.STUDENT:
            profile_data = {
                'enrollment_date': datetime.strptime(student_enrollment_date, '%Y-%m-%d').date() if student_enrollment_date else date.today(),
                'grade_level': grade_level,
                'parent_id': parent_id_normalized
            }
        elif user_role == UserRole.PARENT:
            profile_data = {
                'phone_number': phone_number,
                'address': address
            }
        elif user_role == UserRole.WORKER:
            profile_data = {
                'job_title': job_title,
                'hire_date': datetime.strptime(worker_hire_date, '%Y-%m-%d').date() if worker_hire_date else None,
                'hourly_rate': Decimal(hourly_rate) if hourly_rate else None
            }

        # Create user with profile
        user, error = UserService.create_user_with_profile(
            username, password, email, full_name, user_role, profile_data, db
        )

        if error:
            request.session["error"] = error
            return RedirectResponse(url="/manager/users/create", status_code=302)

        request.session["success"] = f"User '{username}' created successfully."
        return RedirectResponse(url="/manager/users", status_code=302)

    except ValueError as e:
        request.session["error"] = f"Invalid role or data: {str(e)}"
        return RedirectResponse(url="/manager/users/create", status_code=302)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        request.session["error"] = f"Error creating user: {str(e)}"
        return RedirectResponse(url="/manager/users/create", status_code=302)


# ============================================================================
# COURSE MANAGEMENT ROUTES
# ============================================================================

@router.get("/courses", response_class=HTMLResponse)
async def list_courses(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display list of all courses."""
    try:
        require_manager(current_user)
        courses = CourseService.get_all_courses(db)

        # Get success message from session if any
        success = request.session.pop("success", None)

        return templates.TemplateResponse(
            "manager/courses.html",
            {
                "request": request,
                "user": current_user,
                "courses": courses,
                "success": success
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/courses/create", response_class=HTMLResponse)
async def create_course_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display course creation form."""
    try:
        require_manager(current_user)

        # Get list of teachers
        teachers = UserService.get_users_by_role(UserRole.TEACHER, db)

        # Get any error/success messages from session
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "manager/create_course.html",
            {
                "request": request,
                "user": current_user,
                "teachers": teachers,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/courses/create")
async def create_course(
    request: Request,
    course_name: str = Form(...),
    course_code: str = Form(...),
    description: Optional[str] = Form(None),
    teacher_id: Optional[str] = Form(None),  # Changed to str to handle empty strings
    capacity: int = Form(...),
    fee: str = Form(...),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process course creation form."""
    try:
        require_manager(current_user)

        # Parse dates
        parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None

        # Normalize teacher_id: convert empty string to None, then to int if not None
        teacher_id_normalized = None
        if teacher_id and teacher_id.strip():
            try:
                teacher_id_normalized = int(teacher_id)
            except ValueError:
                request.session["error"] = "Invalid teacher ID format."
                return RedirectResponse(url="/manager/courses/create", status_code=302)

        # Create course
        course, error = CourseService.create_course(
            course_name=course_name,
            course_code=course_code,
            description=description,
            teacher_id=teacher_id_normalized,
            capacity=capacity,
            fee=Decimal(fee),
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            db=db
        )

        if error:
            request.session["error"] = error
            return RedirectResponse(url="/manager/courses/create", status_code=302)

        request.session["success"] = f"Course '{course_name}' created successfully."
        return RedirectResponse(url="/manager/courses", status_code=302)

    except ValueError as e:
        request.session["error"] = f"Invalid data: {str(e)}"
        return RedirectResponse(url="/manager/courses/create", status_code=302)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        request.session["error"] = f"Error creating course: {str(e)}"
        return RedirectResponse(url="/manager/courses/create", status_code=302)


# ============================================================================
# QUEUE MONITORING ROUTES
# ============================================================================

@router.get("/queues", response_class=HTMLResponse)
async def view_queues(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display all course queues and suggestions."""
    try:
        require_manager(current_user)

        # Get queue summaries
        queue_summaries = EnrollmentService.get_all_course_queues_summary(db)

        # Filter courses that need new classes (5+ students waiting)
        courses_needing_classes = [
            summary for summary in queue_summaries
            if summary['needs_new_class']
        ]

        return templates.TemplateResponse(
            "manager/queues.html",
            {
                "request": request,
                "user": current_user,
                "queue_summaries": queue_summaries,
                "courses_needing_classes": courses_needing_classes
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/queues/course/{course_id}", response_class=HTMLResponse)
async def view_course_queue(
    request: Request,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display detailed queue for a specific course."""
    try:
        require_manager(current_user)

        # Get course
        course = CourseService.get_course_by_id(course_id, db)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Get queue info
        queue_info = EnrollmentService.get_course_queue_info(course_id, db)

        return templates.TemplateResponse(
            "manager/course_queue_detail.html",
            {
                "request": request,
                "user": current_user,
                "course": course,
                "queue_info": queue_info
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# FINANCIAL ROUTES
# ============================================================================

@router.get("/financial-report", response_class=HTMLResponse)
async def financial_report(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display financial report with charts."""
    try:
        require_manager(current_user)

        # Default to current month if no dates provided
        from datetime import timedelta
        if not start_date or not end_date:
            today = date.today()
            start = date(today.year, today.month, 1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        else:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)

        # Generate financial summary
        summary = FinancialReportService.generate_financial_summary(db, start, end)

        return templates.TemplateResponse(
            "manager/financial_report.html",
            {
                "request": request,
                "user": current_user,
                "summary": summary,
                "start_date": start,
                "end_date": end
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/expenses", response_class=HTMLResponse)
async def list_expenses(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display list of all expenses."""
    try:
        require_manager(current_user)

        expenses = ExpenseService.get_expenses(db)

        return templates.TemplateResponse(
            "manager/expenses.html",
            {
                "request": request,
                "user": current_user,
                "expenses": expenses
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/expenses/create", response_class=HTMLResponse)
async def create_expense_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display expense creation form."""
    try:
        require_manager(current_user)

        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "manager/expense_create.html",
            {
                "request": request,
                "user": current_user,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/expenses/create")
async def create_expense(
    request: Request,
    category: str = Form(...),
    amount: str = Form(...),
    expense_date: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit new expense."""
    try:
        require_manager(current_user)

        try:
            cat = ExpenseCategory(category)
            amt = Decimal(amount)
            exp_date = date.fromisoformat(expense_date)

            ExpenseService.create_expense(
                db,
                category=cat,
                amount=amt,
                expense_date=exp_date,
                description=description if description else None,
                manager_id=current_user.id
            )

            request.session["success"] = "Expense recorded successfully!"
            return RedirectResponse(url="/manager/expenses", status_code=302)

        except ValueError as e:
            request.session["error"] = f"Invalid expense data: {str(e)}"
            return RedirectResponse(url="/manager/expenses/create", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# MAINTENANCE ROUTES
# ============================================================================

@router.get("/maintenance", response_class=HTMLResponse)
async def list_maintenance_tasks(
    request: Request,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display all maintenance tasks."""
    try:
        require_manager(current_user)

        # Get tasks based on status filter
        if status:
            try:
                task_status = TaskStatus(status)
                tasks = MaintenanceService.get_tasks_by_status(db, task_status)
            except ValueError:
                tasks = MaintenanceService.get_all_tasks(db)
        else:
            tasks = MaintenanceService.get_all_tasks(db)

        # Get workers for assignment
        workers = UserService.get_users_by_role(UserRole.WORKER, db)

        # Get statistics
        stats = MaintenanceService.get_task_statistics(db)

        return templates.TemplateResponse(
            "manager/maintenance.html",
            {
                "request": request,
                "user": current_user,
                "tasks": tasks,
                "workers": workers,
                "stats": stats,
                "current_status": status
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/maintenance/create", response_class=HTMLResponse)
async def create_maintenance_task_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display maintenance task creation form."""
    try:
        require_manager(current_user)

        workers = UserService.get_users_by_role(UserRole.WORKER, db)

        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "manager/maintenance_create.html",
            {
                "request": request,
                "user": current_user,
                "workers": workers,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/maintenance/create")
async def create_maintenance_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    priority: str = Form(...),
    worker_id: Optional[str] = Form(None),  # Changed to str to handle empty strings
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit new maintenance task."""
    try:
        require_manager(current_user)

        try:
            task_priority = TaskPriority(priority)

            task = MaintenanceService.create_task(
                db,
                title=title,
                description=description if description else None,
                priority=task_priority,
                reported_by_user_id=current_user.id,
                location=location if location else None
            )

            # Normalize worker_id: convert empty string to None, then to int if not None
            worker_id_normalized = None
            if worker_id and worker_id.strip():
                try:
                    worker_id_normalized = int(worker_id)
                    MaintenanceService.assign_task(db, task.id, worker_id_normalized, current_user.id)
                except ValueError:
                    request.session["error"] = "Invalid worker ID format."
                    return RedirectResponse(url="/manager/maintenance/create", status_code=302)

            request.session["success"] = "Maintenance task created successfully!"
            return RedirectResponse(url="/manager/maintenance", status_code=302)

        except ValueError as e:
            request.session["error"] = f"Error creating task: {str(e)}"
            return RedirectResponse(url="/manager/maintenance/create", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/maintenance/{task_id}/assign")
async def assign_maintenance_task(
    request: Request,
    task_id: int,
    worker_id: Optional[str] = Form(None),  # Changed to str to handle empty strings
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign task to a worker."""
    try:
        require_manager(current_user)

        # Normalize worker_id: convert empty string to None, then to int if not None
        if not worker_id or not worker_id.strip():
            request.session["error"] = "Please select a worker to assign."
            return RedirectResponse(url="/manager/maintenance", status_code=302)

        try:
            worker_id_int = int(worker_id)
            MaintenanceService.assign_task(db, task_id, worker_id_int, current_user.id)
            request.session["success"] = "Task assigned successfully!"
        except ValueError as e:
            request.session["error"] = str(e) if "Invalid" not in str(e) else "Invalid worker ID format."

        return RedirectResponse(url="/manager/maintenance", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
