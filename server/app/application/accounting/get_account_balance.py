from typing import Protocol
from decimal import Decimal
from app.domain.accounting.entities import Account


class JournalRepository(Protocol):
    def get_balance_for_account(self, account_id: str) -> Decimal:
        ...


class GetAccountBalanceRequest:
    def __init__(self, account_id: str):
        self.account_id = account_id


class GetAccountBalance:
    def __init__(self, journal_repo: JournalRepository):
        self.journal_repo = journal_repo

    def execute(self, request: GetAccountBalanceRequest) -> Decimal:
        return self.journal_repo.get_balance_for_account(request.account_id)