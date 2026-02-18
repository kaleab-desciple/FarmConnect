"""add pricing rules table

Revision ID: add_pricing_rules
Revises: c8d8a49d4019
Create Date: 2026-01-22 16:37:30.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_pricing_rules'
down_revision: Union[str, None] = '001_create_core_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    op.execute("DO $$ BEGIN CREATE TYPE rule_type_enum AS ENUM ('PLATFORM_FEE', 'DELIVERY', 'QUALITY', 'DISTANCE'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE fee_type_enum AS ENUM ('PERCENTAGE', 'FIXED'); EXCEPTION WHEN duplicate_object THEN null; END $$;")

    # Create table
    op.create_table('pricing_rules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('rule_type', postgresql.ENUM(name='rule_type_enum', create_type=False), nullable=False),
        sa.Column('product_category', sa.String(), nullable=True),
        sa.Column('quality_grade', sa.String(), nullable=True),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('min_distance_km', sa.Float(), nullable=True),
        sa.Column('max_distance_km', sa.Float(), nullable=True),
        sa.Column('fee_type', postgresql.ENUM(name='fee_type_enum', create_type=False), nullable=False),
        sa.Column('fee_value', sa.Float(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_to', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Seed example rules
    op.execute("""
    INSERT INTO pricing_rules (id, rule_type, product_category, quality_grade, region, min_distance_km, max_distance_km, fee_type, fee_value, priority, active, valid_from) VALUES
    ('rule-1', 'PLATFORM_FEE', NULL, NULL, NULL, NULL, NULL, 'PERCENTAGE', 5.0, 1, true, '2026-01-01 00:00:00+00'),
    ('rule-2', 'DELIVERY', NULL, NULL, NULL, NULL, NULL, 'FIXED', 10.0, 1, true, '2026-01-01 00:00:00+00'),
    ('rule-3', 'QUALITY', NULL, 'A', NULL, NULL, NULL, 'PERCENTAGE', 2.0, 2, true, '2026-01-01 00:00:00+00'),
    ('rule-4', 'DISTANCE', NULL, NULL, NULL, 0, 50, 'FIXED', 5.0, 1, true, '2026-01-01 00:00:00+00'),
    ('rule-5', 'DISTANCE', NULL, NULL, NULL, 50, 100, 'FIXED', 15.0, 1, true, '2026-01-01 00:00:00+00')
    """)


def downgrade() -> None:
    op.drop_table('pricing_rules')
    # Drop enums
    op.execute('DROP TYPE rule_type_enum')
    op.execute('DROP TYPE fee_type_enum')