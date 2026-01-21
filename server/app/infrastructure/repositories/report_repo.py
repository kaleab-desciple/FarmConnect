from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_
from app.infrastructure.db.models.account import AccountORM
from app.infrastructure.db.models.journal_entry import JournalEntryORM, JournalLineORM
from app.domain.accounting.entities import AccountType


class ReportRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_balance_sheet_data(self, as_of: date) -> Dict[str, Any]:
        """Get balance sheet data as of a specific date"""
        # Convert date to datetime for filtering
        as_of_datetime = datetime.combine(as_of, datetime.max.time())

        # Query balances for each account type
        balances_query = self.session.query(
            AccountORM.account_type,
            func.sum(JournalLineORM.debit_amount - JournalLineORM.credit_amount).label('balance')
        ).join(
            JournalLineORM, AccountORM.id == JournalLineORM.account_id
        ).join(
            JournalEntryORM, JournalEntryORM.id == JournalLineORM.journal_entry_id
        ).filter(
            JournalEntryORM.created_at <= as_of_datetime
        ).group_by(AccountORM.account_type).all()

        # Organize by account type
        assets = {}
        liabilities = {}
        equity = {}

        for account_type, balance in balances_query:
            balance_dec = Decimal(str(balance or 0))
            if account_type == AccountType.ASSET:
                assets['total'] = assets.get('total', Decimal(0)) + balance_dec
            elif account_type == AccountType.LIABILITY:
                liabilities['total'] = liabilities.get('total', Decimal(0)) + balance_dec
            elif account_type == AccountType.EQUITY:
                equity['total'] = equity.get('total', Decimal(0)) + balance_dec

        return {
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity
        }

    def get_profit_loss_data(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Get profit & loss data for a date range"""
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        # Query revenue and expenses
        pl_query = self.session.query(
            AccountORM.account_type,
            func.sum(JournalLineORM.debit_amount - JournalLineORM.credit_amount).label('amount')
        ).join(
            JournalLineORM, AccountORM.id == JournalLineORM.account_id
        ).join(
            JournalEntryORM, JournalEntryORM.id == JournalLineORM.journal_entry_id
        ).filter(
            and_(
                JournalEntryORM.created_at >= from_datetime,
                JournalEntryORM.created_at <= to_datetime,
                or_(
                    AccountORM.account_type == AccountType.REVENUE,
                    AccountORM.account_type == AccountType.EXPENSE
                )
            )
        ).group_by(AccountORM.account_type).all()

        revenue = {}
        expenses = {}

        for account_type, amount in pl_query:
            amount_dec = Decimal(str(amount or 0))
            if account_type == AccountType.REVENUE:
                revenue['total'] = revenue.get('total', Decimal(0)) + amount_dec
            elif account_type == AccountType.EXPENSE:
                expenses['total'] = expenses.get('total', Decimal(0)) + amount_dec

        return {
            'revenue': revenue,
            'expenses': expenses
        }

    def get_cash_flow_data(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Get cash flow data for a date range (simplified indirect method)"""
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        # Get net income from P&L
        pl_data = self.get_profit_loss_data(from_date, to_date)
        net_income = (pl_data['revenue'].get('total', Decimal(0)) -
                     pl_data['expenses'].get('total', Decimal(0)))

        # For now, simplified cash flow - just net income
        # In a real implementation, would adjust for non-cash items
        operating = {'net_income': net_income}
        investing = {}  # Stub
        financing = {}  # Stub

        return {
            'operating': operating,
            'investing': investing,
            'financing': financing
        }