"""Harvest domain entities for field-level harvest tracking and batch aggregation."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field as PydanticField, field_validator
import hashlib
import json


class HarvestBatchState(str, Enum):
    """Harvest batch state enum."""
    DRAFT = "DRAFT"
    SEALED = "SEALED"
    QC_PENDING = "QC_PENDING"
    QC_PASSED = "QC_PASSED"
    QC_FAILED = "QC_FAILED"
    ARCHIVED = "ARCHIVED"


# ========================================
# HarvestEvent Entities
# ========================================

class HarvestEventBase(BaseModel):
    """Base HarvestEvent entity for field-level harvest tracking."""
    farm_id: str
    field_id: str
    crop_cycle_id: Optional[UUID] = None
    collected_by: Optional[str] = None
    harvested_at: datetime
    gross_weight_kg: float = PydanticField(..., gt=0)
    moisture_pct: Optional[float] = PydanticField(None, ge=0, le=100)
    loss_kg: Optional[float] = PydanticField(default=0, ge=0)
    photos: Optional[List[Dict[str, Any]]] = None  # List of media metadata with exif/geo
    weighbridge_receipt: Optional[Dict[str, Any]] = None  # Weighbridge receipt metadata
    location: Optional[Dict[str, Any]] = None  # GeoJSON location
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class HarvestEventCreate(HarvestEventBase):
    """HarvestEvent creation entity."""
    pass


class HarvestEventUpdate(BaseModel):
    """HarvestEvent update entity."""
    photos: Optional[List[Dict[str, Any]]] = None
    weighbridge_receipt: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    # Note: Core fields like weight, moisture are append-only after creation


class HarvestEvent(HarvestEventBase):
    """HarvestEvent domain entity with full fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========================================
# HarvestBatchContribution Entities
# ========================================

class HarvestBatchContributionBase(BaseModel):
    """Base HarvestBatchContribution entity for many-to-many relationship."""
    harvest_batch_id: UUID
    harvest_event_id: UUID
    farmer_id: str
    contributed_weight_kg: float = PydanticField(..., gt=0)
    reported_moisture_pct: Optional[float] = PydanticField(None, ge=0, le=100)

    class Config:
        from_attributes = True


class HarvestBatchContributionCreate(HarvestBatchContributionBase):
    """HarvestBatchContribution creation entity."""
    pass


class HarvestBatchContribution(HarvestBatchContributionBase):
    """HarvestBatchContribution domain entity with full fields."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ========================================
# HarvestBatch Entities
# ========================================

class HarvestBatchBase(BaseModel):
    """Base HarvestBatch entity for batch aggregation."""
    batch_code: str
    aggregator_id: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class HarvestBatchCreate(HarvestBatchBase):
    """HarvestBatch creation entity."""
    pass


class HarvestBatchSealRequest(BaseModel):
    """Request to seal a harvest batch."""
    sealed_by: str
    seal_evidence: Optional[Dict[str, Any]] = None  # References to receipts, photos, signatures


class HarvestBatch(HarvestBatchBase):
    """HarvestBatch domain entity with full fields."""
    id: UUID
    aggregator_id: Optional[str] = None
    status: HarvestBatchState = HarvestBatchState.DRAFT
    aggregated_weight_kg: Optional[float] = None
    moisture_avg: Optional[float] = None
    sealed_at: Optional[datetime] = None
    sealed_by: Optional[str] = None
    seal_evidence: Optional[Dict[str, Any]] = None
    lineage_hash: Optional[str] = None
    lineage_signature: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related entities (loaded by repository)
    contributions: List[HarvestBatchContribution] = []

    class Config:
        from_attributes = True


# ========================================
# BatchQCReport Entities
# ========================================

class BatchQCReportBase(BaseModel):
    """Base BatchQCReport entity for lab reports."""
    batch_id: UUID
    lab_id: Optional[str] = None
    tested_at: datetime
    metrics: Optional[Dict[str, Any]] = None  # moisture, aflatoxin, mold, etc.
    passed: bool
    report_url: Optional[str] = None
    signed_hash: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class BatchQCReportCreate(BatchQCReportBase):
    """BatchQCReport creation entity."""
    pass


class BatchQCReport(BatchQCReportBase):
    """BatchQCReport domain entity with full fields."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ========================================
