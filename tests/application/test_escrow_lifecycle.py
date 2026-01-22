"""
Application-level tests for escrow lifecycle service.

Tests atomic transactions, state persistence, and accounting creation.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.application.services.escrow_lifecycle_service import EscrowLifecycleService
from app.domain.payments.entities import Escrow, EscrowState
from app.domain.payments.exceptions import InvalidEscrowTransitionError


class TestEscrowLifecycleService:
    """Test application service for escrow lifecycle management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session = Mock(spec=Session)
        self.lifecycle_service = EscrowLifecycleService(self.session)

        # Mock repositories
        self.lifecycle_service.escrow_repo = Mock()
        self.lifecycle_service.ledger_repo = Mock()
        self.lifecycle_service.account_repo = Mock()
        self.lifecycle_service.journal_repo = Mock()

        # Mock domain service
        with patch.object(self.lifecycle_service, 'domain_service') as mock_domain:
            mock_domain.fund_escrow.return_value = Mock(
                new_state=EscrowState.FUNDED,
                accounting_instructions=[]
            )
            mock_domain.release_escrow.return_value = Mock(
                new_state=EscrowState.RELEASED,
                accounting_instructions=[]
            )
            mock_domain.refund_escrow.return_value = Mock(
                new_state=EscrowState.REFUNDED,
                accounting_instructions=[]
            )
            mock_domain.penalize_escrow.return_value = Mock(
                new_state=EscrowState.PENALIZED,
                accounting_instructions=[]
            )

    def test_fund_escrow_successful(self):
        """Test successful escrow funding."""
        # Mock escrow
        escrow = Mock(spec=Escrow)
        escrow.id = "escrow-123"
        escrow.state = EscrowState.CREATED

        self.lifecycle_service.escrow_repo.get_by_id.return_value = escrow

        # Mock transaction context
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        result = self.lifecycle_service.fund_escrow("escrow-123", "REF-123")

        # Assert
        assert result == escrow
        assert result.state == EscrowState.FUNDED

        # Verify domain service called
        self.lifecycle_service.domain_service.fund_escrow.assert_called_once_with(escrow, "REF-123")

        # Verify persistence
        self.lifecycle_service.escrow_repo.save.assert_called_once()

    def test_release_escrow_successful(self):
        """Test successful escrow release."""
        # Mock escrow
        escrow = Mock(spec=Escrow)
        escrow.id = "escrow-123"
        escrow.state = EscrowState.FUNDED

        self.lifecycle_service.escrow_repo.get_by_id.return_value = escrow

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        result = self.lifecycle_service.release_escrow("escrow-123", "REF-123")

        # Assert
        assert result == escrow
        assert result.state == EscrowState.RELEASED

        # Verify domain service called
        self.lifecycle_service.domain_service.release_escrow.assert_called_once_with(escrow, "REF-123")

    def test_refund_escrow_successful(self):
        """Test successful escrow refund."""
        # Mock escrow
        escrow = Mock(spec=Escrow)
        escrow.id = "escrow-123"
        escrow.state = EscrowState.FUNDED

        self.lifecycle_service.escrow_repo.get_by_id.return_value = escrow

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        result = self.lifecycle_service.refund_escrow("escrow-123", "REF-123")

        # Assert
        assert result == escrow
        assert result.state == EscrowState.REFUNDED

        # Verify domain service called
        self.lifecycle_service.domain_service.refund_escrow.assert_called_once_with(escrow, "REF-123")

    def test_penalize_escrow_successful(self):
        """Test successful escrow penalization."""
        # Mock escrow
        escrow = Mock(spec=Escrow)
        escrow.id = "escrow-123"
        escrow.state = EscrowState.FUNDED

        self.lifecycle_service.escrow_repo.get_by_id.return_value = escrow

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        result = self.lifecycle_service.penalize_escrow("escrow-123", "REF-123")

        # Assert
        assert result == escrow
        assert result.state == EscrowState.PENALIZED

        # Verify domain service called
        self.lifecycle_service.domain_service.penalize_escrow.assert_called_once_with(escrow, "REF-123")

    def test_invalid_transition_raises_error(self):
        """Test that invalid transitions raise domain errors."""
        # Mock escrow in wrong state
        escrow = Mock(spec=Escrow)
        escrow.id = "escrow-123"
        escrow.state = EscrowState.CREATED

        self.lifecycle_service.escrow_repo.get_by_id.return_value = escrow

        # Mock domain service to raise error
        self.lifecycle_service.domain_service.release_escrow.side_effect = InvalidEscrowTransitionError(
            "Cannot release escrow in state CREATED"
        )

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(InvalidEscrowTransitionError, match="Cannot release escrow in state CREATED"):
            self.lifecycle_service.release_escrow("escrow-123", "REF-123")

        # Verify transaction rollback
        self.session.begin.return_value.__exit__.assert_called_once()

    def test_escrow_not_found_raises_error(self):
        """Test that missing escrow raises error."""
        self.lifecycle_service.escrow_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Escrow escrow-123 not found"):
            self.lifecycle_service.fund_escrow("escrow-123", "REF-123")

    def test_transaction_rollback_on_failure(self):
        """Test that any failure causes transaction rollback."""
        # Mock escrow
        escrow = Mock(spec=Escrow)
        escrow.id = "escrow-123"
        escrow.state = EscrowState.FUNDED

        self.lifecycle_service.escrow_repo.get_by_id.return_value = escrow

        # Mock domain service success
        self.lifecycle_service.domain_service.release_escrow.return_value = Mock(
            new_state=EscrowState.RELEASED,
            accounting_instructions=[]
        )

        # Mock save failure
        self.lifecycle_service.escrow_repo.save.side_effect = Exception("DB Error")

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(Exception, match="DB Error"):
            self.lifecycle_service.release_escrow("escrow-123", "REF-123")

        # Verify transaction rollback
        self.session.begin.return_value.__exit__.assert_called_once()

    def test_accounting_entries_created(self):
        """Test that accounting entries are created for transitions."""
        # Mock escrow
        escrow = Mock(spec=Escrow)
        escrow.id = "escrow-123"
        escrow.state = EscrowState.FUNDED

        self.lifecycle_service.escrow_repo.get_by_id.return_value = escrow

        # Mock domain service with accounting instructions
        from app.domain.payments.services.escrow_service import AccountingInstruction
        instructions = [
            AccountingInstruction("ASSET", "account1", debit=Decimal("100")),
            AccountingInstruction("LIABILITY", "account2", credit=Decimal("100"))
        ]

        self.lifecycle_service.domain_service.release_escrow.return_value = Mock(
            new_state=EscrowState.RELEASED,
            accounting_instructions=instructions
        )

        # Mock transaction
        self.session.begin.return_value.__enter__ = Mock(return_value=None)
        self.session.begin.return_value.__exit__ = Mock(return_value=None)

        # Act
        self.lifecycle_service.release_escrow("escrow-123", "REF-123")

        # Assert accounting entries created
        assert self.lifecycle_service.ledger_repo.append.call_count == 2  # 2 ledger events
        assert self.lifecycle_service.post_journal_uc.execute.call_count == 2  # 2 journal entries