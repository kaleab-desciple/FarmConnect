"""merge multiple heads

Revision ID: 5959689b4bca
Revises: a5ffc813a31d, add_pricing_fields
Create Date: 2026-01-25 02:54:29.815338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5959689b4bca'
down_revision: Union[str, Sequence[str], None] = ('a5ffc813a31d', 'add_pricing_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
