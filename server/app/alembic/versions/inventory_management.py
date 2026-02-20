"""inventory_management - Advanced inventory with event sourcing

Revision ID: inventory_mgmt_v1
Revises: 5b1a6834b62d
Create Date: 2026-02-19 11:00:00.000000

This migration implements:
1. Rename quantity_available → total_quantity
2. Add inventory tracking columns to products
3. Add new order status enum values
4. Create product_batches table for batch tracking
5. Create inventory_movements table for event-sourced ledger
6. Add batch tracking fields to orders

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'inventory_mgmt_v1'
down_revision: Union[str, Sequence[str], None] = '5b1a6834b62d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to support advanced inventory management."""
    
    # ========================================
    # Step 2: Add inventory tracking columns to products
    # ========================================
    op.add_column('products', sa.Column('reserved_quantity', sa.Float(), nullable=False, server_default='0'))
    op.add_column('products', sa.Column('sold_quantity', sa.Float(), nullable=False, server_default='0'))
    op.add_column('products', sa.Column('spoiled_quantity', sa.Float(), nullable=False, server_default='0'))
    op.add_column('products', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('products', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))

    # ========================================
    # Step 4: Add order tracking fields
    # ========================================
    op.add_column('orders', sa.Column('batch_id', sa.String(), sa.ForeignKey('product_batches.id'), nullable=True))
    op.add_column('orders', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('cancelled_reason', sa.String(500), nullable=True))
    op.add_column('orders', sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')))
    # ========================================
    # Step 7: Create inventory_movements table
    # ========================================
    op.create_table(
        'inventory_movements',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('product_id', sa.String(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('batch_id', sa.String(), sa.ForeignKey('product_batches.id'), nullable=True),
        sa.Column('movement_type', sa.Enum('STOCK_IN', 'RESERVATION', 'RESERVATION_RELEASE', 'SALE_CONFIRMED', 'SPOILAGE', 'RETURN', 'ADJUSTMENT', 'EXPIRY', name='inventory_movement_type_enum'), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('reference_type', sa.String(50), nullable=False),
        sa.Column('reference_id', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_inv_movements_product', 'inventory_movements', ['product_id'])
    op.create_index('idx_inv_movements_ref', 'inventory_movements', ['reference_type', 'reference_id'])


def downgrade() -> None:
    """Downgrade schema - remove inventory management features."""
    
    # ========================================
    # Drop tables
    # ========================================
    op.drop_index('idx_inv_movements_ref', table_name='inventory_movements')
    op.drop_index('idx_inv_movements_product', table_name='inventory_movements')
    op.drop_table('inventory_movements')
    
    op.drop_index('idx_batches_product', table_name='product_batches')
    op.drop_constraint('uq_product_batch_code', 'product_batches', type_='unique')    
    # ========================================
    # Drop enum type
    # ========================================
    op.execute("DROP TYPE IF EXISTS inventory_movement_type_enum")
    
    # ========================================
    # Remove order fields
    # ========================================
    op.drop_column('orders', 'updated_at')
    op.drop_column('orders', 'delivered_at')
    op.drop_column('orders', 'cancelled_reason')
    op.drop_column('orders', 'cancelled_at')
    op.drop_column('orders', 'batch_id')
    
    # ========================================
    # Remove product inventory columns
    # ========================================
    op.drop_column('products', 'version')
    op.drop_column('products', 'deleted_at')
    op.drop_column('products', 'spoiled_quantity')
    op.drop_column('products', 'sold_quantity')
    op.drop_column('products', 'reserved_quantity')
    
    # ========================================
    # Note: Cannot remove enum values in PostgreSQL
    # This is a limitation - the old enum values will remain
    # ========================================
