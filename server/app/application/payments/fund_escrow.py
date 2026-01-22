from app.domain.payments.entities import Escrow, EscrowState
from app.domain.payments.services.escrow_service import EscrowService
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

        # Get order to get merchant_id
        order = self.order_repo.get_by_id(escrow.order_id)
        if not order or not order.merchant_id:
            raise ValueError("Order or merchant not found")

        # Call payment provider
        reference = self.payment_provider.fund_escrow(escrow_id, escrow.amount)

        # Use domain service for state transition and accounting
        transition_result = EscrowService.fund_escrow(escrow, order.merchant_id, reference)

        # Apply the transition
        escrow.state = transition_result.new_state
        escrow.provider_reference = reference

        # Record the accounting instructions as ledger events
        for instruction in transition_result.accounting_instructions:
            ledger_event = LedgerEvent(
                aggregate_type=AggregateType.ESCROW,
                aggregate_id=escrow_id,
                event_type=LedgerEventType.ESCROW_FUNDED,
                amount=Decimal(instruction.debit or instruction.credit),
                direction=Direction.DEBIT if instruction.debit else Direction.CREDIT,
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                event_metadata={
                    "reference": reference,
                    "account_type": instruction.account_type,
                    "account_owner": instruction.account_owner
                }
            )
            self.record_ledger_event.execute(ledger_event)

        # Save
        return self.escrow_repo.save(escrow)