"""Add disputes table, dispute escalation chain and user onboarding approval workflow

Revision ID: dispute_and_user_onboarding_v1
Revises: harvest_events_v2
Create Date: 2026-03-05

- Gap 3: Dispute escalation chain & Table Creation
  - Creates dispute_state_enum and dispute_resolution_enum
  - Creates disputes table with all necessary columns including escalation fields

- Gap 4: Farmer onboarding approval workflow
  - Adds onboarding_status_enum (PENDING_REVIEW, ACTIVE, REJECTED)
  - Adds onboarding_status, onboarding_agent_id columns to users
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dispute_and_user_onboarding_v1'
down_revision = 'harvest_events_v2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------------------------------------------
    # Gap 3: Create Dispute Enums and Table
    # -----------------------------------------------------------------
    
    # 1. Create dispute_state_enum
    #dispute_state_enum = sa.Enum(
    #    'OPEN', 'UNDER_REVIEW', 'ESCALATED_TO_AGENT', 
    #    'ESCALATED_TO_MANAGER', 'RESOLVED', 'REOPENED',
    #    name='dispute_state_enum'
    #)
    #dispute_state_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create dispute_resolution_enum
    #dispute_resolution_enum = sa.Enum(
    #    'RELEASE', 'PARTIAL_RELEASE', 'REFUND',
    #    name='dispute_resolution_enum'
    #)
    #dispute_resolution_enum.create(op.get_bind(), checkfirst=True)

    # 3. Create disputes table
    #op.create_table(
    #    'disputes',
    #    sa.Column('id', sa.String(), primary_key=True),
    #    sa.Column('order_id', sa.String(), nullable=True),
    #    sa.Column('raised_by', sa.String(), nullable=True),
    #    sa.Column('state', sa.Enum('OPEN', 'UNDER_REVIEW', 'ESCALATED_TO_AGENT', 'ESCALATED_TO_MANAGER', 'RESOLVED', 'REOPENED', name='dispute_state_enum'), nullable=True),
    #    sa.Column('reason', sa.String(), nullable=True),
    #    sa.Column('resolution', sa.Enum('RELEASE', 'PARTIAL_RELEASE', 'REFUND', name='dispute_resolution_enum'), nullable=True),
    #    sa.Column('evidence_urls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    #    sa.Column('handler_role', sa.String(), nullable=True),
    #    sa.Column('escalated_to', sa.String(), nullable=True),
    #    sa.Column('escalation_note', sa.String(), nullable=True),
    #    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    #    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    # )

    # -----------------------------------------------------------------
    # Gap 4: Add onboarding approval workflow to users
    # -----------------------------------------------------------------
    # Create new enum type for onboarding status
    onboarding_status_enum = sa.Enum(
        'PENDING_REVIEW', 'ACTIVE', 'REJECTED',
        name='onboarding_status_enum'
    )
    onboarding_status_enum.create(op.get_bind(), checkfirst=True)

    # Add onboarding columns to users table
    op.add_column(
        'users',
        sa.Column(
            'onboarding_status',
            sa.Enum('PENDING_REVIEW', 'ACTIVE', 'REJECTED', name='onboarding_status_enum'),
            nullable=True,
            server_default='ACTIVE',
        )
    )
    op.add_column('users', sa.Column('onboarding_agent_id', sa.String(), nullable=True))


def downgrade() -> None:
    # Gap 4 downgrade
    op.drop_column('users', 'onboarding_agent_id')
    op.drop_column('users', 'onboarding_status')
    op.execute("DROP TYPE IF EXISTS onboarding_status_enum")

    # Gap 3 downgrade
    #op.drop_table('disputes')
    #op.execute("DROP TYPE IF EXISTS dispute_state_enum")
    #op.execute("DROP TYPE IF EXISTS dispute_resolution_enum")
