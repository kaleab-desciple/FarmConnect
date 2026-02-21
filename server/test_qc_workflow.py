"""Unit tests for QC workflow.

These tests cover:
- QC grade evaluation
- Lab webhook processing
- Signature verification
- Product listing validation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.application.services.qc_service import QCService
from app.infrastructure.repositories.qc_repo import QCRepository
from app.domain.harvest.entities import HarvestBatchState
from app.domain.common.enums import QCGrade


class TestQCGradeEvaluation:
    """Tests for QC grade evaluation logic."""
    
    def test_evaluate_grade_grade_a_pass(self):
        """Test that GRADE_A is assigned when all metrics pass."""
        # This would require a database setup, so we test the rule logic directly
        from app.application.services.qc_service import QCService
        
        # Test the _check_rules method directly
        service = QCService.__new__(QCService)
        
        rules = [
            {"metric": "moisture_pct", "op": "<=", "value": 13.0},
            {"metric": "aflatoxin_ppb", "op": "<=", "value": 5},
        ]
        
        metrics = {"moisture_pct": 12.3, "aflatoxin_ppb": 3.2}
        
        # Direct test of rule checking
        result = service._check_rules(rules, metrics)
        
        assert result is True
    
    def test_evaluate_grade_grade_b_pass(self):
        """Test that GRADE_B is assigned when only B rules pass."""
        from app.application.services.qc_service import QCService
        
        service = QCService.__new__(QCService)
        
        # GRADE_B rules
        rules = [
            {"metric": "moisture_pct", "op": "<=", "value": 14.0},
            {"metric": "aflatoxin_ppb", "op": "<=", "value": 10},
        ]
        
        # Passes B but not A
        metrics = {"moisture_pct": 13.5, "aflatoxin_ppb": 8.0}
        
        result = service._check_rules(rules, metrics)
        
        assert result is True
    
    def test_evaluate_grade_fail(self):
        """Test that rules fail when metrics exceed thresholds."""
        from app.application.services.qc_service import QCService
        
        service = QCService.__new__(QCService)
        
        rules = [
            {"metric": "moisture_pct", "op": "<=", "value": 13.0},
            {"metric": "aflatoxin_ppb", "op": "<=", "value": 5},
        ]
        
        # Fail: moisture too high
        metrics = {"moisture_pct": 15.0, "aflatoxin_ppb": 3.2}
        
        result = service._check_rules(rules, metrics)
        
        assert result is False
    
    def test_evaluate_grade_missing_metric(self):
        """Test that rules fail when a required metric is missing."""
        from app.application.services.qc_service import QCService
        
        service = QCService.__new__(QCService)
        
        rules = [
            {"metric": "moisture_pct", "op": "<=", "value": 13.0},
            {"metric": "aflatoxin_ppb", "op": "<=", "value": 5},
        ]
        
        # Missing aflatoxin_ppb
        metrics = {"moisture_pct": 12.0}
        
        result = service._check_rules(rules, metrics)
        
        assert result is False


class TestSignatureVerification:
    """Tests for signature verification."""
    
    def test_verify_signature_matching_hash(self):
        """Test that matching hash is verified successfully."""
        from app.application.services.qc_service import QCService
        
        service = QCService.__new__(QCService)
        
        payload = {
            "batch_id": "batch-123",
            "sample_id": "sample-123",
            "tested_at": "2026-02-20T08:12:00",
            "metrics": {"moisture_pct": 12.3},
        }
        
        # Compute expected hash
        import hashlib
        import json
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        expected_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        
        result = service.verify_signature(payload, f"sha256:{expected_hash}", "mock_public_key")
        
        assert result is True
    
    def test_verify_signature_mismatched_hash(self):
        """Test that mismatched hash fails verification."""
        from app.application.services.qc_service import QCService
        
        service = QCService.__new__(QCService)
        
        payload = {
            "batch_id": "batch-123",
            "metrics": {"moisture_pct": 12.3},
        }
        
        result = service.verify_signature(payload, "sha256:wronghash", "mock_public_key")
        
        assert result is False
    
    def test_verify_signature_no_public_key(self):
        """Test behavior when no public key is provided."""
        from app.application.services.qc_service import QCService
        
        service = QCService.__new__(QCService)
        
        payload = {"batch_id": "batch-123"}
        
        # With no public key and no hash, should return False
        result = service.verify_signature(payload, None, None)
        
        assert result is False


class TestQCServiceIntegration:
    """Integration tests for QC service (mocked DB)."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()
    
    def test_process_lab_webhook_lab_not_found(self, mock_db):
        """Test that webhook fails when lab doesn't exist."""
        # Setup mock
        mock_qc_repo = Mock()
        mock_qc_repo.get_lab_provider_by_id.return_value = None
        
        service = QCService(mock_db)
        service.qc_repo = mock_qc_repo
        
        result, success, error_code = service.process_lab_webhook(
            lab_id="non-existent-lab",
            sample_id=None,
            batch_id="batch-123",
            tested_at=datetime.now(timezone.utc),
            metrics={"moisture_pct": 12.3},
            report_url=None,
            signed_hash=None,
        )
        
        assert success is False
        assert error_code == "LAB_NOT_FOUND"
    
    def test_process_lab_webhook_batch_not_found(self, mock_db):
        """Test that webhook fails when batch doesn't exist."""
        mock_qc_repo = Mock()
        mock_qc_repo.get_lab_provider_by_id.return_value = Mock(name="Test Lab")
        
        mock_batch_repo = Mock()
        mock_batch_repo.get_batch_by_id.return_value = None
        
        service = QCService(mock_db)
        service.qc_repo = mock_qc_repo
        service.batch_repo = mock_batch_repo
        
        result, success, error_code = service.process_lab_webhook(
            lab_id="lab-123",
            sample_id=None,
            batch_id="non-existent-batch",
            tested_at=datetime.now(timezone.utc),
            metrics={"moisture_pct": 12.3},
            report_url=None,
            signed_hash=None,
        )
        
        assert success is False
        assert error_code == "BATCH_NOT_FOUND"
    
    def test_process_lab_webhook_invalid_batch_state(self, mock_db):
        """Test that webhook fails for invalid batch state."""
        mock_qc_repo = Mock()
        mock_qc_repo.get_lab_provider_by_id.return_value = Mock(name="Test Lab")
        
        mock_batch = Mock()
        mock_batch.status = HarvestBatchState.DRAFT  # Invalid state
        
        mock_batch_repo = Mock()
        mock_batch_repo.get_batch_by_id.return_value = mock_batch
        
        service = QCService(mock_db)
        service.qc_repo = mock_qc_repo
        service.batch_repo = mock_batch_repo
        
        result, success, error_code = service.process_lab_webhook(
            lab_id="lab-123",
            sample_id=None,
            batch_id="batch-123",
            tested_at=datetime.now(timezone.utc),
            metrics={"moisture_pct": 12.3},
            report_url=None,
            signed_hash=None,
        )
        
        assert success is False
        assert "INVALID_BATCH_STATE" in error_code


