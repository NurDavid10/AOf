"""
Payment models.

This module handles payment records, transactions, and financial tracking.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Enum
from sqlalchemy.orm import relationship
import enum
from decimal import Decimal
from datetime import datetime
from app.models.base import BaseModel


class PaymentType(str, enum.Enum):
    """Enumeration of payment types."""
    TUITION = "tuition"
    FEE = "fee"
    SALARY = "salary"
    OTHER = "other"


class PaymentMethod(str, enum.Enum):
    """Enumeration of payment methods."""
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"


class PaymentStatus(str, enum.Enum):
    """Enumeration of payment statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Payment(BaseModel):
    """
    Payment model representing financial transactions.

    Attributes:
        payer_id: ID of the user making/receiving the payment
        amount: Payment amount
        payment_type: Type of payment (tuition, salary, etc.)
        payment_method: Method of payment (cash, card, etc.)
        payment_date: Date and time of payment
        status: Current payment status
        reference_id: Optional reference to related entity (course, task, etc.)
        notes: Additional notes about the payment
    """

    __tablename__ = "payments"

    payer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    reference_id = Column(Integer, nullable=True)
    notes = Column(String(500))

    # Relationships
    payer = relationship("User", backref="payments", foreign_keys=[payer_id])

    @property
    def payer_name(self) -> str:
        """
        Get the payer's name.

        Returns:
            str: Payer's full name
        """
        return self.payer.full_name if self.payer else "Unknown"

    @property
    def amount_value(self) -> Decimal:
        """
        Get the payment amount.

        Returns:
            Decimal: Payment amount
        """
        return self.amount if self.amount else Decimal("0.00")

    @property
    def is_completed(self) -> bool:
        """
        Check if payment is completed.

        Returns:
            bool: True if payment is completed, False otherwise
        """
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_pending(self) -> bool:
        """
        Check if payment is pending.

        Returns:
            bool: True if payment is pending, False otherwise
        """
        return self.status == PaymentStatus.PENDING

    @property
    def formatted_amount(self) -> str:
        """
        Get formatted payment amount.

        Returns:
            str: Formatted amount string (e.g., "$100.00")
        """
        return f"${self.amount_value:.2f}"

    def mark_completed(self):
        """Mark this payment as completed."""
        self.status = PaymentStatus.COMPLETED
        if not self.payment_date:
            self.payment_date = datetime.utcnow()

    def mark_cancelled(self):
        """Mark this payment as cancelled."""
        self.status = PaymentStatus.CANCELLED

    def is_income(self) -> bool:
        """
        Check if this payment is income for the center.

        Returns:
            bool: True if payment is income (tuition, fees), False otherwise
        """
        return self.payment_type in [PaymentType.TUITION, PaymentType.FEE]

    def is_expense(self) -> bool:
        """
        Check if this payment is an expense for the center.

        Returns:
            bool: True if payment is expense (salary), False otherwise
        """
        return self.payment_type == PaymentType.SALARY

    def __repr__(self) -> str:
        """String representation of Payment."""
        return f"<Payment(id={self.id}, amount={self.amount}, type='{self.payment_type.value}', status='{self.status.value}')>"
