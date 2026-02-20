"""Add harvest events, batches, and QC tracking

Revision ID: harvest_events_v1
Revises: inventory_mgmt_v1
Create Date: 2026-02-20 08:00:00.000000

This migration implements:
1. Create harvest_batch_state_enum (DRAFT, SEALED, QC_PENDING, QC_PASSED, QC_FAILED, ARCHIVED)
2. Create harvest_events table for field-level harvest tracking
3. Create harvest_batches table for batch aggregation with lineage hash
4. Create harvest_batch_contributions table (many-to-many)
5. Create batch_qc_reports table for lab reports
6. Add product_batch_sources join table for many-to-many product-to-harvest-batch linkage
7. Add DB trigger to enforce append-only contributions after sealing
8. Add audit_events table for traceability

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'harvest_events_v1'
down_revision: Union[str, Sequence[str], None] = 'inventory_mgmt_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to support harvest events and batch tracking."""
    
    # ========================================
    # Step 0: Ensure pgcrypto extension is enabled for gen_random_uuid()
    # ========================================
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    
    # ========================================
    # Step 1: Create harvest_batch_state_enum (idempotent)
    # ========================================

    
    # ========================================
    # Step 2: Create harvest_events table
    # ========================================
    op.create_table(
        'harvest_events',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('farm_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_id', sa.String(), nullable=False),  # Can be FK to fields.id if available
        sa.Column('crop_cycle_id', sa.String(), nullable=True),
        sa.Column('collected_by', sa.String(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('harvested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('gross_weight_kg', sa.Float(), nullable=False),
        sa.Column('moisture_pct', sa.Float(), nullable=True),
        sa.Column('loss_kg', sa.Float(), nullable=True),
        sa.Column('photos', JSONB(), nullable=True),  # List of media metadata with exif/geo
        sa.Column('weighbridge_receipt', JSONB(), nullable=True),  # Weighbridge receipt metadata
        sa.Column('location', JSONB(), nullable=True),  # GeoJSON location
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_harvest_events_farm_id', 'harvest_events', ['farm_id'])
    op.create_index('idx_harvest_events_field_id', 'harvest_events', ['field_id'])
    op.create_index('idx_harvest_events_crop_cycle_id', 'harvest_events', ['crop_cycle_id'])
    op.create_index('idx_harvest_events_harvested_at', 'harvest_events', ['harvested_at'])
    
    # ========================================
    # Step 3: Create harvest_batches table
    # ========================================
    op.create_table(
        'harvest_batches',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('batch_code', sa.String(100), nullable=False),
        sa.Column('aggregator_id', sa.String(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SEALED', 'QC_PENDING', 'QC_PASSED', 'QC_FAILED', 'ARCHIVED', 
                                   name='harvest_batch_state_enum', create_type=False), 
                 nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column('aggregated_weight_kg', sa.Float(), nullable=True),
        sa.Column('moisture_avg', sa.Float(), nullable=True),
        sa.Column('sealed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sealed_by', sa.String(), nullable=True),
        sa.Column('seal_evidence', JSONB(), nullable=True),  # References to receipts, photos, signatures
        sa.Column('lineage_hash', sa.String(200), nullable=True),  # SHA256 hex of canonical JSON
        sa.Column('lineage_signature', sa.String(500), nullable=True),  # Optional signature
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_harvest_batch_code', 'harvest_batches', ['batch_code'])
    op.create_index('idx_harvest_batches_aggregator_id', 'harvest_batches', ['aggregator_id'])
    op.create_index('idx_harvest_batches_status', 'harvest_batches', ['status'])
    
    # ========================================
    # Step 4: Create harvest_batch_contributions table
    # ========================================
    op.create_table(
        'harvest_batch_contributions',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('harvest_batch_id', sa.String(), 
                 sa.ForeignKey('harvest_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('harvest_event_id', sa.String(), 
                 sa.ForeignKey('harvest_events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('farmer_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contributed_weight_kg', sa.Float(), nullable=False),
        sa.Column('reported_moisture_pct', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    # Unique constraint to prevent duplicate contribution per event
    op.create_unique_constraint('uq_batch_event_contribution', 'harvest_batch_contributions', 
                               ['harvest_batch_id', 'harvest_event_id'])
    op.create_index('idx_contributions_batch_id', 'harvest_batch_contributions', ['harvest_batch_id'])
    op.create_index('idx_contributions_event_id', 'harvest_batch_contributions', ['harvest_event_id'])
    op.create_index('idx_contributions_farmer_id', 'harvest_batch_contributions', ['farmer_id'])
    
    # ========================================
    # Step 5: Create batch_qc_reports table
    # ========================================
    op.create_table(
        'batch_qc_reports',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('batch_id', sa.String(), 
                 sa.ForeignKey('harvest_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lab_id', sa.String(), nullable=True),  # Lab/organization ID
        sa.Column('tested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metrics', JSONB(), nullable=True),  # moisture, aflatoxin, mold, etc.
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('report_url', sa.String(500), nullable=True),  # Signed URL to report
        sa.Column('signed_hash', sa.String(200), nullable=True),  # Hash of report for verification
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_qc_reports_batch_id', 'batch_qc_reports', ['batch_id'])
    op.create_index('idx_qc_reports_lab_id', 'batch_qc_reports', ['lab_id'])
    
    # ========================================
    # Step 6: Create product_batch_sources join table
    # ========================================
    op.create_table(
        'product_batch_sources',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('product_batch_id', sa.String(), sa.ForeignKey('product_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('harvest_batch_id', sa.String(), 
                 sa.ForeignKey('harvest_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contribution_weight_kg', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_product_batch_source', 'product_batch_sources', 
                               ['product_batch_id', 'harvest_batch_id'])
    op.create_index('idx_product_batch_sources_product', 'product_batch_sources', ['product_batch_id'])
    op.create_index('idx_product_batch_sources_harvest', 'product_batch_sources', ['harvest_batch_id'])
    
    # ========================================
    # Step 7: Add harvest_batch_id to product_batches (simple FK path)
    # ========================================
    op.add_column('product_batches', sa.Column('harvest_batch_id', sa.String(), 
                                               sa.ForeignKey('harvest_batches.id', ondelete='SET NULL'), 
                                               nullable=True))
    op.create_index('idx_product_batches_harvest_batch', 'product_batches', ['harvest_batch_id'])
    
    # ========================================
    # Step 8: Create audit_events table
    # ========================================
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('event_type', sa.String(100), nullable=False),  # batch.created, batch.sealed, qc.passed, etc.
        sa.Column('entity_type', sa.String(50), nullable=False),  # harvest_batch, product_listing, etc.
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('payload', JSONB(), nullable=True),
        sa.Column('payload_hash', sa.String(200), nullable=True),  # Hash of payload for verification
        sa.Column('previous_event_hash', sa.String(200), nullable=True),  # Chain hash
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('signature', sa.String(500), nullable=True),  # Optional signature
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_audit_events_entity', 'audit_events', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_events_type', 'audit_events', ['event_type'])
    op.create_index('idx_audit_events_created', 'audit_events', ['created_at'])
    
    # ========================================
    # Step 9: Create DB trigger for append-only contributions
    # ========================================
    # Create function to prevent modifications to contributions when batch is sealed
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_sealed_batch_contribution()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Check if batch is sealed for INSERT/UPDATE
            IF TG_OP IN ('INSERT', 'UPDATE') THEN
                IF (SELECT status FROM harvest_batches WHERE id = NEW.harvest_batch_id) = 'SEALED' THEN
                    RAISE EXCEPTION 'Cannot modify contributions for a SEALED batch. Batch ID: %', NEW.harvest_batch_id;
                END IF;
            END IF;
            
            -- Check if batch is sealed for DELETE
            IF TG_OP = 'DELETE' THEN
                IF (SELECT status FROM harvest_batches WHERE id = OLD.harvest_batch_id) = 'SEALED' THEN
                    RAISE EXCEPTION 'Cannot delete contributions from a SEALED batch. Batch ID: %', OLD.harvest_batch_id;
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER trg_prevent_sealed_contribution
        BEFORE INSERT OR UPDATE OR DELETE ON harvest_batch_contributions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_sealed_batch_contribution();
    """)


def downgrade() -> None:
    """Downgrade schema - remove harvest event tracking features."""
    
    # ========================================
    # Drop triggers and functions
    # ========================================
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_sealed_contribution ON harvest_batch_contributions")
    op.execute("DROP FUNCTION IF EXISTS prevent_sealed_batch_contribution()")
    
    # ========================================
    # Drop audit_events table
    # ========================================
    op.drop_index('idx_audit_events_created', table_name='audit_events')
    op.drop_index('idx_audit_events_type', table_name='audit_events')
    op.drop_index('idx_audit_events_entity', table_name='audit_events')
    op.drop_table('audit_events')
    
    # ========================================
    # Drop product_batch_sources table
    # ========================================
    op.drop_index('idx_product_batch_sources_harvest', table_name='product_batch_sources')
    op.drop_index('idx_product_batch_sources_product', table_name='product_batch_sources')
    op.drop_constraint('uq_product_batch_source', 'product_batch_sources', type_='unique')
    op.drop_table('product_batch_sources')
    
    # ========================================
    # Remove harvest_batch_id from product_batches
    # ========================================
    op.drop_index('idx_product_batches_harvest_batch', table_name='product_batches')
    op.drop_column('product_batches', 'harvest_batch_id')
    
    # ========================================
    # Drop batch_qc_reports table
    # ========================================
    op.drop_index('idx_qc_reports_lab_id', table_name='batch_qc_reports')
    op.drop_index('idx_qc_reports_batch_id', table_name='batch_qc_reports')
    op.drop_table('batch_qc_reports')
    
    # ========================================
    # Drop harvest_batch_contributions table
    # ========================================
    op.drop_index('idx_contributions_farmer_id', table_name='harvest_batch_contributions')
    op.drop_index('idx_contributions_event_id', table_name='harvest_batch_contributions')
    op.drop_index('idx_contributions_batch_id', table_name='harvest_batch_contributions')
    op.drop_constraint('uq_batch_event_contribution', 'harvest_batch_contributions', type_='unique')
    op.drop_table('harvest_batch_contributions')
    
    # ========================================
    # Drop harvest_batches table
    # ========================================
    op.drop_index('idx_harvest_batches_status', table_name='harvest_batches')
    op.drop_index('idx_harvest_batches_aggregator_id', table_name='harvest_batches')
    op.drop_constraint('uq_harvest_batch_code', 'harvest_batches', type_='unique')
    op.drop_table('harvest_batches')
    
    # ========================================
    # Drop harvest_events table
    # ========================================
    op.drop_index('idx_harvest_events_harvested_at', table_name='harvest_events')
    op.drop_index('idx_harvest_events_crop_cycle_id', table_name='harvest_events')
    op.drop_index('idx_harvest_events_field_id', table_name='harvest_events')
    op.drop_index('idx_harvest_events_farm_id', table_name='harvest_events')
    op.drop_table('harvest_events')
    
    # ========================================
    # Drop enum type
    # ========================================
    op.execute("DROP TYPE IF EXISTS harvest_batch_state_enum")