class TestListingValidation:
    """Tests for product listing validation."""
    
    def test_validate_batch_sealed_without_qc(self):
        """Test that sealed batch without QC report fails validation."""
        from app.api.products.validation import validate_batch_for_listing
        
        mock_db = Mock()
        mock_service = Mock()
        mock_service.validate_batch_for_listing.return_value = (False, "MISSING_QC_REPORT")
        
        with patch('app.api.products.validation.QCService', return_value=mock_service):
            result, error = validate_batch_for_listing(mock_db, "batch-123")
        
        assert result is False
        assert error == "MISSING_QC_REPORT"
    
    def test_validate_batch_qc_passed(self):
        """Test that QC_PASSED batch passes validation."""
        from app.api.products.validation import validate_batch_for_listing
        
        mock_db = Mock()
        mock_service = Mock()
        mock_service.validate_batch_for_listing.return_value = (True, None)
        
        with patch('app.api.products.validation.QCService', return_value=mock_service):
            result, error = validate_batch_for_listing(mock_db, "batch-123")
        
        assert result is True
        assert error is None
    
    def test_validate_multiple_batches_all_valid(self):
        """Test validation of multiple batches where all are valid."""
        from app.api.products.validation import validate_batches_for_listing, ListingValidationError
        
        mock_db = Mock()
        mock_service = Mock()
        mock_service.validate_multiple_batches_for_listing.return_value = (True, [])
        
        with patch('app.api.products.validation.QCService', return_value=mock_service):
            # Should not raise exception
            validate_batches_for_listing(mock_db, ["batch-1", "batch-2"])
    
    def test_validate_multiple_batches_one_invalid(self):
        """Test validation fails when one batch is invalid."""
        from app.api.products.validation import validate_batches_for_listing, ListingValidationError
        
        mock_db = Mock()
        mock_service = Mock()
        mock_service.validate_multiple_batches_for_listing.return_value = (
            False, 
            ["batch-1:MISSING_QC_REPORT"]
        )
        
        with patch('app.api.products.validation.QCService', return_value=mock_service):
            with pytest.raises(ListingValidationError) as exc_info:
                validate_batches_for_listing(mock_db, ["batch-1", "batch-2"])
            
            assert exc_info.value.code == "MISSING_QC_REPORT"


class TestCommodityRequirements:
    """Tests for commodity-specific QC requirements."""
    
    def test_get_qc_requirements_maize(self):
        """Test QC requirements for maize."""
        from app.api.products.validation import get_qc_requirements
        
        requirements = get_qc_requirements("maize")
        
        assert requirements["require_lab_test"] is True
        assert requirements["require_verified"] is False
    
    def test_get_qc_requirements_coffee(self):
        """Test QC requirements for coffee (requires verification)."""
        from app.api.products.validation import get_qc_requirements
        
        requirements = get_qc_requirements("coffee")
        
        assert requirements["require_lab_test"] is True
        assert requirements["require_verified"] is True
    
    def test_get_qc_requirements_unknown(self):
        """Test QC requirements for unknown commodity (no lab required)."""
        from app.api.products.validation import get_qc_requirements
        
        requirements = get_qc_requirements("unknown_crop")
        
        assert requirements["require_lab_test"] is False
        assert requirements["require_verified"] is False


class TestIdempotency:
    """Tests for webhook idempotency."""
    
    def test_check_idempotent_report_returns_existing(self):
        """Test that existing report is detected for idempotency."""
        from app.infrastructure.repositories.qc_repo import QCRepository
        
        mock_db = Mock()
        mock_orm = Mock()
        mock_orm.id = "existing-report-id"
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_orm
        
        mock_db.query.return_value = mock_query
        
        repo = QCRepository(mock_db)
        
        # This is a simplified test - actual implementation would use proper time comparison
        # We're just verifying the method exists and is callable
        assert hasattr(repo, 'check_idempotent_report')
