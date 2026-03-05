from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.core.database import get_db
from app.infrastructure.repositories.dispute_repo import DisputeRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.reputation_repo import ReputationRepository
from app.infrastructure.external.banks.mock_bank import MockBankProvider
from app.application.disputes.create_dispute import CreateDisputeUseCase
from app.application.disputes.resolve_dispute import ResolveDisputeUseCase
from shared_models.enums import DisputeResolution
from app.core.auth import require_permission, TokenPayload


class CreateDisputeRequest(BaseModel):
    order_id: str
    raised_by: str
    reason: str


class ResolveDisputeRequest(BaseModel):
    resolution: DisputeResolution
    penalty_amount: Decimal = Decimal(0)


class EscalateDisputeRequest(BaseModel):
    """
    Escalation request for the dispute chain.
    MODERATOR  → target_role: AGENT or MANAGER
    MANAGER    → target_role: ADMIN
    """
    target_role: str  # AGENT | MANAGER | ADMIN
    note: Optional[str] = None


router = APIRouter()


@router.post("/", response_model=dict, dependencies=[Depends(require_permission("disputes:create"))])
def create_dispute(request: CreateDisputeRequest, db: Session = Depends(get_db)):
    dispute_repo = DisputeRepository(db)
    order_repo = OrderRepository(db)
    escrow_repo = EscrowRepository(db)
    use_case = CreateDisputeUseCase(dispute_repo, order_repo, escrow_repo)

    try:
        dispute = use_case.execute(request.order_id, request.raised_by, request.reason)
        db.commit()
        return {
            "dispute_id": dispute.id,
            "order_id": dispute.order_id,
            "state": dispute.state,
            "created_at": dispute.created_at
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise e


@router.post("/{dispute_id}/resolve", response_model=dict, dependencies=[Depends(require_permission("disputes:resolve"))])
def resolve_dispute(dispute_id: str, request: ResolveDisputeRequest, db: Session = Depends(get_db)):
    dispute_repo = DisputeRepository(db)
    escrow_repo = EscrowRepository(db)
    reputation_repo = ReputationRepository(db)
    payment_provider = MockBankProvider()
    use_case = ResolveDisputeUseCase(dispute_repo, escrow_repo, payment_provider, reputation_repo)

    try:
        dispute = use_case.execute(dispute_id, request.resolution, request.penalty_amount)
        db.commit()
        return {
            "dispute_id": dispute.id,
            "state": dispute.state,
            "resolution": dispute.resolution,
            "resolved_at": dispute.resolved_at
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise e


@router.post(
    "/{dispute_id}/escalate",
    response_model=dict,
    summary="Escalate a dispute to the next handler",
    dependencies=[Depends(require_permission("disputes:resolve"))],
)
def escalate_dispute(
    dispute_id: str,
    request: EscalateDisputeRequest,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("disputes:resolve")),
):
    """
    Escalate a dispute along the resolution chain.

    **Allowed escalation paths:**
    - MODERATOR → AGENT   (quality dispute needing physical validation)
    - MODERATOR → MANAGER (suspicious / certification fraud)
    - MANAGER   → ADMIN   (unresolvable conflict)

    Requires `disputes:resolve` permission (ADMIN, MANAGER).
    MODERATOR role is enforced via the permission matrix.
    """
    allowed_targets = {"AGENT", "MANAGER", "ADMIN"}
    target = request.target_role.upper()
    if target not in allowed_targets:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target_role '{target}'. Must be one of {allowed_targets}."
        )

    dispute_repo = DisputeRepository(db)
    dispute = dispute_repo.get_by_id(dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    from app.domain.common.enums import DisputeState
    if dispute.state == DisputeState.RESOLVED:
        raise HTTPException(status_code=400, detail="Resolved disputes cannot be escalated")

    try:
        dispute.escalate(target, note=request.note)
        updated = dispute_repo.update(dispute_id, {
            "state": dispute.state,
            "handler_role": dispute.handler_role,
            "escalated_to": dispute.escalated_to,
            "escalation_note": dispute.escalation_note,
        })
        db.commit()
        return {
            "dispute_id": updated.id,
            "state": updated.state,
            "escalated_to": updated.escalated_to,
            "escalation_note": updated.escalation_note,
            "escalated_by": current_user.sub,
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise e
