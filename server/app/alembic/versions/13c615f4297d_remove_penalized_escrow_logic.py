"""remove_penalized_escrow_logic

Revision ID: 13c615f4297d
Revises: fix_released_at
Create Date: 2026-01-30 16:27:22.193601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13c615f4297d'
down_revision: Union[str, Sequence[str], None] = 'fix_released_at'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove penalty_applied from escrows
    op.drop_column('escrows', 'penalty_applied')
    # Remove penalties_total from reputations
    op.drop_column('reputations', 'penalties_total')


def downgrade() -> None:
    # Add penalties_total to reputations
    op.add_column('reputations', sa.Column('penalties_total', sa.Float(), server_default='0.0', nullable=False))
    # Add penalty_applied to escrows
    op.add_column('escrows', sa.Column('penalty_applied', sa.Boolean(), server_default='false', nullable=False))
