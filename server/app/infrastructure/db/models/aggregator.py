"""Aggregator ORM models for smallholder reconciliation and split settlement.

This module contains:
- AggregatorORM: Collection center that collects harvest from smallholders
- AcceptanceWeighmentORM: Weight recording at aggregator entry
- ReconciliationRecordORM: Comparison of farmer-declared vs aggregator-measured
- SettlementRuleORM: Rules for splitting payments among smallholders
- AggregatorSettlementSummaryORM: Summary of settlement for a batch
- SplitSettlementORM: Individual smallholder's payment calculation
"""

from uuid import uuid4
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum, Index, Float, Boolean, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.harvest import HarvestBatchORM


class AggregatorORM(Base):
    """Aggregator entity - collection center that collects harvest from smallholders."""
    __tablename__ = "aggregators"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    company_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    contact: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    kyc_status: Mapped[str] = mapped_column(SAEnum('PENDING', 'VERIFIED', 'REJECTED', name='aggregator_kyc_status_enum'), nullable=False, server_default='PENDING')
    wallet_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, name="metadata", nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

    # Relationships
    settlement_rules: Mapped[List["SettlementRuleORM"]] = relationship("SettlementRuleORM", back_populates="aggregator")
    settlement_summaries: Mapped[List["AggregatorSettlementSummaryORM"]] = relationship("AggregatorSettlementSummaryORM", back_populates="aggregator")


class AcceptanceWeighmentORM(Base):
    """Weight recording when smallholder delivers harvest to aggregator."""
    __tablename__ = "acceptance_weighments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    weighbridge_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gross_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    tare_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    net_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    receipt_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weigher_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recorded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))

    # Relationships
    batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM", back_populates="acceptance_weighments")


class ReconciliationRecordORM(Base):
    """Reconciliation between farmer-declared quantity and aggregator-measured quantity."""
    __tablename__ = "reconciliation_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    expected_total_kg: Mapped[float] = mapped_column(Float, nullable=False)
    measured_total_kg: Mapped[float] = mapped_column(Float, nullable=False)
    difference_kg: Mapped[float] = mapped_column(Float, nullable=False)
    variance_pct: Mapped[float] = mapped_column(Float, nullable=False)
    recon_status: Mapped[str] = mapped_column(SAEnum('OK', 'WARNING', 'DISPUTE', name='recon_status_enum'), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))

    # Relationships
    batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM", back_populates="reconciliation_records")


class SettlementRuleORM(Base):
    """Rules for splitting payments among smallholders."""
    __tablename__ = "settlement_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    aggregator_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("aggregators.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    split_method: Mapped[str] = mapped_column(SAEnum('BY_WEIGHT', 'BY_VALUE', 'FIXED_RATE', name='split_method_enum'), nullable=False)
    platform_fee_pct: Mapped[float] = mapped_column(Float, nullable=False, server_default='5.0')
    aggregator_commission_pct: Mapped[float] = mapped_column(Float, nullable=False, server_default='10.0')
    min_payout_threshold: Mapped[float] = mapped_column(Float, nullable=False, server_default='10.0')
    rounding_policy: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='false')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))

    # Relationships
    aggregator: Mapped[Optional["AggregatorORM"]] = relationship("AggregatorORM", back_populates="settlement_rules")
    settlement_summaries: Mapped[List["AggregatorSettlementSummaryORM"]] = relationship("AggregatorSettlementSummaryORM", back_populates="settlement_rule")


class AggregatorSettlementSummaryORM(Base):
    """Summary of settlement for a batch at an aggregator."""
    __tablename__ = "aggregator_settlement_summaries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    batch_id: Mapped[str] = mapped_column(String, ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False)
    aggregator_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("aggregators.id", ondelete="SET NULL"), nullable=True)
    gross_sale_amount: Mapped[float] = mapped_column(Float, nullable=False)
    total_platform_fee: Mapped[float] = mapped_column(Float, nullable=False)
    total_commission: Mapped[float] = mapped_column(Float, nullable=False)
    net_to_distribute: Mapped[float] = mapped_column(Float, nullable=False)
    rounding_adjustment: Mapped[float] = mapped_column(Float, nullable=False, server_default='0')
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default='USD')
    status: Mapped[str] = mapped_column(SAEnum('PENDING', 'IN_PROGRESS', 'PAID', 'FAILED', name='settlement_summary_status_enum'), nullable=False, server_default='PENDING')
    settlement_rule_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("settlement_rules.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))

    # Relationships
    batch: Mapped["HarvestBatchORM"] = relationship("HarvestBatchORM", back_populates="settlement_summaries")
    aggregator: Mapped[Optional["AggregatorORM"]] = relationship("AggregatorORM", back_populates="settlement_summaries")
    settlement_rule: Mapped[Optional["SettlementRuleORM"]] = relationship("SettlementRuleORM", back_populates="settlement_summaries")
    split_settlements: Mapped[List["SplitSettlementORM"]] = relationship("SplitSettlementORM", back_populates="settlement_summary")


class SplitSettlementORM(Base):
    """Individual smallholder's share from the settlement."""
    __tablename__ = "split_settlements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    settlement_summary_id: Mapped[str] = mapped_column(String, ForeignKey("aggregator_settlement_summaries.id", ondelete="CASCADE"), nullable=False)
    contribution_id: Mapped[str] = mapped_column(String, nullable=False)  # FK to harvest_batch_contributions
    farmer_id: Mapped[str] = mapped_column(String, nullable=False)
    contributed_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    share_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default='USD')
    status: Mapped[str] = mapped_column(SAEnum('PENDING', 'PREPARED', 'PAYMENT_SENT', 'PAID', 'FAILED', 'ADJUSTED', name='settlement_status_enum'), nullable=False, server_default='PENDING')
    payout_reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    settlement_summary: Mapped["AggregatorSettlementSummaryORM"] = relationship("AggregatorSettlementSummaryORM", back_populates="split_settlements")


# Import at bottom to avoid circular imports
# Already imported at top: from app.infrastructure.db.models.harvest import HarvestBatchORM
