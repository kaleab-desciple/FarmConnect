"""update_disputes_table_order_id_and_resolution

Revision ID: 6151d725bb5e
Revises: bff45b55299b
Create Date: 2026-01-20 00:41:38.379616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6151d725bb5e'
down_revision: Union[str, Sequence[str], None] = 'bff45b55299b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename escrow_id to order_id
    op.alter_column('disputes', 'escrow_id', new_column_name='order_id')
    # Change resolution from string to enum
    op.execute("ALTER TABLE disputes ALTER COLUMN resolution TYPE dispute_resolution_enum USING resolution::dispute_resolution_enum;")


def downgrade() -> None:
    """Downgrade schema."""
    # Change resolution back to string
    op.alter_column('disputes', 'resolution', type_=sa.String())
    # Rename order_id back to escrow_id
    op.alter_column('disputes', 'order_id', new_column_name='escrow_id')
