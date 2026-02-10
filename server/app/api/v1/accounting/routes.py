from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_permission
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from app.application.accounting.get_trial_balance import GetTrialBalance, TrialBalance
from app.application.accounting.get_account_balance import GetAccountBalance, GetAccountBalanceRequest
from app.application.accounting.get_user_balance import GetUserBalance, GetUserBalanceRequest
from app.application.accounting.get_escrow_balance import GetEscrowBalance, GetEscrowBalanceRequest
from app.application.accounting.get_user_statement import GetUserStatement, GetUserStatementRequest
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional

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


@router.get("/users/{user_id}/balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_user_balance(user_id: str, db: Session = Depends(get_db)):
    """Get consolidated balance for a user across all their accounts."""
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    use_case = GetUserBalance(account_repo, journal_repo)
    request = GetUserBalanceRequest(user_id)
    
    try:
        balance = use_case.execute(request)
        return {
            "user_id": balance.user_id,
            "cash_balance": float(balance.cash_balance),
            "payable_balance": float(balance.payable_balance),
            "net_balance": float(balance.net_balance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/escrows/{escrow_id}/balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_escrow_balance(escrow_id: str, db: Session = Depends(get_db)):
    """Get balance for a specific escrow account."""
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    use_case = GetEscrowBalance(account_repo, journal_repo)
    request = GetEscrowBalanceRequest(escrow_id)
    
    try:
        balance = use_case.execute(request)
        return {
            "escrow_id": balance.escrow_id,
            "holding_balance": float(balance.holding_balance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/statement", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_user_statement(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date in ISO format (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get detailed transaction statement for a user."""
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    use_case = GetUserStatement(account_repo, journal_repo)
    
    # Parse dates if provided - make them timezone-aware (UTC) to match database timestamps
    start_dt = None
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
    
    end_dt = None
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        if end_dt.tzinfo is None:
            # Set to end of day for inclusive date range
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            
    request = GetUserStatementRequest(user_id, start_dt, end_dt)
    
    try:
        statement = use_case.execute(request)
        return {
            "user_id": statement.user_id,
            "opening_balance": float(statement.opening_balance),
            "closing_balance": float(statement.closing_balance),
            "lines": [
                {
                    "date": line.date.isoformat(),
                    "description": line.description,
                    "debit": float(line.debit),
                    "credit": float(line.credit),
                    "balance": float(line.balance)
                }
                for line in statement.lines
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))