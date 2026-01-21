from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from ..deps import get_db
from .service import fund_escrow

router = APIRouter()

@router.post("/escrows/{escrow_id}/fund")
def fund(
    escrow_id: UUID,
    amount: Decimal,
    source_account: str,
    provider: str,
    db: Session = Depends(get_db)
):
    escrow = fund_escrow(
        db=db,
        escrow_id=escrow_id,
        amount=amount,
        source_account=source_account,
        provider_type=provider,
    )
    return {
        "escrow_id": escrow.id,
        "state": escrow.state
    }
