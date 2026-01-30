from fastapi import APIRouter, Depends, HTTPException, status
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
