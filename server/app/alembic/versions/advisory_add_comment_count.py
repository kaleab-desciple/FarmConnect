"""Add comment_count to forum_threads

Revision ID: advisory_002
Revises: advisory_001
Create Date: 2024-02-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'advisory_002'
down_revision = 'advisory_001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('forum_threads', sa.Column('comment_count', sa.Integer(), server_default='0', nullable=False))


def downgrade():
    op.drop_column('forum_threads', 'comment_count')
