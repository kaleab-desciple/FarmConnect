"""Add deliveries table and status enum

Revision ID: add_delivery_workflow
Revises: dispute_and_user_onboarding_v1
Create Date: 2026-03-05

- Gap 6: Delivery Workflow
  - Creates delivery_status_enum
  - Creates deliveries table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_delivery_workflow'
down_revision = 'dispute_and_user_onboarding_v1'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 2. Create deliveries table
    op.create_table(
        'deliveries',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('order_id', sa.String(), nullable=False, index=True),
        sa.Column('carrier_id', sa.String(), nullable=False, index=True),
        sa.Column('status', sa.Enum('ASSIGNED', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED', 'FAILED', 'CANCELLED', name='delivery_status_enum'), nullable=False, server_default='ASSIGNED'),
        sa.Column('pickup_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pickup_photo_url', sa.String(), nullable=True),
        sa.Column('delivery_photo_url', sa.String(), nullable=True),
        sa.Column('recipient_signature_url', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('deliveries')
    op.execute("DROP TYPE IF EXISTS delivery_status_enum")
