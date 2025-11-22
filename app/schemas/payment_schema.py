"""
Pydantic schemas for payment-related data validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PaymentBase(BaseModel):
    """Base schema for payment data."""
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payment_type: str = Field(..., pattern="^(tuition|fee|salary|other)$")
    payment_method: str = Field(..., pattern="^(cash|card|transfer)$")
    notes: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment."""
    payer_id: int
    reference_id: Optional[int] = None


class PaymentUpdate(BaseModel):
    """Schema for updating a payment."""
    status: str = Field(..., pattern="^(pending|completed|cancelled)$")
    notes: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class PaymentResponse(PaymentBase):
    """Schema for payment response data."""
    id: int
    payer_id: int
    payer_name: str
    payment_date: datetime
    status: str
    reference_id: Optional[int]
    formatted_amount: str
    is_completed: bool
    is_pending: bool
    created_at: datetime

    class Config:
        from_attributes = True
