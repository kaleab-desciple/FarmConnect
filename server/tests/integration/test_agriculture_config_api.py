"""Integration tests for agriculture configuration endpoints"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


class TestAgricultureConfigEndpoints:
    """Test agriculture configuration API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def admin_token(self):
        """Mock admin token"""
        # In real tests, you'd generate a proper JWT token
        return "mock-admin-token"
    
    def test_health_check_endpoint(self, client):
        """Test agriculture health check endpoint"""
        response = client.get("/api/v1/agriculture/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "features_enabled" in data
        assert "ndvi_monitoring" in data["features_enabled"]
        assert "weather_alerts" in data["features_enabled"]
        assert "advisory_system" in data["features_enabled"]
    
    @patch('app.api.v1.agriculture.config_routes.agriculture_config')
    def test_health_check_with_disabled_features(self, mock_config, client):
        """Test health check when features are disabled"""
        mock_config.enable_ndvi_monitoring = False
        mock_config.enable_weather_alerts = False
        mock_config.enable_advisory_system = True
        
        response = client.get("/api/v1/agriculture/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["features_enabled"]["ndvi_monitoring"] is False
        assert data["features_enabled"]["weather_alerts"] is False
        assert data["features_enabled"]["advisory_system"] is True
    
    @pytest.mark.skip(reason="Requires authentication setup")
    def test_config_endpoint_requires_admin(self, client):
        """Test that config endpoint requires admin role"""
        response = client.get("/api/v1/agriculture/config")
        
        # Should return 401 or 403 without proper auth
        assert response.status_code in [401, 403]
    
    @pytest.mark.skip(reason="Requires authentication setup")
    def test_config_endpoint_with_admin_token(self, client, admin_token):
        """Test config endpoint with admin authentication"""
        response = client.get(
            "/api/v1/agriculture/config",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "weather" in data
        assert "features" in data
        assert "alerts" in data
        
        # Verify weather config
        assert "provider" in data["weather"]
        assert "api_timeout" in data["weather"]
        
        # Verify features
        assert "ndvi_monitoring" in data["features"]
        assert "weather_alerts" in data["features"]
        assert "advisory_system" in data["features"]
        
        # Verify alerts config
        assert "retention_days" in data["alerts"]
        assert "critical_alert_email" in data["alerts"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
