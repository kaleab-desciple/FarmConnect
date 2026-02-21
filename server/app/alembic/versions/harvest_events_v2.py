"""Add QC and Lab tables

Revision ID: harvest_events_v2
Revises: harvest_events_v1
Create Date: 2026-02-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

# revision identifiers, used by Alembic.
revision = 'harvest_events_v2'
down_revision = 'harvest_events_v1'  # Update to latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create enum types
    op.execute("DROP TYPE IF EXISTS qc_grade_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS batch_qc_state_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS certification_type_enum CASCADE")
    
    # op.execute("CREATE TYPE qc_grade_enum AS ENUM ('GRADE_A', 'GRADE_B', 'GRADE_C', 'REJECT')")
    op.execute("CREATE TYPE batch_qc_state_enum AS ENUM ('QC_PENDING', 'QC_PASSED', 'QC_FAILED')")
    # op.execute("CREATE TYPE certification_type_enum AS ENUM ('ORGANIC', 'FAIRTRADE', 'RAINFOREST_ALLIANCE', 'GLOBALGAP', 'OTHER')")
    
    # 2. Create lab_providers table
    op.create_table(
        "lab_providers",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("public_key", sa.Text(), nullable=True),  # PEM public key for signature verification
        sa.Column("metadata", psql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )
    op.create_index('idx_lab_providers_name', 'lab_providers', ['name'])
    
    # 3. Create samples (sampling_requests) table
    op.create_table(
        "samples",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sample_code", sa.String(100), nullable=False),
        sa.Column("harvest_batch_id", sa.String(), sa.ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("collected_by", sa.String(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sample_points", psql.JSONB(), nullable=True),  # GPS points or summary
        sa.Column("photos", psql.JSONB(), nullable=True),  # Array of {url, hash, exif}
        sa.Column("chain_of_custody", psql.JSONB(), nullable=True),
        sa.Column("submitted_to_lab", sa.Boolean(), nullable=False, server_default='false'),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )
    op.create_index('idx_samples_harvest_batch_id', 'samples', ['harvest_batch_id'])
    op.create_index('idx_samples_sample_code', 'samples', ['sample_code'], unique=True)
    
    # 4. Create batch_qc_reports table (expanded from existing)
    # First drop the old table if exists (from harvest_events migration)
    op.execute("DROP TABLE IF EXISTS batch_qc_reports CASCADE")
    
    op.create_table(
        "batch_qc_reports",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("batch_id", sa.String(), sa.ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sample_id", sa.String(), sa.ForeignKey("samples.id", ondelete="SET NULL"), nullable=True),
        sa.Column("lab_id", sa.String(), sa.ForeignKey("lab_providers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metrics", psql.JSONB(), nullable=True),  # {moisture_pct:12.4, aflatoxin_ppb:3.4, foreign_matter_pct:0.5}
        sa.Column("grade", sa.Enum('GRADE_A', 'GRADE_B', 'GRADE_C', 'REJECT', name='qc_grade_enum'), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("report_url", sa.String(500), nullable=True),
        sa.Column("signed_hash", sa.String(200), nullable=True),  # Lab-supplied signature or hash
        sa.Column("verified", sa.Boolean(), nullable=False, server_default='false'),  # Whether signature verification succeeded
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )
    op.create_index('idx_qc_reports_batch_id', 'batch_qc_reports', ['batch_id'])
    op.create_index('idx_qc_reports_lab_id', 'batch_qc_reports', ['lab_id'])
    op.create_index('idx_qc_reports_sample_id', 'batch_qc_reports', ['sample_id'])
    
    # 5. Create certifications table
    op.create_table(
        "certifications",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("harvest_batch_id", sa.String(), sa.ForeignKey("harvest_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issuer", sa.String(255), nullable=False),
        sa.Column("cert_type", sa.Enum('ORGANIC', 'FAIRTRADE', 'RAINFOREST_ALLIANCE', 'GLOBALGAP', 'OTHER', name='certification_type_enum'), nullable=False),
        sa.Column("cert_number", sa.String(100), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cert_url", sa.String(500), nullable=True),
        sa.Column("signed_hash", sa.String(200), nullable=True),
        sa.Column("metadata", psql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )
    op.create_index('idx_certifications_harvest_batch_id', 'certifications', ['harvest_batch_id'])
    op.create_index('idx_certifications_type', 'certifications', ['cert_type'])
    
    # 6. Create qc_grade_rules table (configurable threshold rules)
    op.create_table(
        "qc_grade_rules",
        sa.Column("id", sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("commodity", sa.String(100), nullable=False),  # e.g., "maize", "coffee", "wheat"
        sa.Column("grade", sa.Enum('GRADE_A', 'GRADE_B', 'GRADE_C', 'REJECT', name='qc_grade_enum'), nullable=False),
        sa.Column("rules", psql.JSONB(), nullable=False),  # [{"metric":"moisture_pct","op":"<=","value":13.0}, ...]
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default='true'),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
    )
    op.create_index('idx_qc_grade_rules_commodity', 'qc_grade_rules', ['commodity'])
    
    # 7. Create audit_events table if not exists (from harvest_events)
    # Already exists from harvest_events_v1, but add QC-specific indexes if needed
    
    # 8. Insert default QC grade rules for common commodities
    # Use parameterized query to avoid DBAPI/SQLAlchemy percent-format interpolation issues
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO qc_grade_rules (id, commodity, grade, rules, is_active) VALUES 
        (gen_random_uuid(), :c1, :g1, CAST(:r1 AS jsonb), true),
        (gen_random_uuid(), :c2, :g2, CAST(:r2 AS jsonb), true),
        (gen_random_uuid(), :c3, :g3, CAST(:r3 AS jsonb), true),
        (gen_random_uuid(), :c4, :g4, CAST(:r4 AS jsonb), true),
        (gen_random_uuid(), :c5, :g5, CAST(:r5 AS jsonb), true),
        (gen_random_uuid(), :c6, :g6, CAST(:r6 AS jsonb), true),
        (gen_random_uuid(), :c7, :g7, CAST(:r7 AS jsonb), true)
    """), {
        'c1': 'maize', 'g1': 'GRADE_A', 'r1': '[{"metric":"moisture_pct","op":"<=","value":13.0},{"metric":"aflatoxin_ppb","op":"<=","value":5}]',
        'c2': 'maize', 'g2': 'GRADE_B', 'r2': '[{"metric":"moisture_pct","op":"<=","value":14.0},{"metric":"aflatoxin_ppb","op":"<=","value":10}]',
        'c3': 'maize', 'g3': 'GRADE_C', 'r3': '[{"metric":"moisture_pct","op":"<=","value":15.0},{"metric":"aflatoxin_ppb","op":"<=","value":20}]',
        'c4': 'wheat', 'g4': 'GRADE_A', 'r4': '[{"metric":"moisture_pct","op":"<=","value":12.0},{"metric":"protein_pct","op":">=","value":10}]',
        'c5': 'wheat', 'g5': 'GRADE_B', 'r5': '[{"metric":"moisture_pct","op":"<=","value":14.0},{"metric":"protein_pct","op":">=","value":8}]',
        'c6': 'coffee', 'g6': 'GRADE_A', 'r6': '[{"metric":"moisture_pct","op":"<=","value":12.0},{"metric":"defect_count","op":"<=","value":5}]',
        'c7': 'coffee', 'g7': 'GRADE_B', 'r7': '[{"metric":"moisture_pct","op":"<=","value":13.0},{"metric":"defect_count","op":"<=","value":10}]'
    })


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("certifications")
    op.drop_table("batch_qc_reports")
    op.drop_table("samples")
    op.drop_table("qc_grade_rules")
    op.drop_table("lab_providers")
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS qc_grade_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS batch_qc_state_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS certification_type_enum CASCADE")
