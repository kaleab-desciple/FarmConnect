"""Product Listing Validation for QC requirements.

This module provides validation functions to ensure harvest batches
meet QC requirements before they can be used in product listings.
"""
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.application.services.qc_service import QCService
from app.infrastructure.repositories.harvest_batch_repo import HarvestBatchRepository
from app.domain.harvest.entities import HarvestBatchState


class ListingValidationError(Exception):
    """Exception raised when listing validation fails."""
    
    def __init__(self, code: str, message: str, batch_ids: List[str] = None):
        self.code = code
        self.message = message
        self.batch_ids = batch_ids or []
        super().__init__(message)


def validate_batch_for_listing(
    db: Session,
    batch_id: str,
    require_lab_test: bool = True,
    require_verified: bool = False,
) -> Tuple[bool, Optional[str]]:
    """
    Validate a single batch for product listing.
    
    Args:
        db: Database session
        batch_id: The harvest batch ID
        require_lab_test: Whether lab test is required for this commodity
        require_verified: Whether signature verification is required
    
    Returns:
        Tuple of (is_valid, error_code)
    """
    service = QCService(db)
    return service.validate_batch_for_listing(
        batch_id=batch_id,
        require_lab_test=require_lab_test,
        require_verified=require_verified,
    )


def validate_batches_for_listing(
    db: Session,
    batch_ids: List[str],
    require_lab_test: bool = True,
    require_verified: bool = False,
) -> None:
    """
    Validate multiple batches for product listing.
    
    Raises:
        ListingValidationError: If any batch fails validation
    """
    service = QCService(db)
    
    all_valid, errors = service.validate_multiple_batches_for_listing(
        batch_ids=batch_ids,
        require_lab_test=require_lab_test,
        require_verified=require_verified,
    )
    
    if not all_valid:
        # Determine primary error code
        error_codes = [e.split(":")[1] if ":" in e else e for e in errors]
        
        # Prioritize error codes
        priority_codes = ["MISSING_SEAL", "QC_FAILED", "MISSING_QC_REPORT", "QC_UNVERIFIED", "CERT_EXPIRED"]
        
        primary_code = error_codes[0]
        for code in priority_codes:
            if code in error_codes:
                primary_code = code
                break
        
        failed_batches = [e.split(":")[0] for e in errors]
        
        raise ListingValidationError(
            code=primary_code,
            message=f"Batch validation failed: {', '.join(errors)}",
            batch_ids=failed_batches,
        )


def check_harvest_batch_status(
    db: Session,
    batch_id: str,
) -> Tuple[HarvestBatchState, bool, Optional[str]]:
    """
    Check harvest batch status and QC validity.
    
    Returns:
        Tuple of (status, can_list, error_code)
    """
    batch_repo = HarvestBatchRepository(db)
    batch = batch_repo.get_batch_by_id(batch_id)
    
    if not batch:
        return None, False, "BATCH_NOT_FOUND"
    
    # Check basic status
    if batch.status == HarvestBatchState.DRAFT:
        return batch.status, False, "BATCH_NOT_SEALED"
    
    if batch.status == HarvestBatchState.QC_FAILED:
        return batch.status, False, "QC_FAILED"
    
    # Check for valid QC report
    qc_service = QCService(db)
    is_valid, error = qc_service.validate_batch_for_listing(batch_id)
    
    if not is_valid:
        return batch.status, False, error
    
    return batch.status, True, None


# ========================================
# Commodity-specific Configuration
# ========================================

# Map commodities to their QC requirements
COMMODITY_QC_REQUIREMENTS = {
    "maize": {"require_lab_test": True, "require_verified": False},
    "wheat": {"require_lab_test": True, "require_verified": False},
    "coffee": {"require_lab_test": True, "require_verified": True},
    "rice": {"require_lab_test": True, "require_verified": False},
    "soybeans": {"require_lab_test": True, "require_verified": False},
    # Add more commodities as needed
}


def get_qc_requirements(commodity: str) -> dict:
    """Get QC requirements for a specific commodity."""
    return COMMODITY_QC_REQUIREMENTS.get(
        commodity.lower(), 
        {"require_lab_test": False, "require_verified": False}
    )


def validate_batch_by_commodity(
    db: Session,
    batch_id: str,
    commodity: str,
) -> None:
    """Validate a batch based on its commodity type."""
    requirements = get_qc_requirements(commodity)
    
    validate_batches_for_listing(
        db=db,
        batch_ids=[batch_id],
        require_lab_test=requirements["require_lab_test"],
        require_verified=requirements["require_verified"],
    )
