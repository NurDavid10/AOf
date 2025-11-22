"""
Pydantic schemas for user-related data validation.

These schemas are used for request/response validation in API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class UserBase(BaseModel):
    """Base schema for user data."""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(manager|teacher|student|parent|worker)$")


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ManagerCreate(BaseModel):
    """Schema for creating a manager profile."""
    user_id: int
    department: Optional[str] = Field(None, max_length=100)
    access_level: int = Field(default=1, ge=1, le=10)

    class Config:
        from_attributes = True


class ManagerResponse(BaseModel):
    """Schema for manager response data."""
    user_id: int
    department: Optional[str]
    access_level: int
    username: str
    full_name: str

    class Config:
        from_attributes = True


class TeacherCreate(BaseModel):
    """Schema for creating a teacher profile."""
    user_id: int
    subject_specialization: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[date] = None
    salary: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    class Config:
        from_attributes = True


class TeacherResponse(BaseModel):
    """Schema for teacher response data."""
    user_id: int
    subject_specialization: Optional[str]
    hire_date: Optional[date]
    salary_amount: Decimal
    username: str
    full_name: str

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    """Schema for creating a student profile."""
    user_id: int
    enrollment_date: Optional[date] = None
    grade_level: Optional[str] = Field(None, max_length=20)
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    """Schema for student response data."""
    user_id: int
    enrollment_date: Optional[date]
    grade_level: Optional[str]
    parent_id: Optional[int]
    has_parent: bool
    username: str
    full_name: str

    class Config:
        from_attributes = True


class ParentCreate(BaseModel):
    """Schema for creating a parent profile."""
    user_id: int
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class ParentResponse(BaseModel):
    """Schema for parent response data."""
    user_id: int
    phone_number: Optional[str]
    address: Optional[str]
    username: str
    full_name: str

    class Config:
        from_attributes = True


class WorkerCreate(BaseModel):
    """Schema for creating a worker profile."""
    user_id: int
    job_title: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[date] = None
    hourly_rate: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    class Config:
        from_attributes = True


class WorkerResponse(BaseModel):
    """Schema for worker response data."""
    user_id: int
    job_title: Optional[str]
    hire_date: Optional[date]
    rate: Decimal
    username: str
    full_name: str

    class Config:
        from_attributes = True
