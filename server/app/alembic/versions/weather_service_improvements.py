"""Weather Service Improvements: Pagination, Indexes, Error Handling

Revision ID: weather_service_improvements
Revises: 0143ba166256
Create Date: 2026-02-16 13:35:00.000000

This migration adds:
- Composite indexes for efficient weather queries
- Data retention policies for old weather records
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'weather_service_improvements'
down_revision: Union[str, Sequence[str], None] = '0143ba166256'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add weather service improvements."""
    
    # ============== Composite Indexes for Weather Forecasts ==============
    
    # Index for fetching forecasts by field and date range
    op.create_index(
        'ix_weather_forecasts_field_date',
        'weather_forecasts',
        ['field_id', 'forecast_date'],
        unique=False
    )
    
    # Index for fetching latest forecast by field
    op.create_index(
        'ix_weather_forecasts_field_issued',
        'weather_forecasts',
        ['field_id', 'issued_at'],
        unique=False
    )
    
    # Index for risk-level queries
    op.create_index(
        'ix_weather_forecasts_risk',
        'weather_forecasts',
        ['field_id', 'risk_level', 'forecast_date'],
        unique=False
    )
    
    # ============== Composite Indexes for Weather Snapshots ==============
    
    # Index for fetching snapshots by field and date range
    op.create_index(
        'ix_weather_snapshots_field_recorded',
        'weather_snapshots',
        ['field_id', 'recorded_at'],
        unique=False
    )
    
    # Index for fetching recent snapshots
    op.create_index(
        'ix_weather_snapshots_field_latest',
        'weather_snapshots',
        ['field_id', 'source', 'recorded_at'],
        unique=False
    )
    
    # ============== Indexes for Field Risk Scores ==============
    
    # Index for fetching risk scores by field and date
    op.create_index(
        'ix_field_risk_scores_field_date',
        'field_risk_scores',
        ['field_id', 'score_date'],
        unique=False
    )
    
    # Index for fetching risk scores by crop cycle
    op.create_index(
        'ix_field_risk_scores_crop_cycle',
        'field_risk_scores',
        ['crop_cycle_id', 'score_date'],
        unique=False
    )
    
    # ============== Indexes for Alerts ==============
    
    # Index for fetching active alerts by user
    op.create_index(
        'ix_alerts_user_active',
        'alerts',
        ['user_id', 'acknowledged', 'created_at'],
        unique=False
    )
    
    # Index for fetching alerts by field
    op.create_index(
        'ix_alerts_field',
        'alerts',
        ['field_id', 'created_at'],
        unique=False
    )
    
    # Index for alert type queries
    op.create_index(
        'ix_alerts_type_severity',
        'alerts',
        ['alert_type', 'severity', 'created_at'],
        unique=False
    )
    
    # ============== Add Data Retention Columns ==============
    
    # Add expires_at column to weather_forecasts for TTL policies
    op.add_column(
        'weather_forecasts',
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Add expires_at column to weather_snapshots for TTL policies
    op.add_column(
        'weather_snapshots',
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Add is_active column to alerts
    op.add_column(
        'alerts',
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False)
    )
    
    # ============== Create Weather Alert Subscriptions Table ==============
    
    # Create table for weather alert subscriptions per field/user
    op.execute("""
        CREATE TABLE IF NOT EXISTS weather_alert_subscriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            field_id UUID REFERENCES fields(id) ON DELETE CASCADE,
            alert_type VARCHAR(50) NOT NULL,
            enabled BOOLEAN DEFAULT true,
            notify_email BOOLEAN DEFAULT true,
            notify_sms BOOLEAN DEFAULT false,
            notify_push BOOLEAN DEFAULT true,
            threshold_value NUMERIC,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, field_id, alert_type)
        )
    """)
    
    # Create indexes for weather alert subscriptions
    op.create_index(
        'ix_weather_subscriptions_user',
        'weather_alert_subscriptions',
        ['user_id', 'enabled']
    )
    
    op.create_index(
        'ix_weather_subscriptions_field',
        'weather_alert_subscriptions',
        ['field_id', 'alert_type', 'enabled']
    )


def downgrade() -> None:
    """Remove weather service improvements."""
    
    # Drop weather alert subscriptions indexes
    op.drop_index('ix_weather_subscriptions_field', 'weather_alert_subscriptions')
    op.drop_index('ix_weather_subscriptions_user', 'weather_alert_subscriptions')
    
    # Drop weather alert subscriptions table
    op.execute("DROP TABLE IF EXISTS weather_alert_subscriptions")
    
    # Remove is_active column from alerts
    op.drop_column('alerts', 'is_active')
    
    # Remove expires_at columns
    op.drop_column('weather_snapshots', 'expires_at')
    op.drop_column('weather_forecasts', 'expires_at')
    
    # Drop alerts indexes
    op.drop_index('ix_alerts_type_severity', 'alerts')
    op.drop_index('ix_alerts_field', 'alerts')
    op.drop_index('ix_alerts_user_active', 'alerts')
    
    # Drop field risk scores indexes
    op.drop_index('ix_field_risk_scores_crop_cycle', 'field_risk_scores')
    op.drop_index('ix_field_risk_scores_field_date', 'field_risk_scores')
    
    # Drop weather snapshots indexes
    op.drop_index('ix_weather_snapshots_field_latest', 'weather_snapshots')
    op.drop_index('ix_weather_snapshots_field_recorded', 'weather_snapshots')
    
    # Drop weather forecasts indexes
    op.drop_index('ix_weather_forecasts_risk', 'weather_forecasts')
    op.drop_index('ix_weather_forecasts_field_issued', 'weather_forecasts')
    op.drop_index('ix_weather_forecasts_field_date', 'weather_forecasts')
