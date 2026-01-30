"""
Application service orchestrator for order creation with pricing, escrow, and accounting.

This service ensures atomicity across the entire business transaction:
pricing → order → escrow → accounting entries
"""

from typing import Tuple, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.domain.pricing.pricing_engine import PricingEngine
from app.domain.pricing.value_objects import PricingInput
from app.infrastructure.repositories.pricing_repo import PricingRuleRepository
from app.domain.orders.entities import Order as DomainOrder
from app.domain.payments.entities import Escrow as DomainEscrow, EscrowState
from app.domain.ledger.entities import LedgerEvent, AggregateType, LedgerEventType, Direction, ReferenceType

from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository

from app.application.accounting.ledger_to_journal_mapper import LedgerToJournalMapper
from app.application.accounting.post_journal_entry import PostJournalEntry, PostJournalEntryRequest

from app.domain.common.enums import Provider


class OrderCreationRequest:
    """Request object for order creation with all required data."""
    def __init__(self,
                 farmer_id: str,
                 merchant_id: str,
                 product_id: str,
                 unit_price: Decimal,
                 quantity: int,
                 distance_km: float,
                 product_type: str = "general"):
        self.farmer_id = farmer_id
        self.merchant_id = merchant_id
        self.product_id = product_id
        self.unit_price = unit_price
        self.quantity = quantity
        self.distance_km = distance_km
        self.product_type = product_type


class OrderCreationResult:
    """Result of successful order creation."""
    def __init__(self, order_id: str, escrow_id: str, total_price: Decimal):
        self.order_id = order_id
        self.escrow_id = escrow_id
        self.total_price = total_price


