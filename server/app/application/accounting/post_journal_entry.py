from uuid import uuid4
from datetime import datetime, timezone
from typing import Protocol, List
from decimal import Decimal
from app.domain.accounting.entities import JournalEntry, JournalLine, ReferenceType, Account
from app.domain.accounting.policies import AccountingPolicy


class JournalRepository(Protocol):
    def save(self, entry: JournalEntry) -> None:
        ...

class AccountRepository(Protocol):
    def get_by_id(self, account_id: str) -> Account | None:
        ...


class PostJournalEntryRequest:
    def __init__(self, reference_type: ReferenceType, reference_id: str, description: str, lines: List[dict]):
        self.reference_type = reference_type
        self.reference_id = reference_id
        self.description = description
        self.lines = lines  # List of dicts with account_id, debit_amount, credit_amount


class PostJournalEntry:
    def __init__(self, journal_repo: JournalRepository, account_repo: AccountRepository):
        self.journal_repo = journal_repo
        self.account_repo = account_repo

    def execute(self, request: PostJournalEntryRequest) -> JournalEntry:
        lines = []
        accounts = []
        for line_data in request.lines:
            account = self.account_repo.get_by_id(line_data['account_id'])
            if not account:
                raise ValueError(f"Account {line_data['account_id']} not found")
            accounts.append(account)
            lines.append(JournalLine(
                account_id=account.id,
                debit_amount=Decimal(str(line_data['debit_amount'])),
                credit_amount=Decimal(str(line_data['credit_amount']))
            ))

        # Validate
        AccountingPolicy.validate_journal_entry(lines)
        AccountingPolicy.validate_currency_match(accounts, accounts[0].currency)

        entry = JournalEntry(
            id=uuid4(),
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            description=request.description,
            lines=lines,
            created_at=datetime.now(timezone.utc)
        )
        self.journal_repo.save(entry)
        return entry