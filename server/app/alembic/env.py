import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine
from alembic import context
from dotenv import load_dotenv

# Load .env
load_dotenv()

# this is the Alembic Config object, which provides
# access to values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Import your ORM models and Base
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import (
    UserORM,
    ProductORM,
    OrderORM,
    EscrowORM,
    DisputeORM,
    ReputationORM,
    AccountORM,
    JournalEntryORM,
    JournalLineORM,
    LedgerEventORM,
    PricingRuleORM
)
target_metadata = Base.metadata

# Get DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in .env")

# --- Offline vs Online Mode ---
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
