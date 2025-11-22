"""
Models package initialization.

This module imports and exports all database models for easy access.
"""

from app.models.base import BaseModel, TimestampMixin
from app.models.user import User, Manager, Teacher, Student, Parent, Worker, UserRole
from app.models.course import Course, CourseEnrollment, EnrollmentStatus
from app.models.task import Task, TaskSubmission, TaskType
from app.models.payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from app.models.queue import Queue, QueueItem, QueueType, QueueItemStatus
from app.models.expense import Expense, ExpenseCategory
from app.models.maintenance_task import MaintenanceTask, TaskPriority, TaskStatus

__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    # User models
    "User",
    "Manager",
    "Teacher",
    "Student",
    "Parent",
    "Worker",
    "UserRole",
    # Course models
    "Course",
    "CourseEnrollment",
    "EnrollmentStatus",
    # Task models
    "Task",
    "TaskSubmission",
    "TaskType",
    # Payment models
    "Payment",
    "PaymentType",
    "PaymentMethod",
    "PaymentStatus",
    # Queue models
    "Queue",
    "QueueItem",
    "QueueType",
    "QueueItemStatus",
    # Expense models
    "Expense",
    "ExpenseCategory",
    # Maintenance task models
    "MaintenanceTask",
    "TaskPriority",
    "TaskStatus",
]
