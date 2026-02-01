"""Agricultural Intelligence Configuration"""
import os
from typing import Optional
from pydantic import BaseModel, Field

class AgricultureConfig(BaseModel):
    """Configuration for agricultural intelligence features"""
    
    # Weather API Configuration
    weather_provider: str = Field(default="open_meteo")
    weather_api_timeout: int = Field(default=30)
    
    # Feature Flags
    enable_ndvi_monitoring: bool = Field(default=True)
    enable_weather_alerts: bool = Field(default=True)
    enable_advisory_system: bool = Field(default=True)
    
    # Alert Configuration
    alert_retention_days: int = Field(default=90)
    critical_alert_email: bool = Field(default=True)
    
    @classmethod
    def from_env(cls) -> "AgricultureConfig":
        """Load configuration from environment variables"""
        return cls(
            weather_provider=os.getenv("WEATHER_PROVIDER", "open_meteo"),
            weather_api_timeout=int(os.getenv("WEATHER_API_TIMEOUT", "30")),
            enable_ndvi_monitoring=os.getenv("ENABLE_NDVI_MONITORING", "true").lower() == "true",
            enable_weather_alerts=os.getenv("ENABLE_WEATHER_ALERTS", "true").lower() == "true",
            enable_advisory_system=os.getenv("ENABLE_ADVISORY_SYSTEM", "true").lower() == "true",
            alert_retention_days=int(os.getenv("ALERT_RETENTION_DAYS", "90")),
            critical_alert_email=os.getenv("CRITICAL_ALERT_EMAIL", "true").lower() == "true",
        )

# Global instance loaded from environment
agriculture_config = AgricultureConfig.from_env()
