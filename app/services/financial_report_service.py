"""
Financial report service for generating financial summaries and reports.

This module combines payment and expense data to generate comprehensive financial reports.
"""

from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.services.payment_service import PaymentService
from app.services.expense_service import ExpenseService


class FinancialReportService:
    """Service class for financial reporting operations."""

    @staticmethod
    def generate_financial_summary(
        db: Session,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Generate a comprehensive financial summary for a date range.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            dict: Financial summary with income, expenses, and net result
        """
        # Get income and expenses
        total_income = PaymentService.calculate_total_income(db, start_date, end_date)
        total_expenses = ExpenseService.calculate_total_expenses(db, start_date, end_date)

        # Calculate net result
        net_result = total_income - total_expenses

        # Get breakdowns
        income_by_course = PaymentService.get_income_by_course(db, start_date, end_date)
        expenses_by_category = ExpenseService.get_expenses_by_category(db, start_date, end_date)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_result': net_result,
            'income_by_course': income_by_course,
            'expenses_by_category': expenses_by_category,
            'is_profitable': net_result > 0
        }

    @staticmethod
    def get_budget_summary(db: Session) -> Dict:
        """
        Get budget summary for the current month.

        Args:
            db: Database session

        Returns:
            dict: Budget summary for current month
        """
        # Get current month date range
        today = date.today()
        start_of_month = date(today.year, today.month, 1)

        # Calculate end of month
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)

        return FinancialReportService.generate_financial_summary(
            db,
            start_of_month,
            end_of_month
        )

    @staticmethod
    def get_monthly_trend(
        db: Session,
        months: int = 6
    ) -> List[Dict]:
        """
        Get monthly financial trend for the last N months.

        Args:
            db: Database session
            months: Number of months to include

        Returns:
            List[dict]: Monthly financial data
        """
        trend = []
        today = date.today()

        for i in range(months):
            # Calculate month start and end
            if today.month - i > 0:
                month = today.month - i
                year = today.year
            else:
                month = 12 + (today.month - i)
                year = today.year - 1

            start_of_month = date(year, month, 1)

            # Calculate end of month
            if month == 12:
                end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_of_month = date(year, month + 1, 1) - timedelta(days=1)

            # Get data for this month
            income = PaymentService.calculate_total_income(db, start_of_month, end_of_month)
            expenses = ExpenseService.calculate_total_expenses(db, start_of_month, end_of_month)

            trend.insert(0, {
                'month': start_of_month.strftime('%B %Y'),
                'month_short': start_of_month.strftime('%b %Y'),
                'income': income,
                'expenses': expenses,
                'net': income - expenses
            })

        return trend

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict:
        """
        Get financial summary for dashboard display.

        Args:
            db: Database session

        Returns:
            dict: Dashboard-friendly financial summary
        """
        # Current month
        budget_summary = FinancialReportService.get_budget_summary(db)

        # Year to date
        today = date.today()
        start_of_year = date(today.year, 1, 1)
        year_summary = FinancialReportService.generate_financial_summary(
            db,
            start_of_year,
            today
        )

        # All time
        all_income = PaymentService.calculate_total_income(
            db,
            date(2000, 1, 1),
            today
        )
        all_expenses = ExpenseService.calculate_total_expenses(
            db,
            date(2000, 1, 1),
            today
        )

        return {
            'current_month': {
                'income': budget_summary['total_income'],
                'expenses': budget_summary['total_expenses'],
                'net': budget_summary['net_result']
            },
            'year_to_date': {
                'income': year_summary['total_income'],
                'expenses': year_summary['total_expenses'],
                'net': year_summary['net_result']
            },
            'all_time': {
                'income': all_income,
                'expenses': all_expenses,
                'net': all_income - all_expenses
            }
        }

    @staticmethod
    def get_top_revenue_courses(
        db: Session,
        start_date: date,
        end_date: date,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get top revenue-generating courses.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            limit: Number of courses to return

        Returns:
            List[dict]: Top courses by revenue
        """
        income_by_course = PaymentService.get_income_by_course(db, start_date, end_date)

        # Sort by total_income descending and limit
        sorted_courses = sorted(
            income_by_course,
            key=lambda x: x['total_income'],
            reverse=True
        )[:limit]

        return sorted_courses

    @staticmethod
    def get_expense_summary_by_category(db: Session) -> Dict:
        """
        Get expense summary by category for current month.

        Args:
            db: Database session

        Returns:
            dict: Expense breakdown by category
        """
        today = date.today()
        start_of_month = date(today.year, today.month, 1)

        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)

        expenses_by_category = ExpenseService.get_expenses_by_category(
            db,
            start_of_month,
            end_of_month
        )

        total_expenses = sum(cat['total_amount'] for cat in expenses_by_category)

        # Add percentage to each category
        for category in expenses_by_category:
            if total_expenses > 0:
                category['percentage'] = (float(category['total_amount']) / float(total_expenses)) * 100
            else:
                category['percentage'] = 0

        return {
            'total_expenses': total_expenses,
            'categories': expenses_by_category
        }
