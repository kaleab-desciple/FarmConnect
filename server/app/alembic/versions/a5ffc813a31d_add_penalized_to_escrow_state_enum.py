"""add_penalized_to_escrow_state_enum

Revision ID: a5ffc813a31d
Revises: 835594adc649
Create Date: 2026-01-22 03:33:31.895898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5ffc813a31d'
down_revision: Union[str, Sequence[str], None] = '835594adc649'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DO $$ BEGIN ALTER TYPE escrow_state_enum ADD VALUE 'PENALIZED'; EXCEPTION WHEN duplicate_object THEN null; END $$;")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL doesn't support removing enum values, so we can't downgrade
    pass
