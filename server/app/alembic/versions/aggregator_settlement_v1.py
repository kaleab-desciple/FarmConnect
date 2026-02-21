"""aggregator_reconciliation_settlement - Aggregator, reconciliation and split settlement

Revision ID: aggregator_settlement_v1
Revises: harvest_events_v2
Create Date: 2026-02-21 12:00:00.000000

This migration implements:
1. Add new enums for aggregator and settlement
2. Create aggregators table
3. Create acceptance_weighments table
4. Create reconciliation_records table
5. Create settlement_rules table
6. Create aggregator_settlement_summaries table
7. Create split_settlements table
8. Add aggregator_id to harvest_batches if not present

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'aggregator_settlement_v1'
down_revision: Union[str, Sequence[str], None] = 'harvest_events_v2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to support aggregator reconciliation and split settlement."""
    
    # ========================================
    # Step 1: Create new enum types
    # ========================================
    
    # Aggregator KYC status enum
    #op.execute("""
    #    CREATE TYPE aggregator_kyc_status_enum AS ENUM (
    #        'PENDING',
    #        'VERIFIED',
    #        'REJECTED'
    #    )
    #""")
    
    # Split method enum
    #op.execute("""
    #    CREATE TYPE split_method_enum AS ENUM (
    #        'BY_WEIGHT',
    #        'BY_VALUE',
    #        'FIXED_RATE'
    #    )
    #""")
    
    # Settlement status enum
    #op.execute("""
    #    CREATE TYPE settlement_status_enum AS ENUM (
    #        'PENDING',
    #        'PREPARED',
    #        'PAYMENT_SENT',
    #        'PAID',
    #        'FAILED',
    #        'ADJUSTED'
    #    )
    #""")
    
    # Settlement summary status enum
    #op.execute("""
    #    CREATE TYPE settlement_summary_status_enum AS ENUM (
    #        'PENDING',
    #        'IN_PROGRESS',
    #        'PAID',
    #        'FAILED'
    #    )
    #""")
    
    # Reconciliation status enum
    #op.execute("""
    #    CREATE TYPE recon_status_enum AS ENUM (
    #        'OK',
    #        'WARNING',
    #        'DISPUTE'
    #    )
    #""")
    
    # Batch settlement state enum
    op.execute("""
        CREATE TYPE batch_settlement_state_enum AS ENUM (
            'DRAFT',
            'SEALED',
            'LISTED',
            'SOLD',
            'SETTLEMENT_PENDING',
            'SETTLEMENT_IN_PROGRESS',
            'SETTLED',
            'SETTLEMENT_DISPUTE',
            'RECONCILED',
            'ARCHIVED'
        )
    """)
    
    # ========================================
    # Step 2: Create aggregators table
    # ========================================
    op.create_table(
        'aggregators',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('company_info', JSONB, nullable=True),
        sa.Column('contact', JSONB, nullable=True),
        sa.Column('kyc_status', sa.Enum('PENDING', 'VERIFIED', 'REJECTED', name='aggregator_kyc_status_enum'), nullable=False, server_default='PENDING'),
        sa.Column('wallet_id', sa.String(), nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_aggregators_kyc_status', 'aggregators', ['kyc_status'])
    
    # ========================================
    # Step 3: Create acceptance_weighments table
    # ========================================
    op.create_table(
        'acceptance_weighments',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('batch_id', sa.String(), sa.ForeignKey('harvest_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('weighbridge_id', sa.String(100), nullable=True),
        sa.Column('gross_weight_kg', sa.Float(), nullable=False),
        sa.Column('tare_weight_kg', sa.Float(), nullable=False),
        sa.Column('net_weight_kg', sa.Float(), nullable=False),
        sa.Column('receipt_url', sa.Text(), nullable=True),
        sa.Column('weigher_id', sa.String(), nullable=True),
        sa.Column('location', JSONB, nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_weighments_batch_id', 'acceptance_weighments', ['batch_id'])
    
    # ========================================
    # Step 4: Create reconciliation_records table
    # ========================================
    op.create_table(
        'reconciliation_records',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('batch_id', sa.String(), sa.ForeignKey('harvest_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expected_total_kg', sa.Float(), nullable=False),
        sa.Column('measured_total_kg', sa.Float(), nullable=False),
        sa.Column('difference_kg', sa.Float(), nullable=False),
        sa.Column('variance_pct', sa.Float(), nullable=False),
        sa.Column('recon_status', sa.Enum('OK', 'WARNING', 'DISPUTE', name='recon_status_enum'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_recon_batch_id', 'reconciliation_records', ['batch_id'])
    
    # ========================================
    # Step 5: Create settlement_rules table
    # ========================================
    op.create_table(
        'settlement_rules',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('aggregator_id', sa.String(), sa.ForeignKey('aggregators.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('split_method', sa.Enum('BY_WEIGHT', 'BY_VALUE', 'FIXED_RATE', name='split_method_enum'), nullable=False),
        sa.Column('platform_fee_pct', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('aggregator_commission_pct', sa.Float(), nullable=False, server_default='10.0'),
        sa.Column('min_payout_threshold', sa.Float(), nullable=False, server_default='10.0'),
        sa.Column('rounding_policy', JSONB, nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_settlement_rules_aggregator', 'settlement_rules', ['aggregator_id'])
    
    # ========================================
    # Step 6: Create aggregator_settlement_summaries table
    # ========================================
    op.create_table(
        'aggregator_settlement_summaries',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('batch_id', sa.String(), sa.ForeignKey('harvest_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('aggregator_id', sa.String(), sa.ForeignKey('aggregators.id', ondelete='SET NULL'), nullable=True),
        sa.Column('gross_sale_amount', sa.Float(), nullable=False),
        sa.Column('total_platform_fee', sa.Float(), nullable=False),
        sa.Column('total_commission', sa.Float(), nullable=False),
        sa.Column('net_to_distribute', sa.Float(), nullable=False),
        sa.Column('rounding_adjustment', sa.Float(), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'PAID', 'FAILED', name='settlement_summary_status_enum'), nullable=False, server_default='PENDING'),
        sa.Column('settlement_rule_id', sa.String(), sa.ForeignKey('settlement_rules.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_settlement_summary_batch', 'aggregator_settlement_summaries', ['batch_id'])
    op.create_index('idx_settlement_summary_aggregator', 'aggregator_settlement_summaries', ['aggregator_id'])
    
    # ========================================
    # Step 7: Create split_settlements table
    # ========================================
    op.create_table(
        'split_settlements',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('settlement_summary_id', sa.String(), sa.ForeignKey('aggregator_settlement_summaries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contribution_id', sa.String(), nullable=False),  # FK to harvest_batch_contributions
        sa.Column('farmer_id', sa.String(), nullable=False),
        sa.Column('contributed_weight_kg', sa.Float(), nullable=False),
        sa.Column('share_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('status', sa.Enum('PENDING', 'PREPARED', 'PAYMENT_SENT', 'PAID', 'FAILED', 'ADJUSTED', name='settlement_status_enum'), nullable=False, server_default='PENDING'),
        sa.Column('payout_reference', sa.Text(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_split_settlement_summary', 'split_settlements', ['settlement_summary_id'])
    op.create_index('idx_split_settlement_farmer', 'split_settlements', ['farmer_id'])
    op.create_index('idx_split_settlement_contribution', 'split_settlements', ['contribution_id'])
    
    # ========================================
    # Step 8: Add aggregator_id to harvest_batches if not exists
    # ========================================
    # Check if column already exists using SQL
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'harvest_batches' AND column_name = 'aggregator_id'
    """))
    if result.fetchone() is None:
        op.add_column('harvest_batches', sa.Column('aggregator_id', sa.String(), sa.ForeignKey('aggregators.id', ondelete='SET NULL'), nullable=True))
    
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'harvest_batches' AND column_name = 'settlement_state'
    """))
    if result.fetchone() is None:
        op.add_column('harvest_batches', sa.Column('settlement_state', sa.Enum('DRAFT', 'SEALED', 'LISTED', 'SOLD', 'SETTLEMENT_PENDING', 'SETTLEMENT_IN_PROGRESS', 'SETTLED', 'SETTLEMENT_DISPUTE', 'RECONCILED', 'ARCHIVED', name='batch_settlement_state_enum'), nullable=True))
    
    # Add indexes (check if exists)
    result = conn.execute(sa.text("""
        SELECT indexname FROM pg_indexes WHERE indexname = 'idx_harvest_batches_aggregator'
    """))
    if result.fetchone() is None:
        op.create_index('idx_harvest_batches_aggregator', 'harvest_batches', ['aggregator_id'])


def downgrade() -> None:
    """Downgrade schema - remove aggregator settlement features."""
    
    conn = op.get_bind()
    
    # Drop indexes (check if exists)
    indexes_to_check = [
        'idx_harvest_batches_aggregator',
        'idx_split_settlement_contribution',
        'idx_split_settlement_farmer',
        'idx_split_settlement_summary',
        'idx_settlement_summary_aggregator',
        'idx_settlement_summary_batch',
        'idx_settlement_rules_aggregator',
        'idx_recon_batch_id',
        'idx_weighments_batch_id',
        'idx_aggregators_kyc_status'
    ]
    
    for idx_name in indexes_to_check:
        result = conn.execute(sa.text(f"""
            SELECT indexname FROM pg_indexes WHERE indexname = '{idx_name}'
        """))
        if result.fetchone() is not None:
            if idx_name == 'idx_harvest_batches_aggregator':
                op.drop_index(idx_name, table_name='harvest_batches')
            elif idx_name.startswith('idx_split_settlement'):
                op.drop_index(idx_name, table_name='split_settlements')
            elif idx_name.startswith('idx_settlement_summary'):
                op.drop_index(idx_name, table_name='aggregator_settlement_summaries')
            elif idx_name == 'idx_settlement_rules_aggregator':
                op.drop_index(idx_name, table_name='settlement_rules')
            elif idx_name == 'idx_recon_batch_id':
                op.drop_index(idx_name, table_name='reconciliation_records')
            elif idx_name == 'idx_weighments_batch_id':
                op.drop_index(idx_name, table_name='acceptance_weighments')
            elif idx_name == 'idx_aggregators_kyc_status':
                op.drop_index(idx_name, table_name='aggregators')
    
    # Drop tables
    op.drop_table('split_settlements')
    op.drop_table('aggregator_settlement_summaries')
    op.drop_table('settlement_rules')
    op.drop_table('reconciliation_records')
    op.drop_table('acceptance_weighments')
    op.drop_table('aggregators')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS batch_settlement_state_enum")
    op.execute("DROP TYPE IF EXISTS recon_status_enum")
    op.execute("DROP TYPE IF EXISTS settlement_summary_status_enum")
    op.execute("DROP TYPE IF EXISTS settlement_status_enum")
    op.execute("DROP TYPE IF EXISTS split_method_enum")
    op.execute("DROP TYPE IF EXISTS aggregator_kyc_status_enum")
