"""add keycloak_id to users

Revision ID: dae300f4c591
Revises: 835594adc649
Create Date: 2026-01-25 02:54:39.401611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dae300f4c591'
down_revision: Union[str, Sequence[str], None] = '835594adc649'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('keycloak_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_keycloak_id', 'users', ['keycloak_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_keycloak_id', 'users', type_='unique')
    op.drop_column('users', 'keycloak_id')
