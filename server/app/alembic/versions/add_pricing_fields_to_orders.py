"""add pricing fields to orders

Revision ID: add_pricing_fields
Revises: add_pricing_rules
Create Date: 2026-01-22 21:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_pricing_fields'
down_revision: Union[str, None] = 'add_pricing_rules'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('subtotal', sa.Float(), nullable=True))
    op.add_column('orders', sa.Column('delivery_fee', sa.Float(), nullable=True))
    op.add_column('orders', sa.Column('delivery_margin', sa.Float(), nullable=True))
    op.add_column('orders', sa.Column('quality_fee', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'subtotal')
    op.drop_column('orders', 'delivery_fee')
    op.drop_column('orders', 'delivery_margin')
    op.drop_column('orders', 'quality_fee')