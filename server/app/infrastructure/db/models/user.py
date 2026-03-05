from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.domain.common.enums import UserRole, OnboardingStatus
from app.infrastructure.db.base import Base

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    keycloak_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name='user_role_enum'), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    phone: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc))
    # 'metadata' is a reserved attribute name on Declarative classes (Base.metadata)
    # so expose the column as `metadata_` on the Python class while keeping the
    # database column name as "metadata".
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", nullable=True)
    # Onboarding approval workflow (Gap 4)
    onboarding_status: Mapped[Optional[str]] = mapped_column(
        SAEnum(OnboardingStatus, name='onboarding_status_enum'),
        nullable=True,
        default=OnboardingStatus.ACTIVE.value,
        server_default=OnboardingStatus.ACTIVE.value,
    )
    onboarding_agent_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
