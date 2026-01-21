from app.domain.payments.entities import Escrow, EscrowState
from app.domain.payments.ports import PaymentProvider
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.application.ledger.record_event import RecordLedgerEventUseCase
from app.domain.ledger.entities import LedgerEvent, AggregateType, LedgerEventType, Direction, ReferenceType
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from decimal import Decimal


class FundEscrowUseCase:
    def __init__(self, escrow_repo: EscrowRepository, order_repo: OrderRepository, payment_provider: PaymentProvider, ledger_repo: LedgerRepository, account_repo: AccountRepository, journal_repo: JournalRepository):
        self.escrow_repo = escrow_repo
        self.order_repo = order_repo
        self.payment_provider = payment_provider
        self.record_ledger_event = RecordLedgerEventUseCase(ledger_repo, account_repo, journal_repo)

    def execute(self, escrow_id: str) -> Escrow:
        # Load escrow
        escrow = self.escrow_repo.get_by_id(escrow_id)
        if not escrow:
            raise ValueError("Escrow not found")

        # Ensure state is CREATED
        if escrow.state not in (EscrowState.CREATED, 'CREATED'):
            raise ValueError(f"Escrow is already {escrow.state}")

        # Call payment provider
        reference = self.payment_provider.fund_escrow(escrow_id, escrow.amount)

        # Mark as funded
        escrow.mark_funded(reference)

        # Double-entry logic:
        # 1. Debit the Merchant (Wallet/Bank decrease)
        order = self.order_repo.get_by_id(escrow.order_id)
        if order and order.merchant_id:
            merchant_debit = LedgerEvent(
                aggregate_type=AggregateType.USER,
                aggregate_id=order.merchant_id,
                event_type=LedgerEventType.ESCROW_FUNDED,
                amount=Decimal(escrow.amount),
                direction=Direction.DEBIT,
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                event_metadata={"reference": reference, "note": "Payment for order funded to escrow"}
            )
            self.record_ledger_event.execute(merchant_debit)

        # 2. Credit the Escrow (Escrow system liability increase)
        escrow_credit = LedgerEvent(
            aggregate_type=AggregateType.ESCROW,
            aggregate_id=escrow_id,
            event_type=LedgerEventType.ESCROW_FUNDED,
            amount=Decimal(escrow.amount),
            direction=Direction.CREDIT,
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            event_metadata={"reference": reference}
        )
        self.record_ledger_event.execute(escrow_credit)

        # Save
        return self.escrow_repo.save(escrow)