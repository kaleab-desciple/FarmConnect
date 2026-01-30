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


from app.application.accounting.get_journal_entries import GetJournalEntriesByReference, GetJournalEntriesByReferenceRequest

@router.get("/journal/{reference_type}/{reference_id}", response_model=list)
def get_journal_entries(reference_type: str, reference_id: str, db: Session = Depends(get_db)):
    journal_repo = JournalRepository(db)
    use_case = GetJournalEntriesByReference(journal_repo)
    request = GetJournalEntriesByReferenceRequest(reference_type, reference_id)
    entries = use_case.execute(request)
    
    return [
        {
            "id": str(entry.id),
            "reference_type": entry.reference_type.value,
            "reference_id": entry.reference_id,
            "description": entry.description,
            "created_at": entry.created_at.isoformat(),
            "lines": [
                {
                    "account_id": str(line.account_id),
                    "debit_amount": float(line.debit_amount),
                    "credit_amount": float(line.credit_amount)
                }
                for line in entry.lines
            ]
        }
        for entry in entries
    ]