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
        # Removed self.session.commit() to allow atomic transactions with other operations

    def get_balance_for_account(self, account_id: str) -> Decimal:
        # Get account type first
        account = self.session.query(AccountORM).filter(AccountORM.id == account_id).first()
        if not account:
            return Decimal(0)

        if account.account_type == 'ASSET':
            balance_expr = JournalLineORM.debit_amount - JournalLineORM.credit_amount
        else:  # LIABILITY, EQUITY, REVENUE
            balance_expr = JournalLineORM.credit_amount - JournalLineORM.debit_amount

        result = self.session.query(func.sum(balance_expr)).filter(JournalLineORM.account_id == account_id).scalar()
        return Decimal(str(result or 0))

    def get_trial_balance(self) -> Dict[str, Decimal]:
        # Group by account type and sum balances
        # For assets: debit - credit
        # For liabilities/equity: credit - debit
        query = self.session.query(
            AccountORM.account_type,
            func.sum(
                case(
                    (AccountORM.account_type == 'ASSET', JournalLineORM.debit_amount - JournalLineORM.credit_amount),
                    else_=JournalLineORM.credit_amount - JournalLineORM.debit_amount
                )
            ).label('balance')
        ).join(JournalLineORM, AccountORM.id == JournalLineORM.account_id
        ).group_by(AccountORM.account_type).all()

        balances = {account_type.value.lower(): Decimal(str(balance or 0)) for account_type, balance in query}
        # Include revenue in equity
        equity = balances.get('equity', Decimal(0)) + balances.get('revenue', Decimal(0))
        return {
            'assets': balances.get('asset', Decimal(0)),
            'liabilities': balances.get('liability', Decimal(0)),
            'equity': equity
        }