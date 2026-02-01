"""Open-Meteo Weather Provider Implementation"""
import httpx
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging

from .provider import WeatherProvider
from app.domain.agriculture.enums import WeatherSource, RiskType, RiskLevel

logger = logging.getLogger(__name__)


class OpenMeteoWeatherProvider(WeatherProvider):
    """Open-Meteo weather provider implementation"""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def get_current_weather(
        self, 
        latitude: Decimal, 
        longitude: Decimal
    ) -> Dict[str, Any]:
        """Fetch current weather conditions from Open-Meteo"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.BASE_URL}/forecast",
                    params={
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "current": [
                            "temperature_2m",
                            "relative_humidity_2m",
                            "apparent_temperature",
                            "precipitation",
                            "rain",
                            "weather_code",
                            "cloud_cover",
                            "pressure_msl",
                            "wind_speed_10m",
                            "wind_direction_10m",
                            "wind_gusts_10m"
                        ],
                        "timezone": "auto"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                current = data.get("current", {})
                return {
                    "temperature_c": current.get("temperature_2m"),
                    "feels_like_c": current.get("apparent_temperature"),
                    "humidity_pct": current.get("relative_humidity_2m"),
                    "pressure_hpa": current.get("pressure_msl"),
                    "wind_speed_mps": current.get("wind_speed_10m"),
                    "wind_direction_deg": current.get("wind_direction_10m"),
                    "wind_gust_mps": current.get("wind_gusts_10m"),
                    "rainfall_mm": current.get("rain", 0),
                    "cloud_cover_pct": current.get("cloud_cover"),
                    "recorded_at": datetime.fromisoformat(current.get("time")),
                    "source": WeatherSource.OPEN_METEO.value
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching current weather: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            raise
    
    async def get_forecast(
        self,
        latitude: Decimal,
        longitude: Decimal,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Fetch weather forecast from Open-Meteo"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.BASE_URL}/forecast",
                    params={
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "daily": [
                            "temperature_2m_max",
                            "temperature_2m_min",
                            "precipitation_sum",
                            "precipitation_probability_max",
                            "wind_speed_10m_max",
                            "wind_gusts_10m_max"
                        ],
                        "forecast_days": days,
                        "timezone": "auto"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                daily = data.get("daily", {})
                forecasts = []
                
                for i in range(len(daily.get("time", []))):
                    forecast = {
                        "forecast_date": date.fromisoformat(daily["time"][i]),
                        "temperature_min_c": daily["temperature_2m_min"][i],
                        "temperature_max_c": daily["temperature_2m_max"][i],
                        "precipitation_mm": daily["precipitation_sum"][i],
                        "precipitation_probability_pct": daily["precipitation_probability_max"][i],
                        "wind_speed_max_mps": daily["wind_speed_10m_max"][i],
                        "issued_at": datetime.now(),
                        "source": WeatherSource.OPEN_METEO.value
                    }
                    
                    # Risk assessment
                    forecast.update(self._assess_risks(forecast))
                    forecasts.append(forecast)
                
                return forecasts
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching forecast: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            raise
    
    async def get_historical(
        self,
        latitude: Decimal,
        longitude: Decimal,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Fetch historical weather data from Open-Meteo"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.BASE_URL}/archive",
                    params={
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": [
                            "temperature_2m_max",
                            "temperature_2m_min",
                            "temperature_2m_mean",
                            "precipitation_sum",
                            "rain_sum",
                            "wind_speed_10m_max",
                            "wind_gusts_10m_max"
                        ],
                        "timezone": "auto"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                daily = data.get("daily", {})
                historical = []
                
                for i in range(len(daily.get("time", []))):
                    record = {
                        "recorded_at": datetime.fromisoformat(daily["time"][i] + "T12:00:00"),
                        "temperature_c": daily["temperature_2m_mean"][i],
                        "temperature_min_c": daily["temperature_2m_min"][i],
                        "temperature_max_c": daily["temperature_2m_max"][i],
                        "rainfall_mm": daily.get("rain_sum", [None])[i],
                        "wind_speed_mps": daily["wind_speed_10m_max"][i],
                        "wind_gust_mps": daily.get("wind_gusts_10m_max", [None])[i],
                        "source": WeatherSource.OPEN_METEO.value
                    }
                    historical.append(record)
                
                return historical
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching historical data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    def _assess_risks(self, forecast: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Simple rule-based risk assessment"""
        risks = []
        risk_level = RiskLevel.MINIMAL.value
        
        temp_min = forecast.get("temperature_min_c")
        temp_max = forecast.get("temperature_max_c")
        precip = forecast.get("precipitation_mm", 0)
        wind = forecast.get("wind_speed_max_mps", 0)
        
        # Frost risk
        if temp_min is not None and temp_min <= 0:
            risks.append(RiskType.FROST.value)
            risk_level = RiskLevel.HIGH.value if temp_min < -2 else RiskLevel.MEDIUM.value
        
        # Heat stress risk
        if temp_max is not None and temp_max >= 35:
            risks.append(RiskType.HEAT_STRESS.value)
            risk_level = RiskLevel.HIGH.value if temp_max > 40 else RiskLevel.MEDIUM.value
        
        # Heavy rain risk
        if precip > 50:
            risks.append(RiskType.HEAVY_RAIN.value)
            risk_level = RiskLevel.HIGH.value if precip > 100 else RiskLevel.MEDIUM.value
        
        # Strong wind risk
        if wind > 15:
            risks.append(RiskType.STRONG_WIND.value)
            risk_level = RiskLevel.HIGH.value if wind > 20 else RiskLevel.MEDIUM.value
        
        return {
            "risk_type": risks[0] if risks else None,
            "risk_level": risk_level,
            "risk_description": ", ".join(risks) if risks else None
        }
