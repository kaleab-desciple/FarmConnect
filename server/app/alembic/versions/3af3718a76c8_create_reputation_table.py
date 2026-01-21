"""create_reputation_table

Revision ID: 3af3718a76c8
Revises: 6151d725bb5e
Create Date: 2026-01-20 01:09:11.478309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3af3718a76c8'
down_revision: Union[str, Sequence[str], None] = '6151d725bb5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if table exists before creating
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'reputations'):
        op.create_table(
            'reputations',
            sa.Column('user_id', sa.String(), primary_key=True),
            sa.Column('completed_orders', sa.Integer(), default=0),
            sa.Column('successful_orders', sa.Integer(), default=0),
            sa.Column('disputes_lost', sa.Integer(), default=0),
            sa.Column('penalties_total', sa.Float(), default=0.0),
            sa.Column('avg_delivery_delay', sa.Integer(), nullable=True),
            sa.Column('reputation_score', sa.Integer(), default=50)
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('reputations')
