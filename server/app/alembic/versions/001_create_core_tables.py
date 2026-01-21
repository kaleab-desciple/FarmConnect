"""Create core tables

Revision ID: 001_create_core_tables
Revises:
Create Date: 2026-01-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql
from shared_models.enums import UserRole
from shared_models.enums import OrderStatus
from shared_models.enums import EscrowState
from shared_models.enums import LoanState
from shared_models.enums import DisputeState
from shared_models.product import Category, Unit, QualityGrade
from shared_models.escrow import Provider

# revision identifiers, used by Alembic.
revision = '001_create_core_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing enums if they exist (for re-runs)
    op.execute("DROP TYPE IF EXISTS user_role_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS category_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS unit_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS quality_grade_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS order_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS escrow_state_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS provider_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS loan_state_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS dispute_state_enum CASCADE")

    # Users table
    op.create_table(
        "users",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("role", sa.Enum(*[r.value for r in UserRole], name="user_role_enum"), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True, unique=True),
        sa.Column("phone", sa.String(), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("metadata", psql.JSONB(), nullable=True)
    )

    # Products table
    op.create_table(
        "products",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("farmer_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("category", sa.Enum(*[c.value for c in Category], name="category_enum"), nullable=True),
        sa.Column("unit", sa.Enum(*[u.value for u in Unit], name="unit_enum"), nullable=True),
        sa.Column("base_price", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default=sa.text("'USD'")),
        sa.Column("quantity_available", sa.Float(), nullable=True),
        sa.Column("quality_grade", sa.Enum(*[q.value for q in QualityGrade], name="quality_grade_enum"), nullable=True),
        sa.Column("harvest_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("location", psql.JSONB(), nullable=True),
        sa.Column("images", psql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("metadata", psql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    )

    # Orders table
    op.create_table(
        "orders",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("farmer_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit_price", sa.Float(), nullable=True),
        sa.Column("delivery_cost", sa.Float(), nullable=True),
        sa.Column("platform_fee", sa.Float(), nullable=True),
        sa.Column("total_price", sa.Float(), nullable=True),
        sa.Column("status", sa.Enum(*[s.value for s in OrderStatus], name="order_status_enum"), nullable=True),
        sa.Column("escrow_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()"))
    )

    # Escrows table
    op.create_table(
        "escrows",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("state", sa.Enum(*[s.value for s in EscrowState], name="escrow_state_enum"), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("penalty_applied", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("provider", sa.Enum(*[p.value for p in Provider], name="provider_enum"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()"))
    )

    # Loans table
    op.create_table(
        "loans",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("farmer_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("principal", sa.Float(), nullable=True),
        sa.Column("interest_rate", sa.Float(), nullable=True),
        sa.Column("state", sa.Enum(*[s.value for s in LoanState], name="loan_state_enum"), nullable=True),
        sa.Column("auto_approved", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("repayment_schedule", psql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True)
    )

    # Disputes table
    op.create_table(
        "disputes",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("escrow_id", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("raised_by", psql.UUID(as_uuid=True), nullable=True),
        sa.Column("state", sa.Enum(*[s.value for s in DisputeState], name="dispute_state_enum"), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("resolution", sa.String(), nullable=True),
        sa.Column("evidence_urls", psql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_table("disputes")
    op.drop_table("loans")
    op.drop_table("escrows")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS user_role_enum")
    op.execute("DROP TYPE IF EXISTS category_enum")
    op.execute("DROP TYPE IF EXISTS unit_enum")
    op.execute("DROP TYPE IF EXISTS quality_grade_enum")
    op.execute("DROP TYPE IF EXISTS order_status_enum")
    op.execute("DROP TYPE IF EXISTS escrow_state_enum")
    op.execute("DROP TYPE IF EXISTS provider_enum")
    op.execute("DROP TYPE IF EXISTS loan_state_enum")
    op.execute("DROP TYPE IF EXISTS dispute_state_enum")