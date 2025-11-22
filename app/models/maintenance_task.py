"""
Maintenance task models for facility management.

This module handles facility maintenance tasks, separate from academic tasks.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.models.base import BaseModel


class TaskPriority(str, enum.Enum):
    """Enumeration of task priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    """Enumeration of task statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenanceTask(BaseModel):
    """
    Maintenance task model representing facility maintenance work.

    Attributes:
        title: Task title/summary
        description: Detailed task description
        location: Location or classroom where the issue is (optional)
        priority: Task priority level
        status: Current task status
        assigned_to_worker_id: ID of the worker assigned to this task
        reported_by_user_id: ID of the user who reported this task
        started_at: Timestamp when task was started
        completed_at: Timestamp when task was completed
        notes: Additional notes about the task
    """

    __tablename__ = "maintenance_tasks"

    title = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200), nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    assigned_to_worker_id = Column(Integer, ForeignKey("workers.user_id", ondelete="SET NULL"), nullable=True)
    reported_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text)

    # Relationships
    assigned_to = relationship("Worker", backref="assigned_tasks", foreign_keys=[assigned_to_worker_id])
    reported_by = relationship("User", backref="reported_tasks", foreign_keys=[reported_by_user_id])

    @property
    def assigned_to_name(self) -> str:
        """
        Get the name of the assigned worker.

        Returns:
            str: Worker's full name or "Unassigned"
        """
        if self.assigned_to and self.assigned_to.user:
            return self.assigned_to.user.full_name
        return "Unassigned"

    @property
    def reported_by_name(self) -> str:
        """
        Get the name of the user who reported this task.

        Returns:
            str: Reporter's full name
        """
        if self.reported_by:
            return self.reported_by.full_name
        return "Unknown"

    @property
    def is_assigned(self) -> bool:
        """
        Check if task is assigned to a worker.

        Returns:
            bool: True if task is assigned, False otherwise
        """
        return self.assigned_to_worker_id is not None

    @property
    def is_completed(self) -> bool:
        """
        Check if task is completed.

        Returns:
            bool: True if task is completed, False otherwise
        """
        return self.status == TaskStatus.COMPLETED

    @property
    def is_pending(self) -> bool:
        """
        Check if task is pending.

        Returns:
            bool: True if task is pending, False otherwise
        """
        return self.status == TaskStatus.PENDING

    @property
    def is_in_progress(self) -> bool:
        """
        Check if task is in progress.

        Returns:
            bool: True if task is in progress, False otherwise
        """
        return self.status == TaskStatus.IN_PROGRESS

    @property
    def priority_display(self) -> str:
        """
        Get a display-friendly priority name.

        Returns:
            str: Priority name with proper capitalization
        """
        return self.priority.value.replace("_", " ").title()

    @property
    def status_display(self) -> str:
        """
        Get a display-friendly status name.

        Returns:
            str: Status name with proper capitalization
        """
        return self.status.value.replace("_", " ").title()

    def start_task(self):
        """Mark task as in progress and set start time."""
        self.status = TaskStatus.IN_PROGRESS
        if not self.started_at:
            self.started_at = datetime.utcnow()

    def complete_task(self):
        """Mark task as completed and set completion time."""
        self.status = TaskStatus.COMPLETED
        if not self.completed_at:
            self.completed_at = datetime.utcnow()

    def cancel_task(self):
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED

    def assign_to_worker(self, worker_id: int):
        """
        Assign task to a worker.

        Args:
            worker_id: ID of the worker to assign to
        """
        self.assigned_to_worker_id = worker_id
        # If task was pending, keep it pending for worker to start
        # Don't automatically change status

    def __repr__(self) -> str:
        """String representation of MaintenanceTask."""
        return f"<MaintenanceTask(id={self.id}, title='{self.title}', status='{self.status.value}')>"
