"""
Domain-level tests for escrow state machine.

Tests state transition validation and accounting instructions.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock

from app.domain.payments.services.escrow_service import (
    EscrowDomainService,
    AccountingInstruction
)
from app.domain.payments.entities import Escrow, EscrowState
from app.domain.payments.exceptions import InvalidEscrowTransitionError
from shared_models.enums import EscrowState as SharedEscrowState


class TestEscrowDomainService:
    """Test domain service state transitions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EscrowDomainService()

        # Mock escrow
        self.escrow = Mock(spec=Escrow)
        self.escrow.id = "escrow-123"
        self.escrow.amount = Decimal("100.00")

        # Mock order for farmer/merchant IDs
        self.escrow.order = Mock()
        self.escrow.order.farmer_id = "farmer-456"
        self.escrow.order.merchant_id = "merchant-789"

    def test_fund_escrow_valid_transition(self):
        """Test successful funding transition."""
        self.escrow.state = EscrowState.CREATED

        result = self.service.fund_escrow(self.escrow, "REF-123")

        assert result.new_state == EscrowState.FUNDED
        assert len(result.accounting_instructions) == 2

        # Check accounting instructions
        instructions = result.accounting_instructions
        assert instructions[0].account_type == "ASSET"
        assert instructions[0].account_owner == "USER_merchant-789_ASSET_Merchant_Cash"
        assert instructions[0].debit == Decimal("100.00")

        assert instructions[1].account_type == "LIABILITY"
        assert instructions[1].account_owner == "ESCROW_escrow-123_LIABILITY_Escrow_Holding"
        assert instructions[1].credit == Decimal("100.00")

    def test_fund_escrow_invalid_state(self):
        """Test funding escrow that's already funded."""
        self.escrow.state = EscrowState.FUNDED

        with pytest.raises(InvalidEscrowTransitionError, match="Cannot fund escrow in state FUNDED"):
            self.service.fund_escrow(self.escrow, "REF-123")

    def test_release_escrow_valid_transition(self):
        """Test successful release transition."""
        self.escrow.state = EscrowState.FUNDED

        result = self.service.release_escrow(self.escrow, "REF-123")

        assert result.new_state == EscrowState.RELEASED
        assert len(result.accounting_instructions) == 2

        # Check accounting instructions
        instructions = result.accounting_instructions
        assert instructions[0].account_type == "LIABILITY"
        assert instructions[0].account_owner == "ESCROW_escrow-123_LIABILITY_Escrow_Holding"
        assert instructions[0].debit == Decimal("100.00")

        assert instructions[1].account_type == "LIABILITY"
        assert instructions[1].account_owner == "USER_farmer-456_LIABILITY_Farmer_Payable"
        assert instructions[1].credit == Decimal("100.00")

    def test_release_escrow_invalid_state(self):
        """Test releasing escrow that's not funded."""
        self.escrow.state = EscrowState.CREATED

        with pytest.raises(InvalidEscrowTransitionError, match="Cannot release escrow in state CREATED"):
            self.service.release_escrow(self.escrow, "REF-123")

    def test_refund_escrow_valid_transition(self):
        """Test successful refund transition."""
        self.escrow.state = EscrowState.FUNDED

        result = self.service.refund_escrow(self.escrow, "REF-123")

        assert result.new_state == EscrowState.REFUNDED
        assert len(result.accounting_instructions) == 2

        # Check accounting instructions
        instructions = result.accounting_instructions
        assert instructions[0].account_type == "LIABILITY"
        assert instructions[0].account_owner == "ESCROW_escrow-123_LIABILITY_Escrow_Holding"
        assert instructions[0].debit == Decimal("100.00")

        assert instructions[1].account_type == "LIABILITY"
        assert instructions[1].account_owner == "USER_merchant-789_LIABILITY_Customer_Refund"
        assert instructions[1].credit == Decimal("100.00")

    def test_refund_escrow_invalid_state(self):
        """Test refunding escrow that's not funded."""
        self.escrow.state = EscrowState.CREATED

        with pytest.raises(InvalidEscrowTransitionError, match="Cannot refund escrow in state CREATED"):
            self.service.refund_escrow(self.escrow, "REF-123")

    def test_penalize_escrow_valid_transition(self):
        """Test successful penalize transition."""
        self.escrow.state = EscrowState.FUNDED

        result = self.service.penalize_escrow(self.escrow, "REF-123")

        assert result.new_state == EscrowState.PENALIZED
        assert len(result.accounting_instructions) == 2

        # Check accounting instructions
        instructions = result.accounting_instructions
        assert instructions[0].account_type == "LIABILITY"
        assert instructions[0].account_owner == "ESCROW_escrow-123_LIABILITY_Escrow_Holding"
        assert instructions[0].debit == Decimal("100.00")

        assert instructions[1].account_type == "REVENUE"
        assert instructions[1].account_owner == "SYSTEM_platform_REVENUE_Platform_Revenue"
        assert instructions[1].credit == Decimal("100.00")

    def test_penalize_escrow_invalid_state(self):
        """Test penalizing escrow that's not funded."""
        self.escrow.state = EscrowState.CREATED

        with pytest.raises(InvalidEscrowTransitionError, match="Cannot penalize escrow in state CREATED"):
            self.service.penalize_escrow(self.escrow, "REF-123")

    def test_all_instructions_balance(self):
        """Test that all accounting instructions balance (debits = credits)."""
        self.escrow.state = EscrowState.FUNDED

        transitions = [
            self.service.release_escrow,
            self.service.refund_escrow,
            self.service.penalize_escrow
        ]

        for transition_func in transitions:
            result = transition_func(self.escrow, "REF-123")

            total_debits = sum(inst.debit for inst in result.accounting_instructions)
            total_credits = sum(inst.credit for inst in result.accounting_instructions)

            assert total_debits == total_credits == self.escrow.amount