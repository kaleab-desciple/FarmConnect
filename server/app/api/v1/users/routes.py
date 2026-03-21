from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from shared_models.user import User
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain
from app.infrastructure.repositories.user_repo import UserRepository
from app.infrastructure.repositories.reputation_repo import ReputationRepository
from app.core.database import get_db
from app.core.auth import require_permission, TokenPayload

router = APIRouter()

@router.post("/", response_model=User, dependencies=[Depends(require_permission("users:write"))])
def create_user(user: User, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    try:
        repo.save(user)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "users_phone_key" in error_msg:
            raise HTTPException(status_code=400, detail="User with this phone number already exists.")
        if "users_email_key" in error_msg:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
        raise HTTPException(status_code=400, detail=f"Database integrity error: {error_msg}")
    return user

@router.get("/{user_id}/reputation", response_model=dict, dependencies=[Depends(require_permission("users:reputation"))])
def get_user_reputation(user_id: str, db: Session = Depends(get_db)):
    repo = ReputationRepository(db)
    reputation = repo.create_or_get(user_id)
    db.commit()
    return {
        "user_id": reputation.user_id,
        "completed_orders": reputation.completed_orders,
        "successful_orders": reputation.successful_orders,
        "disputes_lost": reputation.disputes_lost,

        "avg_delivery_delay": reputation.avg_delivery_delay,
        "reputation_score": reputation.reputation_score
    }

@router.get("/{user_id}/credit-score", response_model=dict, dependencies=[Depends(require_permission("users:read"))])
def get_user_credit_score(user_id: str, db: Session = Depends(get_db)):
    repo = ReputationRepository(db)
    reputation = repo.create_or_get(user_id)
    db.commit()

    # Determine risk level
    score = reputation.reputation_score
    if score >= 80:
        risk_level = "LOW"
    elif score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "score": score,
        "risk_level": risk_level
    }


# ---------------------------------------------------------------------------
# Onboarding Approval (Gap 4)
# ---------------------------------------------------------------------------

class OnboardingDecisionRequest(BaseModel):
    """Optional reasoning note for manager/admin to record."""
    note: Optional[str] = None


@router.get(
    "/pending-approval",
    response_model=list,
    summary="List users pending onboarding approval",
    dependencies=[Depends(require_permission("users:approve"))],
)
def list_pending_approval(db: Session = Depends(get_db)):
    """
    Return all FARMER / MERCHANT users whose onboarding_status is PENDING_REVIEW.
    Visible to MANAGER and ADMIN only.
    """
    from app.infrastructure.db.models.user import UserORM
    orms = (
        db.query(UserORM)
        .filter(UserORM.onboarding_status == "PENDING_REVIEW")
        .all()
    )
    return [
        {
            "user_id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "onboarding_status": u.onboarding_status,
            "onboarding_agent_id": u.onboarding_agent_id,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in orms
    ]


@router.post(
    "/{user_id}/approve",
    response_model=dict,
    summary="Approve a pending farmer/merchant onboarding",
    dependencies=[Depends(require_permission("users:approve"))],
)
def approve_user_onboarding(
    user_id: str,
    request: OnboardingDecisionRequest = OnboardingDecisionRequest(),
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:approve")),
):
    """
    Approve an onboarded FARMER or MERCHANT.
    Sets onboarding_status → ACTIVE.

    **Required roles:** MANAGER, ADMIN
    """
    from app.domain.common.enums import OnboardingStatus
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = repo.update(user_id, {"onboarding_status": OnboardingStatus.ACTIVE.value})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update user")

    return {
        "user_id": user_id,
        "onboarding_status": OnboardingStatus.ACTIVE.value,
        "approved_by": current_user.keycloak_id,
        "note": request.note,
    }


@router.post(
    "/{user_id}/reject",
    response_model=dict,
    summary="Reject a pending farmer/merchant onboarding",
    dependencies=[Depends(require_permission("users:approve"))],
)
def reject_user_onboarding(
    user_id: str,
    request: OnboardingDecisionRequest = OnboardingDecisionRequest(),
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_permission("users:approve")),
):
    """
    Reject an onboarded FARMER or MERCHANT application.
    Sets onboarding_status → REJECTED.

    **Required roles:** MANAGER, ADMIN
    """
    from app.domain.common.enums import OnboardingStatus
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = repo.update(user_id, {"onboarding_status": OnboardingStatus.REJECTED.value})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update user")

    return {
        "user_id": user_id,
        "onboarding_status": OnboardingStatus.REJECTED.value,
        "rejected_by": current_user.keycloak_id,
        "note": request.note,
    }
