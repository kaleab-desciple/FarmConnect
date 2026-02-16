"""Add indexes for weather queries

Revision ID: weather_indexes
Revises: weather_service_improvements
Create Date: 2026-02-16 17:35:00.000000

Improves query performance for weather data retrieval.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'weather_indexes'
down_revision = 'weather_service_improvements'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for better weather query performance"""
    
    # Improve weather snapshot queries by field and date
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_snapshots_field_date 
        ON weather_snapshots(field_id, recorded_at DESC);
    """)
    
    # Improve forecast queries by field and date
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_forecasts_field_date 
        ON weather_forecasts(field_id, forecast_date);
    """)
    
    # Improve field lookups by farm
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_fields_farm_id 
        ON fields(farm_id) WHERE farm_id IS NOT NULL;
    """)
    
    # Add index for weather snapshots source (for data provenance queries)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_snapshots_source
        ON weather_snapshots(source);
    """)


def downgrade():
    """Remove indexes"""
    op.execute("DROP INDEX IF EXISTS idx_weather_snapshots_field_date")
    op.execute("DROP INDEX IF EXISTS idx_weather_forecasts_field_date")
    op.execute("DROP INDEX IF EXISTS idx_fields_farm_id")
    op.execute("DROP INDEX IF EXISTS idx_weather_snapshots_source")
