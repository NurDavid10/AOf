"""
Pydantic schemas for task-related data validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TaskBase(BaseModel):
    """Base schema for task data."""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    task_type: str = Field(default="assignment", pattern="^(assignment|exam|project|homework)$")
    max_points: Decimal = Field(default=Decimal("100.00"), ge=0, decimal_places=2)

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    course_id: int


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    task_type: Optional[str] = Field(None, pattern="^(assignment|exam|project|homework)$")
    max_points: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """Schema for task response data."""
    id: int
    course_id: int
    course_name: str
    created_by: Optional[int]
    creator_name: str
    is_overdue: bool
    submission_count: int
    graded_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    """Schema for creating a task submission."""
    task_id: int
    submission_text: Optional[str] = None

    class Config:
        from_attributes = True


class SubmissionGrade(BaseModel):
    """Schema for grading a submission."""
    grade: Decimal = Field(..., ge=0, decimal_places=2)
    feedback: Optional[str] = None

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    """Schema for submission response data."""
    id: int
    task_id: int
    student_id: int
    task_title: str
    student_name: str
    submission_date: datetime
    submission_text: Optional[str]
    grade: Optional[Decimal]
    feedback: Optional[str]
    is_graded: bool
    grade_percentage: float
    was_late: bool

    class Config:
        from_attributes = True
