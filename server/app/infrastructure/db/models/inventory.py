"""
ORM models for Inventory Management:
- InventoryMovementORM: event-sourced inventory ledger
- ProductBatchORM: batch tracking for products
"""

from uuid import uuid4
from datetime import datetime, date, timezone
import sqlalchemy as sa
from sqlalchemy import String, Float, Date, DateTime, Boolean, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.common.enums import InventoryMovementType, QualityGrade


class InventoryMovementORM(Base):
    """Event-sourced inventory ledger. Positive = stock in, negative = stock out."""
    __tablename__ = "inventory_movements"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4()),
        server_default=sa.text("gen_random_uuid()")
    )
    product_id: Mapped[str] = mapped_column(
        String, ForeignKey("products.id"), nullable=False, index=True
    )
    batch_id: Mapped[str] = mapped_column(
        String, ForeignKey("product_batches.id"), nullable=True
    )
    movement_type: Mapped[InventoryMovementType] = mapped_column(
        SAEnum(InventoryMovementType, name="inventory_movement_type_enum",
               create_type=False),
        nullable=False,
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ProductBatchORM(Base):
    """Batch tracking for products (different harvest lots, dates, grades)."""
    __tablename__ = "product_batches"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4()),
        server_default=sa.text("gen_random_uuid()")
    )
    product_id: Mapped[str] = mapped_column(
        String, ForeignKey("products.id"), nullable=False, index=True
    )
    batch_code: Mapped[str] = mapped_column(String(50), nullable=False)
    total_quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    reserved_quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    sold_quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    spoiled_quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=True)
    quality_grade: Mapped[QualityGrade] = mapped_column(
        SAEnum(QualityGrade, name="quality_grade_enum", create_type=False),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        sa.UniqueConstraint("product_id", "batch_code", name="uq_product_batch_code"),
    )
