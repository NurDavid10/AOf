"""
Queue models for managing waiting lists.

This module handles queue management for various services like registration,
payment processing, and support requests.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.models.base import BaseModel


class QueueType(str, enum.Enum):
    """Enumeration of queue types."""
    REGISTRATION = "registration"
    PAYMENT = "payment"
    SUPPORT = "support"
    GENERAL = "general"


class QueueItemStatus(str, enum.Enum):
    """Enumeration of queue item statuses."""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Queue(BaseModel):
    """
    Queue model representing a service queue.

    Attributes:
        queue_name: Name of the queue
        description: Description of the queue's purpose
        queue_type: Type of queue (registration, payment, etc.)
        max_capacity: Maximum number of items in queue (0 = unlimited)
    """

    __tablename__ = "queues"

    queue_name = Column(String(100), nullable=False)
    description = Column(Text)
    queue_type = Column(Enum(QueueType), nullable=False)
    max_capacity = Column(Integer, default=0)  # 0 means unlimited

    # Relationships
    items = relationship("QueueItem", back_populates="queue", cascade="all, delete-orphan")

    @property
    def current_length(self) -> int:
        """
        Get the current number of waiting items in the queue.

        Returns:
            int: Number of items with 'waiting' status
        """
        return sum(1 for item in self.items if item.status == QueueItemStatus.WAITING)

    @property
    def in_progress_count(self) -> int:
        """
        Get the number of items currently being processed.

        Returns:
            int: Number of items with 'in_progress' status
        """
        return sum(1 for item in self.items if item.status == QueueItemStatus.IN_PROGRESS)

    @property
    def is_full(self) -> bool:
        """
        Check if the queue is at maximum capacity.

        Returns:
            bool: True if queue is full, False otherwise
        """
        if self.max_capacity == 0:
            return False
        return self.current_length >= self.max_capacity

    @property
    def next_position(self) -> int:
        """
        Get the next available position number in the queue.

        Returns:
            int: Next position number
        """
        if not self.items:
            return 1
        waiting_items = [item for item in self.items if item.status == QueueItemStatus.WAITING]
        if not waiting_items:
            return 1
        return max(item.position for item in waiting_items) + 1

    def get_next_waiting_item(self):
        """
        Get the next item in the waiting queue.

        Returns:
            QueueItem or None: The next waiting item with highest priority/earliest position
        """
        waiting_items = [item for item in self.items if item.status == QueueItemStatus.WAITING]
        if not waiting_items:
            return None
        # Sort by priority (descending) then by position (ascending)
        return sorted(waiting_items, key=lambda x: (-x.priority, x.position))[0]

    def can_add_item(self) -> bool:
        """
        Check if a new item can be added to the queue.

        Returns:
            bool: True if queue can accept new items, False otherwise
        """
        return not self.is_full

    def __repr__(self) -> str:
        """String representation of Queue."""
        return f"<Queue(id={self.id}, name='{self.queue_name}', type='{self.queue_type.value}')>"


class QueueItem(BaseModel):
    """
    Queue item model representing an individual entry in a queue.

    Attributes:
        queue_id: ID of the associated queue
        user_id: ID of the user in the queue
        position: Position number in the queue
        status: Current status of the queue item
        priority: Priority level (higher = served first)
        joined_at: Timestamp when user joined the queue
        completed_at: Timestamp when service was completed
        notes: Additional notes about the queue item
    """

    __tablename__ = "queue_items"

    queue_id = Column(Integer, ForeignKey("queues.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    status = Column(Enum(QueueItemStatus), default=QueueItemStatus.WAITING, nullable=False)
    priority = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text)

    # Relationships
    queue = relationship("Queue", back_populates="items", foreign_keys=[queue_id])
    user = relationship("User", backref="queue_items", foreign_keys=[user_id])

    @property
    def queue_name(self) -> str:
        """
        Get the queue name.

        Returns:
            str: Queue name
        """
        return self.queue.queue_name if self.queue else "Unknown"

    @property
    def user_name(self) -> str:
        """
        Get the user's name.

        Returns:
            str: User's full name
        """
        return self.user.full_name if self.user else "Unknown"

    @property
    def is_waiting(self) -> bool:
        """
        Check if item is in waiting status.

        Returns:
            bool: True if waiting, False otherwise
        """
        return self.status == QueueItemStatus.WAITING

    @property
    def is_in_progress(self) -> bool:
        """
        Check if item is currently being processed.

        Returns:
            bool: True if in progress, False otherwise
        """
        return self.status == QueueItemStatus.IN_PROGRESS

    @property
    def is_completed(self) -> bool:
        """
        Check if item is completed.

        Returns:
            bool: True if completed, False otherwise
        """
        return self.status == QueueItemStatus.COMPLETED

    @property
    def wait_time_minutes(self) -> int:
        """
        Calculate wait time in minutes.

        Returns:
            int: Wait time in minutes since joining
        """
        if not self.joined_at:
            return 0
        end_time = self.completed_at if self.completed_at else datetime.utcnow()
        delta = end_time - self.joined_at
        return int(delta.total_seconds() / 60)

    def start_processing(self):
        """Mark this queue item as in progress."""
        self.status = QueueItemStatus.IN_PROGRESS

    def mark_completed(self):
        """Mark this queue item as completed."""
        self.status = QueueItemStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def cancel(self):
        """Cancel this queue item."""
        self.status = QueueItemStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    def __repr__(self) -> str:
        """String representation of QueueItem."""
        return f"<QueueItem(id={self.id}, queue_id={self.queue_id}, user_id={self.user_id}, position={self.position}, status='{self.status.value}')>"
