"""enforce_product_constraints

Revision ID: 5c3bb23bb69d
Revises: harvest_mgmt_v1
Create Date: 2026-02-17 10:13:06.917582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c3bb23bb69d'
down_revision: Union[str, Sequence[str], None] = 'harvest_mgmt_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Step 1: Add missing enum values."""
    # Note: ALTER TYPE ADD VALUE cannot run in a transaction block with other statements
    # that use the new values. 
    op.execute("ALTER TYPE category_enum ADD VALUE IF NOT EXISTS 'DAIRY'")
    op.execute("ALTER TYPE category_enum ADD VALUE IF NOT EXISTS 'MEAT'")
    op.execute("ALTER TYPE category_enum ADD VALUE IF NOT EXISTS 'SPICES'")
    op.execute("ALTER TYPE category_enum ADD VALUE IF NOT EXISTS 'OTHER'")


def downgrade() -> None:
    """Downgrade schema."""
    # Enum values cannot be easily removed in Postgres
    pass
