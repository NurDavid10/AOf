"""
Teacher routes for course management, tasks, and grading.

This module provides endpoints for teachers to manage their courses and students.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.models.task import TaskType
from app.models.course import Course, CourseEnrollment, EnrollmentStatus
from app.models.task import Task, TaskSubmission
from app.services.course_service import CourseService

# Set up templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Create router
router = APIRouter(prefix="/teacher", tags=["teacher"])


def require_teacher(user: User):
    """Helper function to ensure user is a teacher."""
    if user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Access denied. Teacher role required.")
    return user


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard", response_class=HTMLResponse)
async def teacher_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Teacher dashboard with statistics and quick actions."""
    try:
        require_teacher(current_user)

        # Get teacher's courses
        courses = CourseService.get_courses_by_teacher(current_user.id, db)
        course_count = len(courses)

        # Calculate total enrolled students across all courses
        total_students = 0
        for course in courses:
            enrollments = db.query(CourseEnrollment).filter(
                CourseEnrollment.course_id == course.id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            ).count()
            total_students += enrollments

        # Count pending submissions (ungraded)
        # Get all tasks created by this teacher
        teacher_tasks = db.query(Task).filter(Task.created_by == current_user.id).all()
        task_ids = [t.id for t in teacher_tasks]

        pending_submissions = 0
        if task_ids:
            pending_submissions = db.query(TaskSubmission).filter(
                TaskSubmission.task_id.in_(task_ids),
                TaskSubmission.grade == None
            ).count()

        return templates.TemplateResponse(
            "teacher/dashboard.html",
            {
                "request": request,
                "user": current_user,
                "course_count": course_count,
                "total_students": total_students,
                "pending_submissions": pending_submissions
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# COURSES
# ============================================================================

@router.get("/courses", response_class=HTMLResponse)
async def view_courses(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View all courses taught by the teacher."""
    try:
        require_teacher(current_user)

        # Get teacher's courses
        courses = CourseService.get_courses_by_teacher(current_user.id, db)

        # Enhance courses with enrollment counts
        courses_data = []
        for course in courses:
            enrolled_count = db.query(CourseEnrollment).filter(
                CourseEnrollment.course_id == course.id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            ).count()

            courses_data.append({
                'course': course,
                'enrolled_count': enrolled_count
            })

        return templates.TemplateResponse(
            "teacher/courses.html",
            {
                "request": request,
                "user": current_user,
                "courses_data": courses_data
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/courses/{course_id}/students", response_class=HTMLResponse)
async def view_course_students(
    course_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View students enrolled in a specific course."""
    try:
        require_teacher(current_user)

        # Get course and verify it belongs to this teacher
        course = CourseService.get_course_by_id(course_id, db)
        if not course:
            request.session["error"] = "Course not found."
            return RedirectResponse(url="/teacher/courses", status_code=302)

        if course.teacher_id != current_user.id:
            request.session["error"] = "You do not have permission to view this course."
            return RedirectResponse(url="/teacher/courses", status_code=302)

        # Get enrolled students
        enrollments = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE
        ).all()

        # Get error/success messages
        error = request.session.pop("error", None)
        success = request.session.pop("success", None)

        return templates.TemplateResponse(
            "teacher/course_students.html",
            {
                "request": request,
                "user": current_user,
                "course": course,
                "enrollments": enrollments,
                "error": error,
                "success": success
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# TASKS
# ============================================================================

@router.get("/tasks/create", response_class=HTMLResponse)
async def create_task_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display form to create a new task/assignment."""
    try:
        require_teacher(current_user)

        # Get teacher's courses
        courses = CourseService.get_courses_by_teacher(current_user.id, db)

        # Get error/success messages
        error = request.session.pop("error", None)
        success = request.session.pop("success", None)

        return templates.TemplateResponse(
            "teacher/create_task.html",
            {
                "request": request,
                "user": current_user,
                "courses": courses,
                "task_types": TaskType,
                "error": error,
                "success": success
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/tasks/create")
async def create_task(
    request: Request,
    course_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    task_type: str = Form(...),
    due_date: str = Form(...),
    max_points: float = Form(100.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process task creation form."""
    try:
        require_teacher(current_user)

        # Verify course belongs to teacher
        course = CourseService.get_course_by_id(course_id, db)
        if not course or course.teacher_id != current_user.id:
            request.session["error"] = "Invalid course or you don't have permission."
            return RedirectResponse(url="/teacher/tasks/create", status_code=302)

        # Parse due date
        try:
            due_date_obj = datetime.fromisoformat(due_date)
        except ValueError:
            request.session["error"] = "Invalid due date format."
            return RedirectResponse(url="/teacher/tasks/create", status_code=302)

        # Create task
        task = Task(
            title=title,
            description=description,
            course_id=course_id,
            due_date=due_date_obj,
            created_by=current_user.id,
            task_type=TaskType(task_type),
            max_points=Decimal(str(max_points))
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        request.session["success"] = f"Task '{title}' created successfully!"
        return RedirectResponse(url="/teacher/tasks/create", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        db.rollback()
        request.session["error"] = f"Error creating task: {str(e)}"
        return RedirectResponse(url="/teacher/tasks/create", status_code=302)


# ============================================================================
# SUBMISSIONS AND GRADING
# ============================================================================

@router.get("/submissions", response_class=HTMLResponse)
async def view_submissions(
    request: Request,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View all submissions for grading."""
    try:
        require_teacher(current_user)

        # Get teacher's courses
        courses = CourseService.get_courses_by_teacher(current_user.id, db)
        course_ids = [c.id for c in courses]

        # Get tasks for these courses
        query = db.query(Task).filter(Task.course_id.in_(course_ids))

        # Filter by course if specified
        if course_id:
            # Verify course belongs to teacher
            if course_id not in course_ids:
                request.session["error"] = "Invalid course."
                return RedirectResponse(url="/teacher/submissions", status_code=302)
            query = query.filter(Task.course_id == course_id)

        tasks = query.all()
        task_ids = [t.id for t in tasks]

        # Get ungraded submissions
        submissions = []
        if task_ids:
            submissions = db.query(TaskSubmission).filter(
                TaskSubmission.task_id.in_(task_ids),
                TaskSubmission.grade == None
            ).all()

        # Get error/success messages
        error = request.session.pop("error", None)
        success = request.session.pop("success", None)

        return templates.TemplateResponse(
            "teacher/submissions.html",
            {
                "request": request,
                "user": current_user,
                "submissions": submissions,
                "courses": courses,
                "selected_course_id": course_id,
                "error": error,
                "success": success
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/submissions/{submission_id}/grade", response_class=HTMLResponse)
async def grade_submission_form(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display form to grade a submission."""
    try:
        require_teacher(current_user)

        # Get submission
        submission = db.query(TaskSubmission).filter(
            TaskSubmission.id == submission_id
        ).first()

        if not submission:
            request.session["error"] = "Submission not found."
            return RedirectResponse(url="/teacher/submissions", status_code=302)

        # Verify this submission belongs to teacher's course
        task = submission.task
        course = task.course

        if course.teacher_id != current_user.id:
            request.session["error"] = "You do not have permission to grade this submission."
            return RedirectResponse(url="/teacher/submissions", status_code=302)

        # Get error/success messages
        error = request.session.pop("error", None)
        success = request.session.pop("success", None)

        return templates.TemplateResponse(
            "teacher/grade_submission.html",
            {
                "request": request,
                "user": current_user,
                "submission": submission,
                "task": task,
                "course": course,
                "error": error,
                "success": success
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: int,
    request: Request,
    grade: float = Form(...),
    feedback: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process grading of a submission."""
    try:
        require_teacher(current_user)

        # Get submission
        submission = db.query(TaskSubmission).filter(
            TaskSubmission.id == submission_id
        ).first()

        if not submission:
            request.session["error"] = "Submission not found."
            return RedirectResponse(url="/teacher/submissions", status_code=302)

        # Verify permission
        task = submission.task
        course = task.course

        if course.teacher_id != current_user.id:
            request.session["error"] = "You do not have permission to grade this submission."
            return RedirectResponse(url="/teacher/submissions", status_code=302)

        # Validate grade
        if grade < 0 or grade > float(task.max_points):
            request.session["error"] = f"Grade must be between 0 and {task.max_points}."
            return RedirectResponse(url=f"/teacher/submissions/{submission_id}/grade", status_code=302)

        # Assign grade
        submission.assign_grade(Decimal(str(grade)), feedback)
        db.commit()

        request.session["success"] = "Submission graded successfully!"
        return RedirectResponse(url="/teacher/submissions", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        db.rollback()
        request.session["error"] = f"Error grading submission: {str(e)}"
        return RedirectResponse(url=f"/teacher/submissions/{submission_id}/grade", status_code=302)
