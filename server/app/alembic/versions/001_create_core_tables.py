"""Create core tables

Revision ID: 001_create_core_tables
Revises:
Create Date: 2026-01-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql
from app.domain.common.enums import UserRole, OrderStatus, EscrowState, LoanState, DisputeState, Category, Unit, QualityGrade, Provider, InventoryMovementType, ProductStatus

# revision identifiers, used by Alembic.
revision = '001_create_core_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 0. Ensure pgcrypto extension is enabled for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    
    # 1. Create Sequences
    op.execute("CREATE SEQUENCE user_id_seq START 1")

    # 2. Drop existing enums if they exist (for re-runs)
    op.execute("DROP TYPE IF EXISTS user_role_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS category_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS unit_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS quality_grade_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS order_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS escrow_state_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS provider_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS dispute_resolution_enum CASCADE") # Added for idempotency

    # 3. Create the dispute_resolution_enum type (not created by sa.Enum in table definitions)
    op.execute("CREATE TYPE dispute_resolution_enum AS ENUM ('RELEASE', 'PARTIAL_RELEASE', 'REFUND')")

    # 4. Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("role", sa.Enum(*[r.value for r in UserRole], name="user_role_enum"), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True, unique=True),
        sa.Column("phone", sa.String(), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("metadata", psql.JSONB(), nullable=True)
    )

    
    # Insert admin user
    # op.execute("INSERT INTO users (id, name, email, created_at, keycloak_id, role) VALUES ( 'ADM-00001', 'admin admin',  'admin@gmail.com',  '2026-02-18 14:54:24+00',   'c8e54abc-9ef1-4ae2-2b85-c68fceaa98a4',  'ADMIN');")

    # 5. Products table
    op.create_table(
        "products",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("farmer_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("category", sa.Enum(*[c.value for c in Category], name="category_enum"), nullable=True),
        sa.Column("unit", sa.Enum(*[u.value for u in Unit], name="unit_enum"), nullable=True),
        sa.Column("base_price", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default=sa.text("'USD'")),
        sa.Column("total_quantity", sa.Float(), nullable=True),
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
    # ========================================
    # Step 6: Create product_batches table
    # ========================================
    op.create_table(
        'product_batches',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('product_id', sa.String(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('batch_code', sa.String(50), nullable=False),
        sa.Column('total_quantity', sa.Float(), nullable=False, server_default='0'),
        sa.Column('reserved_quantity', sa.Float(), nullable=False, server_default='0'),
        sa.Column('sold_quantity', sa.Float(), nullable=False, server_default='0'),
        sa.Column('spoiled_quantity', sa.Float(), nullable=False, server_default='0'),
        sa.Column('harvest_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('quality_grade', sa.Enum('GRADE_A', 'GRADE_B', 'GRADE_C', 'PREMIUM', 'STANDARD', 'A', 'B', 'C', name='quality_grade_enum'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_product_batch_code', 'product_batches', ['product_id', 'batch_code'])
    op.create_index('idx_batches_product', 'product_batches', ['product_id'])
    
    # 6. Orders table
    op.create_table(
        "orders",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("farmer_id", sa.String(), nullable=True),
        sa.Column("merchant_id", sa.String(), nullable=True),
        sa.Column("product_id", sa.String(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit_price", sa.Float(), nullable=True),
        sa.Column("delivery_cost", sa.Float(), nullable=True),
        sa.Column("platform_fee", sa.Float(), nullable=True),
        sa.Column("subtotal", sa.Float(), nullable=True),
        sa.Column("delivery_fee", sa.Float(), nullable=True),
        sa.Column("delivery_margin", sa.Float(), nullable=True),
        sa.Column("quality_fee", sa.Float(), nullable=True),
        sa.Column("total_price", sa.Float(), nullable=True),
        sa.Column("status", sa.Enum(*[s.value for s in OrderStatus], name="order_status_enum"), nullable=True),
        sa.Column("escrow_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()"))
    )

    # 7. Escrows table
    op.create_table(
        "escrows",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_id", sa.String(), nullable=True),
        sa.Column("state", sa.Enum(*[s.value for s in EscrowState], name="escrow_state_enum"), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("provider", sa.Enum(*[p.value for p in Provider], name="provider_enum"), nullable=True),
        sa.Column("funded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_reference", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    # Dropping tables in reverse order
    op.drop_table("escrows")
    op.drop_table("orders")
    op.drop_table("product_batches")
    op.drop_table("products")
    op.drop_table("users")

    # Drop sequences
    op.execute("DROP SEQUENCE user_id_seq")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS user_role_enum")
    op.execute("DROP TYPE IF EXISTS category_enum")
    op.execute("DROP TYPE IF EXISTS unit_enum")
    op.execute("DROP TYPE IF EXISTS quality_grade_enum")
    op.execute("DROP TYPE IF EXISTS order_status_enum")
    op.execute("DROP TYPE IF EXISTS escrow_state_enum")
    op.execute("DROP TYPE IF EXISTS provider_enum")
    op.execute("DROP TYPE IF EXISTS dispute_resolution_enum")