"""
Tests for the atomic order creation transaction flow.

Tests ensure that pricing → order → escrow → accounting happens atomically,
and that failures cause complete rollback.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.application.services.order_service import (
    OrderApplicationService,
    OrderCreationRequest,
    OrderCreationResult
)
from app.infrastructure.repositories.order_repo import OrderRepository
from app.infrastructure.repositories.payment_repo import EscrowRepository
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository


class TestOrderTransactionFlow:
    """Test the complete order creation transaction flow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session = Mock(spec=Session)
        self.order_repo = Mock(spec=OrderRepository)
        self.escrow_repo = Mock(spec=EscrowRepository)
        self.ledger_repo = Mock(spec=LedgerRepository)
        self.account_repo = Mock(spec=AccountRepository)
        self.journal_repo = Mock(spec=JournalRepository)

        # Create service with mocked repos
        self.service = OrderApplicationService(self.session)
        self.service.order_repo = self.order_repo
        self.service.escrow_repo = self.escrow_repo
        self.service.ledger_repo = self.ledger_repo
        self.service.account_repo = self.account_repo
        self.service.journal_repo = self.journal_repo

    def test_successful_full_transaction_flow(self):
        """Test successful creation of order, escrow, and accounting entries."""
        # Arrange
        request = OrderCreationRequest(
            farmer_id="farmer-123",
            merchant_id="merchant-456",
            product_id="product-789",
            unit_price=Decimal("10.00"),
            quantity=2,
            distance_km=5.0,
            product_type="vegetables"
        )

        # Mock saved entities
        mock_order = Mock()
        mock_order.id = "order-123"
        mock_order.total_price = Decimal("51.00")

        mock_escrow = Mock()
        mock_escrow.id = "escrow-456"

        self.order_repo.save.return_value = mock_order
        self.escrow_repo.save.return_value = mock_escrow
        self.order_repo.update.return_value = mock_order

        # Mock context manager for transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        with patch.object(self.service, '_create_accounting_entries'):
            result = self.service.create_order_with_pricing_and_escrow(request)

        # Assert
        assert isinstance(result, OrderCreationResult)
        assert result.order_id == "order-123"
        assert result.escrow_id == "escrow-456"
        assert result.total_price == Decimal("51.00")

        # Verify order was saved with correct pricing
        self.order_repo.save.assert_called_once()
        saved_order = self.order_repo.save.call_args[0][0]
        assert saved_order.total_price == Decimal("51.00")  # 20 + 1 + 30
        assert saved_order.platform_fee == Decimal("1.00")  # 5% of 20
        assert saved_order.delivery_cost == Decimal("30.00")  # 20 + (5*2)

        # Verify escrow was created with matching amount
        self.escrow_repo.save.assert_called_once()
        saved_escrow = self.escrow_repo.save.call_args[0][0]
        assert saved_escrow.amount == Decimal("51.00")

        # Verify order was updated with escrow_id
        self.order_repo.update.assert_called_once_with("order-123", {"escrow_id": "escrow-456"})

    def test_transaction_rollback_on_escrow_failure(self):
        """Test that transaction rolls back if escrow creation fails."""
        request = OrderCreationRequest(
            farmer_id="farmer-123",
            merchant_id="merchant-456",
            product_id="product-789",
            unit_price=Decimal("10.00"),
            quantity=2,
            distance_km=5.0
        )

        # Mock order save success
        mock_order = Mock()
        mock_order.id = "order-123"
        self.order_repo.save.return_value = mock_order

        # Mock escrow save failure
        self.escrow_repo.save.side_effect = Exception("Escrow creation failed")

        # Mock transaction context
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(Exception, match="Escrow creation failed"):
            self.service.create_order_with_pricing_and_escrow(request)

        # Verify transaction rollback occurred
        self.session.begin.return_value.__exit__.assert_called_once()

    def test_transaction_rollback_on_accounting_failure(self):
        """Test that transaction rolls back if accounting entries creation fails."""
        request = OrderCreationRequest(
            farmer_id="farmer-123",
            merchant_id="merchant-456",
            product_id="product-789",
            unit_price=Decimal("10.00"),
            quantity=2,
            distance_km=5.0
        )

        # Mock successful saves
        mock_order = Mock()
        mock_order.id = "order-123"
        self.order_repo.save.return_value = mock_order

        mock_escrow = Mock()
        mock_escrow.id = "escrow-456"
        self.escrow_repo.save.return_value = mock_escrow

        # Mock transaction context
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Mock accounting failure
        with patch.object(self.service, '_create_accounting_entries', side_effect=Exception("Accounting failed")):
            with pytest.raises(Exception, match="Accounting failed"):
                self.service.create_order_with_pricing_and_escrow(request)

        # Verify transaction rollback occurred
        self.session.begin.return_value.__exit__.assert_called_once()

    def test_business_invariant_maintained(self):
        """Test that pricing total equals order total equals escrow amount."""
        request = OrderCreationRequest(
            farmer_id="farmer-123",
            merchant_id="merchant-456",
            product_id="product-789",
            unit_price=Decimal("15.50"),
            quantity=1,
            distance_km=0.0
        )

        # Mock saved entities
        mock_order = Mock()
        mock_order.id = "order-123"
        mock_order.total_price = Decimal("36.28")

        mock_escrow = Mock()
        mock_escrow.id = "escrow-456"

        self.order_repo.save.return_value = mock_order
        self.escrow_repo.save.return_value = mock_escrow

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        with patch.object(self.service, '_create_accounting_entries'):
            result = self.service.create_order_with_pricing_and_escrow(request)

        # Assert business invariant
        # pricing: 15.50 + 0.78 + 20.00 = 36.28
        assert result.total_price == Decimal("36.28")

        # Verify escrow amount matches
        self.escrow_repo.save.assert_called_once()
        saved_escrow = self.escrow_repo.save.call_args[0][0]
        assert saved_escrow.amount == result.total_price

    def test_accounting_entries_created_correctly(self):
        """Test that balanced accounting entries are created."""
        request = OrderCreationRequest(
            farmer_id="farmer-123",
            merchant_id="merchant-456",
            product_id="product-789",
            unit_price=Decimal("10.00"),
            quantity=1,
            distance_km=0.0
        )

        # Mock entities
        mock_order = Mock()
        mock_order.id = "order-123"
        mock_order.merchant_id = "merchant-456"
        mock_order.total_price = Decimal("31.00")  # 10 + 0.5 + 20.5

        mock_escrow = Mock()
        mock_escrow.id = "escrow-456"

        self.order_repo.save.return_value = mock_order
        self.escrow_repo.save.return_value = mock_escrow

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        result = self.service.create_order_with_pricing_and_escrow(request)

        # Assert accounting entries were created
        # Should create 6 ledger events (3 pairs of debit/credit)
        assert self.ledger_repo.append.call_count == 6

        # Should create 6 journal entries (one for each ledger event)
        assert self.service.post_journal_uc.execute.call_count == 6