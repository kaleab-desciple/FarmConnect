from typing import Protocol, Dict
from decimal import Decimal
from app.domain.accounting.entities import AccountType


class JournalRepository(Protocol):
    def get_trial_balance(self) -> Dict[str, Decimal]:
        ...


class TrialBalance:
    def __init__(self, assets: Decimal, liabilities: Decimal, equity: Decimal):
        self.assets = assets
        self.liabilities = liabilities
        self.equity = equity


class GetTrialBalance:
    def __init__(self, journal_repo: JournalRepository):
        self.journal_repo = journal_repo

    def execute(self) -> TrialBalance:
        balances = self.journal_repo.get_trial_balance()
        return TrialBalance(
            assets=balances.get('assets', Decimal(0)),
            liabilities=balances.get('liabilities', Decimal(0)),
            equity=balances.get('equity', Decimal(0))
        )