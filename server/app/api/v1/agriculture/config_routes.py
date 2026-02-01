from fastapi import APIRouter, Depends
from app.core.auth.dependencies import require_roles
from app.core.config.agriculture_config import agriculture_config

router = APIRouter()

@router.get("/config")
def get_agriculture_config(
    current_user: dict = Depends(require_roles(["ADMIN"]))
):
    """Get current agricultural intelligence configuration (Admin only)"""
    return {
        "weather": {
            "provider": agriculture_config.weather_provider,
            "api_timeout": agriculture_config.weather_api_timeout
        },
        "features": {
            "ndvi_monitoring": agriculture_config.enable_ndvi_monitoring,
            "weather_alerts": agriculture_config.enable_weather_alerts,
            "advisory_system": agriculture_config.enable_advisory_system
        },
        "alerts": {
            "retention_days": agriculture_config.alert_retention_days,
            "critical_alert_email": agriculture_config.critical_alert_email
        }
    }


@router.get("/health")
def agriculture_health_check():
    """Health check for agricultural intelligence features"""
    return {
        "status": "healthy",
        "features_enabled": {
            "ndvi_monitoring": agriculture_config.enable_ndvi_monitoring,
            "weather_alerts": agriculture_config.enable_weather_alerts,
            "advisory_system": agriculture_config.enable_advisory_system
        }
    }
