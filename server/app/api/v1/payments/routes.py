from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_permission
from app.application.services.escrow_lifecycle_service import EscrowLifecycleService
from app.infrastructure.external.provider_factory import get_payment_provider

router = APIRouter()

@router.post("/{escrow_id}/fund", response_model=dict, dependencies=[Depends(require_permission("escrow:fund"))])
def fund_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """
    Fund an escrow - CREATED → FUNDED

    Creates accounting entries for customer payment obligation.
    """
    try:
        # Get payment provider reference (simulate external payment confirmation)
        payment_provider = get_payment_provider("BANK")
        provider_reference = f"MOCK-TXN-{escrow_id[:8].upper()}"

        # Use lifecycle service for atomic transition
        lifecycle_service = EscrowLifecycleService(db)
        funded_escrow = lifecycle_service.fund_escrow(escrow_id, provider_reference)

        return {
            "escrow_id": funded_escrow.id,
            "state": funded_escrow.state.value,
            "provider_reference": provider_reference,
            "message": "Escrow funded successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fund escrow: {str(e)}")

@router.post("/{escrow_id}/release", response_model=dict, dependencies=[Depends(require_permission("escrow:release"))])
def release_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """
    Release an escrow - FUNDED → RELEASED

    Creates accounting entries for farmer payment.
    """
    try:
        provider_reference = f"RELEASE-{escrow_id[:8].upper()}"

        lifecycle_service = EscrowLifecycleService(db)
        released_escrow = lifecycle_service.release_escrow(escrow_id, provider_reference)

        return {
            "escrow_id": released_escrow.id,
            "state": released_escrow.state.value,
            "provider_reference": provider_reference,
            "message": "Escrow released successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to release escrow: {str(e)}")


@router.post("/{escrow_id}/refund", response_model=dict, dependencies=[Depends(require_permission("escrow:refund"))])
def refund_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """
    Refund an escrow - FUNDED → REFUNDED

    Creates accounting entries for customer refund.
    """
    try:
        provider_reference = f"REFUND-{escrow_id[:8].upper()}"

        lifecycle_service = EscrowLifecycleService(db)
        refunded_escrow = lifecycle_service.refund_escrow(escrow_id, provider_reference)

        return {
            "escrow_id": refunded_escrow.id,
            "state": refunded_escrow.state.value,
            "provider_reference": provider_reference,
            "message": "Escrow refunded successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refund escrow: {str(e)}")

