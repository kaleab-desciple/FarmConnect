"""add_disputed_refunded_to_escrow_state_enum

Revision ID: bff45b55299b
Revises: c3c0d16b89a2
Create Date: 2026-01-20 00:40:42.580369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bff45b55299b'
down_revision: Union[str, Sequence[str], None] = 'c3c0d16b89a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use DO blocks to make adding enum values and creating types idempotent
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = 'escrow_state_enum' AND e.enumlabel = 'DISPUTED') THEN
                ALTER TYPE escrow_state_enum ADD VALUE 'DISPUTED';
            END IF;
        END
        $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = 'escrow_state_enum' AND e.enumlabel = 'REFUNDED') THEN
                ALTER TYPE escrow_state_enum ADD VALUE 'REFUNDED';
            END IF;
        END
        $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'dispute_resolution_enum') THEN
                CREATE TYPE dispute_resolution_enum AS ENUM ('RELEASE', 'PARTIAL_RELEASE', 'REFUND');
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL doesn't support removing enum values or types easily
    pass
