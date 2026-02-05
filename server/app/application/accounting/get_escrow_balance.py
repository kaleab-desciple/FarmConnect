from typing import Protocol, Optional
from decimal import Decimal
from app.domain.accounting.entities import Account, OwnerType, AccountType


class AccountRepository(Protocol):
    def get_by_owner_and_type(self, owner_type: OwnerType, owner_id: str, account_type: AccountType) -> Optional[Account]:
        ...


class JournalRepository(Protocol):
    def get_balance_for_account(self, account_id: str) -> Decimal:
        ...


class GetEscrowBalanceRequest:
    def __init__(self, escrow_id: str):
        self.escrow_id = escrow_id


class EscrowBalance:
    def __init__(self, escrow_id: str, holding_balance: Decimal):
        self.escrow_id = escrow_id
        self.holding_balance = holding_balance  # LIABILITY account (funds held in escrow)


class GetEscrowBalance:
    def __init__(self, account_repo: AccountRepository, journal_repo: JournalRepository):
        self.account_repo = account_repo
        self.journal_repo = journal_repo

    def execute(self, request: GetEscrowBalanceRequest) -> EscrowBalance:
        """Get balance for a specific escrow account."""
        holding_balance = Decimal(0)

        # Get escrow holding account (LIABILITY)
        holding_account = self.account_repo.get_by_owner_and_type(
            OwnerType.ESCROW, request.escrow_id, AccountType.LIABILITY
        )
        if holding_account:
            holding_balance = self.journal_repo.get_balance_for_account(str(holding_account.id))

        return EscrowBalance(
            escrow_id=request.escrow_id,
            holding_balance=holding_balance
        )
