"""
Tests for Weather Service Enhancements
Tests historical weather, farm summaries, and data validation
"""
import pytest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.application.weather.service import WeatherService
from app.infrastructure.db.models.weather import WeatherSnapshotORM
from app.infrastructure.db.models.farm import FieldORM, FarmORM
from app.infrastructure.repositories.weather_repo import WeatherRepository


# ============== Fixtures ==============

@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def weather_service(mock_db_session):
    """Create a WeatherService instance with mocked DB"""
    return WeatherService(db_session=mock_db_session)


@pytest.fixture
def sample_field():
    """Create a sample field for testing"""
    field = FieldORM(
        id=uuid4(),
        name="Test Field",
        farm_id=uuid4(),
        centroid_geojson='{"type": "Point", "coordinates": [-74.0060, 40.7128]}',
        boundary_geojson='{"type": "Polygon", "coordinates": [[[-74.01, 40.71], [-74.00, 40.71], [-74.00, 40.72], [-74.01, 40.72], [-74.01, 40.71]]]}',
        area_hectares=Decimal('10.5')
    )
    return field


@pytest.fixture
def sample_snapshots():
    """Create sample weather snapshots"""
    field_id = uuid4()
    snapshots = []
    
    for i in range(10):
        snapshot = WeatherSnapshotORM(
            id=uuid4(),
            field_id=field_id,
            source="OPEN_METEO",
            recorded_at=datetime.now(timezone.utc) - timedelta(days=i),
            temperature_c=Decimal('20.5') + i,
            humidity_pct=Decimal('65.0'),
            rainfall_mm=Decimal('2.5'),
            wind_speed_mps=Decimal('4.5'),
            evapotranspiration_mm=Decimal('3.2')
        )
        snapshots.append(snapshot)
    
    return snapshots, field_id


# ============== Test Historical Weather ==============

def test_get_field_historical_weather(weather_service, sample_snapshots):
    """Test retrieving historical weather data"""
    snapshots, field_id = sample_snapshots
    
    # Mock repository response
    pagination = {
        'current_page': 1,
        'page_size': 100,
        'total_records': len(snapshots)
    }
    
    weather_service._repo = Mock()
    weather_service._repo.get_snapshots = Mock(return_value=(snapshots, pagination))
    
    # Call the method
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    
    results, returned_pagination = weather_service.get_field_historical_weather(
        field_id=str(field_id),
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=100
    )
    
    # Assertions
    assert len(results) == len(snapshots)
    assert returned_pagination == pagination
    
    # Verify data structure
    first_result = results[0]
    assert 'id' in first_result
    assert 'field_id' in first_result
    assert 'temperature_c' in first_result
    assert 'humidity_pct' in first_result
    assert 'rainfall_mm' in first_result
    assert 'wind_speed_kmh' in first_result
    assert 'source' in first_result
    
    # Verify wind speed conversion from m/s to km/h
    first_snapshot = snapshots[0]
    expected_wind_kmh = float(first_snapshot.wind_speed_mps) * 3.6
    assert first_result['wind_speed_kmh'] == expected_wind_kmh


def test_historical_weather_pagination(weather_service):
    """Test pagination works correctly"""
    field_id = str(uuid4())
    snapshots = []
    
    # Create 250 snapshots
    for i in range(250):
        snapshot = Mock()
        snapshot.id = uuid4()
        snapshot.field_id = field_id
        snapshot.recorded_at = datetime.now(timezone.utc) - timedelta(days=i)
        snapshot.source = "OPEN_METEO"
        snapshot.temperature_c = Decimal('20.0')
        snapshot.temperature_min_c = None
        snapshot.temperature_max_c = None
        snapshot.humidity_pct = Decimal('60.0')
        snapshot.rainfall_mm = Decimal('0.0')
        snapshot.wind_speed_mps = Decimal('3.0')
        snapshot.solar_radiation_wm2 = None
        snapshot.evapotranspiration_mm = None
        snapshots.append(snapshot)
    
    # Mock page 1 (first 100 records)
    page1_snapshots = snapshots[0:100]
    pagination1 = {'current_page': 1, 'page_size': 100, 'total_records': 250}
    
    weather_service._repo = Mock()
    weather_service._repo.get_snapshots = Mock(return_value=(page1_snapshots, pagination1))
    
    results, pagination = weather_service.get_field_historical_weather(
        field_id=field_id,
        start_date=date.today() - timedelta(days=365),
        end_date=date.today(),
        page=1,
        page_size=100
    )
    
    assert len(results) == 100
    assert pagination['current_page'] == 1
    assert pagination['total_records'] == 250


