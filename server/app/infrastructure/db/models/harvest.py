"""Harvest ORM model for agricultural management."""
from uuid import uuid4
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, DateTime, Date, Numeric, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base
from app.domain.common.enums import Unit, QualityGrade

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