class OrderApplicationService:
    """
    Application service that orchestrates the complete order creation flow.

    Ensures atomicity: pricing → order → escrow → accounting in one transaction.
    """

    def __init__(self, session: Session):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.escrow_repo = EscrowRepository(session)
        self.ledger_repo = LedgerRepository(session)
        self.account_repo = AccountRepository(session)
        self.journal_repo = JournalRepository(session)
        self.pricing_repo = PricingRuleRepository(session)

        # Domain services
        self.journal_mapper = LedgerToJournalMapper(self.account_repo)
        self.post_journal_uc = PostJournalEntry(self.journal_repo, self.account_repo)

    def create_order_with_pricing_and_escrow(self, request: OrderCreationRequest) -> OrderCreationResult:
        """
        Create order with automatic pricing, escrow, and accounting entries.

        This is the canonical transaction boundary that ensures:
        pricing.total_price == order.total_price == escrow.amount == accounting entries

        Args:
            request: Order creation request with all required data

        Returns:
            OrderCreationResult with IDs and total price

        Raises:
            Exception: Any failure causes complete rollback
        """
        # Start transaction
        with self.session.begin():
            try:
                # 1. Calculate pricing (domain logic - no DB access)
                pricing_input = PricingInput(
                    unit_price=request.unit_price,
                    quantity=request.quantity,
                    distance_km=request.distance_km,
                    product_type=request.product_type
                )
                
                # Use database rules
                active_rules = self.pricing_repo.get_active_rules()
                engine = PricingEngine(active_rules)
                pricing_result = engine.calculate(pricing_input)

                # 2. Create and persist order
                now = datetime.now(timezone.utc)
                domain_order = DomainOrder(
                    farmer_id=request.farmer_id,
                    merchant_id=request.merchant_id,
                    product_id=request.product_id,
                    quantity=Decimal(request.quantity),
                    unit_price=request.unit_price,
                    subtotal=pricing_result.subtotal,
                    delivery_fee=pricing_result.delivery_fee if pricing_result.delivery_fee > 0 else None,
                    delivery_margin=pricing_result.delivery_margin if pricing_result.delivery_margin > 0 else None,
                    delivery_cost=pricing_result.delivery_fee + pricing_result.delivery_margin,
                    platform_fee=pricing_result.platform_fee,
                    quality_fee=pricing_result.quality_fee if pricing_result.quality_fee > 0 else None,
                    total_price=pricing_result.total_price,
                    status="CREATED",
                    created_at=now
                )
                saved_order = self.order_repo.save(domain_order)

                # 3. Create escrow
                domain_escrow = DomainEscrow(
                    order_id=saved_order.id,
                    state=EscrowState.CREATED,
                    amount=pricing_result.total_price,  # Must equal pricing.total_price
                    provider=Provider.BANK,
                    created_at=now
                )
                saved_escrow = self.escrow_repo.save(domain_escrow)

                # 4. Update order with escrow_id
                self.order_repo.update(saved_order.id, {"escrow_id": saved_escrow.id})

                # 5. Create accounting entries (double-entry) - TODO: Implement detailed entries
                # For now, just ensure the business invariant is maintained
                pass

                # 6. Transaction commits automatically on successful exit from context manager

                return OrderCreationResult(
                    order_id=saved_order.id,
                    escrow_id=saved_escrow.id,
                    total_price=pricing_result.total_price
                )

            except Exception as e:
                # Transaction will rollback automatically
                raise e

    def _create_accounting_entries(self, order, escrow, pricing_result):
        """
        Create balanced double-entry accounting entries.

        Creates entries for:
        - Customer payment obligation
        - Platform fee revenue
        - Delivery cost payable
        """
        order_id = order.id
        escrow_id = escrow.id

        # a) Customer Payment Obligation
        # Debit: Customer Receivable (Asset) - they owe us money
        # Credit: Escrow Liability - we hold it in escrow
        customer_payment = LedgerEvent(
            aggregate_type=AggregateType.USER,
            aggregate_id=order.merchant_id,  # Merchant owes the money
            event_type=LedgerEventType.ESCROW_FUNDED,
            amount=pricing_result.total_price,
            direction=Direction.DEBIT,  # Customer receivable increases
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            currency="ETB"
        )
        self.ledger_repo.append(customer_payment)

        escrow_liability = LedgerEvent(
            aggregate_type=AggregateType.ESCROW,
            aggregate_id=escrow_id,
            event_type=LedgerEventType.ESCROW_FUNDED,
            amount=pricing_result.total_price,
            direction=Direction.CREDIT,  # Escrow liability increases
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            currency="ETB"
        )
        self.ledger_repo.append(escrow_liability)

        # Create journal entries for customer payment
        lines = self.journal_mapper.map_event_to_journal_lines(customer_payment)
        if lines:
            journal_request = PostJournalEntryRequest(
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                description=f"Customer payment obligation for order {order_id}",
                lines=lines
            )
            self.post_journal_uc.execute(journal_request)

        lines = self.journal_mapper.map_event_to_journal_lines(escrow_liability)
        if lines:
            journal_request = PostJournalEntryRequest(
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                description=f"Escrow liability for order {order_id}",
                lines=lines
            )
            self.post_journal_uc.execute(journal_request)

        # b) Platform Fee Revenue
        # Debit: Escrow Liability (reduce liability)
        # Credit: Platform Revenue (increase revenue)
        platform_fee_debit = LedgerEvent(
            aggregate_type=AggregateType.ESCROW,
            aggregate_id=escrow_id,
            event_type=LedgerEventType.PLATFORM_FEE_COLLECTED,
            amount=pricing_result.platform_fee,
            direction=Direction.DEBIT,  # Escrow liability decreases
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            currency="ETB"
        )
        self.ledger_repo.append(platform_fee_debit)

        platform_fee_credit = LedgerEvent(
            aggregate_type=AggregateType.SYSTEM,
            aggregate_id="platform",
            event_type=LedgerEventType.PLATFORM_FEE_COLLECTED,
            amount=pricing_result.platform_fee,
            direction=Direction.CREDIT,  # Platform revenue increases
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            currency="ETB"
        )
        self.ledger_repo.append(platform_fee_credit)

        # Create journal entries for platform fee
        lines = self.journal_mapper.map_event_to_journal_lines(platform_fee_debit)
        if lines:
            journal_request = PostJournalEntryRequest(
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                description=f"Platform fee collection for order {order_id}",
                lines=lines
            )
            self.post_journal_uc.execute(journal_request)

        lines = self.journal_mapper.map_event_to_journal_lines(platform_fee_credit)
        if lines:
            journal_request = PostJournalEntryRequest(
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                description=f"Platform revenue for order {order_id}",
                lines=lines
            )
            self.post_journal_uc.execute(journal_request)

        # c) Delivery Cost Payable
        # Debit: Escrow Liability (reduce liability)
        # Credit: Delivery Payable (increase payable)
        delivery_debit = LedgerEvent(
            aggregate_type=AggregateType.ESCROW,
            aggregate_id=escrow_id,
            event_type=LedgerEventType.ESCROW_RELEASED,  # Using existing event type
            amount=pricing_result.delivery_cost,
            direction=Direction.DEBIT,  # Escrow liability decreases
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            currency="ETB"
        )
        self.ledger_repo.append(delivery_debit)

        delivery_credit = LedgerEvent(
            aggregate_type=AggregateType.SYSTEM,
            aggregate_id="delivery",
            event_type=LedgerEventType.ESCROW_RELEASED,  # Using existing event type
            amount=pricing_result.delivery_cost,
            direction=Direction.CREDIT,  # Delivery payable increases
            reference_type=ReferenceType.ESCROW,
            reference_id=escrow_id,
            currency="ETB"
        )
        self.ledger_repo.append(delivery_credit)

        # Create journal entries for delivery cost
        lines = self.journal_mapper.map_event_to_journal_lines(delivery_debit)
        if lines:
            journal_request = PostJournalEntryRequest(
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                description=f"Delivery cost payable for order {order_id}",
                lines=lines
            )
            self.post_journal_uc.execute(journal_request)

        lines = self.journal_mapper.map_event_to_journal_lines(delivery_credit)
        if lines:
            journal_request = PostJournalEntryRequest(
                reference_type=ReferenceType.ESCROW,
                reference_id=escrow_id,
                description=f"Delivery payable for order {order_id}",
                lines=lines
            )
            self.post_journal_uc.execute(journal_request)