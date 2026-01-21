"""add released_at to escrows

Revision ID: 24230ea0162c
Revises: 3b09d0771e20
Create Date: 2026-01-20 00:00:28.935242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24230ea0162c'
down_revision: Union[str, Sequence[str], None] = '3b09d0771e20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

## Manually changed the above
##def upgrade() -> None:
#    op.add_column('escrows', sa.Column('released_at', sa.DateTime(timezone=True), nullable=True))

#def downgrade() -> None:
#    op.drop_column('escrows', 'released_at')
