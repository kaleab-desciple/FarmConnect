"""Add harvest management and update products

Revision ID: harvest_mgmt_v1
Revises: weather_indexes
Create Date: 2026-02-17 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

# revision identifiers, used by Alembic.
revision = 'harvest_mgmt_v1'
down_revision = 'weather_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add 'PARTIALLY_HARVESTED' to crop_cycle_status enum
    # Note: ALTER TYPE ... ADD VALUE cannot be run in a transaction block in some Postgres versions
    # but Alembic usually handles it or we can use op.execute with autocommit if needed.
    # For PostgreSQL 12+, it's fine.
    op.execute("ALTER TYPE crop_cycle_status ADD VALUE IF NOT EXISTS 'PARTIALLY_HARVESTED'")

    # 2. Create harvests table
    op.create_table(
        'harvests',
        sa.Column('id', psql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('farmer_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('crop_cycle_id', psql.UUID(as_uuid=False), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('field_id', psql.UUID(as_uuid=False), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('harvest_date', sa.Date(), nullable=False),
        sa.Column('quantity_harvested', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('unit', psql.ENUM('KG', 'TON', 'LITER', 'UNIT', 'CRATE', 'BAG', name='unit_enum', create_type=False), nullable=True),
        sa.Column('quality_grade', psql.ENUM('GRADE_A', 'GRADE_B', 'GRADE_C', 'PREMIUM', 'STANDARD', 'A', 'B', 'C', name='quality_grade_enum', create_type=False), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', psql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # 3. Update products table
    op.add_column('products', sa.Column('harvest_id', psql.UUID(as_uuid=False), sa.ForeignKey('harvests.id', ondelete='SET NULL'), nullable=True))
    op.add_column('products', sa.Column('crop_cycle_id', psql.UUID(as_uuid=False), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL'), nullable=True))

    # 4. Add indexes
    op.create_index('idx_harvests_farmer_id', 'harvests', ['farmer_id'])
    op.create_index('idx_harvests_crop_cycle_id', 'harvests', ['crop_cycle_id'])
    op.create_index('idx_harvests_field_id', 'harvests', ['field_id'])
    op.create_index('idx_products_harvest_id', 'products', ['harvest_id'])


def downgrade():
    op.drop_index('idx_products_harvest_id', table_name='products')
    op.drop_column('products', 'crop_cycle_id')
    op.drop_column('products', 'harvest_id')
    
    op.drop_index('idx_harvests_field_id', table_name='harvests')
    op.drop_index('idx_harvests_crop_cycle_id', table_name='harvests')
    op.drop_index('idx_harvests_farmer_id', table_name='harvests')
    op.drop_table('harvests')
    
    # Note: Removing a value from an ENUM is complex in Postgres and often not done in migrations
    # as it requires dropping and re-creating the type if it's being used.
    # We'll leave the enum value 'PARTIALLY_HARVESTED' as it doesn't hurt.
