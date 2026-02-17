"""enforce_product_not_null_constraints

Revision ID: 5b1a6834b62d
Revises: 5c3bb23bb69d
Create Date: 2026-02-17 10:28:11.350585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b1a6834b62d'
down_revision: Union[str, Sequence[str], None] = '5c3bb23bb69d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Step 2: Enforce NOT NULL constraints."""
    # 1. Update existing nulls or 0.0 values (exclusiveMinimum: 0 is enforced by DTOs)
    op.execute("UPDATE products SET category = 'OTHER' WHERE category IS NULL")
    op.execute("UPDATE products SET base_price = 0.01 WHERE base_price IS NULL OR base_price <= 0")
    
    # 2. Alter columns to NOT NULL
    op.alter_column('products', 'category',
               existing_type=sa.Enum('GRAINS', 'VEGETABLES', 'FRUITS', 'DAIRY', 'MEAT', 'SPICES', 'OTHER', name='category_enum'),
               nullable=False)
    op.alter_column('products', 'base_price',
               existing_type=sa.Float(),
               nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('products', 'base_price',
               existing_type=sa.Float(),
               nullable=True)
    op.alter_column('products', 'category',
               existing_type=sa.Enum('GRAINS', 'VEGETABLES', 'FRUITS', 'DAIRY', 'MEAT', 'SPICES', 'OTHER', name='category_enum'),
               nullable=True)
