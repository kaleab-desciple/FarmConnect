"""add accounting tables

Revision ID: 835594adc649
Revises: add_pricing_rules
Create Date: 2026-01-21 14:22:53.312519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '835594adc649'
down_revision: Union[str, Sequence[str], None] = 'add_pricing_rules'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums for Ledger and Accounting idempotently
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'aggregate_type_enum') THEN
                CREATE TYPE aggregate_type_enum AS ENUM ('USER', 'ESCROW', 'SYSTEM');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ledger_event_type_enum') THEN
                CREATE TYPE ledger_event_type_enum AS ENUM ('ESCROW_FUNDED', 'ESCROW_RELEASED', 'ESCROW_REFUNDED', 'PLATFORM_FEE_COLLECTED', 'PENALTY_APPLIED', 'LOAN_DISBURSED', 'LOAN_REPAID');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'direction_enum') THEN
                CREATE TYPE direction_enum AS ENUM ('DEBIT', 'CREDIT');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reference_type_enum') THEN
                CREATE TYPE reference_type_enum AS ENUM ('ORDER', 'ESCROW', 'DISPUTE', 'LOAN');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'owner_type_enum') THEN
                CREATE TYPE owner_type_enum AS ENUM ('USER', 'ESCROW', 'SYSTEM');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'account_type_enum') THEN
                CREATE TYPE account_type_enum AS ENUM ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE');
            END IF;
        END $$;
    """)

    # 2. Create Ledger Events Table
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'ledger_events'):
        op.create_table(
            'ledger_events',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('aggregate_type', postgresql.ENUM('USER', 'ESCROW', 'SYSTEM', name='aggregate_type_enum', create_type=False), nullable=False),
            sa.Column('aggregate_id', sa.String(), nullable=False),
            sa.Column('event_type', postgresql.ENUM('ESCROW_FUNDED', 'ESCROW_RELEASED', 'ESCROW_REFUNDED', 'PLATFORM_FEE_COLLECTED', 'PENALTY_APPLIED', 'LOAN_DISBURSED', 'LOAN_REPAID', name='ledger_event_type_enum', create_type=False), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('currency', sa.String(), nullable=False, server_default="ETB"),
            sa.Column('direction', postgresql.ENUM('DEBIT', 'CREDIT', name='direction_enum', create_type=False), nullable=False),
            sa.Column('reference_type', postgresql.ENUM('ORDER', 'ESCROW', 'DISPUTE', 'LOAN', name='reference_type_enum', create_type=False), nullable=False),
            sa.Column('reference_id', sa.String(), nullable=False),
            sa.Column('event_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
        )

    # 3. Create Accounting Tables (Accounts, Journal Entries, Journal Lines)
    if not conn.dialect.has_table(conn, 'accounts'):
        op.create_table(
            'accounts',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('owner_type', postgresql.ENUM('USER', 'ESCROW', 'SYSTEM', name='owner_type_enum', create_type=False), nullable=False),
            sa.Column('owner_id', sa.String(), nullable=False),
            sa.Column('account_type', postgresql.ENUM('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE', name='account_type_enum', create_type=False), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('currency', sa.String(), nullable=False, server_default="ETB"),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
        )

    if not conn.dialect.has_table(conn, 'journal_entries'):
        op.create_table(
            'journal_entries',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('reference_type', sa.String(), nullable=False),
            sa.Column('reference_id', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
        )

    if not conn.dialect.has_table(conn, 'journal_lines'):
        op.create_table(
            'journal_lines',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('journal_entry_id', sa.String(), sa.ForeignKey('journal_entries.id'), nullable=False),
            sa.Column('account_id', sa.String(), sa.ForeignKey('accounts.id'), nullable=False),
            sa.Column('debit_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
            sa.Column('credit_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0')
        )


def downgrade() -> None:
    # 1. Drop Accounting and Ledger Tables
    op.drop_table('journal_lines')
    op.drop_table('journal_entries')
    op.drop_table('accounts')
    op.drop_table('ledger_events')

    # 2. Drop Enums
    op.execute("DROP TYPE IF EXISTS account_type_enum;")
    op.execute("DROP TYPE IF EXISTS owner_type_enum;")
    op.execute("DROP TYPE IF EXISTS reference_type_enum;")
    op.execute("DROP TYPE IF EXISTS direction_enum;")
    op.execute("DROP TYPE IF EXISTS ledger_event_type_enum;")
    op.execute("DROP TYPE IF EXISTS aggregate_type_enum;")
