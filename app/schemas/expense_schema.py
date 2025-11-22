"""
Expense schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from decimal import Decimal
from typing import Optional

from app.models.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    """Schema for creating an expense."""
    category: ExpenseCategory
    amount: Decimal = Field(gt=0, description="Amount must be greater than 0")
    expense_date: date
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ExpenseResponse(BaseModel):
    """Schema for expense response."""
    id: int
    category: ExpenseCategory
    amount: Decimal
    expense_date: date
    description: Optional[str] = None
    created_by_manager_id: Optional[int] = None
    created_at: date

    model_config = ConfigDict(from_attributes=True)
