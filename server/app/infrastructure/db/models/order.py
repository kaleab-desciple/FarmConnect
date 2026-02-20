from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.common.enums import OrderStatus

class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    farmer_id: Mapped[str] = mapped_column(String, nullable=True)
    merchant_id: Mapped[str] = mapped_column(String, nullable=True)
    product_id: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=True)
    unit_price: Mapped[float] = mapped_column(Float, nullable=True)
    subtotal: Mapped[float] = mapped_column(Float, nullable=True)
    delivery_fee: Mapped[float] = mapped_column(Float, nullable=True)
    delivery_margin: Mapped[float] = mapped_column(Float, nullable=True)
    quality_fee: Mapped[float] = mapped_column(Float, nullable=True)
    platform_fee: Mapped[float] = mapped_column(Float, nullable=True)
    total_price: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus, name='order_status_enum', create_type=False), nullable=True)
    escrow_id: Mapped[str] = mapped_column(String, nullable=True)
    batch_id: Mapped[str] = mapped_column(String, ForeignKey("product_batches.id"), nullable=True)
    cancelled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)
