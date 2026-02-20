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
    """
    __tablename__ = "batch_qc_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    lab_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    report_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    signed_hash: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM", back_populates="qc_reports")
    
    __table_args__ = (
        Index('idx_qc_reports_batch_id', 'batch_id'),
        Index('idx_qc_reports_lab_id', 'lab_id'),
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
