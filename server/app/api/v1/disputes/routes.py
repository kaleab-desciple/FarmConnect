from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
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


from app.core.auth import require_permission


class CreateDisputeRequest(BaseModel):
    order_id: str
    raised_by: str
    reason: str


class ResolveDisputeRequest(BaseModel):
    resolution: DisputeResolution
    penalty_amount: Decimal = Decimal(0)


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
