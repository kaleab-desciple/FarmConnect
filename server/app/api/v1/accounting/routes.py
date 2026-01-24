from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_permission
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from app.application.accounting.get_trial_balance import GetTrialBalance, TrialBalance
from app.application.accounting.get_account_balance import GetAccountBalance, GetAccountBalanceRequest
from decimal import Decimal

# Use the same tag casing as `api_router.include_router(..., tags=["Accounting"])`
# so the OpenAPI UI groups endpoints under a single, consistent heading.
router = APIRouter(tags=["Accounting"])

@router.get("/trial-balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_trial_balance(db: Session = Depends(get_db)):
    journal_repo = JournalRepository(db)
    use_case = GetTrialBalance(journal_repo)
    balance = use_case.execute()
    return {
        "assets": float(balance.assets),
        "liabilities": float(balance.liabilities),
        "equity": float(balance.equity)
    }


@router.get("/accounts", response_model=list, dependencies=[Depends(require_permission("ledger:read"))])
def get_accounts(db: Session = Depends(get_db)):
    from app.infrastructure.db.models.account import AccountORM
    accounts = db.query(AccountORM).all()
    return [
        {
            "id": account.id,
            "owner_type": account.owner_type.value,
            "owner_id": account.owner_id,
            "account_type": account.account_type.value,
            "name": account.name,
            "currency": account.currency,
            "created_at": account.created_at.isoformat()
        }
        for account in accounts
    ]


@router.get("/accounts/{account_id}/balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_account_balance(account_id: str, db: Session = Depends(get_db)):
    journal_repo = JournalRepository(db)
    use_case = GetAccountBalance(journal_repo)
    request = GetAccountBalanceRequest(account_id)
    balance = use_case.execute(request)
    return {"balance": float(balance)}


@router.get("/journal/{reference_type}/{reference_id}", response_model=list, dependencies=[Depends(require_permission("ledger:read"))])
def get_journal_entries(reference_type: str, reference_id: str, db: Session = Depends(get_db)):
    journal_repo = JournalRepository(db)
    # Query journal entries by reference
    # For now, return a simple list - in production you'd implement proper repository method
    from app.infrastructure.db.models.journal_entry import JournalEntryORM, JournalLineORM
    from sqlalchemy.orm import joinedload

    entries = db.query(JournalEntryORM).options(joinedload(JournalEntryORM.lines)).filter(
        JournalEntryORM.reference_type == reference_type,
        JournalEntryORM.reference_id == reference_id
    ).all()

    result = []
    for entry in entries:
        result.append({
            "id": entry.id,
            "reference_type": entry.reference_type,
            "reference_id": entry.reference_id,
            "description": entry.description,
            "created_at": entry.created_at.isoformat(),
            "lines": [
                {
                    "account_id": line.account_id,
                    "debit_amount": float(line.debit_amount),
                    "credit_amount": float(line.credit_amount)
                }
                for line in entry.lines
            ]
        })
    return result