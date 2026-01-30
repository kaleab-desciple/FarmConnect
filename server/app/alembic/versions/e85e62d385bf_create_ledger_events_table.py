"""create_ledger_events_table

Revision ID: e85e62d385bf
Revises: 3af3718a76c8
Create Date: 2026-01-20 02:38:15.043244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e85e62d385bf'
down_revision: Union[str, Sequence[str], None] = '3af3718a76c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enums idempotently
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'aggregate_type_enum') THEN
                CREATE TYPE aggregate_type_enum AS ENUM ('USER', 'ESCROW', 'SYSTEM');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ledger_event_type_enum') THEN
                CREATE TYPE ledger_event_type_enum AS ENUM ('ESCROW_FUNDED', 'ESCROW_RELEASED', 'ESCROW_REFUNDED', 'PLATFORM_FEE_COLLECTED', 'PENALTY_APPLIED', 'LOAN_DISBURSED', 'LOAN_REPAID');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'direction_enum') THEN
                CREATE TYPE direction_enum AS ENUM ('DEBIT', 'CREDIT');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reference_type_enum') THEN
                CREATE TYPE reference_type_enum AS ENUM ('ORDER', 'ESCROW', 'DISPUTE', 'LOAN');
            END IF;
        END $$;
    """)

    # Create table idempotently
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'ledger_events'):
        op.create_table(
            'ledger_events',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('aggregate_type', postgresql.ENUM('USER', 'ESCROW', 'SYSTEM', name='aggregate_type_enum', create_type=False), nullable=False),
            sa.Column('aggregate_id', sa.String(), nullable=False),
            sa.Column('event_type', postgresql.ENUM('ESCROW_FUNDED', 'ESCROW_RELEASED', 'ESCROW_REFUNDED', 'PLATFORM_FEE_COLLECTED', 'PENALTY_APPLIED', 'LOAN_DISBURSED', 'LOAN_REPAID', name='ledger_event_type_enum', create_type=False), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('currency', sa.String(), nullable=False, default="ETB"),
            sa.Column('direction', postgresql.ENUM('DEBIT', 'CREDIT', name='direction_enum', create_type=False), nullable=False),
            sa.Column('reference_type', postgresql.ENUM('ORDER', 'ESCROW', 'DISPUTE', 'LOAN', name='reference_type_enum', create_type=False), nullable=False),
            sa.Column('reference_id', sa.String(), nullable=False),
            sa.Column('event_metadata', sa.dialects.postgresql.JSONB(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('ledger_events')
    op.execute("DROP TYPE IF EXISTS reference_type_enum;")
    op.execute("DROP TYPE IF EXISTS direction_enum;")
    op.execute("DROP TYPE IF EXISTS ledger_event_type_enum;")
    op.execute("DROP TYPE IF EXISTS aggregate_type_enum;")
