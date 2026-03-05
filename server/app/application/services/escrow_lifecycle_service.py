"""
Application service for escrow lifecycle management.

Handles state transitions with accounting entries in atomic transactions.
Integrates with inventory service for stock management.
"""

from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
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
from app.application.services.inventory_service import InventoryService


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
        self.inventory_service = InventoryService(session)

    def fund_escrow(self, escrow_id: str, provider_reference: str, auto_confirm: bool = True) -> Escrow:
        """
        Fund an escrow - CREATED → FUNDED

        Creates accounting entries for customer payment obligation.
        
        Args:
            escrow_id: The escrow ID to fund
            provider_reference: Reference from the payment provider
            auto_confirm: If True (default), automatically confirm the order after funding.
                         Set to False to require manual farmer confirmation.
        """
        return self._execute_transition(
            escrow_id,
            lambda escrow: self._fund_escrow_with_order(escrow, provider_reference, auto_confirm),
            LedgerEventType.ESCROW_FUNDED,
            f"Escrow funded with reference {provider_reference}"
        )

    def _fund_escrow_with_order(self, escrow: Escrow, provider_reference: str, auto_confirm: bool = True) -> EscrowTransitionResult:
        """Helper to get order and call domain service."""
        order = self.order_repo.get_by_id(escrow.order_id)
        if not order or not order.merchant_id:
            raise ValueError("Order or merchant not found")
        
        result = self.domain_service.fund_escrow(escrow, order.merchant_id, provider_reference)
        
        # Apply side effects
        escrow.funded_at = datetime.now(timezone.utc)
        escrow.provider_reference = provider_reference
        
        # CRITICAL: Confirm sale - move reserved → sold
        # This is called after escrow is funded (payment received)
        try:
            self.inventory_service.confirm_sale(
                product_id=order.product_id,
                order_id=order.id,
                qty=order.quantity
            )
        except Exception as e:
            # Log but don't fail - inventory can be reconciled manually
            print(f"Warning: Failed to confirm sale in inventory: {e}")
        
        # Update order status based on auto_confirm flag
        from app.domain.common.enums import OrderStatus
        from app.domain.orders.state_machine import OrderStateMachine
        
        if auto_confirm:
            # Auto-confirm: FUNDED → CONFIRMED
            try:
                order.status = OrderStateMachine.transition(order.status, OrderStatus.CONFIRMED)
            except Exception:
                # If transition fails (e.g., already confirmed), just set to FUNDED
                order.status = OrderStatus.FUNDED
        else:
            # Manual confirmation required: just set to FUNDED
            order.status = OrderStatus.FUNDED
            
        order.updated_at = datetime.now(timezone.utc)
        self.order_repo.save(order)
        
        return result

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

    def _release_escrow_with_order(self, escrow: Escrow, provider_reference: str) -> EscrowTransitionResult:
        """Helper to get order and call domain service."""
        order = self.order_repo.get_by_id(escrow.order_id)
        if not order or not order.farmer_id:
            raise ValueError("Order or farmer not found")
            
        result = self.domain_service.release_escrow(escrow, order.farmer_id, provider_reference)
        
        # Apply side effects
        escrow.released_at = datetime.now(timezone.utc)
        escrow.provider_reference = provider_reference
        
        return result

    def _refund_escrow_with_order(self, escrow: Escrow, provider_reference: str) -> EscrowTransitionResult:
        """Helper to get order and call domain service."""
        order = self.order_repo.get_by_id(escrow.order_id)
        if not order or not order.merchant_id:
            raise ValueError("Order or merchant not found")
            
        result = self.domain_service.refund_escrow(escrow, order.merchant_id, provider_reference)
        
        # Apply side effects
        escrow.provider_reference = provider_reference
        
        # CRITICAL: Release reservation - return stock to available
        # This is called when escrow is refunded (order cancelled after payment)
        try:
            self.inventory_service.release_reservation(
                product_id=order.product_id,
                order_id=order.id,
                qty=order.quantity,
                reason="escrow_refunded"
            )
        except Exception as e:
            print(f"Warning: Failed to release reservation in inventory: {e}")
        
        # Also update order status to CANCELLED
        from app.domain.common.enums import OrderStatus
        order.status = OrderStatus.CANCELLED
        order.cancelled_reason = "Refund processed"
        order.cancelled_at = datetime.now(timezone.utc)
        order.updated_at = datetime.now(timezone.utc)
        self.order_repo.save(order)
        
        return result

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

            # Parse account_owner to determine aggregate
            # Format: OWNERTYPE_OWNERID_ACCOUNTTYPE_ACCOUNTNAME
            # Example: USER_MER-00001_ASSET_Merchant_Cash
            parts = instruction.account_owner.split('_', 2)
            if len(parts) >= 2:
                owner_type_str = parts[0]
                owner_id = parts[1]
                # Map OwnerType to AggregateType
                try:
                    aggregate_type = AggregateType(owner_type_str)
                    aggregate_id = owner_id
                except ValueError:
                    # Fallback if mapping fails
                    aggregate_type = AggregateType.ESCROW
                    aggregate_id = escrow.id
            else:
                aggregate_type = AggregateType.ESCROW
                aggregate_id = escrow.id

            ledger_event = LedgerEvent(
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
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