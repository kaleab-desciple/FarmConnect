from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, Enum as SAEnum, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.infrastructure.db.base import Base
from app.domain.common.enums import DeliveryStatus

class DeliveryORM(Base):
    __tablename__ = "deliveries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    order_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    carrier_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[DeliveryStatus] = mapped_column(SAEnum(DeliveryStatus, name='delivery_status_enum', create_type=False), nullable=False, default=DeliveryStatus.ASSIGNED)
    pickup_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    pickup_photo_url: Mapped[str] = mapped_column(String, nullable=True)
    delivery_photo_url: Mapped[str] = mapped_column(String, nullable=True)
    recipient_signature_url: Mapped[str] = mapped_column(String, nullable=True)
    notes: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)
