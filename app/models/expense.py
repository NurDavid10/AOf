"""
Expense models for financial tracking.

This module handles expense records for the learning center.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DECIMAL, Enum
from sqlalchemy.orm import relationship
import enum
from decimal import Decimal
from datetime import date
from app.models.base import BaseModel


class ExpenseCategory(str, enum.Enum):
    """Enumeration of expense categories."""
    SALARY = "salary"
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    SUPPLIES = "supplies"
    OTHER = "other"


class Expense(BaseModel):
    """
    Expense model representing center expenses.

    Attributes:
        category: Category of the expense (salary, maintenance, etc.)
        amount: Expense amount
        expense_date: Date of the expense
        description: Detailed description of the expense
        created_by_manager_id: ID of the manager who created this record
    """

    __tablename__ = "expenses"

    category = Column(Enum(ExpenseCategory), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    description = Column(Text)
    created_by_manager_id = Column(Integer, ForeignKey("managers.user_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    created_by = relationship("Manager", backref="expenses_created", foreign_keys=[created_by_manager_id])

    @property
    def amount_value(self) -> Decimal:
        """
        Get the expense amount.

        Returns:
            Decimal: Expense amount
        """
        return self.amount if self.amount else Decimal("0.00")

    @property
    def formatted_amount(self) -> str:
        """
        Get formatted expense amount.

        Returns:
            str: Formatted amount string (e.g., "$100.00")
        """
        return f"${self.amount_value:.2f}"

    @property
    def created_by_name(self) -> str:
        """
        Get the name of the manager who created this expense.

        Returns:
            str: Manager's full name
        """
        if self.created_by and self.created_by.user:
            return self.created_by.user.full_name
        return "Unknown"

    @property
    def category_display(self) -> str:
        """
        Get a display-friendly category name.

        Returns:
            str: Category name with proper capitalization
        """
        return self.category.value.replace("_", " ").title()

    def __repr__(self) -> str:
        """String representation of Expense."""
        return f"<Expense(id={self.id}, category='{self.category.value}', amount={self.amount})>"
