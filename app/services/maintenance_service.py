"""
Maintenance service for managing facility maintenance tasks.

This module provides business logic for maintenance task operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime

from app.models.maintenance_task import MaintenanceTask, TaskPriority, TaskStatus
from app.models.user import Worker, UserRole


class MaintenanceService:
    """Service class for maintenance task operations."""

    @staticmethod
    def create_task(
        db: Session,
        title: str,
        description: Optional[str],
        priority: TaskPriority,
        reported_by_user_id: int,
        location: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Create a new maintenance task.

        Args:
            db: Database session
            title: Task title
            description: Task description
            priority: Task priority level
            reported_by_user_id: ID of the user reporting the task
            location: Optional location or classroom where the issue is

        Returns:
            MaintenanceTask: Created task object

        Raises:
            ValueError: If validation fails
        """
        if not title or len(title.strip()) == 0:
            raise ValueError("Task title is required")

        task = MaintenanceTask(
            title=title.strip(),
            description=description,
            location=location.strip() if location else None,
            priority=priority,
            status=TaskStatus.PENDING,
            reported_by_user_id=reported_by_user_id
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[MaintenanceTask]:
        """
        Get a maintenance task by ID.

        Args:
            db: Database session
            task_id: Task ID

        Returns:
            MaintenanceTask or None: Task object if found
        """
        return db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()

    @staticmethod
    def assign_task(
        db: Session,
        task_id: int,
        worker_id: int,
        assigned_by_manager_id: int
    ) -> Optional[MaintenanceTask]:
        """
        Assign a task to a worker.

        Args:
            db: Database session
            task_id: Task ID
            worker_id: Worker user ID
            assigned_by_manager_id: Manager user ID assigning the task

        Returns:
            MaintenanceTask or None: Updated task if found

        Raises:
            ValueError: If worker doesn't exist or has wrong role
        """
        task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
        if not task:
            return None

        # Verify worker exists
        from app.models.user import User
        worker = db.query(User).filter(
            and_(
                User.id == worker_id,
                User.role == UserRole.WORKER
            )
        ).first()

        if not worker:
            raise ValueError("Invalid worker ID or user is not a worker")

        task.assign_to_worker(worker_id)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def update_task_status(
        db: Session,
        task_id: int,
        new_status: TaskStatus,
        updated_by_user_id: int
    ) -> Optional[MaintenanceTask]:
        """
        Update a task's status.

        Args:
            db: Database session
            task_id: Task ID
            new_status: New status
            updated_by_user_id: User ID updating the task

        Returns:
            MaintenanceTask or None: Updated task if found
        """
        task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
        if not task:
            return None

        # Update status and timestamps based on the new status
        if new_status == TaskStatus.IN_PROGRESS:
            task.start_task()
        elif new_status == TaskStatus.COMPLETED:
            task.complete_task()
        elif new_status == TaskStatus.CANCELLED:
            task.cancel_task()
        else:
            task.status = new_status

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def get_tasks_by_status(
        db: Session,
        status: Optional[TaskStatus] = None
    ) -> List[MaintenanceTask]:
        """
        Get tasks filtered by status.

        Args:
            db: Database session
            status: Optional status filter

        Returns:
            List[MaintenanceTask]: List of tasks
        """
        query = db.query(MaintenanceTask)

        if status:
            query = query.filter(MaintenanceTask.status == status)

        return query.order_by(MaintenanceTask.created_at.desc()).all()

    @staticmethod
    def get_worker_tasks(
        db: Session,
        worker_id: int,
        status: Optional[TaskStatus] = None
    ) -> List[MaintenanceTask]:
        """
        Get tasks assigned to a specific worker.

        Args:
            db: Database session
            worker_id: Worker user ID
            status: Optional status filter

        Returns:
            List[MaintenanceTask]: List of assigned tasks
        """
        query = db.query(MaintenanceTask).filter(
            MaintenanceTask.assigned_to_worker_id == worker_id
        )

        if status:
            query = query.filter(MaintenanceTask.status == status)

        return query.order_by(MaintenanceTask.created_at.desc()).all()

    @staticmethod
    def get_open_tasks_count(db: Session) -> int:
        """
        Count tasks that are pending or in progress.

        Args:
            db: Database session

        Returns:
            int: Count of open tasks
        """
        return db.query(MaintenanceTask).filter(
            MaintenanceTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).count()

    @staticmethod
    def get_all_tasks(
        db: Session,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[MaintenanceTask]:
        """
        Get all tasks with optional filters.

        Args:
            db: Database session
            status: Optional status filter
            priority: Optional priority filter

        Returns:
            List[MaintenanceTask]: List of tasks
        """
        query = db.query(MaintenanceTask)

        if status:
            query = query.filter(MaintenanceTask.status == status)
        if priority:
            query = query.filter(MaintenanceTask.priority == priority)

        return query.order_by(MaintenanceTask.created_at.desc()).all()

    @staticmethod
    def add_notes(
        db: Session,
        task_id: int,
        notes: str,
        user_id: int
    ) -> Optional[MaintenanceTask]:
        """
        Add notes to a task.

        Args:
            db: Database session
            task_id: Task ID
            notes: Notes to add
            user_id: User ID adding the notes

        Returns:
            MaintenanceTask or None: Updated task if found
        """
        task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
        if not task:
            return None

        # Append notes with timestamp and user info
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        new_note = f"[{timestamp}] {notes}"

        if task.notes:
            task.notes += f"\n{new_note}"
        else:
            task.notes = new_note

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def get_task_statistics(db: Session) -> dict:
        """
        Get statistics about maintenance tasks.

        Args:
            db: Database session

        Returns:
            dict: Statistics including counts by status
        """
        total = db.query(MaintenanceTask).count()
        pending = db.query(MaintenanceTask).filter(
            MaintenanceTask.status == TaskStatus.PENDING
        ).count()
        in_progress = db.query(MaintenanceTask).filter(
            MaintenanceTask.status == TaskStatus.IN_PROGRESS
        ).count()
        completed = db.query(MaintenanceTask).filter(
            MaintenanceTask.status == TaskStatus.COMPLETED
        ).count()
        cancelled = db.query(MaintenanceTask).filter(
            MaintenanceTask.status == TaskStatus.CANCELLED
        ).count()

        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'cancelled': cancelled,
            'open': pending + in_progress
        }

    @staticmethod
    def get_unassigned_tasks(db: Session) -> List[MaintenanceTask]:
        """
        Get all unassigned tasks.

        Args:
            db: Database session

        Returns:
            List[MaintenanceTask]: List of unassigned tasks
        """
        return db.query(MaintenanceTask).filter(
            MaintenanceTask.assigned_to_worker_id.is_(None)
        ).order_by(MaintenanceTask.priority.desc(), MaintenanceTask.created_at).all()

    @staticmethod
    def get_urgent_tasks(db: Session) -> List[MaintenanceTask]:
        """
        Get all urgent or high priority tasks that are not completed.

        Args:
            db: Database session

        Returns:
            List[MaintenanceTask]: List of urgent/high priority tasks
        """
        return db.query(MaintenanceTask).filter(
            and_(
                MaintenanceTask.priority.in_([TaskPriority.URGENT, TaskPriority.HIGH]),
                MaintenanceTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
            )
        ).order_by(MaintenanceTask.priority.desc(), MaintenanceTask.created_at).all()
