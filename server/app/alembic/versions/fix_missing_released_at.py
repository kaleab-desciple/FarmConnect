"""fix missing released_at

Revision ID: fix_released_at
Revises: dae300f4c591
Create Date: 2026-01-30 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_released_at'
down_revision: Union[str, Sequence[str], None] = 'dae300f4c591'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column exists to be safe
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='escrows' AND column_name='released_at'"))
    if not result.scalar():
        op.add_column('escrows', sa.Column('released_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('escrows', 'released_at')
