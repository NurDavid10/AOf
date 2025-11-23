"""
Parent routes for enrollment and queue management.

This module provides endpoints for parents to manage their children's enrollments
and view queue positions.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.models.payment import PaymentType, PaymentMethod
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService
from app.services.payment_service import PaymentService
from typing import Optional


# Set up templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Create router
router = APIRouter(prefix="/parent", tags=["parent"])


def require_parent(user: User):
    """Helper function to ensure user is a parent."""
    if user.role != UserRole.PARENT:
        raise HTTPException(status_code=403, detail="Access denied. Parent role required.")
    return user


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard", response_class=HTMLResponse)
async def parent_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Parent dashboard with statistics."""
    try:
        require_parent(current_user)

        # Get parent's children
        children = UserService.get_parent_children(current_user.id, db)
        children_count = len(children)

        # Count total enrolled courses across all children
        total_courses = 0
        for child in children:
            courses_and_queues = EnrollmentService.get_student_courses_and_queues(child.user_id, db)
            total_courses += len(courses_and_queues['enrolled_courses'])

        # For now, set pending payments to 0
        # This can be enhanced later with actual payment tracking
        pending_payments = 0

        return templates.TemplateResponse(
            "parent/dashboard.html",
            {
                "request": request,
                "user": current_user,
                "children_count": children_count,
                "total_courses": total_courses,
                "pending_payments": pending_payments
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# CHILDREN MANAGEMENT
# ============================================================================

@router.get("/children", response_class=HTMLResponse)
async def view_children(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display parent's children and their enrollments."""
    try:
        require_parent(current_user)

        # Get parent's children
        children = UserService.get_parent_children(current_user.id, db)

        # Get enrollment and queue info for each child
        children_info = []
        for child in children:
            courses_and_queues = EnrollmentService.get_student_courses_and_queues(child.user_id, db)
            children_info.append({
                'child': child,
                'enrolled_courses': courses_and_queues['enrolled_courses'],
                'queued_courses': courses_and_queues['queued_courses']
            })

        # Get success/error messages from session
        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "parent/children.html",
            {
                "request": request,
                "user": current_user,
                "children_info": children_info,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# ENROLLMENT ROUTES
# ============================================================================

@router.get("/enroll", response_class=HTMLResponse)
async def enroll_child_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display form to enroll a child in a course."""
    try:
        require_parent(current_user)

        # Get parent's children
        children = UserService.get_parent_children(current_user.id, db)

        # Get all available courses
        courses = CourseService.get_all_courses(db)

        # Get error message from session if any
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "parent/enroll.html",
            {
                "request": request,
                "user": current_user,
                "children": children,
                "courses": courses,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/enroll")
async def enroll_child(
    request: Request,
    student_id: Optional[str] = Form(None),  # Changed to str to handle empty strings from dropdown
    course_id: Optional[str] = Form(None),  # Changed to str to handle empty strings from dropdown
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process child enrollment in a course."""
    try:
        require_parent(current_user)

        # Validate and convert IDs from strings
        if not student_id or not student_id.strip():
            request.session["error"] = "Please select a child."
            return RedirectResponse(url="/parent/enroll", status_code=302)
        if not course_id or not course_id.strip():
            request.session["error"] = "Please select a course."
            return RedirectResponse(url="/parent/enroll", status_code=302)

        try:
            student_id_int = int(student_id)
            course_id_int = int(course_id)
        except ValueError:
            request.session["error"] = "Invalid student or course selection."
            return RedirectResponse(url="/parent/enroll", status_code=302)

        # Verify the student is a child of the current parent
        children = UserService.get_parent_children(current_user.id, db)
        child_ids = [child.user_id for child in children]

        if student_id_int not in child_ids:
            request.session["error"] = "You can only enroll your own children."
            return RedirectResponse(url="/parent/enroll", status_code=302)

        # Attempt enrollment
        success, message, info = EnrollmentService.enroll_student(student_id_int, course_id_int, db)

        if success:
            if info and info['enrolled']:
                request.session["success"] = "Child enrolled successfully in the course!"
            else:
                request.session["success"] = message  # Will show queue position
        else:
            request.session["error"] = message

        return RedirectResponse(url="/parent/children", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        request.session["error"] = f"Error enrolling child: {str(e)}"
        return RedirectResponse(url="/parent/enroll", status_code=302)


@router.post("/drop-enrollment")
async def drop_enrollment(
    request: Request,
    enrollment_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Drop a child's enrollment from a course."""
    try:
        require_parent(current_user)

        # Get the enrollment to verify ownership
        from app.models.course import CourseEnrollment
        enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.id == enrollment_id
        ).first()

        if not enrollment:
            request.session["error"] = "Enrollment not found."
            return RedirectResponse(url="/parent/children", status_code=302)

        # Verify the student is a child of the current parent
        children = UserService.get_parent_children(current_user.id, db)
        child_ids = [child.user_id for child in children]

        if enrollment.student_id not in child_ids:
            request.session["error"] = "You can only manage your own children's enrollments."
            return RedirectResponse(url="/parent/children", status_code=302)

        # Drop enrollment
        success, message = EnrollmentService.drop_enrollment(enrollment_id, db)

        if success:
            request.session["success"] = "Enrollment dropped successfully."
        else:
            request.session["error"] = message

        return RedirectResponse(url="/parent/children", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        request.session["error"] = f"Error dropping enrollment: {str(e)}"
        return RedirectResponse(url="/parent/children", status_code=302)


# ============================================================================
# QUEUE VIEWING ROUTES
# ============================================================================

@router.get("/queue/{student_id}/{course_id}", response_class=HTMLResponse)
async def view_queue_position(
    request: Request,
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View detailed queue position for a child in a course."""
    try:
        require_parent(current_user)

        # Verify the student is a child of the current parent
        children = UserService.get_parent_children(current_user.id, db)
        child_ids = [child.user_id for child in children]

        if student_id not in child_ids:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get student and course info
        from app.models.user import Student
        student = db.query(Student).filter(Student.user_id == student_id).first()
        course = CourseService.get_course_by_id(course_id, db)

        if not student or not course:
            raise HTTPException(status_code=404, detail="Student or course not found")

        # Get queue position
        position = EnrollmentService.get_student_queue_position(student_id, course_id, db)

        # Get full queue info
        queue_info = EnrollmentService.get_course_queue_info(course_id, db)

        return templates.TemplateResponse(
            "parent/queue_detail.html",
            {
                "request": request,
                "user": current_user,
                "student": student,
                "course": course,
                "position": position,
                "queue_info": queue_info
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# PAYMENT ROUTES
# ============================================================================

@router.get("/payments", response_class=HTMLResponse)
async def view_payments(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display parent's payment history."""
    try:
        require_parent(current_user)

        # Get payment summary and history
        payments = PaymentService.get_parent_payments(db, current_user.id)
        summary = PaymentService.get_payment_summary(db, current_user.id)

        return templates.TemplateResponse(
            "parent/payments.html",
            {
                "request": request,
                "user": current_user,
                "payments": payments,
                "summary": summary
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/payments/create", response_class=HTMLResponse)
async def create_payment_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display payment creation form."""
    try:
        require_parent(current_user)

        # Get parent's children
        children = UserService.get_parent_children(current_user.id, db)

        # Get all courses
        courses = CourseService.get_all_courses(db)

        # Get messages
        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "parent/payment_create.html",
            {
                "request": request,
                "user": current_user,
                "children": children,
                "courses": courses,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/payments/create")
async def create_payment(
    request: Request,
    course_id: Optional[str] = Form(None),  # Changed to str to handle empty strings from dropdown
    amount: str = Form(...),
    payment_method: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit new payment."""
    try:
        require_parent(current_user)

        # Validate course_id
        if not course_id or not course_id.strip():
            request.session["error"] = "Please select a course."
            return RedirectResponse(url="/parent/payments/create", status_code=302)

        try:
            course_id_int = int(course_id)
        except ValueError:
            request.session["error"] = "Invalid course selection."
            return RedirectResponse(url="/parent/payments/create", status_code=302)

        # Validate and create payment
        try:
            amount_decimal = Decimal(amount)
            method = PaymentMethod(payment_method)

            PaymentService.record_payment(
                db,
                payer_id=current_user.id,
                amount=amount_decimal,
                payment_type=PaymentType.TUITION,
                payment_method=method,
                reference_id=course_id_int,
                notes=notes if notes else None
            )

            request.session["success"] = "Payment recorded successfully!"
            return RedirectResponse(url="/parent/payments", status_code=302)

        except ValueError as e:
            request.session["error"] = f"Invalid payment data: {str(e)}"
            return RedirectResponse(url="/parent/payments/create", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
