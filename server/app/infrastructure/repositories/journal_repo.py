from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from decimal import Decimal
from app.domain.accounting.entities import JournalEntry, JournalLine, AccountType
from app.infrastructure.db.models.journal_entry import JournalEntryORM, JournalLineORM
from app.infrastructure.db.models.account import AccountORM


class JournalRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, entry: JournalEntry) -> None:
        orm = JournalEntryORM(
            id=str(entry.id),
            reference_type=entry.reference_type.value,
            reference_id=entry.reference_id,
            description=entry.description,
            created_at=entry.created_at
        )
        for line in entry.lines:
            line_orm = JournalLineORM(
                journal_entry_id=str(entry.id),
                account_id=str(line.account_id),
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount
            )
            orm.lines.append(line_orm)
        self.session.add(orm)
        self.session.commit()

    def get_balance_for_account(self, account_id: str) -> Decimal:
        result = self.session.query(
            func.sum(JournalLineORM.debit_amount - JournalLineORM.credit_amount)
        ).filter(JournalLineORM.account_id == account_id).scalar()
        return Decimal(str(result or 0))

    def get_trial_balance(self) -> Dict[str, Decimal]:
        # Group by account type and sum balances
        query = self.session.query(
            AccountORM.account_type,
            func.sum(JournalLineORM.debit_amount - JournalLineORM.credit_amount).label('balance')
        ).join(JournalLineORM, AccountORM.id == JournalLineORM.account_id
        ).group_by(AccountORM.account_type).all()

        balances = {account_type.value.lower(): Decimal(str(balance or 0)) for account_type, balance in query}
        return {
            'assets': balances.get('asset', Decimal(0)),
            'liabilities': balances.get('liability', Decimal(0)),
            'equity': balances.get('equity', Decimal(0))
        }