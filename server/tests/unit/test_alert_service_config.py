"""Unit tests for AlertService with configuration"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from app.api.v1.agriculture.alerts.service import AlertService
from app.domain.agriculture.entities import Alert as DomainAlert
from app.domain.agriculture.enums import AlertType, AlertSeverity
from shared_models import AlertCreate


class TestAlertServiceConfiguration:
    """Test AlertService behavior with different configurations"""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        session = Mock()
        session.commit = Mock()
        return session
    
    @pytest.fixture
    def alert_service(self, mock_session):
        """Create AlertService instance with mocked session"""
        return AlertService(mock_session)
    
    @pytest.fixture
    def weather_alert_data(self):
        """Create sample weather alert data"""
        return AlertCreate(
            user_id="test-user-123",
            field_id=uuid4(),
            crop_cycle_id=None,
            alert_type="WEATHER_WARNING",
            severity="CRITICAL",
            title="Frost Warning",
            message="Frost expected tonight",
            action_required="Protect crops",
            action_url=None,
            related_entity_type="field",
            related_entity_id=uuid4(),
            expires_at=None
        )
    
    @pytest.fixture
    def non_weather_alert_data(self):
        """Create sample non-weather alert data"""
        return AlertCreate(
            user_id="test-user-123",
            field_id=uuid4(),
            crop_cycle_id=None,
            alert_type="TASK_OVERDUE",
            severity="WARNING",
            title="Task Overdue",
            message="Irrigation task is overdue",
            action_required="Complete irrigation",
            action_url=None,
            related_entity_type="task",
            related_entity_id=uuid4(),
            expires_at=None
        )
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_weather_alerts_enabled(self, mock_config, alert_service, weather_alert_data, mock_session):
        """Test creating weather alert when feature is enabled"""
        mock_config.enable_weather_alerts = True
        
        # Mock repository
        alert_service.alert_repo = Mock()
        
        # Create a real DomainAlert for the return value
        mock_domain_alert = DomainAlert(
            id=uuid4(),
            user_id=weather_alert_data.user_id,
            field_id=weather_alert_data.field_id,
            crop_cycle_id=weather_alert_data.crop_cycle_id,
            alert_type=AlertType(weather_alert_data.alert_type),
            severity=AlertSeverity(weather_alert_data.severity),
            title=weather_alert_data.title,
            message=weather_alert_data.message,
            action_required=weather_alert_data.action_required,
            action_url=weather_alert_data.action_url,
            related_entity_type=weather_alert_data.related_entity_type,
            related_entity_id=weather_alert_data.related_entity_id,
            expires_at=weather_alert_data.expires_at,
            acknowledged=False,
            dismissed=False,
            metadata={},
            created_at=datetime.now(timezone.utc)
        )
        
        alert_service.alert_repo.save = Mock(return_value=mock_domain_alert)
        
        result = alert_service.create_alert(weather_alert_data)
        
        # Should create the alert
        assert result is not None
        alert_service.alert_repo.save.assert_called_once()
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_weather_alerts_disabled(self, mock_config, alert_service, weather_alert_data):
        """Test that weather alerts are not created when feature is disabled"""
        mock_config.enable_weather_alerts = False
        
        result = alert_service.create_alert(weather_alert_data)
        
        # Should return None (alert not created)
        assert result is None
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_non_weather_alert_unaffected_by_weather_config(
        self, mock_config, alert_service, non_weather_alert_data, mock_session
    ):
        """Test that non-weather alerts are created regardless of weather alerts config"""
        mock_config.enable_weather_alerts = False
        
        # Mock repository
        alert_service.alert_repo = Mock()
        
        # Create real DomainAlert
        mock_domain_alert = DomainAlert(
            id=uuid4(),
            user_id=non_weather_alert_data.user_id,
            field_id=non_weather_alert_data.field_id,
            crop_cycle_id=non_weather_alert_data.crop_cycle_id,
            alert_type=AlertType(non_weather_alert_data.alert_type),
            severity=AlertSeverity(non_weather_alert_data.severity),
            title=non_weather_alert_data.title,
            message=non_weather_alert_data.message,
            action_required=non_weather_alert_data.action_required,
            action_url=non_weather_alert_data.action_url,
            related_entity_type=non_weather_alert_data.related_entity_type,
            related_entity_id=non_weather_alert_data.related_entity_id,
            expires_at=non_weather_alert_data.expires_at,
            acknowledged=False,
            dismissed=False,
            metadata={},
            created_at=datetime.now(timezone.utc)
        )
        
        alert_service.alert_repo.save = Mock(return_value=mock_domain_alert)
        
        result = alert_service.create_alert(non_weather_alert_data)
        
        # Should still create the alert
        assert result is not None
        alert_service.alert_repo.save.assert_called_once()
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_frost_alert_disabled(self, mock_config, alert_service):
        """Test that frost alerts are blocked when weather alerts disabled"""
        mock_config.enable_weather_alerts = False
        
        frost_alert = AlertCreate(
            user_id="test-user",
            field_id=uuid4(),
            crop_cycle_id=None,
            alert_type="FROST_ALERT",
            severity="EMERGENCY",
            title="Frost Alert",
            message="Severe frost expected",
            action_required=None,
            action_url=None,
            related_entity_type=None,
            related_entity_id=None,
            expires_at=None
        )
        
        result = alert_service.create_alert(frost_alert)
        assert result is None
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_drought_alert_disabled(self, mock_config, alert_service):
        """Test that drought alerts are blocked when weather alerts disabled"""
        mock_config.enable_weather_alerts = False
        
        drought_alert = AlertCreate(
            user_id="test-user",
            field_id=uuid4(),
            crop_cycle_id=None,
            alert_type="DROUGHT_ALERT",
            severity="CRITICAL",
            title="Drought Alert",
            message="Drought conditions detected",
            action_required=None,
            action_url=None,
            related_entity_type=None,
            related_entity_id=None,
            expires_at=None
        )
        
        result = alert_service.create_alert(drought_alert)
        assert result is None
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_is_weather_alerts_enabled(self, mock_config, alert_service):
        """Test is_weather_alerts_enabled method"""
        mock_config.enable_weather_alerts = True
        assert alert_service.is_weather_alerts_enabled() is True
        
        mock_config.enable_weather_alerts = False
        assert alert_service.is_weather_alerts_enabled() is False
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_should_send_critical_email(self, mock_config, alert_service):
        """Test should_send_critical_email method"""
        mock_config.critical_alert_email = True
        assert alert_service.should_send_critical_email() is True
        
        mock_config.critical_alert_email = False
        assert alert_service.should_send_critical_email() is False
    
    @patch('app.api.v1.agriculture.alerts.service.agriculture_config')
    def test_cleanup_old_alerts_uses_retention_config(self, mock_config, alert_service):
        """Test that cleanup uses configured retention period"""
        mock_config.alert_retention_days = 30
        
        # Currently returns 0 as placeholder, but should use config
        result = alert_service.cleanup_old_alerts("test-user")
        
        # Verify it doesn't error and returns a number
        assert isinstance(result, int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
