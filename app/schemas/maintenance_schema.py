"""
Maintenance task schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

from app.models.maintenance_task import TaskPriority, TaskStatus


class MaintenanceTaskCreate(BaseModel):
    """Schema for creating a maintenance task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    priority: TaskPriority = TaskPriority.MEDIUM

    model_config = ConfigDict(from_attributes=True)


class MaintenanceTaskUpdate(BaseModel):
    """Schema for updating a maintenance task."""
    status: Optional[TaskStatus] = None
    location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaintenanceTaskResponse(BaseModel):
    """Schema for maintenance task response."""
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    priority: TaskPriority
    status: TaskStatus
    assigned_to_worker_id: Optional[int] = None
    reported_by_user_id: Optional[int] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
