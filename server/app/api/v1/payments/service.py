from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from app.infrastructure.db.models.payment import EscrowORM
from app.infrastructure.external.provider_factory import get_payment_provider
from app.domain.payments.entities import EscrowState
from app.domain.payments.exceptions import PaymentFailed
from app.api.v1.payments.state_machine import transition

def fund_escrow(
    db: Session,
    escrow_id: UUID,
    amount: Decimal,
    source_account: str,
    provider_type: str,
):
    escrow = db.get(EscrowORM, escrow_id)

    if escrow is None:
        raise ValueError("Escrow not found")

    provider = get_payment_provider(provider_type)

    try:
        provider.debit(
            reference_id=escrow.id,
            amount=amount,
            source_account=source_account,
        )
    except PaymentFailed as e:
        # no state change, retry allowed
        raise e

    # state transition AFTER money movement
    escrow.state = transition(
        EscrowState(escrow.state),
        EscrowState.FUNDED
    ).value

    db.commit()
    return escrow


class PaymentService:
    pass
