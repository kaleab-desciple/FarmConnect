from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, Float, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from shared_models.enums import OrderStatus

class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    farmer_id: Mapped[str] = mapped_column(String, nullable=True)
    merchant_id: Mapped[str] = mapped_column(String, nullable=True)
    product_id: Mapped[str] = mapped_column(String, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=True)
    unit_price: Mapped[float] = mapped_column(Float, nullable=True)
    delivery_cost: Mapped[float] = mapped_column(Float, nullable=True)
    platform_fee: Mapped[float] = mapped_column(Float, nullable=True)
    total_price: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus, name='order_status_enum'), nullable=True)
    escrow_id: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
