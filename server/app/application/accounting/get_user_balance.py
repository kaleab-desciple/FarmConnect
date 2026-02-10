from typing import Protocol, Optional, Dict, List
from decimal import Decimal
from app.domain.accounting.entities import Account, OwnerType, AccountType


class AccountRepository(Protocol):
    def get_by_owner_and_type(self, owner_type: OwnerType, owner_id: str, account_type: AccountType) -> Optional[Account]:
        pass
    
    def get_all_by_owner(self, owner_type: OwnerType, owner_id: str) -> List[Account]:
        """Get ALL accounts owned by a specific owner."""
        pass


class JournalRepository(Protocol):
    def get_balance_for_account(self, account_id: str) -> Decimal:
        pass


class GetUserBalanceRequest:
    def __init__(self, user_id: str):
        self.user_id = user_id


class UserBalance:
    def __init__(self, user_id: str, cash_balance: Decimal, payable_balance: Decimal):
        self.user_id = user_id
        self.cash_balance = cash_balance
        self.payable_balance = payable_balance
        self.net_balance = cash_balance + payable_balance


class GetUserBalance:
    def __init__(self, account_repo: AccountRepository, journal_repo: JournalRepository):
        self.account_repo = account_repo
        self.journal_repo = journal_repo

    def execute(self, request: GetUserBalanceRequest) -> UserBalance:
        cash_balance = Decimal(0)
        payable_balance = Decimal(0)
        
        # Get ALL ASSET accounts for the user
        all_accounts = self.account_repo.get_all_by_owner(
            OwnerType.USER, request.user_id
        )
        
        for account in all_accounts:
            if account.account_type == AccountType.ASSET:
                cash_balance += self.journal_repo.get_balance_for_account(str(account.id))
            elif account.account_type == AccountType.LIABILITY:
                payable_balance += self.journal_repo.get_balance_for_account(str(account.id))

        return UserBalance(
            user_id=request.user_id,
            cash_balance=cash_balance,
            payable_balance=payable_balance
        )
