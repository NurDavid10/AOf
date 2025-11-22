"""
Pydantic schemas for queue-related data validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QueueBase(BaseModel):
    """Base schema for queue data."""
    queue_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    queue_type: str = Field(..., pattern="^(registration|payment|support|general)$")
    max_capacity: int = Field(default=0, ge=0)

    class Config:
        from_attributes = True


class QueueCreate(QueueBase):
    """Schema for creating a new queue."""
    pass


class QueueResponse(QueueBase):
    """Schema for queue response data."""
    id: int
    current_length: int
    in_progress_count: int
    is_full: bool
    next_position: int
    created_at: datetime

    class Config:
        from_attributes = True


class QueueItemCreate(BaseModel):
    """Schema for adding an item to a queue."""
    queue_id: int
    user_id: int
    priority: int = Field(default=0, ge=0, le=10)
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class QueueItemUpdate(BaseModel):
    """Schema for updating a queue item."""
    status: str = Field(..., pattern="^(waiting|in_progress|completed|cancelled)$")
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class QueueItemResponse(BaseModel):
    """Schema for queue item response data."""
    id: int
    queue_id: int
    user_id: int
    queue_name: str
    user_name: str
    position: int
    status: str
    priority: int
    joined_at: datetime
    completed_at: Optional[datetime]
    wait_time_minutes: int
    is_waiting: bool
    is_in_progress: bool
    is_completed: bool
    notes: Optional[str]

    class Config:
        from_attributes = True
