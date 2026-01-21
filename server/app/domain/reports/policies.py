from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any


class FinancialReportPolicy:
    @staticmethod
    def validate_balance_sheet_balance(assets: Decimal, liabilities: Decimal, equity: Decimal) -> bool:
        """Validate that Assets = Liabilities + Equity"""
        return abs(assets - (liabilities + equity)) < Decimal('0.01')

    @staticmethod
    def validate_date_range(from_date: date, to_date: date) -> None:
        """Validate that date range is valid"""
        if from_date > to_date:
            raise ValueError("From date cannot be after to date")
        if from_date > date.today():
            raise ValueError("From date cannot be in the future")
        if to_date > date.today():
            raise ValueError("To date cannot be in the future")

    @staticmethod
    def validate_as_of_date(as_of: date) -> None:
        """Validate that as_of date is not in the future"""
        if as_of > date.today():
            raise ValueError("As of date cannot be in the future")

    @staticmethod
    def calculate_net_income(revenue: Decimal, expenses: Decimal) -> Decimal:
        """Calculate net income as revenue minus expenses"""
        return revenue - expenses

    @staticmethod
    def format_currency(amount: Decimal) -> str:
        """Format decimal amount as currency string"""
        return f"{amount:.2f}"