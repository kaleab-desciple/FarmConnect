from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_permission
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.application.ledger.get_balance import GetBalanceForUserUseCase, GetBalanceForEscrowUseCase, GetLedgerForReferenceUseCase

router = APIRouter()

@router.get("/users/{user_id}", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_user_ledger(user_id: str, db: Session = Depends(get_db)):
    ledger_repo = LedgerRepository(db)
    use_case = GetBalanceForUserUseCase(ledger_repo)

    try:
        result = use_case.execute(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/escrows/{escrow_id}", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_escrow_ledger(escrow_id: str, db: Session = Depends(get_db)):
    ledger_repo = LedgerRepository(db)
    use_case = GetBalanceForEscrowUseCase(ledger_repo)

    try:
        result = use_case.execute(escrow_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/references/{reference_type}/{reference_id}", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_reference_ledger(reference_type: str, reference_id: str, db: Session = Depends(get_db)):
    ledger_repo = LedgerRepository(db)
    use_case = GetLedgerForReferenceUseCase(ledger_repo)

    try:
        result = use_case.execute(reference_type, reference_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))