"""Agricultural Intelligence Extension

Revision ID: 001_agricultural_intelligence
Revises: c8d8a49d4019
Create Date: 2026-01-30 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_agricultural_intelligence'
down_revision = '13c615f4297d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension (Skipped - using JSONB)
    # op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create custom ENUM types
    op.execute("""
        CREATE TYPE crop_cycle_status AS ENUM (
            'PLANNED', 'PLANTED', 'GROWING', 'HARVESTED', 'FAILED', 'ABANDONED'
        )
    """)
    
    op.execute("""
        CREATE TYPE ndvi_source AS ENUM (
            'SENTINEL_2', 'LANDSAT_8', 'LANDSAT_9', 'MODIS', 'MANUAL'
        )
    """)
    
    op.execute("""
        CREATE TYPE stress_level AS ENUM (
            'NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        )
    """)
    
    op.execute("""
        CREATE TYPE soil_reading_source AS ENUM (
            'IOT_SENSOR', 'MANUAL_TEST', 'LAB_ANALYSIS', 'ESTIMATED'
        )
    """)
    
    op.execute("""
        CREATE TYPE severity_level AS ENUM (
            'TRACE', 'LOW', 'MEDIUM', 'HIGH', 'SEVERE'
        )
    """)
    
    op.execute("""
        CREATE TYPE recommendation_source AS ENUM (
            'AGRONOMIST', 'SYSTEM', 'AI_MODEL', 'COMMUNITY'
        )
    """)
    
    op.execute("""
        CREATE TYPE task_type AS ENUM (
            'LAND_PREPARATION', 'SOWING', 'PLANTING', 'IRRIGATION', 'FERTILIZATION',
            'WEEDING', 'PEST_CONTROL', 'DISEASE_CONTROL', 'PRUNING', 'THINNING',
            'HARVESTING', 'POST_HARVEST', 'INSPECTION', 'MAINTENANCE', 'OTHER'
        )
    """)
    
    op.execute("""
        CREATE TYPE task_status AS ENUM (
            'PENDING', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED', 'OVERDUE'
        )
    """)
    
    op.execute("""
        CREATE TYPE task_priority AS ENUM (
            'LOW', 'MEDIUM', 'HIGH', 'URGENT'
        )
    """)
    
    op.execute("""
        CREATE TYPE weather_source AS ENUM (
            'NOAA_GFS', 'NOAA_HRRR', 'OPEN_METEO', 'LOCAL_STATION', 'MANUAL'
        )
    """)
    
    op.execute("""
        CREATE TYPE risk_type AS ENUM (
            'FROST', 'FREEZE', 'HEAT_STRESS', 'DROUGHT', 'HEAVY_RAIN', 'FLOOD',
            'HAIL', 'STRONG_WIND', 'STORM', 'HURRICANE', 'TORNADO', 'WILDFIRE',
            'PEST_OUTBREAK', 'DISEASE_OUTBREAK'
        )
    """)
    
    op.execute("""
        CREATE TYPE risk_level AS ENUM (
            'MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        )
    """)
    
    op.execute("""
        CREATE TYPE alert_type AS ENUM (
            'WEATHER_WARNING', 'FROST_ALERT', 'DROUGHT_ALERT', 'PEST_DETECTED',
            'DISEASE_DETECTED', 'NDVI_ANOMALY', 'SOIL_MOISTURE_LOW', 'SOIL_MOISTURE_HIGH',
            'TASK_OVERDUE', 'HARVEST_READY', 'LOAN_RISK', 'PAYMENT_DUE',
            'ESCROW_HOLD', 'PRICE_ALERT', 'SYSTEM_NOTIFICATION'
        )
    """)
    
    op.execute("""
        CREATE TYPE alert_severity AS ENUM (
            'INFO', 'WARNING', 'CRITICAL', 'EMERGENCY'
        )
    """)
    
    op.execute("""
        CREATE TYPE advisory_status AS ENUM (
            'REQUESTED', 'SCHEDULED', 'OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', 'CANCELLED'
        )
    """)
    
    op.execute("""
        CREATE TYPE advisory_topic AS ENUM (
            'CROP_SELECTION', 'PEST_MANAGEMENT', 'DISEASE_MANAGEMENT', 'SOIL_HEALTH',
            'IRRIGATION', 'FERTILIZATION', 'HARVEST_TIMING', 'POST_HARVEST',
            'MARKET_ADVICE', 'FINANCIAL_PLANNING', 'GENERAL'
        )
    """)
    
    op.execute("""
        CREATE TYPE message_type AS ENUM (
            'TEXT', 'IMAGE', 'DOCUMENT', 'VOICE', 'VIDEO', 'LOCATION', 'SYSTEM'
        )
    """)
    
    # DOMAIN 1: PRECISION CROP & FIELD MANAGEMENT
    
    # 1.1 Farms table
    op.create_table(
        'farms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('farmer_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('location_lat', sa.Numeric(10, 8), nullable=False),
        sa.Column('location_lng', sa.Numeric(11, 8), nullable=False),
        sa.Column('location_address', sa.Text()),
        sa.Column('total_area_ha', sa.Numeric(10, 4)),
        sa.Column('boundary_geom', postgresql.JSONB),  # Using JSONB instead of GEOMETRY for simplicity
        sa.Column('boundary_geojson', postgresql.JSONB),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.CheckConstraint('total_area_ha > 0', name='valid_area'),
        sa.CheckConstraint('location_lat BETWEEN -90 AND 90 AND location_lng BETWEEN -180 AND 180', name='valid_coordinates')
    )
    
    op.create_index('idx_farms_farmer_id', 'farms', ['farmer_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_farms_created_at', 'farms', [sa.text('created_at DESC')], postgresql_where=sa.text('deleted_at IS NULL'))
    
    # 1.2 Fields table
    op.create_table(
        'fields',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('farm_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('area_ha', sa.Numeric(10, 4), nullable=False),
        sa.Column('boundary_geom', postgresql.JSONB, nullable=False),
        sa.Column('boundary_geojson', postgresql.JSONB, nullable=False),
        sa.Column('centroid_geom', postgresql.JSONB),
        sa.Column('soil_type', sa.String(100)),
        sa.Column('soil_classification', sa.String(100)),
        sa.Column('elevation_m', sa.Numeric(8, 2)),
        sa.Column('slope_degree', sa.Numeric(5, 2)),
        sa.Column('irrigation_type', sa.String(50)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.CheckConstraint('area_ha > 0', name='valid_area'),
        sa.CheckConstraint('slope_degree >= 0 AND slope_degree <= 90', name='valid_slope')
    )
    
    op.create_index('idx_fields_farm_id', 'fields', ['farm_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_fields_soil_type', 'fields', ['soil_type'], postgresql_where=sa.text('deleted_at IS NULL'))
    
    # 1.3 Crop Cycles table
    op.create_table(
        'crop_cycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_category', sa.String(50), nullable=False),
        sa.Column('crop_name', sa.String(255), nullable=False),
        sa.Column('variety', sa.String(255)),
        sa.Column('cultivar', sa.String(255)),
        sa.Column('planting_date', sa.Date(), nullable=False),
        sa.Column('expected_harvest_date', sa.Date()),
        sa.Column('actual_harvest_date', sa.Date()),
        sa.Column('status', postgresql.ENUM(name='crop_cycle_status', create_type=False), nullable=False, server_default='PLANNED'),
        sa.Column('expected_yield_kg', sa.Numeric(12, 2)),
        sa.Column('actual_yield_kg', sa.Numeric(12, 2)),
        sa.Column('seed_source', sa.String(255)),
        sa.Column('planting_density_per_ha', sa.Integer()),
        sa.Column('notes', sa.Text()),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.CheckConstraint('expected_harvest_date IS NULL OR expected_harvest_date > planting_date', name='valid_dates'),
        sa.CheckConstraint('actual_harvest_date IS NULL OR actual_harvest_date >= planting_date', name='valid_actual_harvest'),
        sa.CheckConstraint('(expected_yield_kg IS NULL OR expected_yield_kg >= 0) AND (actual_yield_kg IS NULL OR actual_yield_kg >= 0)', name='valid_yields')
    )
    
    op.create_index('idx_crop_cycles_field_id', 'crop_cycles', ['field_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_crop_cycles_status', 'crop_cycles', ['status'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_crop_cycles_dates', 'crop_cycles', ['planting_date', 'expected_harvest_date'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_crop_cycles_crop_name', 'crop_cycles', ['crop_name'], postgresql_where=sa.text('deleted_at IS NULL'))
    
    # 1.4 NDVI Snapshots table
    op.create_table(
        'ndvi_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL')),
        sa.Column('source', postgresql.ENUM(name='ndvi_source', create_type=False), nullable=False),
        sa.Column('source_metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('ndvi_mean', sa.Numeric(5, 4), nullable=False),
        sa.Column('ndvi_min', sa.Numeric(5, 4)),
        sa.Column('ndvi_max', sa.Numeric(5, 4)),
        sa.Column('ndvi_stddev', sa.Numeric(5, 4)),
        sa.Column('stress_level', postgresql.ENUM(name='stress_level', create_type=False)),
        sa.Column('cloud_cover_pct', sa.Numeric(5, 2)),
        sa.Column('captured_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('ndvi_mean BETWEEN -1 AND 1', name='valid_ndvi_mean'),
        sa.CheckConstraint('ndvi_min IS NULL OR (ndvi_min BETWEEN -1 AND 1)', name='valid_ndvi_min'),
        sa.CheckConstraint('ndvi_max IS NULL OR (ndvi_max BETWEEN -1 AND 1)', name='valid_ndvi_max'),
        sa.CheckConstraint('cloud_cover_pct IS NULL OR (cloud_cover_pct BETWEEN 0 AND 100)', name='valid_cloud_cover')
    )
    
    op.create_index('idx_ndvi_field_id', 'ndvi_snapshots', ['field_id'])
    op.create_index('idx_ndvi_captured_at', 'ndvi_snapshots', [sa.text('captured_at DESC')])
    op.create_index('idx_ndvi_stress_level', 'ndvi_snapshots', ['stress_level'], postgresql_where=sa.text("stress_level IN ('HIGH', 'CRITICAL')"))
    op.create_index('idx_ndvi_crop_cycle', 'ndvi_snapshots', ['crop_cycle_id'], postgresql_where=sa.text('crop_cycle_id IS NOT NULL'))
    
    # 1.5 Soil Readings table
    op.create_table(
        'soil_readings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('location_geom', postgresql.JSONB),
        sa.Column('depth_cm', sa.Integer()),
        sa.Column('moisture_pct', sa.Numeric(5, 2)),
        sa.Column('temperature_c', sa.Numeric(5, 2)),
        sa.Column('nitrogen_ppm', sa.Numeric(8, 2)),
        sa.Column('phosphorus_ppm', sa.Numeric(8, 2)),
        sa.Column('potassium_ppm', sa.Numeric(8, 2)),
        sa.Column('ph', sa.Numeric(4, 2)),
        sa.Column('organic_matter_pct', sa.Numeric(5, 2)),
        sa.Column('electrical_conductivity', sa.Numeric(8, 2)),
        sa.Column('source', postgresql.ENUM(name='soil_reading_source', create_type=False), nullable=False),
        sa.Column('sensor_id', sa.String(255)),
        sa.Column('lab_name', sa.String(255)),
        sa.Column('recorded_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('moisture_pct IS NULL OR (moisture_pct BETWEEN 0 AND 100)', name='valid_moisture'),
        sa.CheckConstraint('ph IS NULL OR (ph BETWEEN 0 AND 14)', name='valid_ph'),
        sa.CheckConstraint('depth_cm IS NULL OR depth_cm > 0', name='valid_depth')
    )
    
    op.create_index('idx_soil_field_id', 'soil_readings', ['field_id'])
    op.create_index('idx_soil_recorded_at', 'soil_readings', [sa.text('recorded_at DESC')])
    op.create_index('idx_soil_source', 'soil_readings', ['source'])
    
    # 1.6 Pest & Disease Reports table
    op.create_table(
        'pest_disease_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL')),
        sa.Column('reported_by', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('location_geom', postgresql.JSONB),
        sa.Column('image_urls', postgresql.ARRAY(sa.Text())),
        sa.Column('suspected_issue', sa.String(255), nullable=False),
        sa.Column('issue_type', sa.String(50)),
        sa.Column('scientific_name', sa.String(255)),
        sa.Column('confidence_pct', sa.Numeric(5, 2)),
        sa.Column('severity', postgresql.ENUM(name='severity_level', create_type=False)),
        sa.Column('affected_area_ha', sa.Numeric(10, 4)),
        sa.Column('symptoms', sa.Text()),
        sa.Column('notes', sa.Text()),
        sa.Column('detected_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('verified_by', sa.String(), sa.ForeignKey('users.id')),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('confidence_pct IS NULL OR (confidence_pct BETWEEN 0 AND 100)', name='valid_confidence'),
        sa.CheckConstraint('affected_area_ha IS NULL OR affected_area_ha > 0', name='valid_affected_area')
    )
    
    op.create_index('idx_pest_field_id', 'pest_disease_reports', ['field_id'])
    op.create_index('idx_pest_crop_cycle', 'pest_disease_reports', ['crop_cycle_id'], postgresql_where=sa.text('crop_cycle_id IS NOT NULL'))
    op.create_index('idx_pest_reported_by', 'pest_disease_reports', ['reported_by'])
    op.create_index('idx_pest_detected_at', 'pest_disease_reports', [sa.text('detected_at DESC')])
    op.create_index('idx_pest_severity', 'pest_disease_reports', ['severity'], postgresql_where=sa.text("severity IN ('HIGH', 'SEVERE')"))
    
    # 1.7 Treatment Recommendations table
    op.create_table(
        'treatment_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pest_disease_reports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommended_by', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('recommendation_source', postgresql.ENUM(name='recommendation_source', create_type=False), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('treatment_type', sa.String(100)),
        sa.Column('chemical_name', sa.String(255)),
        sa.Column('active_ingredient', sa.String(255)),
        sa.Column('dosage', sa.String(255)),
        sa.Column('application_method', sa.String(100)),
        sa.Column('organic', sa.Boolean(), server_default='false'),
        sa.Column('estimated_cost_usd', sa.Numeric(12, 2)),
        sa.Column('effectiveness_rating', sa.Numeric(3, 2)),
        sa.Column('safety_precautions', sa.Text()),
        sa.Column('withdrawal_period_days', sa.Integer()),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('effectiveness_rating IS NULL OR (effectiveness_rating BETWEEN 0 AND 5)', name='valid_effectiveness')
    )
    
    op.create_index('idx_treatment_report_id', 'treatment_recommendations', ['report_id'])
    op.create_index('idx_treatment_recommended_by', 'treatment_recommendations', ['recommended_by'])
    op.create_index('idx_treatment_source', 'treatment_recommendations', ['recommendation_source'])
    op.create_index('idx_treatment_organic', 'treatment_recommendations', ['organic'], postgresql_where=sa.text('organic = TRUE'))
    
    # DOMAIN 2: PLANNING & OPERATIONAL TOOLS
    
    # 2.1 Farm Tasks table
    op.create_table(
        'farm_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL')),
        sa.Column('task_type', postgresql.ENUM(name='task_type', create_type=False), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', postgresql.ENUM(name='task_status', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('priority', postgresql.ENUM(name='task_priority', create_type=False), server_default='MEDIUM'),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('scheduled_time', sa.Time()),
        sa.Column('completed_date', sa.Date()),
        sa.Column('completed_time', sa.Time()),
        sa.Column('assigned_to', sa.String(), sa.ForeignKey('users.id')),
        sa.Column('estimated_duration_hours', sa.Numeric(6, 2)),
        sa.Column('actual_duration_hours', sa.Numeric(6, 2)),
        sa.Column('estimated_cost_usd', sa.Numeric(12, 2)),
        sa.Column('actual_cost_usd', sa.Numeric(12, 2)),
        sa.Column('labor_count', sa.Integer()),
        sa.Column('equipment_needed', postgresql.ARRAY(sa.Text())),
        sa.Column('materials_needed', postgresql.JSONB),
        sa.Column('weather_dependent', sa.Boolean(), server_default='false'),
        sa.Column('notes', sa.Text()),
        sa.Column('completion_notes', sa.Text()),
        sa.Column('auto_generated', sa.Boolean(), server_default='false'),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farm_tasks.id')),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True)),
        sa.CheckConstraint('completed_date IS NULL OR completed_date >= scheduled_date', name='valid_completion'),
        sa.CheckConstraint('(estimated_duration_hours IS NULL OR estimated_duration_hours > 0) AND (actual_duration_hours IS NULL OR actual_duration_hours > 0)', name='valid_duration')
    )
    
    op.create_index('idx_tasks_field_id', 'farm_tasks', ['field_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_tasks_crop_cycle', 'farm_tasks', ['crop_cycle_id'], postgresql_where=sa.text('crop_cycle_id IS NOT NULL AND deleted_at IS NULL'))
    op.create_index('idx_tasks_status', 'farm_tasks', ['status'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_tasks_scheduled_date', 'farm_tasks', ['scheduled_date'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_tasks_assigned_to', 'farm_tasks', ['assigned_to'], postgresql_where=sa.text('assigned_to IS NOT NULL AND deleted_at IS NULL'))
    op.create_index('idx_tasks_priority', 'farm_tasks', ['priority', 'scheduled_date'], postgresql_where=sa.text("status IN ('PENDING', 'SCHEDULED') AND deleted_at IS NULL"))
    
    # 2.2 Task Completions table
    op.create_table(
        'task_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farm_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('completed_by', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('completion_photos', postgresql.ARRAY(sa.Text())),
        sa.Column('quality_rating', sa.Integer()),
        sa.Column('issues_encountered', sa.Text()),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('quality_rating IS NULL OR (quality_rating BETWEEN 1 AND 5)', name='valid_quality_rating')
    )
    
    op.create_index('idx_task_completions_task_id', 'task_completions', ['task_id'])
    op.create_index('idx_task_completions_completed_by', 'task_completions', ['completed_by'])
    
    # DOMAIN 3: RISK MITIGATION & INTELLIGENCE
    
    # 3.1 Weather Snapshots table
    op.create_table(
        'weather_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', postgresql.ENUM(name='weather_source', create_type=False), nullable=False),
        sa.Column('source_station_id', sa.String(100)),
        sa.Column('temperature_c', sa.Numeric(5, 2)),
        sa.Column('feels_like_c', sa.Numeric(5, 2)),
        sa.Column('humidity_pct', sa.Numeric(5, 2)),
        sa.Column('pressure_hpa', sa.Numeric(7, 2)),
        sa.Column('wind_speed_mps', sa.Numeric(6, 2)),
        sa.Column('wind_direction_deg', sa.Integer()),
        sa.Column('wind_gust_mps', sa.Numeric(6, 2)),
        sa.Column('rainfall_mm', sa.Numeric(8, 2)),
        sa.Column('rainfall_intensity', sa.String(50)),
        sa.Column('cloud_cover_pct', sa.Numeric(5, 2)),
        sa.Column('visibility_m', sa.Numeric(8, 2)),
        sa.Column('uv_index', sa.Numeric(4, 2)),
        sa.Column('dew_point_c', sa.Numeric(5, 2)),
        sa.Column('soil_temperature_c', sa.Numeric(5, 2)),
        sa.Column('evapotranspiration_mm', sa.Numeric(6, 2)),
        sa.Column('recorded_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('humidity_pct IS NULL OR (humidity_pct BETWEEN 0 AND 100)', name='valid_humidity'),
        sa.CheckConstraint('wind_direction_deg IS NULL OR (wind_direction_deg BETWEEN 0 AND 360)', name='valid_wind_direction'),
        sa.CheckConstraint('cloud_cover_pct IS NULL OR (cloud_cover_pct BETWEEN 0 AND 100)', name='valid_cloud_cover')
    )
    
    op.create_index('idx_weather_field_id', 'weather_snapshots', ['field_id'])
    op.create_index('idx_weather_recorded_at', 'weather_snapshots', [sa.text('recorded_at DESC')])
    op.create_index('idx_weather_source', 'weather_snapshots', ['source'])
    
    # 3.2 Weather Forecasts table
    op.create_table(
        'weather_forecasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', postgresql.ENUM(name='weather_source', create_type=False), nullable=False),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('forecast_hour', sa.Integer()),
        sa.Column('temperature_min_c', sa.Numeric(5, 2)),
        sa.Column('temperature_max_c', sa.Numeric(5, 2)),
        sa.Column('precipitation_probability_pct', sa.Numeric(5, 2)),
        sa.Column('precipitation_mm', sa.Numeric(8, 2)),
        sa.Column('wind_speed_max_mps', sa.Numeric(6, 2)),
        sa.Column('humidity_avg_pct', sa.Numeric(5, 2)),
        sa.Column('risk_type', postgresql.ENUM(name='risk_type', create_type=False)),
        sa.Column('risk_level', postgresql.ENUM(name='risk_level', create_type=False)),
        sa.Column('risk_description', sa.Text()),
        sa.Column('confidence_pct', sa.Numeric(5, 2)),
        sa.Column('issued_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('forecast_hour IS NULL OR (forecast_hour BETWEEN 0 AND 23)', name='valid_forecast_hour'),
        sa.CheckConstraint('precipitation_probability_pct IS NULL OR (precipitation_probability_pct BETWEEN 0 AND 100)', name='valid_precipitation_prob'),
        sa.CheckConstraint('confidence_pct IS NULL OR (confidence_pct BETWEEN 0 AND 100)', name='valid_confidence')
    )
    
    op.create_index('idx_forecast_field_id', 'weather_forecasts', ['field_id'])
    op.create_index('idx_forecast_date', 'weather_forecasts', ['forecast_date'])
    op.create_index('idx_forecast_risk', 'weather_forecasts', ['risk_level', 'forecast_date'], postgresql_where=sa.text("risk_level IN ('HIGH', 'CRITICAL')"))
    op.create_index('idx_forecast_issued_at', 'weather_forecasts', [sa.text('issued_at DESC')])
    
    # 3.3 Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE')),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL')),
        sa.Column('alert_type', postgresql.ENUM(name='alert_type', create_type=False), nullable=False),
        sa.Column('severity', postgresql.ENUM(name='alert_severity', create_type=False), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('action_required', sa.Text()),
        sa.Column('action_url', sa.String(500)),
        sa.Column('related_entity_type', sa.String(50)),
        sa.Column('related_entity_id', postgresql.UUID(as_uuid=True)),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('acknowledged', sa.Boolean(), server_default='false'),
        sa.Column('acknowledged_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('dismissed', sa.Boolean(), server_default='false'),
        sa.Column('dismissed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('(acknowledged = FALSE AND acknowledged_at IS NULL) OR (acknowledged = TRUE AND acknowledged_at IS NOT NULL)', name='valid_acknowledgement')
    )
    
    op.create_index('idx_alerts_user_id', 'alerts', ['user_id'], postgresql_where=sa.text('dismissed = FALSE'))
    op.create_index('idx_alerts_field_id', 'alerts', ['field_id'], postgresql_where=sa.text('field_id IS NOT NULL AND dismissed = FALSE'))
    op.create_index('idx_alerts_severity', 'alerts', ['severity', sa.text('created_at DESC')], postgresql_where=sa.text('dismissed = FALSE'))
    op.create_index('idx_alerts_type', 'alerts', ['alert_type'], postgresql_where=sa.text('dismissed = FALSE'))
    op.create_index('idx_alerts_unacknowledged', 'alerts', ['user_id', sa.text('created_at DESC')], postgresql_where=sa.text('acknowledged = FALSE AND dismissed = FALSE'))
    
    # 3.4 Alert Actions table
    op.create_table(
        'alert_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('action_details', sa.Text()),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()'))
    )
    
    op.create_index('idx_alert_actions_alert_id', 'alert_actions', ['alert_id'])
    op.create_index('idx_alert_actions_user_id', 'alert_actions', ['user_id'])
    
    # 3.5 Field Risk Scores table
    op.create_table(
        'field_risk_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL')),
        sa.Column('score_date', sa.Date(), nullable=False),
        sa.Column('overall_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('weather_risk_score', sa.Numeric(5, 2)),
        sa.Column('pest_disease_risk_score', sa.Numeric(5, 2)),
        sa.Column('soil_health_score', sa.Numeric(5, 2)),
        sa.Column('crop_health_score', sa.Numeric(5, 2)),
        sa.Column('management_score', sa.Numeric(5, 2)),
        sa.Column('factors', postgresql.JSONB),
        sa.Column('recommendations', postgresql.ARRAY(sa.Text())),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('overall_score BETWEEN 0 AND 100', name='valid_overall_score'),
        sa.CheckConstraint(
            '(weather_risk_score IS NULL OR (weather_risk_score BETWEEN 0 AND 100)) AND '
            '(pest_disease_risk_score IS NULL OR (pest_disease_risk_score BETWEEN 0 AND 100)) AND '
            '(soil_health_score IS NULL OR (soil_health_score BETWEEN 0 AND 100)) AND '
            '(crop_health_score IS NULL OR (crop_health_score BETWEEN 0 AND 100)) AND '
            '(management_score IS NULL OR (management_score BETWEEN 0 AND 100))',
            name='valid_component_scores'
        )
    )
    
    op.create_index('idx_risk_scores_field_id', 'field_risk_scores', ['field_id'])
    op.create_index('idx_risk_scores_crop_cycle', 'field_risk_scores', ['crop_cycle_id'], postgresql_where=sa.text('crop_cycle_id IS NOT NULL'))
    op.create_index('idx_risk_scores_date', 'field_risk_scores', [sa.text('score_date DESC')])
    op.create_index('idx_risk_scores_overall', 'field_risk_scores', ['overall_score'], postgresql_where=sa.text('overall_score < 50'))
    
    # DOMAIN 4: EXPERT ADVISORY & COMMUNITY
    
    # 4.1 Advisory Sessions table
    op.create_table(
        'advisory_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('farmer_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agronomist_id', sa.String(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='SET NULL')),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL')),
        sa.Column('topic', postgresql.ENUM(name='advisory_topic', create_type=False), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', postgresql.ENUM(name='advisory_status', create_type=False), nullable=False, server_default='REQUESTED'),
        sa.Column('priority', postgresql.ENUM(name='task_priority', create_type=False), server_default='MEDIUM'),
        sa.Column('scheduled_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('closed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('rating', sa.Integer()),
        sa.Column('feedback', sa.Text()),
        sa.Column('tags', postgresql.ARRAY(sa.Text())),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('rating IS NULL OR (rating BETWEEN 1 AND 5)', name='valid_rating')
    )
    
    op.create_index('idx_advisory_farmer_id', 'advisory_sessions', ['farmer_id'])
    op.create_index('idx_advisory_agronomist_id', 'advisory_sessions', ['agronomist_id'], postgresql_where=sa.text('agronomist_id IS NOT NULL'))
    op.create_index('idx_advisory_status', 'advisory_sessions', ['status'], postgresql_where=sa.text("status IN ('REQUESTED', 'OPEN', 'IN_PROGRESS')"))
    op.create_index('idx_advisory_topic', 'advisory_sessions', ['topic'])
    op.create_index('idx_advisory_field_id', 'advisory_sessions', ['field_id'], postgresql_where=sa.text('field_id IS NOT NULL'))
    op.create_index('idx_advisory_created_at', 'advisory_sessions', [sa.text('created_at DESC')])
    
    # 4.2 Advisory Messages table
    op.create_table(
        'advisory_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('advisory_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('message_type', postgresql.ENUM(name='message_type', create_type=False), nullable=False, server_default='TEXT'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('attachments', postgresql.JSONB),
        sa.Column('attachment_urls', postgresql.ARRAY(sa.Text())),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('read_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('edited_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True))
    )
    
    op.create_index('idx_advisory_messages_session_id', 'advisory_messages', ['session_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_advisory_messages_sender_id', 'advisory_messages', ['sender_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_advisory_messages_sent_at', 'advisory_messages', [sa.text('sent_at DESC')], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_advisory_messages_unread', 'advisory_messages', ['session_id', 'sent_at'], postgresql_where=sa.text('read_at IS NULL AND deleted_at IS NULL'))
    
    # 4.3 Knowledge Articles table
    op.create_table(
        'knowledge_articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('author_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('topic', postgresql.ENUM(name='advisory_topic', create_type=False), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('tags', postgresql.ARRAY(sa.Text())),
        sa.Column('crop_types', postgresql.ARRAY(sa.Text())),
        sa.Column('region', sa.String(100)),
        sa.Column('language', sa.String(10), server_default='en'),
        sa.Column('view_count', sa.Integer(), server_default='0'),
        sa.Column('helpful_count', sa.Integer(), server_default='0'),
        sa.Column('published', sa.Boolean(), server_default='false'),
        sa.Column('published_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True))
    )
    
    op.create_index('idx_knowledge_topic', 'knowledge_articles', ['topic'], postgresql_where=sa.text('published = TRUE AND deleted_at IS NULL'))
    op.create_index('idx_knowledge_tags', 'knowledge_articles', ['tags'], postgresql_using='gin', postgresql_where=sa.text('published = TRUE AND deleted_at IS NULL'))
    op.create_index('idx_knowledge_crops', 'knowledge_articles', ['crop_types'], postgresql_using='gin', postgresql_where=sa.text('published = TRUE AND deleted_at IS NULL'))
    op.create_index('idx_knowledge_published_at', 'knowledge_articles', [sa.text('published_at DESC')], postgresql_where=sa.text('published = TRUE AND deleted_at IS NULL'))
    op.create_index('idx_knowledge_helpful', 'knowledge_articles', [sa.text('helpful_count DESC')], postgresql_where=sa.text('published = TRUE AND deleted_at IS NULL'))
    
    # INTEGRATION TABLES
    
    # Link Products to Crop Cycles
    op.create_table(
        'crop_cycle_products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.String(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity_kg', sa.Numeric(12, 2), nullable=False),
        sa.Column('quality_grade', sa.String(50)),
        sa.Column('harvest_date', sa.Date(), nullable=False),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('quantity_kg > 0', name='valid_quantity'),
        sa.UniqueConstraint('crop_cycle_id', 'product_id', 'harvest_date', name='unique_crop_product')
    )
    
    op.create_index('idx_crop_products_cycle', 'crop_cycle_products', ['crop_cycle_id'])
    op.create_index('idx_crop_products_product', 'crop_cycle_products', ['product_id'])
    
    # Link Orders to Fields
    op.create_table(
        'order_field_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('order_id', sa.String(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='SET NULL')),
        sa.Column('quantity_kg', sa.Numeric(12, 2), nullable=False),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('quantity_kg > 0', name='valid_quantity')
    )
    
    op.create_index('idx_order_sources_order', 'order_field_sources', ['order_id'])
    op.create_index('idx_order_sources_field', 'order_field_sources', ['field_id'])
    
    # Link Loans to Crop Cycles
    op.create_table(
        'loan_crop_cycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('loan_id', sa.String(), sa.ForeignKey('loans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('crop_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('allocated_amount_usd', sa.Numeric(12, 2), nullable=False),
        sa.Column('purpose', sa.Text()),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('allocated_amount_usd > 0', name='valid_amount'),
        sa.UniqueConstraint('loan_id', 'crop_cycle_id', name='unique_loan_crop')
    )
    
    op.create_index('idx_loan_crops_loan', 'loan_crop_cycles', ['loan_id'])
    op.create_index('idx_loan_crops_cycle', 'loan_crop_cycles', ['crop_cycle_id'])
    
    # Escrow conditions based on field data
    op.create_table(
        'escrow_field_conditions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('escrow_id', sa.String(), sa.ForeignKey('escrows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('condition_type', sa.String(100), nullable=False),
        sa.Column('condition_description', sa.Text(), nullable=False),
        sa.Column('threshold_value', sa.Numeric(12, 4)),
        sa.Column('current_value', sa.Numeric(12, 4)),
        sa.Column('met', sa.Boolean(), server_default='false'),
        sa.Column('checked_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()'))
    )
    
    op.create_index('idx_escrow_conditions_escrow', 'escrow_field_conditions', ['escrow_id'])
    op.create_index('idx_escrow_conditions_field', 'escrow_field_conditions', ['field_id'])
    op.create_index('idx_escrow_conditions_unmet', 'escrow_field_conditions', ['escrow_id'], postgresql_where=sa.text('met = FALSE'))


def downgrade() -> None:
    # Drop integration tables
    op.drop_table('escrow_field_conditions')
    op.drop_table('loan_crop_cycles')
    op.drop_table('order_field_sources')
    op.drop_table('crop_cycle_products')
    
    # Drop Domain 4 tables
    op.drop_table('knowledge_articles')
    op.drop_table('advisory_messages')
    op.drop_table('advisory_sessions')
    
    # Drop Domain 3 tables
    op.drop_table('field_risk_scores')
    op.drop_table('alert_actions')
    op.drop_table('alerts')
    op.drop_table('weather_forecasts')
    op.drop_table('weather_snapshots')
    
    # Drop Domain 2 tables
    op.drop_table('task_completions')
    op.drop_table('farm_tasks')
    
    # Drop Domain 1 tables
    op.drop_table('treatment_recommendations')
    op.drop_table('pest_disease_reports')
    op.drop_table('soil_readings')
    op.drop_table('ndvi_snapshots')
    op.drop_table('crop_cycles')
    op.drop_table('fields')
    op.drop_table('farms')
    
    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS message_type')
    op.execute('DROP TYPE IF EXISTS advisory_topic')
    op.execute('DROP TYPE IF EXISTS advisory_status')
    op.execute('DROP TYPE IF EXISTS alert_severity')
    op.execute('DROP TYPE IF EXISTS alert_type')
    op.execute('DROP TYPE IF EXISTS risk_level')
    op.execute('DROP TYPE IF EXISTS risk_type')
    op.execute('DROP TYPE IF EXISTS weather_source')
    op.execute('DROP TYPE IF EXISTS task_priority')
    op.execute('DROP TYPE IF EXISTS task_status')
    op.execute('DROP TYPE IF EXISTS task_type')
    op.execute('DROP TYPE IF EXISTS recommendation_source')
    op.execute('DROP TYPE IF EXISTS severity_level')
    op.execute('DROP TYPE IF EXISTS soil_reading_source')
    op.execute('DROP TYPE IF EXISTS stress_level')
    op.execute('DROP TYPE IF EXISTS ndvi_source')
    op.execute('DROP TYPE IF EXISTS crop_cycle_status')
