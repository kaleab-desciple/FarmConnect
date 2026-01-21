from app.domain.payments.entities import Escrow, EscrowState
from app.domain.payments.ports import PaymentProvider
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.infrastructure.repositories.reputation_repo import ReputationRepository
from app.application.ledger.record_event import RecordLedgerEventUseCase
from app.domain.ledger.entities import LedgerEvent, AggregateType, LedgerEventType, Direction, ReferenceType
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from decimal import Decimal


class ReleaseEscrowUseCase:
    def __init__(self, escrow_repo: EscrowRepository, order_repo: OrderRepository, payment_provider: PaymentProvider, ledger_repo: LedgerRepository, account_repo: AccountRepository, journal_repo: JournalRepository, reputation_repo: ReputationRepository):
        self.escrow_repo = escrow_repo
        self.order_repo = order_repo
        self.payment_provider = payment_provider
        self.record_ledger_event = RecordLedgerEventUseCase(ledger_repo, account_repo, journal_repo)
        self.reputation_repo = reputation_repo

    def execute(self, escrow_id: str) -> Escrow:
        # Load escrow
        escrow = self.escrow_repo.get_by_id(escrow_id)
        if not escrow:
            raise ValueError("Escrow not found")

        # Ensure state is FUNDED
        if escrow.state not in (EscrowState.FUNDED, 'FUNDED'):
            raise ValueError(f"Escrow must be in FUNDED state to be released, current state: {escrow.state}")

        # Call payment provider
        reference = self.payment_provider.release_funds(escrow_id)

        # Mark as released
        escrow.release(reference)

        # Record Ledger events
        # 1. Debit the Escrow (Escrow system liability decrease)
        escrow_debit = LedgerEvent(
            aggregate_type=AggregateType.ESCROW,
            aggregate_id=escrow_id,
            event_type=LedgerEventType.ESCROW_RELEASED,
            amount=Decimal(escrow.amount),
            direction=Direction.DEBIT,
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            event_metadata={"reference": reference}
        )
        self.record_ledger_event.execute(escrow_debit)

        # 2. Credit the Farmer (Asset/Wallet increase)
        order = self.order_repo.get_by_id(escrow.order_id)
        if order and order.farmer_id:
            farmer_credit = LedgerEvent(
                aggregate_type=AggregateType.USER,
                aggregate_id=order.farmer_id,
                event_type=LedgerEventType.ESCROW_RELEASED,
                amount=Decimal(escrow.amount),
                direction=Direction.CREDIT,
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                event_metadata={"reference": reference, "note": "Funds released from escrow for completed order"}
            )
            self.record_ledger_event.execute(farmer_credit)

        # Save

        # Update reputation for successful order completion
        if order:
            # Update farmer reputation
            if order.farmer_id:
                farmer_reputation = self.reputation_repo.create_or_get(order.farmer_id)
                farmer_reputation.record_successful_order()
                self.reputation_repo.save(farmer_reputation)
            
            # Update merchant reputation
            if order.merchant_id:
                merchant_reputation = self.reputation_repo.create_or_get(order.merchant_id)
                merchant_reputation.record_successful_order()
                self.reputation_repo.save(merchant_reputation)

        # Save
        return self.escrow_repo.save(escrow)
