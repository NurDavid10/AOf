"""
Student routes for viewing courses, tasks, and grades.

This module provides endpoints for students to view their academic information.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from decimal import Decimal

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.models.course import CourseEnrollment, EnrollmentStatus
from app.models.task import Task, TaskSubmission
from app.services.course_service import CourseService

# Set up templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Create router
router = APIRouter(prefix="/student", tags=["student"])


def require_student(user: User):
    """Helper function to ensure user is a student."""
    if user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Access denied. Student role required.")
    return user


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard", response_class=HTMLResponse)
async def student_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Student dashboard with statistics and quick actions."""
    try:
        require_student(current_user)

        # Get student's enrollments
        enrollments = CourseService.get_student_enrollments(current_user.id, db)
        active_enrollments = [e for e in enrollments if e.status == EnrollmentStatus.ACTIVE]
        course_count = len(active_enrollments)

        # Get all tasks for student's enrolled courses
        course_ids = [e.course_id for e in active_enrollments]
        pending_tasks_count = 0
        if course_ids:
            # Get all tasks for these courses
            all_tasks = db.query(Task).filter(Task.course_id.in_(course_ids)).all()

            # Count tasks that haven't been submitted yet
            for task in all_tasks:
                submission = db.query(TaskSubmission).filter(
                    TaskSubmission.task_id == task.id,
                    TaskSubmission.student_id == current_user.id
                ).first()
                if not submission:
                    pending_tasks_count += 1

        # Calculate average grade across all submissions
        submissions = db.query(TaskSubmission).filter(
            TaskSubmission.student_id == current_user.id,
            TaskSubmission.grade.isnot(None)
        ).all()

        average_grade = 0.0
        if submissions:
            total_percentage = 0.0
            for submission in submissions:
                if submission.task and submission.task.max_points:
                    percentage = float((submission.grade / submission.task.max_points) * 100)
                    total_percentage += percentage
            average_grade = round(total_percentage / len(submissions), 1)

        return templates.TemplateResponse(
            "student/dashboard.html",
            {
                "request": request,
                "user": current_user,
                "course_count": course_count,
                "pending_tasks_count": pending_tasks_count,
                "average_grade": average_grade
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
    """View all courses student is enrolled in."""
    try:
        require_student(current_user)

        # Get student's active enrollments
        enrollments = db.query(CourseEnrollment).filter(
            CourseEnrollment.student_id == current_user.id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE
        ).all()

        return templates.TemplateResponse(
            "student/courses.html",
            {
                "request": request,
                "user": current_user,
                "enrollments": enrollments
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# TASKS
# ============================================================================

@router.get("/tasks", response_class=HTMLResponse)
async def view_tasks(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View all tasks for student's enrolled courses."""
    try:
        require_student(current_user)

        # Get student's active enrollments
        enrollments = db.query(CourseEnrollment).filter(
            CourseEnrollment.student_id == current_user.id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE
        ).all()

        course_ids = [e.course_id for e in enrollments]

        # Get all tasks for these courses
        tasks_data = []
        if course_ids:
            tasks = db.query(Task).filter(Task.course_id.in_(course_ids)).order_by(Task.due_date).all()

            for task in tasks:
                # Check if student has submitted
                submission = db.query(TaskSubmission).filter(
                    TaskSubmission.task_id == task.id,
                    TaskSubmission.student_id == current_user.id
                ).first()

                task_status = "Not Submitted"
                if submission:
                    if submission.is_graded:
                        task_status = "Graded"
                    else:
                        task_status = "Submitted"

                tasks_data.append({
                    'task': task,
                    'submission': submission,
                    'status': task_status
                })

        return templates.TemplateResponse(
            "student/tasks.html",
            {
                "request": request,
                "user": current_user,
                "tasks_data": tasks_data
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# GRADES
# ============================================================================

@router.get("/grades", response_class=HTMLResponse)
async def view_grades(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View all grades for student's submissions."""
    try:
        require_student(current_user)

        # Get all graded submissions
        submissions = db.query(TaskSubmission).filter(
            TaskSubmission.student_id == current_user.id,
            TaskSubmission.grade.isnot(None)
        ).all()

        # Organize by course
        courses_grades = {}
        for submission in submissions:
            course_id = submission.task.course_id
            course_name = submission.task.course.course_name

            if course_id not in courses_grades:
                courses_grades[course_id] = {
                    'course_name': course_name,
                    'course_code': submission.task.course.course_code,
                    'submissions': [],
                    'total_points': Decimal('0'),
                    'max_points': Decimal('0')
                }

            courses_grades[course_id]['submissions'].append(submission)
            courses_grades[course_id]['total_points'] += submission.grade
            courses_grades[course_id]['max_points'] += submission.task.max_points

        # Calculate averages for each course
        for course_data in courses_grades.values():
            if course_data['max_points'] > 0:
                course_data['average'] = round(
                    float((course_data['total_points'] / course_data['max_points']) * 100), 1
                )
            else:
                course_data['average'] = 0.0

        # Calculate overall average
        overall_total = sum(c['total_points'] for c in courses_grades.values())
        overall_max = sum(c['max_points'] for c in courses_grades.values())
        overall_average = 0.0
        if overall_max > 0:
            overall_average = round(float((overall_total / overall_max) * 100), 1)

        return templates.TemplateResponse(
            "student/grades.html",
            {
                "request": request,
                "user": current_user,
                "courses_grades": courses_grades,
                "overall_average": overall_average
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
