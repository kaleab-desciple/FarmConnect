from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.domain.common.enums import UserRole
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