# ============== Test Data Validation ==============

def test_validate_weather_data_valid(weather_service):
    """Test validation with valid weather data"""
    valid_data = {
        'temperature_c': 25.0,
        'rainfall_mm': 10.5,
        'humidity_pct': 70.0,
        'wind_speed_kmh': 15.0,
        'pressure_hpa': 1013.25
    }
    
    warnings = weather_service.validate_weather_data(valid_data)
    assert len(warnings) == 0


def test_validate_weather_data_invalid_temperature(weather_service):
    """Test validation catches invalid temperature"""
    invalid_data = {
        'temperature_c': 150.0  # Too hot!
    }
    
    warnings = weather_service.validate_weather_data(invalid_data)
    assert len(warnings) == 1
    assert "Temperature" in warnings[0]
    assert "150" in warnings[0]


def test_validate_weather_data_invalid_rainfall(weather_service):
    """Test validation catches invalid rainfall"""
    invalid_data = {
        'rainfall_mm': -5.0  # Negative rainfall!
    }
    
    warnings = weather_service.validate_weather_data(invalid_data)
    assert len(warnings) == 1
    assert "Rainfall" in warnings[0]


def test_validate_weather_data_multiple_issues(weather_service):
    """Test validation catches multiple issues"""
    invalid_data = {
        'temperature_c': -100.0,  # Too cold
        'humidity_pct': 150.0,     # Over 100%
        'wind_speed_kmh': 600.0    # Impossibly fast
    }
    
    warnings = weather_service.validate_weather_data(invalid_data)
    assert len(warnings) == 3
    assert any("Temperature" in w for w in warnings)
    assert any("Humidity" in w for w in warnings)
    assert any("Wind" in w for w in warnings)


# ============== Test Field Clustering ==============

def test_fields_are_clustered_single_field(weather_service):
    """Test that a single field is considered clustered"""
    field = Mock()
    field.centroid_geojson = '{"type": "Point", "coordinates": [-74.0060, 40.7128]}'
    
    result = weather_service._fields_are_clustered([field], max_distance_km=10)
    assert result is True


def test_fields_are_clustered_nearby_fields(weather_service):
    """Test that nearby fields are considered clustered"""
    # Two fields in New York City (< 5km apart)
    field1 = Mock()
    field1.centroid_geojson = '{"type": "Point", "coordinates": [-74.0060, 40.7128]}'  # Times Square
    
    field2 = Mock()
    field2.centroid_geojson = '{"type": "Point", "coordinates": [-73.9857, 40.7580]}'  # Central Park
    
    result = weather_service._fields_are_clustered([field1, field2], max_distance_km=10)
    assert result is True


def test_fields_are_not_clustered_distant_fields(weather_service):
    """Test that distant fields are not considered clustered"""
    # New York and Los Angeles (very far apart)
    field1 = Mock()
    field1.centroid_geojson = '{"type": "Point", "coordinates": [-74.0060, 40.7128]}'  # NYC
    
    field2 = Mock()
    field2.centroid_geojson = '{"type": "Point", "coordinates": [-118.2437, 34.0522]}'  # LA
    
    result = weather_service._fields_are_clustered([field1, field2], max_distance_km=10)
    assert result is False


# ============== Test Centroid Calculation ==============

