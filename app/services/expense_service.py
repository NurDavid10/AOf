"""
Expense service for managing expense operations.

This module provides business logic for expense-related operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.models.expense import Expense, ExpenseCategory


class ExpenseService:
    """Service class for expense-related operations."""

    @staticmethod
    def create_expense(
        db: Session,
        category: ExpenseCategory,
        amount: Decimal,
        expense_date: date,
        description: Optional[str],
        manager_id: int
    ) -> Expense:
        """
        Create a new expense record.

        Args:
            db: Database session
            category: Expense category
            amount: Expense amount
            expense_date: Date of the expense
            description: Description of the expense
            manager_id: ID of the manager creating the expense

        Returns:
            Expense: Created expense object

        Raises:
            ValueError: If validation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero")

        # Create expense
        expense = Expense(
            category=category,
            amount=amount,
            expense_date=expense_date,
            description=description,
            created_by_manager_id=manager_id
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
        """
        Get an expense by ID.

        Args:
            db: Database session
            expense_id: Expense ID

        Returns:
            Expense or None: Expense object if found
        """
        return db.query(Expense).filter(Expense.id == expense_id).first()

    @staticmethod
    def get_expenses(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[ExpenseCategory] = None
    ) -> List[Expense]:
        """
        Get expenses with optional filters.

        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            category: Optional category filter

        Returns:
            List[Expense]: List of expense records
        """
        query = db.query(Expense)

        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        if end_date:
            query = query.filter(Expense.expense_date <= end_date)
        if category:
            query = query.filter(Expense.category == category)

        return query.order_by(Expense.expense_date.desc()).all()

    @staticmethod
    def calculate_total_expenses(
        db: Session,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """
        Calculate total expenses in a date range.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            Decimal: Total expense amount
        """
        result = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            )
        ).scalar()

        return result if result else Decimal("0.00")

    @staticmethod
    def get_expenses_by_category(
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """
        Get expense breakdown by category.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            List[dict]: List of dicts with category and total_amount
        """
        results = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total_amount')
        ).filter(
            and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            )
        ).group_by(Expense.category).all()

        return [
            {
                'category': result.category.value,
                'category_display': result.category.value.replace("_", " ").title(),
                'total_amount': result.total_amount
            }
            for result in results
        ]

    @staticmethod
    def update_expense(
        db: Session,
        expense_id: int,
        category: Optional[ExpenseCategory] = None,
        amount: Optional[Decimal] = None,
        expense_date: Optional[date] = None,
        description: Optional[str] = None
    ) -> Optional[Expense]:
        """
        Update an expense record.

        Args:
            db: Database session
            expense_id: Expense ID
            category: Optional new category
            amount: Optional new amount
            expense_date: Optional new date
            description: Optional new description

        Returns:
            Expense or None: Updated expense object if found

        Raises:
            ValueError: If validation fails
        """
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return None

        if category is not None:
            expense.category = category
        if amount is not None:
            if amount <= 0:
                raise ValueError("Expense amount must be greater than zero")
            expense.amount = amount
        if expense_date is not None:
            expense.expense_date = expense_date
        if description is not None:
            expense.description = description

        db.commit()
        db.refresh(expense)

        return expense

    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> bool:
        """
        Delete an expense record.

        Args:
            db: Database session
            expense_id: Expense ID

        Returns:
            bool: True if deleted, False if not found
        """
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return False

        db.delete(expense)
        db.commit()

        return True

    @staticmethod
    def get_expense_summary_by_manager(db: Session, manager_id: int) -> dict:
        """
        Get expense summary for expenses created by a specific manager.

        Args:
            db: Database session
            manager_id: Manager user ID

        Returns:
            dict: Summary with total_expenses and expense_count
        """
        result = db.query(
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.created_by_manager_id == manager_id
        ).first()

        return {
            'total_expenses': result.total if result.total else Decimal("0.00"),
            'expense_count': result.count if result.count else 0
        }
