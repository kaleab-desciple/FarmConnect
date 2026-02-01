# Agriculture Configuration Tests

This directory contains tests for the agriculture configuration module and related services.

## Test Structure

```
tests/
├── unit/
│   ├── test_agriculture_config.py      # Configuration loading and defaults
│   └── test_alert_service_config.py    # AlertService with config integration
└── integration/
    └── test_agriculture_config_api.py  # API endpoints for configuration
```

## Running Tests

### All Tests
```bash
pytest server/tests/ -v
```

### Unit Tests Only
```bash
pytest server/tests/unit/ -v
```

### Integration Tests Only
```bash
pytest server/tests/integration/ -v
```

### Specific Test File
```bash
pytest server/tests/unit/test_agriculture_config.py -v
```

### With Coverage
```bash
pytest server/tests/ --cov=app.core.config.agriculture --cov-report=html
```

## Test Coverage

### `test_agriculture_config.py`
Tests the `AgricultureConfig` class:
- ✅ Default values
- ✅ Custom environment variables
- ✅ Feature flag toggling
- ✅ Case insensitivity
- ✅ Edge cases and validation

### `test_alert_service_config.py`
Tests `AlertService` integration with configuration:
- ✅ Weather alerts enabled/disabled
- ✅ Different alert types (weather vs non-weather)
- ✅ Frost and drought alert filtering
- ✅ Configuration helper methods
- ✅ Retention period usage

### `test_agriculture_config_api.py`
Tests API endpoints:
- ✅ Health check endpoint
- ✅ Configuration endpoint (admin only)
- ✅ Feature flag visibility
- ✅ Authentication requirements

## Test Data

### Sample Environment Variables
```python
{
    'WEATHER_PROVIDER': 'open_meteo',
    'WEATHER_API_TIMEOUT': '30',
    'ENABLE_NDVI_MONITORING': 'true',
    'ENABLE_WEATHER_ALERTS': 'true',
    'ENABLE_ADVISORY_SYSTEM': 'true',
    'ALERT_RETENTION_DAYS': '90',
    'CRITICAL_ALERT_EMAIL': 'true'
}
```

### Sample Alert Data
```python
AlertCreate(
    user_id="test-user-123",
    alert_type="WEATHER_WARNING",
    severity="CRITICAL",
    title="Frost Warning",
    message="Frost expected tonight"
)
```

## Mocking Strategy

### Configuration Mocking
```python
@patch('app.api.v1.agriculture.alerts.service.agriculture_config')
def test_feature(mock_config):
    mock_config.enable_weather_alerts = False
    # Test with feature disabled
```

### Database Session Mocking
```python
@pytest.fixture
def mock_session():
    session = Mock()
    session.commit = Mock()
    return session
```

## Known Issues

1. **Authentication Tests**: Some tests are skipped because they require full authentication setup
2. **Database Tests**: Integration tests may need a test database

## Future Improvements

- [ ] Add tests for email notification integration
- [ ] Add tests for alert cleanup job
- [ ] Add performance tests for configuration loading
- [ ] Add tests for configuration hot-reloading
- [ ] Add tests for invalid configuration values
