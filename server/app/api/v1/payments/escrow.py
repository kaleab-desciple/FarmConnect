from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared_models.escrow import Escrow as EscrowDTO
from app.core.database import get_db
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.reputation_repo import ReputationRepository
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from app.infrastructure.external.banks.mock_bank import MockBankProvider
from app.application.payments.fund_escrow import FundEscrowUseCase
from app.application.payments.release_escrow import ReleaseEscrowUseCase
from app.infrastructure.db.mappers import domain_to_dto

router = APIRouter()

@router.post("/{escrow_id}/fund", response_model=dict)
def fund_escrow(escrow_id: str, db: Session = Depends(get_db)):
    escrow_repo = EscrowRepository(db)
    order_repo = OrderRepository(db)
    ledger_repo = LedgerRepository(db)
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    payment_provider = MockBankProvider()
    use_case = FundEscrowUseCase(escrow_repo, order_repo, payment_provider, ledger_repo, account_repo, journal_repo)

    try:
        funded_escrow = use_case.execute(escrow_id)
        escrow_dto = domain_to_dto(funded_escrow)
        db.commit()
        return {
            "escrow_id": escrow_dto.id,
            "state": escrow_dto.state,
            "provider_reference": escrow_dto.provider_reference
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{escrow_id}/release", response_model=dict)
def release_escrow(escrow_id: str, db: Session = Depends(get_db)):
    escrow_repo = EscrowRepository(db)
    order_repo = OrderRepository(db)
    ledger_repo = LedgerRepository(db)
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    reputation_repo = ReputationRepository(db)
    payment_provider = MockBankProvider()
    use_case = ReleaseEscrowUseCase(escrow_repo, order_repo, payment_provider, ledger_repo, account_repo, journal_repo, reputation_repo)

    try:
        released_escrow = use_case.execute(escrow_id)
        escrow_dto = domain_to_dto(released_escrow)
        db.commit()
        return {
            "escrow_id": escrow_dto.id,
            "state": escrow_dto.state,
            "provider_reference": escrow_dto.provider_reference
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise e