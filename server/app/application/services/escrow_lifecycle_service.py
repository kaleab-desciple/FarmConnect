"""
Application service for escrow lifecycle management.

Handles state transitions with accounting entries in atomic transactions.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.domain.payments.services.escrow_service import (
    EscrowDomainService,
    EscrowTransitionResult,
    AccountingInstruction
)
from app.domain.payments.entities import Escrow, EscrowState
from app.domain.ledger.entities import LedgerEvent, AggregateType, LedgerEventType, Direction, ReferenceType
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from app.infrastructure.repositories.order_repo import OrderRepository
from app.application.accounting.ledger_to_journal_mapper import LedgerToJournalMapper
from app.application.accounting.post_journal_entry import PostJournalEntry, PostJournalEntryRequest


class EscrowLifecycleService:
    """
    Application service managing escrow state transitions.

    Ensures atomicity: state change + accounting entries.
    """

    def __init__(self, session: Session):
        self.session = session
        self.escrow_repo = EscrowRepository(session)
        self.ledger_repo = LedgerRepository(session)
        self.account_repo = AccountRepository(session)
        self.journal_repo = JournalRepository(session)
        self.order_repo = OrderRepository(session)
        self.domain_service = EscrowDomainService()
        self.journal_mapper = LedgerToJournalMapper(self.account_repo)
        self.post_journal_uc = PostJournalEntry(self.journal_repo, self.account_repo)

    def fund_escrow(self, escrow_id: str, provider_reference: str) -> Escrow:
        """
        Fund an escrow - CREATED → FUNDED

        Creates accounting entries for customer payment obligation.
        """
        return self._execute_transition(
            escrow_id,
            lambda escrow: self._fund_escrow_with_order(escrow, provider_reference),
            LedgerEventType.ESCROW_FUNDED,
            f"Escrow funded with reference {provider_reference}"
        )

    def _fund_escrow_with_order(self, escrow: Escrow, provider_reference: str) -> EscrowTransitionResult:
        """Helper to get order and call domain service."""
        order = self.order_repo.get_by_id(escrow.order_id)
        if not order or not order.merchant_id:
            raise ValueError("Order or merchant not found")
        return self.domain_service.fund_escrow(escrow, order.merchant_id, provider_reference)

    def release_escrow(self, escrow_id: str, provider_reference: str) -> Escrow:
        """
        Release an escrow - FUNDED → RELEASED

        Creates accounting entries for farmer payment.
        """
        return self._execute_transition(
            escrow_id,
            lambda escrow: self._release_escrow_with_order(escrow, provider_reference),
            LedgerEventType.ESCROW_RELEASED,
            f"Escrow released with reference {provider_reference}"
        )

    def refund_escrow(self, escrow_id: str, provider_reference: str) -> Escrow:
        """
        Refund an escrow - FUNDED → REFUNDED

        Creates accounting entries for customer refund.
        """
        return self._execute_transition(
            escrow_id,
            lambda escrow: self._refund_escrow_with_order(escrow, provider_reference),
            LedgerEventType.ESCROW_REFUNDED,
            f"Escrow refunded with reference {provider_reference}"
        )

    def penalize_escrow(self, escrow_id: str, provider_reference: str) -> Escrow:
        """
        Penalize an escrow - FUNDED → PENALIZED

        Creates accounting entries for platform penalty revenue.
        """
        return self._execute_transition(
            escrow_id,
            lambda escrow: self.domain_service.penalize_escrow(escrow, provider_reference),
            LedgerEventType.PENALTY_APPLIED,
            f"Escrow penalized with reference {provider_reference}"
        )

    def _release_escrow_with_order(self, escrow: Escrow, provider_reference: str) -> EscrowTransitionResult:
        """Helper to get order and call domain service."""
        order = self.order_repo.get_by_id(escrow.order_id)
        if not order or not order.farmer_id:
            raise ValueError("Order or farmer not found")
        return self.domain_service.release_escrow(escrow, order.farmer_id, provider_reference)

    def _refund_escrow_with_order(self, escrow: Escrow, provider_reference: str) -> EscrowTransitionResult:
        """Helper to get order and call domain service."""
        order = self.order_repo.get_by_id(escrow.order_id)
        if not order or not order.merchant_id:
            raise ValueError("Order or merchant not found")
        return self.domain_service.refund_escrow(escrow, order.merchant_id, provider_reference)

    def _execute_transition(self, escrow_id: str, domain_transition_func, ledger_event_type: LedgerEventType, description: str) -> Escrow:
        """
        Execute a state transition with accounting entries atomically.
        """
        # Load escrow
        escrow = self.escrow_repo.get_by_id(escrow_id)
        if not escrow:
            raise ValueError(f"Escrow {escrow_id} not found")

        # Execute domain transition (validation + accounting instructions)
        result: EscrowTransitionResult = domain_transition_func(escrow)

        # Update escrow state
        escrow.state = result.new_state
        # Timestamps will be handled by the database triggers or entity save logic

        self.escrow_repo.save(escrow)

        # Create accounting entries
        self._create_accounting_entries(escrow, result.accounting_instructions, ledger_event_type, description)

        # Commit all changes atomically
        self.session.commit()

        return escrow

    def _create_accounting_entries(self, escrow: Escrow, instructions: list[AccountingInstruction], event_type: LedgerEventType, description: str):
        """
        Create balanced accounting entries from domain instructions.
        """
        # Create journal lines directly from accounting instructions
        lines = []
        for instruction in instructions:
            account_id = self._get_or_create_account_from_instruction(instruction)
            if instruction.debit > 0:
                lines.append({
                    "account_id": str(account_id),
                    "debit_amount": str(instruction.debit),
                    "credit_amount": "0"
                })
            elif instruction.credit > 0:
                lines.append({
                    "account_id": str(account_id),
                    "debit_amount": "0",
                    "credit_amount": str(instruction.credit)
                })

        if lines:
            journal_request = PostJournalEntryRequest(
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow.id,
                description=description,
                lines=lines
            )
            self.post_journal_uc.execute(journal_request)

        # Also create ledger events for backward compatibility and audit trail
        for instruction in instructions:
            if instruction.debit > 0:
                direction = Direction.DEBIT
                amount = instruction.debit
            elif instruction.credit > 0:
                direction = Direction.CREDIT
                amount = instruction.credit
            else:
                continue

            ledger_event = LedgerEvent(
                aggregate_type=AggregateType.ESCROW,
                aggregate_id=escrow.id,
                event_type=event_type,
                amount=amount,
                direction=direction,
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow.id,
                currency="ETB",
                event_metadata={"account_owner": instruction.account_owner}
            )
            self.ledger_repo.append(ledger_event)

    def _get_or_create_account_from_instruction(self, instruction: AccountingInstruction):
        """Get or create account from accounting instruction."""
        from app.domain.accounting.entities import OwnerType, AccountType
        from app.application.accounting.create_account import CreateAccount, CreateAccountRequest

        # Parse account_owner string: "USER_{user_id}_LIABILITY_Farmer_Payable"
        parts = instruction.account_owner.split('_', 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid account_owner format: {instruction.account_owner}")

        owner_type_str = parts[0]
        owner_id = parts[1]
        account_type_and_name = parts[2]

        # Parse account type and name: "LIABILITY_Farmer_Payable"
        type_parts = account_type_and_name.split('_', 1)
        if len(type_parts) < 2:
            raise ValueError(f"Invalid account type format: {account_type_and_name}")

        account_type_str = type_parts[0]
        account_name = type_parts[1].replace('_', ' ')

        owner_type = OwnerType(owner_type_str)
        account_type = AccountType(account_type_str)

        create_account_uc = CreateAccount(self.account_repo)
        request = CreateAccountRequest(owner_type, owner_id, account_type, account_name, "ETB")
        account = create_account_uc.execute(request)
        return account.id