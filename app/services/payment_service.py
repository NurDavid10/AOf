"""
Payment service for managing payment operations.

This module provides business logic for payment-related operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.models.payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from app.models.course import Course, CourseEnrollment, EnrollmentStatus
from app.models.user import Parent, Student


class PaymentService:
    """Service class for payment-related operations."""

    @staticmethod
    def record_payment(
        db: Session,
        payer_id: int,
        amount: Decimal,
        payment_type: PaymentType,
        payment_method: PaymentMethod,
        reference_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Payment:
        """
        Record a new payment.

        Args:
            db: Database session
            payer_id: ID of the user making the payment (parent)
            amount: Payment amount
            payment_type: Type of payment
            payment_method: Method of payment
            reference_id: Optional reference ID (e.g., course_id)
            notes: Optional notes

        Returns:
            Payment: Created payment object

        Raises:
            ValueError: If validation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")

        # Create payment
        payment = Payment(
            payer_id=payer_id,
            amount=amount,
            payment_type=payment_type,
            payment_method=payment_method,
            payment_date=datetime.utcnow(),
            status=PaymentStatus.COMPLETED,
            reference_id=reference_id,
            notes=notes
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
        """
        Get a payment by ID.

        Args:
            db: Database session
            payment_id: Payment ID

        Returns:
            Payment or None: Payment object if found
        """
        return db.query(Payment).filter(Payment.id == payment_id).first()

    @staticmethod
    def get_parent_payments(
        db: Session,
        parent_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Payment]:
        """
        Get all payments made by a parent.

        Args:
            db: Database session
            parent_id: Parent user ID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List[Payment]: List of payment records
        """
        query = db.query(Payment).filter(Payment.payer_id == parent_id)

        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)

        return query.order_by(Payment.payment_date.desc()).all()

    @staticmethod
    def get_course_payments(db: Session, course_id: int) -> List[Payment]:
        """
        Get all payments for a specific course.

        Args:
            db: Database session
            course_id: Course ID

        Returns:
            List[Payment]: List of payment records for the course
        """
        return db.query(Payment).filter(
            and_(
                Payment.reference_id == course_id,
                Payment.payment_type == PaymentType.TUITION
            )
        ).all()

    @staticmethod
    def calculate_total_income(
        db: Session,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """
        Calculate total income in a date range.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            Decimal: Total income amount
        """
        result = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date,
                Payment.payment_type.in_([PaymentType.TUITION, PaymentType.FEE]),
                Payment.status == PaymentStatus.COMPLETED
            )
        ).scalar()

        return result if result else Decimal("0.00")

    @staticmethod
    def get_income_by_course(
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """
        Get income breakdown by course.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            List[dict]: List of dicts with course_id, course_name, and total_income
        """
        results = db.query(
            Payment.reference_id.label('course_id'),
            func.sum(Payment.amount).label('total_income')
        ).filter(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date,
                Payment.payment_type == PaymentType.TUITION,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).group_by(Payment.reference_id).all()

        # Enrich with course names
        income_by_course = []
        for result in results:
            course = db.query(Course).filter(Course.id == result.course_id).first()
            income_by_course.append({
                'course_id': result.course_id,
                'course_name': course.course_name if course else 'Unknown',
                'total_income': result.total_income
            })

        return income_by_course

    @staticmethod
    def get_all_payments(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        payment_type: Optional[PaymentType] = None
    ) -> List[Payment]:
        """
        Get all payments with optional filters.

        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            payment_type: Optional payment type filter

        Returns:
            List[Payment]: List of payment records
        """
        query = db.query(Payment)

        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        if payment_type:
            query = query.filter(Payment.payment_type == payment_type)

        return query.order_by(Payment.payment_date.desc()).all()

    @staticmethod
    def get_payment_summary(db: Session, parent_id: int) -> dict:
        """
        Get payment summary for a parent.

        Args:
            db: Database session
            parent_id: Parent user ID

        Returns:
            dict: Summary with total_paid and payment_count
        """
        result = db.query(
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('count')
        ).filter(
            and_(
                Payment.payer_id == parent_id,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).first()

        return {
            'total_paid': result.total if result.total else Decimal("0.00"),
            'payment_count': result.count if result.count else 0
        }
