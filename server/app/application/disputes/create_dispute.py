from datetime import datetime, timezone
from app.domain.disputes.entities import Dispute
from app.domain.payments.entities import Escrow, EscrowState
from app.infrastructure.repositories.dispute_repo import DisputeRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.payment_repo import EscrowRepository


class CreateDisputeUseCase:
    def __init__(self, dispute_repo: DisputeRepository, order_repo: OrderRepository, escrow_repo: EscrowRepository):
        self.dispute_repo = dispute_repo
        self.order_repo = order_repo
        self.escrow_repo = escrow_repo

    def execute(self, order_id: str, raised_by: str, reason: str) -> Dispute:
        # Load order
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Load escrow
        escrow = self.escrow_repo.get_by_order_id(order_id)
        if not escrow:
            raise ValueError("Escrow not found for order")

        # Ensure escrow is FUNDED
        if escrow.state not in (EscrowState.FUNDED, 'FUNDED'):
            raise ValueError(f"Cannot dispute escrow in state {escrow.state}")

        # Create dispute
        dispute = Dispute(
            order_id=order_id,
            raised_by=raised_by,
            reason=reason,
            state='OPEN',
            created_at=datetime.now(timezone.utc)
        )

        # Mark escrow as disputed
        escrow.mark_disputed()

        # Save dispute and escrow
        saved_dispute = self.dispute_repo.save(dispute)
        self.escrow_repo.save(escrow)

        return saved_dispute