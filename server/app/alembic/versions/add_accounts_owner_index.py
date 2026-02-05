"""add accounts owner index

Revision ID: add_accounts_owner_index
Revises: 001_agricultural_intelligence, 835594adc649
Create Date: 2026-02-05 16:37:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_accounts_owner_index'
down_revision = ('001_agricultural_intelligence', '835594adc649')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create index on (owner_type, owner_id, account_type) for efficient account lookups
    op.create_index(
        'idx_accounts_owner_type_id_account_type',
        'accounts',
        ['owner_type', 'owner_id', 'account_type'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_accounts_owner_type_id_account_type', table_name='accounts')
