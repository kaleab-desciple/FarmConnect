"""Unit tests for product listing QC guard.

These tests verify that:
- QC pass allows listing
- QC fail blocks listing
- Signature verification affects listing eligibility
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from uuid import uuid4

from app.api.products.validation import (
    ListingValidationError,
    validate_batch_for_listing,
    validate_batches_for_listing,
    check_harvest_batch_status,
    validate_batch_by_commodity,
    get_qc_requirements,
)
from app.domain.harvest.entities import HarvestBatchState


class TestQCPassAllowsListing:
    """Tests verifying QC pass allows product listing."""
    
    def test_qc_passed_batch_allows_listing(self):
        """Test that batch with QC_PASSED status allows listing."""
        mock_db = Mock()
        
        # Mock the batch to have QC_PASSED status
        mock_batch = Mock()
        mock_batch.status = HarvestBatchState.QC_PASSED
        
        mock_repo = Mock()
        mock_repo.get_batch_by_id.return_value = mock_batch
        
        # Mock QC validation to return valid
        mock_service = Mock()
        mock_service.validate_batch_for_listing.return_value = (True, None)
        
        with patch('app.api.products.validation.HarvestBatchRepository', return_value=mock_repo):
            with patch('app.api.products.validation.QCService', return_value=mock_service):
                status, can_list, error = check_harvest_batch_status(mock_db, "batch-123")
        
        assert can_list is True
        assert error is None
    
    def test_sealed_batch_with_valid_qc_allows_listing(self):
        """Test that SEALED batch with valid QC report allows listing."""
        mock_db = Mock()
        
        mock_batch = Mock()
        mock_batch.status = HarvestBatchState.SEALED
        
        mock_repo = Mock()
        mock_repo.get_batch_by_id.return_value = mock_batch
        
        mock_service = Mock()
        mock_service.validate_batch_for_listing.return_value = (True, None)
        
        with patch('app.api.products.validation.HarvestBatchRepository', return_value=mock_repo):
            with patch('app.api.products.validation.QCService', return_value=mock_service):
                status, can_list, error = check_harvest_batch_status(mock_db, "batch-123")
        
        assert can_list is True
        assert error is None


class TestQCFailBlocksListing:
    """Tests verifying QC fail blocks product listing."""
    
    def test_qc_failed_batch_blocks_listing(self):
        """Test that QC_FAILED batch blocks listing."""
        mock_db = Mock()
        
        mock_batch = Mock()
        mock_batch.status = HarvestBatchState.QC_FAILED
        
        mock_repo = Mock()
        mock_repo.get_batch_by_id.return_value = mock_batch
        
        with patch('app.api.products.validation.HarvestBatchRepository', return_value=mock_repo):
            status, can_list, error = check_harvest_batch_status(mock_db, "batch-123")
        
        assert can_list is False
        assert error == "QC_FAILED"
    
    def test_draft_batch_blocks_listing(self):
        """Test that DRAFT batch blocks listing."""
        mock_db = Mock()
        
        mock_batch = Mock()
        mock_batch.status = HarvestBatchState.DRAFT
        
        mock_repo = Mock()
        mock_repo.get_batch_by_id.return_value = mock_batch
        
        with patch('app.api.products.validation.HarvestBatchRepository', return_value=mock_repo):
            status, can_list, error = check_harvest_batch_status(mock_db, "batch-123")
        
        assert can_list is False
        assert error == "BATCH_NOT_SEALED"
    
    def test_missing_qc_report_blocks_listing(self):
        """Test that missing QC report blocks listing."""
        mock_db = Mock()
        
        mock_batch = Mock()
        mock_batch.status = HarvestBatchState.SEALED
        
        mock_repo = Mock()
        mock_repo.get_batch_by_id.return_value = mock_batch
        
        mock_service = Mock()
        mock_service.validate_batch_for_listing.return_value = (False, "MISSING_QC_REPORT")
        
        with patch('app.api.products.validation.HarvestBatchRepository', return_value=mock_repo):
            with patch('app.api.products.validation.QCService', return_value=mock_service):
                status, can_list, error = check_harvest_batch_status(mock_db, "batch-123")
        
        assert can_list is False
        assert error == "MISSING_QC_REPORT"


class TestSignatureVerificationBlocksListing:
    """Tests verifying signature verification requirements."""
    
    def test_unverified_lab_report_blocks_verification_required(self):
        """Test that unverified report blocks listing when verification required."""
        mock_db = Mock()
        
        mock_batch = Mock()
        mock_batch.status = HarvestBatchState.SEALED
        
        mock_repo = Mock()
        mock_repo.get_batch_by_id.return_value = mock_batch
        
        mock_service = Mock()
        mock_service.validate_batch_for_listing.return_value = (False, "QC_UNVERIFIED")
        
        with patch('app.api.products.validation.HarvestBatchRepository', return_value=mock_repo):
            with patch('app.api.products.validation.QCService', return_value=mock_service):
                # Test with require_verified=True
                result, error = validate_batch_for_listing(
                    mock_db, "batch-123", 
                    require_lab_test=True, 
                    require_verified=True
                )
        
        assert result is False
        assert error == "QC_UNVERIFIED"


class TestBatchNotFound:
    """Tests for non-existent batch handling."""
    
    def test_batch_not_found_returns_error(self):
        """Test that non-existent batch returns appropriate error."""
        mock_db = Mock()
        
        mock_repo = Mock()
        mock_repo.get_batch_by_id.return_value = None
        
        with patch('app.api.products.validation.HarvestBatchRepository', return_value=mock_repo):
            status, can_list, error = check_harvest_batch_status(mock_db, "non-existent")
        
        assert can_list is False
        assert error == "BATCH_NOT_FOUND"


class TestMultipleBatchValidation:
    """Tests for validating multiple batches."""
    
    def test_all_batches_valid_no_error(self):
        """Test that all valid batches don't raise errors."""
        mock_db = Mock()
        
        mock_service = Mock()
        mock_service.validate_multiple_batches_for_listing.return_value = (True, [])
        
        with patch('app.api.products.validation.QCService', return_value=mock_service):
            validate_batches_for_listing(
                mock_db, 
                ["batch-1", "batch-2", "batch-3"]
            )
    
    def test_one_batch_invalid_raises_error(self):
        """Test that one invalid batch raises ListingValidationError."""
        mock_db = Mock()
        
        mock_service = Mock()
        mock_service.validate_multiple_batches_for_listing.return_value = (
            False, 
            ["batch-2:QC_FAILED"]
        )
        
        with patch('app.api.products.validation.QCService', return_value=mock_service):
            with pytest.raises(ListingValidationError) as exc_info:
                validate_batches_for_listing(
                    mock_db, 
                    ["batch-1", "batch-2", "batch-3"]
                )
            
            assert exc_info.value.code == "QC_FAILED"
            assert "batch-2" in exc_info.value.batch_ids
    
    def test_multiple_errors_priority(self):
        """Test that error priority is correctly applied."""
        mock_db = Mock()
        
        # Return multiple errors
        mock_service = Mock()
        mock_service.validate_multiple_batches_for_listing.return_value = (
            False, 
            ["batch-1:MISSING_QC_REPORT", "batch-2:MISSING_SEAL"]
        )
        
        with patch('app.api.products.validation.QCService', return_value=mock_service):
            with pytest.raises(ListingValidationError) as exc_info:
                validate_batches_for_listing(mock_db, ["batch-1", "batch-2"])
            
            # MISSING_SEAL should take priority
            assert exc_info.value.code == "MISSING_SEAL"


class TestCommodityValidation:
    """Tests for commodity-specific validation."""
    
    def test_validate_maize_batch(self):
        """Test validation for maize commodity."""
        from app.api.products.validation import get_qc_requirements
        
        # Get requirements for maize - should require lab test but not verification
        reqs = get_qc_requirements("maize")
        
        assert reqs["require_lab_test"] is True
        assert reqs["require_verified"] is False
    
    def test_validate_coffee_requires_verification(self):
        """Test that coffee requires signature verification."""
        # Get requirements
        reqs = get_qc_requirements("coffee")
        
        assert reqs["require_verified"] is True
