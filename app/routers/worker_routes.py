"""
Worker routes for maintenance task management.

This module provides endpoints for workers to view and update their assigned tasks.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.models.maintenance_task import TaskPriority, TaskStatus
from app.services.maintenance_service import MaintenanceService

# Set up templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Create router
router = APIRouter(prefix="/worker", tags=["worker"])


def require_worker(user: User):
    """Helper function to ensure user is a worker."""
    if user.role != UserRole.WORKER:
        raise HTTPException(status_code=403, detail="Access denied. Worker role required.")
    return user


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard", response_class=HTMLResponse)
async def worker_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display worker dashboard with task statistics."""
    try:
        require_worker(current_user)

        # Get worker's tasks
        pending_tasks = MaintenanceService.get_worker_tasks(db, current_user.id, TaskStatus.PENDING)
        in_progress_tasks = MaintenanceService.get_worker_tasks(db, current_user.id, TaskStatus.IN_PROGRESS)
        completed_tasks = MaintenanceService.get_worker_tasks(db, current_user.id, TaskStatus.COMPLETED)

        # Get task statistics
        stats = {
            'pending': len(pending_tasks),
            'in_progress': len(in_progress_tasks),
            'completed': len(completed_tasks),
            'total': len(pending_tasks) + len(in_progress_tasks) + len(completed_tasks)
        }

        # Get success/error messages
        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "worker/dashboard.html",
            {
                "request": request,
                "user": current_user,
                "stats": stats,
                "pending_tasks": pending_tasks[:5],  # Show only 5 most recent
                "in_progress_tasks": in_progress_tasks[:5],
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# TASK MANAGEMENT
# ============================================================================

@router.get("/tasks", response_class=HTMLResponse)
async def view_tasks(
    request: Request,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display worker's assigned tasks."""
    try:
        require_worker(current_user)

        # Get tasks based on status filter
        if status:
            try:
                task_status = TaskStatus(status)
                tasks = MaintenanceService.get_worker_tasks(db, current_user.id, task_status)
            except ValueError:
                tasks = MaintenanceService.get_worker_tasks(db, current_user.id)
        else:
            tasks = MaintenanceService.get_worker_tasks(db, current_user.id)

        return templates.TemplateResponse(
            "worker/tasks.html",
            {
                "request": request,
                "user": current_user,
                "tasks": tasks,
                "current_status": status
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/tasks/{task_id}", response_class=HTMLResponse)
async def view_task_detail(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display detailed view of a task."""
    try:
        require_worker(current_user)

        task = MaintenanceService.get_task_by_id(db, task_id)
        if not task:
            request.session["error"] = "Task not found"
            return RedirectResponse(url="/worker/tasks", status_code=302)

        # Verify this task is assigned to the current worker
        if task.assigned_to_worker_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied. Task not assigned to you.")

        # Get success/error messages
        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "worker/task_detail.html",
            {
                "request": request,
                "user": current_user,
                "task": task,
                "success": success,
                "error": error
            }
        )
    except HTTPException as e:
        if e.status_code == 403:
            request.session["error"] = "You don't have permission to view this task"
            return RedirectResponse(url="/worker/tasks", status_code=302)
        return RedirectResponse(url="/login", status_code=302)


@router.post("/tasks/{task_id}/status")
async def update_task_status(
    request: Request,
    task_id: int,
    new_status: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the status of a task."""
    try:
        require_worker(current_user)

        # Get the task
        task = MaintenanceService.get_task_by_id(db, task_id)
        if not task:
            request.session["error"] = "Task not found"
            return RedirectResponse(url="/worker/tasks", status_code=302)

        # Verify this task is assigned to the current worker
        if task.assigned_to_worker_id != current_user.id:
            request.session["error"] = "You don't have permission to update this task"
            return RedirectResponse(url="/worker/tasks", status_code=302)

        # Update status
        try:
            task_status = TaskStatus(new_status)
            MaintenanceService.update_task_status(db, task_id, task_status, current_user.id)
            request.session["success"] = f"Task status updated to {task_status.value.replace('_', ' ').title()}"
        except ValueError:
            request.session["error"] = "Invalid status"

        return RedirectResponse(url=f"/worker/tasks/{task_id}", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/tasks/{task_id}/notes")
async def add_task_notes(
    request: Request,
    task_id: int,
    notes: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add notes to a task."""
    try:
        require_worker(current_user)

        # Get the task
        task = MaintenanceService.get_task_by_id(db, task_id)
        if not task:
            request.session["error"] = "Task not found"
            return RedirectResponse(url="/worker/tasks", status_code=302)

        # Verify this task is assigned to the current worker
        if task.assigned_to_worker_id != current_user.id:
            request.session["error"] = "You don't have permission to update this task"
            return RedirectResponse(url="/worker/tasks", status_code=302)

        # Add notes
        MaintenanceService.add_notes(db, task_id, notes, current_user.id)
        request.session["success"] = "Notes added successfully"

        return RedirectResponse(url=f"/worker/tasks/{task_id}", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# REPORT ISSUE
# ============================================================================

@router.get("/report-issue", response_class=HTMLResponse)
async def report_issue_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display form to report a new maintenance issue."""
    try:
        require_worker(current_user)

        # Get success/error messages
        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "worker/report_issue.html",
            {
                "request": request,
                "user": current_user,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/report-issue")
async def report_issue(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    priority: str = Form("medium"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a new maintenance issue report."""
    try:
        require_worker(current_user)

        # Create the task
        try:
            task_priority = TaskPriority(priority)
            MaintenanceService.create_task(
                db,
                title=title,
                description=description if description else None,
                priority=task_priority,
                reported_by_user_id=current_user.id,
                location=location if location else None
            )
            request.session["success"] = "Issue reported successfully. A manager will review it."
        except ValueError as e:
            request.session["error"] = str(e)
            return RedirectResponse(url="/worker/report-issue", status_code=302)

        return RedirectResponse(url="/worker/dashboard", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
