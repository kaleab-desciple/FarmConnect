"""add_released_to_escrow_state_enum

Revision ID: c3c0d16b89a2
Revises: 24230ea0162c
Create Date: 2026-01-20 00:30:13.354877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3c0d16b89a2'
down_revision: Union[str, Sequence[str], None] = '24230ea0162c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE escrow_state_enum ADD VALUE 'RELEASED';")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL doesn't support removing enum values, so we can't downgrade
    pass
