"""Harvest ORM models for agricultural management.

This module contains:
- HarvestORM: Legacy harvest tracking for individual farmer field harvests
- HarvestEventORM: Field-level harvest events with weight, moisture, photos
- HarvestBatchORM: Aggregated batches with lineage hash and sealing
- HarvestBatchContributionORM: Many-to-many between batches and events
- BatchQCReportORM: Quality control lab reports
- ProductBatchSourceORM: Many-to-many between product batches and harvest batches
- AuditEventORM: Audit trail for traceability
"""
from uuid import uuid4
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, UniqueConstraint, Index, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.domain.common.enums import Unit, QualityGrade
from app.domain.harvest.entities import HarvestBatchState
from app.domain.common.enums import QCGrade, CertificationType

class HarvestORM(Base):
    """Harvest entity representing a harvest event for a specific crop cycle and field."""
    __tablename__ = "harvests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    farmer_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    field_id: Mapped[str] = mapped_column(String, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_harvested: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[Optional[Unit]] = mapped_column(SAEnum(Unit, name='unit_enum', create_type=False), nullable=True)
    quality_grade: Mapped[Optional[QualityGrade]] = mapped_column(SAEnum(QualityGrade, name='quality_grade_enum', create_type=False), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    farmer: Mapped["UserORM"] = relationship("UserORM")
    field: Mapped["FieldORM"] = relationship("FieldORM")
    crop_cycle: Mapped[Optional["CropCycleORM"]] = relationship("CropCycleORM")
    products: Mapped[list["ProductORM"]] = relationship("ProductORM", back_populates="harvest")


class HarvestEventORM(Base):
    """
    HarvestEvent entity for field-level harvest tracking.
    Records who, where, weight, moisture, and photos for each harvest event.
    """
    __tablename__ = "harvest_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    farm_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    field_id: Mapped[str] = mapped_column(String, nullable=False)
    crop_cycle_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    collected_by: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    harvested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    gross_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    moisture_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    loss_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    weighbridge_receipt: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    location: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    farm: Mapped["UserORM"] = relationship("UserORM", foreign_keys=[farm_id])
    collector: Mapped[Optional["UserORM"]] = relationship("UserORM", foreign_keys=[collected_by])


class HarvestBatchORM(Base):
    """
    HarvestBatch entity that aggregates HarvestEvent contributions.
    Acts as the immutable provenance anchor for downstream ProductBatch/listings.
    """
    __tablename__ = "harvest_batches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    batch_code: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregator_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    settlement_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # For batch settlement state
    status: Mapped[HarvestBatchState] = mapped_column(
        SAEnum(HarvestBatchState, name='harvest_batch_state_enum', create_type=False),
        nullable=False,
        default=HarvestBatchState.DRAFT
    )
    aggregated_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    moisture_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sealed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sealed_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    seal_evidence: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    lineage_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    lineage_signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    aggregator: Mapped[Optional["UserORM"]] = relationship("UserORM")
    contributions: Mapped[list["HarvestBatchContributionORM"]] = relationship(
        "HarvestBatchContributionORM", back_populates="batch", cascade="all, delete-orphan"
    )
    qc_reports: Mapped[list["BatchQCReportORM"]] = relationship("BatchQCReportORM", back_populates="batch", cascade="all, delete-orphan")
    samples: Mapped[list["SampleORM"]] = relationship("SampleORM", back_populates="harvest_batch", cascade="all, delete-orphan")
    certifications: Mapped[list["CertificationORM"]] = relationship("CertificationORM", back_populates="harvest_batch", cascade="all, delete-orphan")
    
    # Aggregator settlement relationships
    acceptance_weighments: Mapped[list["AcceptanceWeighmentORM"]] = relationship(
        "AcceptanceWeighmentORM", back_populates="batch", cascade="all, delete-orphan"
    )
    reconciliation_records: Mapped[list["ReconciliationRecordORM"]] = relationship(
        "ReconciliationRecordORM", back_populates="batch", cascade="all, delete-orphan"
    )
    settlement_summaries: Mapped[list["AggregatorSettlementSummaryORM"]] = relationship(
        "AggregatorSettlementSummaryORM", back_populates="batch", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint('batch_code', name='uq_harvest_batch_code'),
        Index('idx_harvest_batches_aggregator_id', 'aggregator_id'),
        Index('idx_harvest_batches_status', 'status'),
    )


class HarvestBatchContributionORM(Base):
    """
    HarvestBatchContribution - many-to-many relationship between harvest events and batches.
    """
    __tablename__ = "harvest_batch_contributions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    harvest_batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    harvest_event_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_events.id", ondelete="CASCADE"), nullable=False)
    farmer_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contributed_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    reported_moisture_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM", back_populates="contributions")
    harvest_event: Mapped["HarvestEventORM"] = relationship("HarvestEventORM")
    farmer: Mapped["UserORM"] = relationship("UserORM")
    
    __table_args__ = (
        UniqueConstraint('harvest_batch_id', 'harvest_event_id', name='uq_batch_event_contribution'),
        Index('idx_contributions_batch_id', 'harvest_batch_id'),
        Index('idx_contributions_event_id', 'harvest_event_id'),
        Index('idx_contributions_farmer_id', 'farmer_id'),
    )


