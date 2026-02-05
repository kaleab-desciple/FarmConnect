from typing import Protocol, Optional, Dict
from decimal import Decimal
from app.domain.accounting.entities import Account, OwnerType, AccountType


class AccountRepository(Protocol):
    def get_by_owner_and_type(self, owner_type: OwnerType, owner_id: str, account_type: AccountType) -> Optional[Account]:
        ...


class JournalRepository(Protocol):
    def get_balance_for_account(self, account_id: str) -> Decimal:
        ...


class GetUserBalanceRequest:
    def __init__(self, user_id: str):
        self.user_id = user_id


class UserBalance:
    def __init__(self, user_id: str, cash_balance: Decimal, payable_balance: Decimal):
        self.user_id = user_id
        self.cash_balance = cash_balance  # ASSET account (what user has)
        self.payable_balance = payable_balance  # LIABILITY account (what we owe user)
        self.net_balance = cash_balance + payable_balance


class GetUserBalance:
    def __init__(self, account_repo: AccountRepository, journal_repo: JournalRepository):
        self.account_repo = account_repo
        self.journal_repo = journal_repo

    def execute(self, request: GetUserBalanceRequest) -> UserBalance:
        """Get consolidated balance for a user across all their accounts."""
        cash_balance = Decimal(0)
        payable_balance = Decimal(0)

        # Get user's cash account (ASSET)
        cash_account = self.account_repo.get_by_owner_and_type(
            OwnerType.USER, request.user_id, AccountType.ASSET
        )
        if cash_account:
            cash_balance = self.journal_repo.get_balance_for_account(str(cash_account.id))

        # Get user's payable account (LIABILITY)
        payable_account = self.account_repo.get_by_owner_and_type(
            OwnerType.USER, request.user_id, AccountType.LIABILITY
        )
        if payable_account:
            payable_balance = self.journal_repo.get_balance_for_account(str(payable_account.id))

        return UserBalance(
            user_id=request.user_id,
            cash_balance=cash_balance,
            payable_balance=payable_balance
        )
