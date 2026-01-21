"""add accounting tables

Revision ID: 835594adc649
Revises: e85e62d385bf
Create Date: 2026-01-21 14:22:53.312519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '835594adc649'
down_revision: Union[str, Sequence[str], None] = 'e85e62d385bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enums idempotently
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'owner_type_enum') THEN
                CREATE TYPE owner_type_enum AS ENUM ('USER', 'ESCROW', 'SYSTEM');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'account_type_enum') THEN
                CREATE TYPE account_type_enum AS ENUM ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE');
            END IF;
        END $$;
    """)

    # Create accounts table
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'accounts'):
        op.create_table(
            'accounts',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('owner_type', sa.Enum('USER', 'ESCROW', 'SYSTEM', name='owner_type_enum'), nullable=False),
            sa.Column('owner_id', sa.String(), nullable=False),
            sa.Column('account_type', sa.Enum('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE', name='account_type_enum'), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('currency', sa.String(), nullable=False, default="ETB"),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
        )

    # Create journal_entries table
    if not conn.dialect.has_table(conn, 'journal_entries'):
        op.create_table(
            'journal_entries',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('reference_type', sa.String(), nullable=False),
            sa.Column('reference_id', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
        )

    # Create journal_lines table
    if not conn.dialect.has_table(conn, 'journal_lines'):
        op.create_table(
            'journal_lines',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('journal_entry_id', sa.String(), sa.ForeignKey('journal_entries.id'), nullable=False),
            sa.Column('account_id', sa.String(), sa.ForeignKey('accounts.id'), nullable=False),
            sa.Column('debit_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
            sa.Column('credit_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0)
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('journal_lines')
    op.drop_table('journal_entries')
    op.drop_table('accounts')
    op.execute("DROP TYPE IF EXISTS account_type_enum;")
    op.execute("DROP TYPE IF EXISTS owner_type_enum;")
