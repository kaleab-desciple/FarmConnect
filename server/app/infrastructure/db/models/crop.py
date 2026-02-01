from uuid import uuid4
from datetime import datetime, date, timezone
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import Base

class CropCycleORM(Base):
    __tablename__ = "crop_cycles"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    field_id: Mapped[str] = mapped_column(String, ForeignKey("fields.id"), nullable=False)
    product_category: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variety: Mapped[str] = mapped_column(String(100), nullable=True)
    cultivar: Mapped[str] = mapped_column(String(100), nullable=True)
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_harvest_date: Mapped[date] = mapped_column(Date, nullable=True)
    actual_harvest_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PLANTED")
    expected_yield_kg: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    actual_yield_kg: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    seed_source: Mapped[str] = mapped_column(String(255), nullable=True)
    planting_density_per_ha: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Using metadata_ to avoid conflict with Base.metadata
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", nullable=False, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship to field
    field = relationship("FieldORM", back_populates="crop_cycles")
