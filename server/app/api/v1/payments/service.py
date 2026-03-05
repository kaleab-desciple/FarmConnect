from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from app.infrastructure.db.models.escrow import EscrowORM
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
    auto_confirm: bool = True,
):
    """
    Fund an escrow and optionally auto-confirm the order.
    
    Args:
        db: Database session
        escrow_id: The escrow ID to fund
        amount: Amount to fund
        source_account: Source account for the payment
        provider_type: Payment provider type
        auto_confirm: If True (default), automatically confirm the order after funding.
                     This transitions the order from FUNDED to CONFIRMED, allowing delivery assignment.
    """
    from app.application.services.escrow_lifecycle_service import EscrowLifecycleService
    
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

    # Use the lifecycle service to handle state transition with all side effects
    # This will:
    # 1. Transition escrow CREATED → FUNDED
    # 2. Confirm sale in inventory (reserved → sold)
    # 3. Update order status (FUNDED → CONFIRMED if auto_confirm=True)
    lifecycle_service = EscrowLifecycleService(db)
    try:
        # Pass provider reference as the payment reference
        funded_escrow = lifecycle_service.fund_escrow(
            escrow_id=str(escrow_id),
            provider_reference=f"payment_{escrow_id}",
            auto_confirm=auto_confirm
        )
        return funded_escrow
    except Exception as e:
        # If lifecycle service fails, at least ensure the escrow state is updated
        # This is a fallback to ensure the payment is recorded
        escrow.state = transition(
            EscrowState(escrow.state),
            EscrowState.FUNDED
        ).value
        db.commit()
        raise e


class PaymentService:
    pass