def test_calculate_centroid_single_field(weather_service):
    """Test centroid calculation with single field"""
    field = Mock()
    field.centroid_geojson = '{"type": "Point", "coordinates": [-74.0060, 40.7128]}'
    
    centroid = weather_service._calculate_centroid([field])
    
    assert 'lat' in centroid
    assert 'lng' in centroid
    assert centroid['lat'] == 40.7128
    assert centroid['lng'] == -74.0060


def test_calculate_centroid_multiple_fields(weather_service):
    """Test centroid calculation with multiple fields"""
    field1 = Mock()
    field1.centroid_geojson = '{"type": "Point", "coordinates": [-74.0, 40.0]}'
    
    field2 = Mock()
    field2.centroid_geojson = '{"type": "Point", "coordinates": [-74.0, 42.0]}'
    
    centroid = weather_service._calculate_centroid([field1, field2])
    
    # Average of latitudes: (40.0 + 42.0) / 2 = 41.0
    # Average of longitudes: (-74.0 + -74.0) / 2 = -74.0
    assert centroid['lat'] == 41.0
    assert centroid['lng'] == -74.0


def test_calculate_centroid_no_coordinates(weather_service):
    """Test centroid calculation handles missing coordinates gracefully"""
    field = Mock()
    field.centroid_geojson = None
    
    with pytest.raises(ValueError, match="No valid coordinates found"):
        weather_service._calculate_centroid([field])


# ============== Test Farm Weather Summary ==============

@patch('app.infrastructure.repositories.farm_repo.FarmRepository')
def test_get_farm_weather_summary_clustered(mock_farm_repo_class, weather_service):
    """Test farm weather summary with clustered fields"""
    farm_id = str(uuid4())
    
    # Mock farm
    mock_farm = Mock()
    mock_farm.id = farm_id
    
    # Mock fields (all nearby)
    field1 = Mock()
    field1.id = uuid4()
    field1.centroid_geojson = '{"type": "Point", "coordinates": [-74.00, 40.71]}'
    
    field2 = Mock()
    field2.id = uuid4()
    field2.centroid_geojson = '{"type": "Point", "coordinates": [-74.01, 40.72]}'
    
    fields = [field1, field2]
    
    # Mock repository
    mock_repo = Mock()
    mock_repo.get_by_id = Mock(return_value=mock_farm)
    mock_repo.get_fields_by_farm_id = Mock(return_value=fields)
    mock_farm_repo_class.return_value = mock_repo
    
    # Mock weather service methods
    weather_service.get_field_forecast = Mock(return_value={'forecast': 'data'})
    
    # Call the method
    summary = weather_service.get_farm_weather_summary(farm_id)
    
    # Assertions
    assert summary['type'] == 'aggregated'
    assert summary['fields_count'] == 2
    assert 'location' in summary
    assert 'weather' in summary


@patch('app.infrastructure.repositories.farm_repo.FarmRepository')
def test_get_farm_weather_summary_empty_farm(mock_farm_repo_class, weather_service):
    """Test farm weather summary with no fields"""
    farm_id = str(uuid4())
    
    # Mock farm with no fields
    mock_farm = Mock()
    mock_farm.id = farm_id
    
    mock_repo = Mock()
    mock_repo.get_by_id = Mock(return_value=mock_farm)
    mock_repo.get_fields_by_farm_id = Mock(return_value=[])
    mock_farm_repo_class.return_value = mock_repo
    
    summary = weather_service.get_farm_weather_summary(farm_id)
    
    assert summary['type'] == 'empty'
    assert summary['fields'] == []


@patch('app.infrastructure.repositories.farm_repo.FarmRepository')
def test_get_farm_weather_summary_nonexistent_farm(mock_farm_repo_class, weather_service):
    """Test farm weather summary with non-existent farm"""
    mock_repo = Mock()
    mock_repo.get_by_id = Mock(return_value=None)
    mock_farm_repo_class.return_value = mock_repo
    
    with pytest.raises(ValueError, match="not found"):
        weather_service.get_farm_weather_summary("nonexistent-farm-id")


# ============== Run Tests ==============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
