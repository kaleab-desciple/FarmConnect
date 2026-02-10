# get_user_statement.py - Fix balance calculation per account type
from typing import Protocol, Optional, List
from decimal import Decimal
from datetime import datetime
from app.domain.accounting.entities import Account, OwnerType, AccountType, JournalEntry


class AccountRepository(Protocol):
    def get_all_by_owner(self, owner_type: OwnerType, owner_id: str) -> List[Account]:
        """Get ALL accounts owned by a specific owner."""
        ...


class JournalRepository(Protocol):
    def get_entries_for_account(self, account_id: str) -> List[JournalEntry]:
        ...


class GetUserStatementRequest:
    def __init__(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date


class StatementLine:
    def __init__(self, date: datetime, description: str, debit: Decimal, credit: Decimal, balance: Decimal):
        self.date = date
        self.description = description
        self.debit = debit
        self.credit = credit
        self.balance = balance


class UserStatement:
    def __init__(self, user_id: str, lines: List[StatementLine], opening_balance: Decimal, closing_balance: Decimal):
        self.user_id = user_id
        self.lines = lines
        self.opening_balance = opening_balance
        self.closing_balance = closing_balance


class GetUserStatement:
    def __init__(self, account_repo: AccountRepository, journal_repo: JournalRepository):
        self.account_repo = account_repo
        self.journal_repo = journal_repo

    def execute(self, request: GetUserStatementRequest) -> UserStatement:
        """Get transaction statement for a user showing all debits and credits."""
        lines = []
        running_balance = Decimal(0)

        # Get ALL user accounts
        all_accounts = self.account_repo.get_all_by_owner(
            OwnerType.USER, request.user_id
        )
        
        # Build a map of account_id -> account_type for balance calculations
        account_map = {str(acc.id): acc.account_type for acc in all_accounts}
        account_ids = list(account_map.keys())

        if not account_ids:
            return UserStatement(
                user_id=request.user_id,
                lines=[],
                opening_balance=Decimal(0),
                closing_balance=Decimal(0)
            )

        # Get all journal entries for these accounts
        all_entries = []
        for account_id in account_ids:
            entries = self.journal_repo.get_entries_for_account(account_id)
            all_entries.extend(entries)

        # Sort by date
        all_entries.sort(key=lambda e: e.created_at)

        # Build statement lines
        for entry in all_entries:
            for line in entry.lines:
                if str(line.account_id) in account_ids:
                    # Filter by date if specified
                    if request.start_date and entry.created_at < request.start_date:
                        continue
                    if request.end_date and entry.created_at > request.end_date:
                        continue

                    # Calculate balance based on account type
                    account_type = account_map.get(str(line.account_id))
                    
                    # ASSET/EXPENSE: debit increases, credit decreases
                    # LIABILITY/EQUITY/REVENUE: credit increases, debit decreases
                    if account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                        running_balance += line.debit_amount - line.credit_amount
                    else:  # LIABILITY, EQUITY, REVENUE
                        running_balance += line.credit_amount - line.debit_amount
                    
                    lines.append(StatementLine(
                        date=entry.created_at,
                        description=entry.description,
                        debit=line.debit_amount,
                        credit=line.credit_amount,
                        balance=running_balance
                    ))

        opening_balance = Decimal(0)
        closing_balance = running_balance

        return UserStatement(
            user_id=request.user_id,
            lines=lines,
            opening_balance=opening_balance,
            closing_balance=closing_balance
        )
