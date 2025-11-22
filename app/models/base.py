"""
Base model classes with common functionality.

This module defines abstract base classes that provide common fields
and methods for all models, demonstrating OOP principles.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.database import Base


class TimestampMixin:
    """
    Mixin class providing timestamp fields.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def created_at_formatted(self) -> str:
        """
        Get formatted creation timestamp.

        Returns:
            str: Formatted datetime string
        """
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""

    @property
    def updated_at_formatted(self) -> str:
        """
        Get formatted update timestamp.

        Returns:
            str: Formatted datetime string
        """
        return self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model class for all database models.

    Provides common functionality including:
    - Primary key field
    - Timestamp fields (created_at, updated_at)
    - Common utility methods

    Note:
        This is an abstract class and should not be instantiated directly.
        Use __abstract__ = True to prevent SQLAlchemy from creating a table.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.

        Returns:
            dict: Dictionary representation of the model

        Note:
            This method is useful for serialization and API responses
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def __repr__(self) -> str:
        """
        String representation of the model.

        Returns:
            str: String representation showing class name and id
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
