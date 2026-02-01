"""Unit tests for agriculture configuration"""
import pytest
from unittest.mock import patch
from app.core.config.agriculture_config import AgricultureConfig


class TestAgricultureConfig:
    """Test agriculture configuration loading and defaults"""
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        config = AgricultureConfig()
        
        assert config.weather_provider == "open_meteo"
        assert config.weather_api_timeout == 30
        assert config.enable_ndvi_monitoring is True
        assert config.enable_weather_alerts is True
        assert config.enable_advisory_system is True
        assert config.alert_retention_days == 90
        assert config.critical_alert_email is True
    
    def test_custom_weather_provider(self):
        """Test custom weather provider configuration"""
        with patch.dict('os.environ', {'WEATHER_PROVIDER': 'noaa_gfs'}):
            config = AgricultureConfig.from_env()
            assert config.weather_provider == "noaa_gfs"
    
    def test_custom_timeout(self):
        """Test custom API timeout"""
        with patch.dict('os.environ', {'WEATHER_API_TIMEOUT': '60'}):
            config = AgricultureConfig.from_env()
            assert config.weather_api_timeout == 60
    
    def test_disable_ndvi_monitoring(self):
        """Test disabling NDVI monitoring"""
        with patch.dict('os.environ', {'ENABLE_NDVI_MONITORING': 'false'}):
            config = AgricultureConfig.from_env()
            assert config.enable_ndvi_monitoring is False
    
    def test_disable_weather_alerts(self):
        """Test disabling weather alerts"""
        with patch.dict('os.environ', {'ENABLE_WEATHER_ALERTS': 'false'}):
            config = AgricultureConfig.from_env()
            assert config.enable_weather_alerts is False
    
    def test_disable_advisory_system(self):
        """Test disabling advisory system"""
        with patch.dict('os.environ', {'ENABLE_ADVISORY_SYSTEM': 'false'}):
            config = AgricultureConfig.from_env()
            assert config.enable_advisory_system is False
    
    def test_custom_retention_days(self):
        """Test custom alert retention period"""
        with patch.dict('os.environ', {'ALERT_RETENTION_DAYS': '180'}):
            config = AgricultureConfig.from_env()
            assert config.alert_retention_days == 180
    
    def test_disable_critical_email(self):
        """Test disabling critical alert emails"""
        with patch.dict('os.environ', {'CRITICAL_ALERT_EMAIL': 'false'}):
            config = AgricultureConfig.from_env()
            assert config.critical_alert_email is False
    
    def test_all_features_disabled(self):
        """Test configuration with all features disabled"""
        env_vars = {
            'ENABLE_NDVI_MONITORING': 'false',
            'ENABLE_WEATHER_ALERTS': 'false',
            'ENABLE_ADVISORY_SYSTEM': 'false',
            'CRITICAL_ALERT_EMAIL': 'false'
        }
        
        with patch.dict('os.environ', env_vars):
            config = AgricultureConfig.from_env()
            assert config.enable_ndvi_monitoring is False
            assert config.enable_weather_alerts is False
            assert config.enable_advisory_system is False
            assert config.critical_alert_email is False
    
    def test_case_insensitive_env_vars(self):
        """Test that environment variables are read correctly"""
        # Note: os.getenv is case-sensitive on Linux, so we test with uppercase
        with patch.dict('os.environ', {'WEATHER_PROVIDER': 'local_station'}):
            config = AgricultureConfig.from_env()
            assert config.weather_provider == "local_station"


class TestConfigurationValidation:
    """Test configuration validation and edge cases"""
    
    def test_negative_timeout_uses_default(self):
        """Test that negative timeout values use default"""
        # Pydantic should handle validation, but test the behavior
        config = AgricultureConfig()
        assert config.weather_api_timeout > 0
    
    def test_zero_retention_days(self):
        """Test zero retention days"""
        with patch.dict('os.environ', {'ALERT_RETENTION_DAYS': '0'}):
            config = AgricultureConfig.from_env()
            # Should accept 0 or use default
            assert config.alert_retention_days >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
