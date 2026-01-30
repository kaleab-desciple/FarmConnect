import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, Boolean, Numeric
from sqlalchemy.dialects import postgresql
from app.infrastructure.db.base import Base

# Use create_type=False to avoid attempting to create the PG enum types at import time
EscrowStateEnum = postgresql.ENUM(
    "CREATED",
    "FUNDED",
    "RELEASED",
    "DISPUTED",
    "REFUNDED",
    "SETTLED",
    "REVERSED",
    name="escrow_state_enum",
    create_type=False,
)

ProviderEnum = postgresql.ENUM(
    "BANK",
    "WALLET",
    name="provider_enum",
    create_type=False,
)


class EscrowORM(Base):
    __tablename__ = "escrows"
    __table_args__ = {"extend_existing": True}

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),           # Python-side default when constructing ORM instances
        server_default=sa.text("gen_random_uuid()"), # DB-side default (optional; requires pgcrypto or uuid-ossp)
    )
    order_id = Column(String, nullable=False)
    state = Column(EscrowStateEnum, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    provider = Column(ProviderEnum, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    funded_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    provider_reference = Column(String, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - simple helper
        return f"<EscrowORM id={self.id} state={self.state}>"