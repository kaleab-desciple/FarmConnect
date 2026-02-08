"""Agricultural Intelligence Extension

Revision ID: 001_agricultural_intelligence
Revises: 13c615f4297d
Create Date: 2026-01-30 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a8391ae9c1a3'
down_revision = '13c615f4297d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
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
    # 1. Base Infrastructure (Farms and Fields)
    op.execute("""
    CREATE TABLE farms (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        farmer_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        location_lat NUMERIC(10, 8) NOT NULL CHECK (location_lat BETWEEN -90 AND 90),
        location_lng NUMERIC(11, 8) NOT NULL CHECK (location_lng BETWEEN -180 AND 180),
        location_address TEXT,
        total_area_ha NUMERIC(10, 4) CHECK (total_area_ha > 0),
        boundary_geojson JSONB,
        centroid_geojson JSONB,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        deleted_at TIMESTAMPTZ,
        CONSTRAINT valid_coordinates CHECK (location_lat BETWEEN -90 AND 90 AND location_lng BETWEEN -180 AND 180)
    );
    CREATE INDEX idx_farms_farmer_active ON farms(farmer_id) WHERE deleted_at IS NULL;
    """)

    op.execute("""
    CREATE TABLE fields (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        area_ha NUMERIC(10, 4) NOT NULL CHECK (area_ha > 0),
        boundary_geojson JSONB NOT NULL,
        centroid_geojson JSONB,
        soil_type VARCHAR(100),
        soil_classification VARCHAR(100),
        elevation_m NUMERIC(8, 2),
        slope_degree NUMERIC(5, 2) CHECK (slope_degree BETWEEN 0 AND 90),
        irrigation_type VARCHAR(50),
        drainage_type VARCHAR(50),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        deleted_at TIMESTAMPTZ
    );
    CREATE INDEX idx_fields_farm ON fields(farm_id) WHERE deleted_at IS NULL;
    """)

    # 2. Crop Management
    op.execute("""
    CREATE TABLE crop_cycles (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        product_category VARCHAR(50) NOT NULL,
        crop_name VARCHAR(255) NOT NULL,
        variety VARCHAR(255),
        cultivar VARCHAR(255),
        planting_date DATE NOT NULL,
        expected_harvest_date DATE,
        actual_harvest_date DATE,
        status crop_cycle_status DEFAULT 'PLANNED',
        expected_yield_kg NUMERIC(12, 2) CHECK (expected_yield_kg >= 0),
        actual_yield_kg NUMERIC(12, 2) CHECK (actual_yield_kg >= 0),
        yield_quality_grade VARCHAR(50),
        seed_source VARCHAR(255),
        planting_density_per_ha INTEGER,
        seed_cost_usd NUMERIC(10, 2),
        notes TEXT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        deleted_at TIMESTAMPTZ,
        CONSTRAINT valid_harvest_dates CHECK (expected_harvest_date IS NULL OR expected_harvest_date > planting_date),
        CONSTRAINT valid_actual_harvest CHECK (actual_harvest_date IS NULL OR actual_harvest_date >= planting_date)
    );
    CREATE INDEX idx_crop_cycles_field ON crop_cycles(field_id) WHERE deleted_at IS NULL;
    """)

    
    # 3. Operations and Tasks
    op.execute("""
    CREATE TABLE farm_tasks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        crop_cycle_id UUID REFERENCES crop_cycles(id) ON DELETE SET NULL,
        task_type task_type NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        status task_status DEFAULT 'PENDING',
        priority task_priority DEFAULT 'MEDIUM',
        scheduled_date DATE NOT NULL,
        scheduled_time TIME,
        duration_estimate_hours NUMERIC(6, 2),
        window_start_date DATE,
        window_end_date DATE,
        completed_date DATE,
        completed_time TIME,
        completed_by VARCHAR REFERENCES users(id),
        duration_actual_hours NUMERIC(6, 2),
        assigned_to VARCHAR REFERENCES users(id),
        labor_count INTEGER,
        equipment_needed TEXT[],
        materials_needed JSONB,
        estimated_cost_usd NUMERIC(12, 2),
        actual_cost_usd NUMERIC(12, 2),
        parent_task_id UUID REFERENCES farm_tasks(id),
        depends_on_tasks UUID[],
        weather_dependent BOOLEAN DEFAULT FALSE,
        soil_moisture_condition VARCHAR(50),
        auto_generated BOOLEAN DEFAULT FALSE,
        generation_reason TEXT,
        notes TEXT,
        completion_notes TEXT,
        completion_photos TEXT[],
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        deleted_at TIMESTAMPTZ,
        CONSTRAINT valid_completion_date CHECK (completed_date IS NULL OR completed_date >= scheduled_date)
    );
    """)

    op.execute("""
    CREATE TABLE task_dependencies (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        task_id UUID NOT NULL REFERENCES farm_tasks(id) ON DELETE CASCADE,
        depends_on_task_id UUID NOT NULL REFERENCES farm_tasks(id) ON DELETE CASCADE,
        dependency_type VARCHAR(50) DEFAULT 'finish_to_start',
        lag_hours INTEGER DEFAULT 0,
        UNIQUE(task_id, depends_on_task_id)
    );
    """)

    # 4. Monitoring and Health (NDVI, Pest, Soil)
    op.execute("""
    CREATE TABLE ndvi_snapshots (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        crop_cycle_id UUID REFERENCES crop_cycles(id) ON DELETE SET NULL,
        source ndvi_source NOT NULL,
        source_metadata JSONB DEFAULT '{}',
        captured_at TIMESTAMPTZ NOT NULL,
        processed_at TIMESTAMPTZ DEFAULT NOW(),
        ndvi_mean NUMERIC(5, 4) NOT NULL CHECK (ndvi_mean BETWEEN -1 AND 1),
        ndvi_min NUMERIC(5, 4) CHECK (ndvi_min BETWEEN -1 AND 1),
        ndvi_max NUMERIC(5, 4) CHECK (ndvi_max BETWEEN -1 AND 1),
        ndvi_stddev NUMERIC(5, 4),
        stress_level stress_level,
        cloud_cover_pct NUMERIC(5, 2) CHECK (cloud_cover_pct BETWEEN 0 AND 100),
        data_quality_score NUMERIC(3, 2),
        tile_urls JSONB,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE pest_disease_reports (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        crop_cycle_id UUID REFERENCES crop_cycles(id) ON DELETE SET NULL,
        reported_by VARCHAR NOT NULL REFERENCES users(id),
        location_geojson JSONB,
        image_urls TEXT[],
        drone_flight_id UUID,
        suspected_issue VARCHAR(255) NOT NULL,
        issue_type VARCHAR(50),
        scientific_name VARCHAR(255),
        common_names TEXT[],
        ai_diagnosis_id UUID,
        confidence_pct NUMERIC(5, 2) CHECK (confidence_pct BETWEEN 0 AND 100),
        severity severity_level,
        affected_area_ha NUMERIC(10, 4) CHECK (affected_area_ha > 0),
        affected_plant_count INTEGER,
        symptoms TEXT,
        spread_pattern VARCHAR(100),
        verified_by VARCHAR REFERENCES users(id),
        verified_at TIMESTAMPTZ,
        verification_notes TEXT,
        first_observed_date DATE,
        detected_at TIMESTAMPTZ NOT NULL,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE treatment_recommendations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        report_id UUID NOT NULL REFERENCES pest_disease_reports(id) ON DELETE CASCADE,
        recommended_by VARCHAR NOT NULL REFERENCES users(id),
        recommendation_source recommendation_source NOT NULL,
        description TEXT NOT NULL,
        treatment_type VARCHAR(100),
        chemical_name VARCHAR(255),
        active_ingredient VARCHAR(255),
        formulation VARCHAR(100),
        dosage_per_ha VARCHAR(255),
        application_method VARCHAR(100),
        application_timing VARCHAR(255),
        organic BOOLEAN DEFAULT FALSE,
        restricted_use BOOLEAN DEFAULT FALSE,
        required_ppe TEXT[],
        reentry_interval_hours INTEGER,
        pre_harvest_interval_days INTEGER,
        withdrawal_period_days INTEGER,
        estimated_cost_per_ha_usd NUMERIC(10, 2),
        effectiveness_rating NUMERIC(3, 2) CHECK (effectiveness_rating BETWEEN 0 AND 5),
        expected_results_days INTEGER,
        accepted_by_farmer BOOLEAN,
        accepted_at TIMESTAMPTZ,
        applied BOOLEAN DEFAULT FALSE,
        applied_at TIMESTAMPTZ,
        application_notes TEXT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE soil_readings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        location_geojson JSONB,
        sample_depth_cm INTEGER CHECK (sample_depth_cm > 0),
        sample_depth_range VARCHAR(50),
        moisture_pct NUMERIC(5, 2) CHECK (moisture_pct BETWEEN 0 AND 100),
        temperature_c NUMERIC(5, 2),
        ph NUMERIC(4, 2) CHECK (ph BETWEEN 0 AND 14),
        nitrogen_ppm NUMERIC(8, 2),
        phosphorus_ppm NUMERIC(8, 2),
        potassium_ppm NUMERIC(8, 2),
        organic_matter_pct NUMERIC(5, 2),
        cation_exchange_capacity NUMERIC(6, 2),
        electrical_conductivity_ms_cm NUMERIC(8, 2),
        texture_analysis JSONB,
        source soil_reading_source NOT NULL,
        lab_name VARCHAR(255),
        lab_report_url TEXT,
        recorded_by VARCHAR REFERENCES users(id),
        recorded_at TIMESTAMPTZ NOT NULL,
        weather_conditions VARCHAR(255),
        days_since_rain INTEGER,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # 5. Weather Services
    op.execute("""
    CREATE TABLE weather_forecasts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        source weather_source NOT NULL,
        forecast_date DATE NOT NULL,
        forecast_hour INTEGER CHECK (forecast_hour BETWEEN 0 AND 23),
        forecast_horizon_hours INTEGER,
        issued_at TIMESTAMPTZ NOT NULL,
        temperature_min_c NUMERIC(5, 2),
        temperature_max_c NUMERIC(5, 2),
        temperature_avg_c NUMERIC(5, 2),
        precipitation_probability_pct NUMERIC(5, 2) CHECK (precipitation_probability_pct BETWEEN 0 AND 100),
        precipitation_mm NUMERIC(8, 2),
        precipitation_type VARCHAR(50),
        wind_speed_max_mps NUMERIC(6, 2),
        wind_direction_deg INTEGER,
        humidity_avg_pct NUMERIC(5, 2),
        pressure_hpa NUMERIC(7, 2),
        growing_degree_days_accumulated NUMERIC(8, 2),
        evapotranspiration_mm NUMERIC(6, 2),
        risk_type risk_type,
        risk_level risk_level,
        risk_description TEXT,
        risk_confidence_pct NUMERIC(5, 2),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE weather_snapshots (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        source weather_source NOT NULL,
        source_station_id VARCHAR(100),
        source_station_distance_km NUMERIC(6, 2),
        recorded_at TIMESTAMPTZ NOT NULL,
        temperature_c NUMERIC(5, 2),
        feels_like_c NUMERIC(5, 2),
        humidity_pct NUMERIC(5, 2) CHECK (humidity_pct BETWEEN 0 AND 100),
        pressure_hpa NUMERIC(7, 2),
        wind_speed_mps NUMERIC(6, 2),
        wind_direction_deg INTEGER CHECK (wind_direction_deg BETWEEN 0 AND 360),
        wind_gust_mps NUMERIC(6, 2),
        rainfall_mm NUMERIC(8, 2),
        rainfall_intensity VARCHAR(50),
        snowfall_mm NUMERIC(6, 2),
        cloud_cover_pct NUMERIC(5, 2) CHECK (cloud_cover_pct BETWEEN 0 AND 100),
        visibility_m NUMERIC(8, 2),
        uv_index NUMERIC(4, 2),
        soil_temperature_c NUMERIC(5, 2),
        soil_moisture_pct NUMERIC(5, 2),
        leaf_wetness_hours NUMERIC(4, 1),
        evapotranspiration_mm NUMERIC(6, 2),
        growing_degree_days NUMERIC(8, 2),
        raw_data JSONB,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # 6. Advisory and Knowledge Base
    op.execute("""
    CREATE TABLE advisory_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        farmer_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        agronomist_id VARCHAR REFERENCES users(id) ON DELETE SET NULL,
        field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
        crop_cycle_id UUID REFERENCES crop_cycles(id) ON DELETE SET NULL,
        topic advisory_topic NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        status advisory_status DEFAULT 'REQUESTED',
        priority task_priority DEFAULT 'MEDIUM',
        requested_at TIMESTAMPTZ DEFAULT NOW(),
        scheduled_at TIMESTAMPTZ,
        started_at TIMESTAMPTZ,
        closed_at TIMESTAMPTZ,
        communication_method VARCHAR(50),
        meeting_link TEXT,
        resolution_summary TEXT,
        recommendations_given TEXT[],
        farmer_rating INTEGER CHECK (farmer_rating BETWEEN 1 AND 5),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE advisory_messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID NOT NULL REFERENCES advisory_sessions(id) ON DELETE CASCADE,
        sender_id VARCHAR NOT NULL REFERENCES users(id),
        message_type message_type DEFAULT 'TEXT',
        message TEXT NOT NULL,
        attachments JSONB,
        sent_at TIMESTAMPTZ DEFAULT NOW(),
        read_at TIMESTAMPTZ,
        metadata JSONB DEFAULT '{}'
    );
    """)

    op.execute("""
    CREATE TABLE knowledge_articles (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        author_id VARCHAR NOT NULL REFERENCES users(id),
        topic advisory_topic NOT NULL,
        title VARCHAR(255) NOT NULL,
        slug VARCHAR(255) UNIQUE,
        summary TEXT,
        content TEXT NOT NULL,
        status VARCHAR(20) DEFAULT 'draft',
        published_at TIMESTAMPTZ,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # 7. Financial and Supply Chain
    op.execute("""
    CREATE TABLE crop_cycle_products (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        crop_cycle_id UUID NOT NULL REFERENCES crop_cycles(id) ON DELETE CASCADE,
        product_id VARCHAR NOT NULL REFERENCES products(id) ON DELETE CASCADE,
        quantity_kg NUMERIC(12, 2) NOT NULL CHECK (quantity_kg > 0),
        quality_grade VARCHAR(50),
        harvest_date DATE NOT NULL,
        lot_number VARCHAR(100),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(crop_cycle_id, product_id, harvest_date, lot_number)
    );
    """)

    op.execute("""
    CREATE TABLE order_field_sources (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        order_id VARCHAR NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        crop_cycle_id UUID REFERENCES crop_cycles(id) ON DELETE SET NULL,
        quantity_kg NUMERIC(12, 2) NOT NULL CHECK (quantity_kg > 0),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE escrow_field_conditions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        escrow_id VARCHAR NOT NULL REFERENCES escrows(id) ON DELETE CASCADE,
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        condition_type VARCHAR(100) NOT NULL,
        met BOOLEAN DEFAULT FALSE,
        met_at TIMESTAMPTZ,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # 8. Risk and Alerts
    op.execute("""
    CREATE TABLE field_risk_scores (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
        crop_cycle_id UUID REFERENCES crop_cycles(id) ON DELETE SET NULL,
        score_date DATE NOT NULL,
        overall_score NUMERIC(5, 2) NOT NULL CHECK (overall_score BETWEEN 0 AND 100),
        risk_trend VARCHAR(20),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE alerts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        field_id UUID REFERENCES fields(id) ON DELETE CASCADE,
        alert_type alert_type NOT NULL,
        severity alert_severity NOT NULL,
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        acknowledged BOOLEAN DEFAULT FALSE,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

def downgrade() -> None:
    """Downgrade schema."""
    # Drop in reverse order of creation
    op.execute("DROP TABLE IF EXISTS alerts CASCADE;")
    op.execute("DROP TABLE IF EXISTS field_risk_scores CASCADE;")
    op.execute("DROP TABLE IF EXISTS escrow_field_conditions CASCADE;")
    op.execute("DROP TABLE IF EXISTS order_field_sources CASCADE;")
    op.execute("DROP TABLE IF EXISTS crop_cycle_products CASCADE;")
    op.execute("DROP TABLE IF EXISTS knowledge_articles CASCADE;")
    op.execute("DROP TABLE IF EXISTS advisory_messages CASCADE;")
    op.execute("DROP TABLE IF EXISTS advisory_sessions CASCADE;")
    op.execute("DROP TABLE IF EXISTS weather_snapshots CASCADE;")
    op.execute("DROP TABLE IF EXISTS weather_forecasts CASCADE;")
    op.execute("DROP TABLE IF EXISTS soil_readings CASCADE;")
    op.execute("DROP TABLE IF EXISTS treatment_recommendations CASCADE;")
    op.execute("DROP TABLE IF EXISTS pest_disease_reports CASCADE;")
    op.execute("DROP TABLE IF EXISTS ndvi_snapshots CASCADE;")
    op.execute("DROP TABLE IF EXISTS task_dependencies CASCADE;")
    op.execute("DROP TABLE IF EXISTS farm_tasks CASCADE;")
    op.execute("DROP TABLE IF EXISTS crop_cycles CASCADE;")
    op.execute("DROP TABLE IF EXISTS fields CASCADE;")
    op.execute("DROP TABLE IF EXISTS farms CASCADE;")