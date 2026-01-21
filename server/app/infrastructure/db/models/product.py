from uuid import uuid4
from datetime import datetime, date, timezone
from sqlalchemy import String, Float, Date, DateTime, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from shared_models.product import Category, Unit, QualityGrade

class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    farmer_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    category: Mapped[Category] = mapped_column(SAEnum(Category, name='category_enum'), nullable=True)
    unit: Mapped[Unit] = mapped_column(SAEnum(Unit, name='unit_enum'), nullable=True)
    base_price: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    quantity_available: Mapped[float] = mapped_column(Float, nullable=True)
    quality_grade: Mapped[QualityGrade] = mapped_column(SAEnum(QualityGrade, name='quality_grade_enum'), nullable=True)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=True)
    # Optional location as JSON
    location: Mapped[dict] = mapped_column(JSONB, nullable=True)
    # Images URLs list as JSON
    images: Mapped[list] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    # Avoid naming the attribute `metadata` because it's reserved by SQLAlchemy's
    # declarative base (Base.metadata). Use `metadata_` in Python and map the
    # column name to `metadata` in the database.
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