class BatchQCReportORM(Base):
    """
    BatchQCReport entity for quality control lab results.
    Expanded with sample_id, grade, and verified fields.
    """
    __tablename__ = "batch_qc_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    sample_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("samples.id", ondelete="SET NULL"), nullable=True)
    lab_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # qc_grade_enum
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    report_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    signed_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM", back_populates="qc_reports")
    
    __table_args__ = (
        Index('idx_qc_reports_batch_id', 'batch_id'),
        Index('idx_qc_reports_lab_id', 'lab_id'),
        Index('idx_qc_reports_sample_id', 'sample_id'),
    )


class ProductBatchSourceORM(Base):
    """
    ProductBatchSource - many-to-many relationship between product batches and harvest batches.
    """
    __tablename__ = "product_batch_sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    product_batch_id: Mapped[str] = mapped_column(String, ForeignKey("product_batches.id", ondelete="CASCADE"), nullable=False)
    harvest_batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    contribution_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    product_batch: Mapped["ProductBatchORM"] = relationship("ProductBatchORM")
    harvest_batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM")
    
    __table_args__ = (
        UniqueConstraint('product_batch_id', 'harvest_batch_id', name='uq_product_batch_source'),
        Index('idx_product_batch_sources_product', 'product_batch_id'),
        Index('idx_product_batch_sources_harvest', 'harvest_batch_id'),
    )


class AuditEventORM(Base):
    """
    AuditEvent for append-only traceability.
    Records critical events: batch.created, batch.sealed, qc.passed, listing.created, settlement.
    """
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    payload_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    previous_event_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_audit_events_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_events_type', 'event_type'),
        Index('idx_audit_events_created', 'created_at'),
    )


# ========================================
# QC/Grading ORM Models
# ========================================


class LabProviderORM(Base):
    """LabProvider ORM entity for lab accreditation."""
    __tablename__ = "lab_providers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    public_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # PEM public key
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_lab_providers_name', 'name'),
    )


class SampleORM(Base):
    """Sample ORM entity for QC sampling requests."""
    __tablename__ = "samples"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    sample_code: Mapped[str] = mapped_column(String(100), nullable=False)
    harvest_batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    collected_by: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sample_points: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # GPS points
    photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)  # Array of {url, hash, exif}
    chain_of_custody: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    submitted_to_lab: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    harvest_batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM", back_populates="samples")
    
    __table_args__ = (
        Index('idx_samples_harvest_batch_id', 'harvest_batch_id'),
        Index('idx_samples_sample_code', 'sample_code', unique=True),
    )


class CertificationORM(Base):
    """Certification ORM entity for product certifications."""
    __tablename__ = "certifications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    harvest_batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    cert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # certification_type_enum
    cert_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cert_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    signed_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    harvest_batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM")
    
    __table_args__ = (
        Index('idx_certifications_harvest_batch_id', 'harvest_batch_id'),
        Index('idx_certifications_type', 'cert_type'),
    )


class QCGradeRuleORM(Base):
    """QCGradeRule ORM entity for configurable grade thresholds."""
    __tablename__ = "qc_grade_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    commodity: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)  # qc_grade_enum
    rules: Mapped[list] = mapped_column(JSONB, nullable=False)  # [{"metric":"moisture_pct","op":"<=","value":13.0}]
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_qc_grade_rules_commodity', 'commodity'),
    )


# ========================================
# Aliases for backwards compatibility
# ========================================

# BatchQCReportV2ORM is an alias for BatchQCReportORM
# The V2 version added sample_id, grade, and verified fields
BatchQCReportV2ORM = BatchQCReportORM
