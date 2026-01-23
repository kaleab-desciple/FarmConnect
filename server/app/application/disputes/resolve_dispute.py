from datetime import datetime, timezone
from decimal import Decimal
from app.domain.disputes.entities import Dispute
from app.domain.payments.entities import Escrow
from app.domain.payments.ports import PaymentProvider
from app.infrastructure.repositories.dispute_repo import DisputeRepository
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.reputation_repo import ReputationRepository
from app.application.reputation.update_reputation import UpdateReputationUseCase
from app.domain.common.enums import DisputeResolution


class ResolveDisputeUseCase:
    def __init__(self, dispute_repo: DisputeRepository, escrow_repo: EscrowRepository, payment_provider: PaymentProvider, reputation_repo: ReputationRepository):
        self.dispute_repo = dispute_repo
        self.escrow_repo = escrow_repo
        self.payment_provider = payment_provider
        self.reputation_repo = reputation_repo
        self.update_reputation_use_case = UpdateReputationUseCase(reputation_repo)

    def execute(self, dispute_id: str, resolution: DisputeResolution, penalty_amount: Decimal = Decimal(0)) -> Dispute:
        # Load dispute
        dispute = self.dispute_repo.get_by_id(dispute_id)
        if not dispute:
            raise ValueError("Dispute not found")

        # Load escrow
        escrow = self.escrow_repo.get_by_order_id(dispute.order_id)
        if not escrow:
            raise ValueError("Escrow not found for dispute")

        # Ensure dispute is OPEN
        if dispute.state != 'OPEN':
            raise ValueError(f"Dispute is already {dispute.state}")

        # Apply resolution
        if resolution == DisputeResolution.RELEASE:
            reference = self.payment_provider.release_funds(escrow.id)
            escrow.resolve_release(reference)
        elif resolution == DisputeResolution.PARTIAL_RELEASE:
            reference = self.payment_provider.partial_release(escrow.id, penalty_amount)
            escrow.resolve_partial_release(penalty_amount, reference)
        elif resolution == DisputeResolution.REFUND:
            reference = self.payment_provider.refund_funds(escrow.id)
            escrow.resolve_refund(reference)
        else:
            raise ValueError(f"Invalid resolution: {resolution}")

        # Update dispute
        dispute.resolve(resolution)

        # Determine winner and update reputation
        if resolution == DisputeResolution.RELEASE:
            # Farmer wins (gets full payment)
            self.update_reputation_use_case.execute(dispute.raised_by, 'dispute_won')
        elif resolution == DisputeResolution.PARTIAL_RELEASE:
            # Partial win for farmer, penalty for merchant
            self.update_reputation_use_case.execute(dispute.raised_by, 'penalty_applied', penalty_amount=penalty_amount)
        elif resolution == DisputeResolution.REFUND:
            # Merchant wins, farmer loses dispute
            self.update_reputation_use_case.execute(dispute.raised_by, 'dispute_lost')

        # Save
        saved_dispute = self.dispute_repo.save(dispute)
        self.escrow_repo.save(escrow)

        return saved_dispute