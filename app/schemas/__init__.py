"""
Schemas package initialization.

This module imports and exports all Pydantic schemas for easy access.
"""

from app.schemas.user_schema import (
    UserBase, UserCreate, UserLogin, UserResponse,
    ManagerCreate, ManagerResponse,
    TeacherCreate, TeacherResponse,
    StudentCreate, StudentResponse,
    ParentCreate, ParentResponse,
    WorkerCreate, WorkerResponse
)
from app.schemas.course_schema import (
    CourseBase, CourseCreate, CourseUpdate, CourseResponse,
    EnrollmentCreate, EnrollmentResponse
)
from app.schemas.task_schema import (
    TaskBase, TaskCreate, TaskUpdate, TaskResponse,
    SubmissionCreate, SubmissionGrade, SubmissionResponse
)
from app.schemas.payment_schema import (
    PaymentBase, PaymentCreate, PaymentUpdate, PaymentResponse
)
from app.schemas.queue_schema import (
    QueueBase, QueueCreate, QueueResponse,
    QueueItemCreate, QueueItemUpdate, QueueItemResponse
)

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserLogin", "UserResponse",
    "ManagerCreate", "ManagerResponse",
    "TeacherCreate", "TeacherResponse",
    "StudentCreate", "StudentResponse",
    "ParentCreate", "ParentResponse",
    "WorkerCreate", "WorkerResponse",
    # Course schemas
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse",
    "EnrollmentCreate", "EnrollmentResponse",
    # Task schemas
    "TaskBase", "TaskCreate", "TaskUpdate", "TaskResponse",
    "SubmissionCreate", "SubmissionGrade", "SubmissionResponse",
    # Payment schemas
    "PaymentBase", "PaymentCreate", "PaymentUpdate", "PaymentResponse",
    # Queue schemas
    "QueueBase", "QueueCreate", "QueueResponse",
    "QueueItemCreate", "QueueItemUpdate", "QueueItemResponse",
]