# ProductBatchSource Entities
# ========================================

class ProductBatchSourceBase(BaseModel):
    """Base ProductBatchSource entity for many-to-many product-to-harvest-batch linkage."""
    product_batch_id: str
    harvest_batch_id: UUID
    contribution_weight_kg: float = PydanticField(..., gt=0)

    class Config:
        from_attributes = True


class ProductBatchSourceCreate(ProductBatchSourceBase):
    """ProductBatchSource creation entity."""
    pass


class ProductBatchSource(ProductBatchSourceBase):
    """ProductBatchSource domain entity with full fields."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ========================================
# AuditEvent Entities
# ========================================

class AuditEventBase(BaseModel):
    """Base AuditEvent entity for traceability."""
    event_type: str  # batch.created, batch.sealed, qc.passed, etc.
    entity_type: str  # harvest_batch, product_listing, etc.
    entity_id: str
    payload: Optional[Dict[str, Any]] = None
    payload_hash: Optional[str] = None
    previous_event_hash: Optional[str] = None
    user_id: Optional[str] = None
    signature: Optional[str] = None

    class Config:
        from_attributes = True


class AuditEventCreate(AuditEventBase):
    """AuditEvent creation entity."""
    pass


class AuditEvent(AuditEventBase):
    """AuditEvent domain entity with full fields."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ========================================
# Lineage Hash Computation Utilities
# ========================================

def compute_lineage_hash(
    batch_id: str,
    aggregator_id: Optional[str],
    created_at: datetime,
    contributions: List[Dict[str, Any]]
) -> str:
    """
    Compute canonical lineage hash for a harvest batch.
    
    This function creates a deterministic SHA256 hash of the batch's
    contributions and metadata to provide immutable proof of the batch contents.
    
    Args:
        batch_id: The batch UUID
        aggregator_id: The aggregator user ID
        created_at: The batch creation timestamp
        contributions: List of contribution dicts with keys:
            - harvest_event_id
            - farmer_id
            - contributed_weight_kg
            - reported_moisture_pct
            - harvested_at
    
    Returns:
        SHA256 hex digest of the canonical JSON
    """
    # Sort contributions by multiple fields for deterministic ordering
    # This ensures the entire contribution record stays together regardless of input order
    sorted_contributions = sorted(
        contributions,
        key=lambda x: (
            str(x.get('harvest_event_id', '')),
            str(x.get('farmer_id', '')),
            str(x.get('contributed_weight_kg', 0)),
            str(x.get('harvested_at', ''))
        )
    )
    
    # Build canonical object
    canonical_data = {
        "batch_id": str(batch_id),
        "aggregator_id": str(aggregator_id) if aggregator_id else None,
        "created_at": created_at.isoformat() if created_at else None,
        "contributions": [
            {
                "harvest_event_id": str(c.get('harvest_event_id', '')),
                "farmer_id": str(c.get('farmer_id', '')),
                "weight_kg": round(c.get('contributed_weight_kg', 0), 2),
                "moisture_pct": round(c.get('reported_moisture_pct', 0), 2) if c.get('reported_moisture_pct') else None,
                "harvested_at": c.get('harvested_at').isoformat() if c.get('harvested_at') else None
            }
            for c in sorted_contributions
        ]
    }
    
    # Serialize with deterministic ordering (sort keys)
    canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    
    # Compute SHA256 hex
    lineage_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    return lineage_hash


def verify_lineage_hash(
    batch_id: str,
    aggregator_id: Optional[str],
    created_at: datetime,
    contributions: List[Dict[str, Any]],
    expected_hash: str
) -> bool:
    """
    Verify a lineage hash matches the expected value.
    
    Args:
        batch_id: The batch UUID
        aggregator_id: The aggregator user ID  
        created_at: The batch creation timestamp
        contributions: List of contribution dicts
        expected_hash: The hash to verify against
    
    Returns:
        True if hash matches, False otherwise
    """
    computed_hash = compute_lineage_hash(batch_id, aggregator_id, created_at, contributions)
    return computed_hash == expected_hash
