"""
Pydantic schemas for course-related data validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class CourseBase(BaseModel):
    """Base schema for course data."""
    course_name: str = Field(..., max_length=100)
    course_code: str = Field(..., max_length=20)
    description: Optional[str] = None
    capacity: int = Field(default=30, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    fee: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    class Config:
        from_attributes = True


class CourseCreate(CourseBase):
    """Schema for creating a new course."""
    teacher_id: Optional[int] = None


class CourseUpdate(BaseModel):
    """Schema for updating a course."""
    course_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    teacher_id: Optional[int] = None
    capacity: Optional[int] = Field(None, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    fee: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    class Config:
        from_attributes = True


class CourseResponse(CourseBase):
    """Schema for course response data."""
    id: int
    teacher_id: Optional[int]
    teacher_name: str
    enrolled_count: int
    available_slots: int
    is_full: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentCreate(BaseModel):
    """Schema for creating a course enrollment."""
    student_id: int
    course_id: int

    class Config:
        from_attributes = True


class EnrollmentResponse(BaseModel):
    """Schema for enrollment response data."""
    id: int
    student_id: int
    course_id: int
    student_name: str
    course_name: str
    enrollment_date: Optional[datetime]
    status: str
    is_active: bool

    class Config:
        from_attributes = True
