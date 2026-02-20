"""Harvest batch validation guards for product listing.

This module provides validation functions to ensure that products can only
be created from sealed and QC-passed harvest batches, as required by
the supply chain provenance requirements.
"""
from typing import Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.repositories.harvest_batch_repo import HarvestBatchRepository
from app.domain.harvest.entities import HarvestBatchState


class HarvestBatchGuard:
    """Guard class for validating harvest batch requirements."""
    
    @staticmethod
    def validate_batch_for_product_creation(
        db: Session,
        harvest_batch_id: Optional[str],
        require_sealed: bool = True,
    ) -> Tuple[bool, str]:
        """
        Validate that a harvest batch can be used for product creation.
        
        Args:
            db: Database session
            harvest_batch_id: Optional harvest batch ID to validate
            require_sealed: Whether to require sealed QC_PASSED batch (default True)
        
        Returns:
            Tuple of (is_valid, error_message)
            If is_valid is True, error_message will be empty.
        """
        # If no harvest batch is provided and it's required, fail
        if require_sealed and not harvest_batch_id:
            return False, "A sealed harvest batch is required to create this product listing"
        
        # If no harvest batch and not required, allow
        if not harvest_batch_id:
            return True, ""
        
        # Validate the batch exists and is in correct state
        repo = HarvestBatchRepository(db)
        
        try:
            batch = repo.get_batch_by_id(harvest_batch_id)
            if not batch:
                return False, f"Harvest batch not found: {harvest_batch_id}"
            
            if batch.status != HarvestBatchState.QC_PASSED:
                return False, (
                    f"Harvest batch must be QC_PASSED to create a product listing. "
                    f"Current status: {batch.status.value}"
                )
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validating harvest batch: {str(e)}"
    
    @staticmethod
    def validate_batch_for_listing_publish(
        db: Session,
        harvest_batch_ids: list[str],
    ) -> Tuple[bool, str]:
        """
        Validate that all harvest batches can be used for publishing a listing.
        
        This guard is called when publishing a product listing to ensure
        all linked harvest batches are SEALED and have passed QC.
        
        Args:
            db: Database session
            harvest_batch_ids: List of harvest batch IDs to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not harvest_batch_ids:
            return True, ""  # Allow listings without harvest batches
        
        repo = HarvestBatchRepository(db)
        
        for batch_id in harvest_batch_ids:
            is_valid, error = repo.verify_batch_can_be_used_for_listing(batch_id)
            if not is_valid:
                return False, error
        
        return True, ""
    
    @staticmethod
    def require_harvest_batch_for_product(
        db: Session,
        harvest_batch_id: str,
    ) -> None:
        """
        Raise an exception if harvest batch is not valid for product creation.
        
        Args:
            db: Database session
            harvest_batch_id: Harvest batch ID to validate
        
        Raises:
            ValueError: If batch is not valid
        """
        is_valid, error = HarvestBatchGuard.validate_batch_for_product_creation(
            db, harvest_batch_id, require_sealed=True
        )
        
        if not is_valid:
            raise ValueError(error)
