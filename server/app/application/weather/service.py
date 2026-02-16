"""
Weather Service - Open-Meteo Integration with Farm/Field Support
Farm Connect AgriManagement

Provides weather forecasting, historical data, agricultural risk alerts,
and integrates with Farm and Field entities for location-specific weather.

Features:
- Field-specific weather data with crop-aware alerts
- Pagination support for large datasets
- Retry logic with exponential backoff
- Redis caching support
- Comprehensive error handling
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
import httpx
import json
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

# Open-Meteo API Base URL
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2


class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class WeatherServiceUnavailable(WeatherServiceError):
    """Weather API is unavailable."""
    pass


class WeatherDataNotFound(WeatherServiceError):
    """Weather data not found."""
    pass


class WeatherService:
    """Service for weather data from Open-Meteo and local storage with farm/field integration."""
    
    def __init__(self, db_session=None, redis_client=None):
        self.db_session = db_session
        self.redis_client = redis_client
        self._repo = None
    
    @property
    def repo(self):
        """Lazy load repository to avoid circular imports."""
        if self._repo is None and self.db_session is not None:
            from app.infrastructure.repositories.weather_repo import WeatherRepository
            self._repo = WeatherRepository(self.db_session)
        return self._repo
    
    # ============== Farm/Field Integration ==============
    
    def get_field_weather_data(self, field_id: str) -> Optional[Dict[str, Any]]:
        """
        Get weather data for a specific field, including field and crop info.
        
        Args:
            field_id: The unique identifier of the field
            
        Returns:
            Dictionary containing field, current weather, forecast, and alerts
            
        Raises:
            WeatherServiceError: If database session is not available
        """
        if not self.repo:
            raise WeatherServiceError("Database session not available")
        
        try:
            field = self.repo.get_field_by_id(field_id)
            if not field:
                return None
            
            # Get weather data for the field
            forecast = self.get_field_forecast(field_id)
            current = self.get_field_current_weather(field_id)
            alerts = self.get_field_alerts(field_id)
            
            return {
                "field": field,
                "current_weather": current,
                "forecast": forecast,
                "alerts": alerts,
                "location": {
                    "latitude": field.get("latitude"),
                    "longitude": field.get("longitude")
                }
            }
        except Exception as e:
            logger.error(f"Error getting field weather data for {field_id}: {e}")
            raise WeatherServiceError(f"Failed to get field weather data: {str(e)}")
    
    def _extract_coordinates(self, geojson_data: Any) -> Optional[Tuple[float, float]]:
        """
        Extract (longitude, latitude) from GeoJSON Point data.
        Handles both dictionary and JSON string inputs.
        """
        if not geojson_data:
            return None
            
        try:
            if isinstance(geojson_data, str):
                data = json.loads(geojson_data)
            else:
                data = geojson_data
                
            if data and data.get("type") == "Point" and "coordinates" in data:
                coords = data["coordinates"]
                if len(coords) >= 2:
                    return (float(coords[0]), float(coords[1]))
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            logger.warning(f"Failed to extract coordinates from GeoJSON: {e}")
            
        return None

    
    def get_fields_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Find fields near given coordinates (simple distance check)."""
        # In production, use PostGIS for spatial queries
        # For now, return empty list - would require full table scan
        return []
    
    # ============== Field-Specific Weather ==============
    
    def get_field_current_weather(self, field_id: str) -> Optional[Dict[str, Any]]:
        """Get current weather for a field with caching."""
        if not self.repo:
            raise WeatherServiceError("Database session not available")
        
        try:
            field = self.repo.get_field_by_id(field_id)
            if not field or not field.get("latitude") or not field.get("longitude"):
                return None
            
            # Try to get cached/latest snapshot first
            snapshot = self.repo.get_latest_snapshot(field_id)
            if snapshot:
                # Check if snapshot is recent (within 1 hour)
                if (datetime.now(timezone.utc) - snapshot.recorded_at).total_seconds() < 3600:
                    return self._format_snapshot(snapshot)
            
            # Fetch fresh data from Open-Meteo
            try:
                weather = self._fetch_with_retry(
                    field["latitude"],
                    field["longitude"]
                )
                
                if weather:
                    # Save snapshot to database
                    self.repo.save_snapshot(field_id, {
                        "source": "OPEN_METEO",
                        "recorded_at": datetime.now(timezone.utc),
                        "temperature_c": weather.get("temperature"),
                        "feels_like_c": weather.get("feels_like"),
                        "humidity_pct": weather.get("humidity"),
                        "pressure_hpa": weather.get("pressure"),
                        "wind_speed_mps": weather.get("wind_speed"),
                        "wind_direction_deg": weather.get("wind_direction"),
                        "rainfall_mm": weather.get("rainfall"),
                        "cloud_cover_pct": weather.get("cloud_cover"),
                        "raw_data": weather,
                    })
                    self.repo.commit()
                
                return weather
            except WeatherServiceUnavailable as e:
                logger.error(f"Weather API unavailable for field {field_id}: {e}")
                # Try to return stale cache if available
                if snapshot:
                    return self._format_snapshot(snapshot)
                raise
        except Exception as e:
            logger.error(f"Error fetching current weather for field {field_id}: {e}")
            self.repo.rollback()
            # Include exception type and args for better debugging
            error_msg = str(e) if str(e) else f"{type(e).__name__}: {e.args if e.args else 'Unknown error'}"
            raise WeatherServiceError(f"Failed to get current weather: {error_msg}")
    
    def get_field_forecast(
        self,
        field_id: str,
        days: int = 7
    ) -> Optional[List[Dict[str, Any]]]:
        """Get weather forecast for a field with caching."""
        if not self.repo:
            raise WeatherServiceError("Database session not available")
        
        try:
            field = self.repo.get_field_by_id(field_id)
            if not field or not field.get("latitude") or not field.get("longitude"):
                return None
            
            # Try to get cached forecast
            cached_forecast, _ = self.repo.get_forecasts(field_id, limit=days)
            if cached_forecast:
                # Check if forecast is recent (within 3 hours)
                latest = cached_forecast[0] if cached_forecast else None
                if latest and (datetime.now(timezone.utc) - latest.issued_at).total_seconds() < 10800:
                    return [self._format_forecast(f) for f in cached_forecast[:days]]
            
            # Fetch fresh data from Open-Meteo
            try:
                import asyncio
                try:
                    # Try to get existing event loop
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # No event loop exists, create a new one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run the async fetch
                if loop.is_running():
                    # We're in an async context - use threadsafe approach
                    future = asyncio.run_coroutine_threadsafe(
                        self._fetch_forecast_async(
                            field["latitude"],
                            field["longitude"],
                            days
                        ),
                        loop
                    )
                    forecast_data = future.result(timeout=30)
                else:
                    # No running loop - we can use run_until_complete
                    forecast_data = loop.run_until_complete(
                        self._fetch_forecast_async(
                            field["latitude"],
                            field["longitude"],
                            days
                        )
                    )
                
                # Save forecasts to database
                if forecast_data and forecast_data.get("daily"):
                    for day in forecast_data["daily"]:
                        forecast_date = self._parse_date(day.get("date"))
                        
                        self.repo.save_forecast(field_id, {
                            "source": "OPEN_METEO",
                            "forecast_date": forecast_date,
                            "issued_at": datetime.now(timezone.utc),
                            "temperature_min_c": day.get("temperature_min"),
                            "temperature_max_c": day.get("temperature_max"),
                            "temperature_avg_c": (day.get("temperature_min", 0) + day.get("temperature_max", 0)) / 2,
                            "precipitation_probability_pct": day.get("precipitation_probability"),
                            "precipitation_mm": day.get("precipitation_sum"),
                            "wind_speed_max_mps": day.get("wind_speed_max"),
                            "wind_direction_deg": day.get("wind_direction"),
                            "humidity_avg_pct": day.get("humidity_avg"),
                            "evapotranspiration_mm": day.get("evapotranspiration"),
                        })
                    self.repo.commit()
                
                return forecast_data.get("daily", []) if forecast_data else []
            except WeatherServiceUnavailable as e:
                logger.error(f"Weather API unavailable for field {field_id}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error fetching forecast for field {field_id}: {e}")
            self.repo.rollback()
            # Include exception type and args for better debugging
            error_msg = str(e) if str(e) else f"{type(e).__name__}: {e.args if e.args else 'Unknown error'}"
            raise WeatherServiceError(f"Failed to get forecast: {error_msg}")
    
    def get_field_historical(
        self,
        field_id: str,
        start_date: date,
        end_date: date
    ) -> Optional[Dict[str, Any]]:
        """Get historical weather for a field."""
        if not self.repo:
            raise WeatherServiceError("Database session not available")
        
        try:
            field = self.repo.get_field_by_id(field_id)
            if not field or not field.get("latitude") or not field.get("longitude"):
                return None
            
            # Check for cached historical data first
            snapshots, _ = self.repo.get_snapshots(field_id, start_date, end_date)
            if snapshots and len(snapshots) > 0:
                return {
                    "field_id": field_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "source": "database",
                    "data": [self._format_snapshot(s) for s in snapshots]
                }
            
            # Fetch from Open-Meteo
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    historical = asyncio.run_coroutine_threadsafe(
                        self._fetch_historical_async(
                            field["latitude"],
                            field["longitude"],
                            start_date,
                            end_date
                        ),
                        loop
                    ).result(timeout=30)
                else:
                    historical = loop.run_until_complete(
                        self._fetch_historical_async(
                            field["latitude"],
                            field["longitude"],
                            start_date,
                            end_date
                        )
                    )
                
                # Save to database
                if historical and historical.get("daily"):
                    for day in historical["daily"]:
                        day_date = self._parse_date(day.get("date"))
                        
                        self.repo.save_snapshot(field_id, {
                            "source": "OPEN_METEO",
                            "recorded_at": datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc),
                            "temperature_c": day.get("temperature_avg"),
                            "temperature_min_c": day.get("temperature_min"),
                            "temperature_max_c": day.get("temperature_max"),
                            "rainfall_mm": day.get("precipitation_sum"),
                            "wind_speed_mps": day.get("wind_speed_max"),
                            "raw_data": day,
                        })
                    self.repo.commit()
                
                return historical
            except WeatherServiceUnavailable as e:
                logger.error(f"Weather API unavailable for field {field_id}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error fetching historical weather for field {field_id}: {e}")
            self.repo.rollback()
            raise WeatherServiceError(f"Failed to get historical weather: {str(e)}")
    
    # ============== Agricultural Alerts ==============
    
    def get_field_alerts(self, field_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get weather alerts for a field based on forecast and crop info.
        
        Args:
            field_id: The unique identifier of the field
            limit: Maximum number of alerts to return
            
        Returns:
            List of weather alerts sorted by severity and time
        """
        if not self.repo:
            raise WeatherServiceError("Database session not available")
        
        try:
            field = self.repo.get_field_by_id(field_id)
            if not field:
                return []
            
            alerts = []
            
            # Get weather data - handle errors gracefully
            try:
                forecast = self.get_field_forecast(field_id, days=5)
            except WeatherServiceError:
                forecast = None
                
            try:
                current = self.get_field_current_weather(field_id)
            except WeatherServiceError:
                current = None
            
            # Get crop info for crop-specific alerts
            crop_info = field.get("active_crop", {})
            crop_name = crop_info.get("crop_name", "").lower() if crop_info else ""
            
            # Check current conditions
            if current:
                alerts.extend(self._check_current_conditions(
                    field_id, current, crop_name
                ))
            
            # Check forecast for upcoming risks
            if forecast:
                alerts.extend(self._check_forecast_risks(
                    field_id, forecast, crop_name
                ))
            
            # Sort alerts by severity (critical > high > medium > low) and limit
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            alerts.sort(key=lambda x: (severity_order.get(x.get("severity", "low"), 3), x.get("start_time", "")))
            
            return alerts[:limit]
        except Exception as e:
            logger.error(f"Error getting field alerts for {field_id}: {e}")
            return []
    
    def _check_current_conditions(
        self,
        field_id: str,
        current: Dict[str, Any],
        crop_name: str
    ) -> List[Dict[str, Any]]:
        """Check current weather conditions for alerts."""
        alerts = []
        
        temp = current.get("temperature", 20)
        
        # Frost alerts
        if temp < 0:
            alerts.append({
                "id": str(uuid4()),
                "field_id": field_id,
                "alert_type": "FROST_ALERT",
                "severity": "CRITICAL" if temp < -5 else "WARNING",
                "title": "Frost Warning",
                "message": f"Temperature is {temp}°C. Protect sensitive crops.",
                "data": {"temperature": temp}
            })
        
        # Heat stress
        if temp > 40:
            alerts.append({
                "id": str(uuid4()),
                "field_id": field_id,
                "alert_type": "HEAT_STRESS",
                "severity": "CRITICAL",
                "title": "Extreme Heat Warning",
                "message": f"Temperature is {temp}°C. Ensure adequate irrigation.",
                "data": {"temperature": temp}
            })
        
        # Heavy rainfall
        rainfall = current.get("rainfall", 0)
        if rainfall > 50:
            alerts.append({
                "id": str(uuid4()),
                "field_id": field_id,
                "alert_type": "HEAVY_RAIN",
                "severity": "WARNING",
                "title": "Heavy Rain Alert",
                "message": f"Heavy rainfall of {rainfall}mm recorded.",
                "data": {"rainfall": rainfall}
            })
        
        return alerts
    
    def _check_forecast_risks(
        self,
        field_id: str,
        forecast: List[Dict[str, Any]],
        crop_name: str
    ) -> List[Dict[str, Any]]:
        """Check forecast for upcoming weather risks."""
        alerts = []
        
        # Crop-specific temperature thresholds
        crop_thresholds = {
            "tomato": {"frost": 5, "heat": 35, "optimal_min": 15, "optimal_max": 30},
            "pepper": {"frost": 5, "heat": 35, "optimal_min": 18, "optimal_max": 30},
            "corn": {"frost": 10, "heat": 38, "optimal_min": 18, "optimal_max": 32},
            "wheat": {"frost": -2, "heat": 35, "optimal_min": 10, "optimal_max": 25},
            "rice": {"frost": 10, "heat": 40, "optimal_min": 20, "optimal_max": 35},
            "potato": {"frost": 2, "heat": 30, "optimal_min": 10, "optimal_max": 22},
        }
        
        thresholds = crop_thresholds.get(crop_name, {
            "frost": 0, "heat": 38, "optimal_min": 10, "optimal_max": 30
        })
        
        for day in forecast:
            temp_min = day.get("temperature_min", 20)
            temp_max = day.get("temperature_max", 20)
            precip = day.get("precipitation_sum", 0)
            date_str = day.get("date")
            
            # Frost risk
            if temp_min < thresholds["frost"]:
                alerts.append({
                    "id": str(uuid4()),
                    "field_id": field_id,
                    "alert_type": "FROST_ALERT",
                    "severity": "WARNING",
                    "title": "Frost Risk Forecast",
                    "message": f"Frost expected on {date_str}. Min temp: {temp_min}°C",
                    "data": {"date": date_str, "temperature_min": temp_min}
                })
            
            # Heat risk
            if temp_max > thresholds["heat"]:
                alerts.append({
                    "id": str(uuid4()),
                    "field_id": field_id,
                    "alert_type": "HEAT_STRESS",
                    "severity": "WARNING",
                    "title": "Heat Risk Forecast",
                    "message": f"High temperature expected on {date_str}. Max temp: {temp_max}°C",
                    "data": {"date": date_str, "temperature_max": temp_max}
                })
            
            # Heavy rain
            if precip > 30:
                alerts.append({
                    "id": str(uuid4()),
                    "field_id": field_id,
                    "alert_type": "HEAVY_RAIN",
                    "severity": "INFO",
                    "title": "Heavy Rain Expected",
                    "message": f"Heavy rainfall ({precip}mm) expected on {date_str}",
                    "data": {"date": date_str, "precipitation": precip}
                })
        
        return alerts
    
    def generate_field_risk_scores(self, field_id: str) -> Dict[str, Any]:
        """Generate risk scores for a field based on weather."""
        if not self.repo:
            raise WeatherServiceError("Database session not available")
        
        try:
            field = self.repo.get_field_by_id(field_id)
            if not field:
                return None
            
            forecast = self.get_field_forecast(field_id, days=7)
            
            # Calculate overall risk score (0-100, lower is better)
            risk_score = 0
            risk_factors = []
            
            if forecast:
                for day in forecast:
                    temp_min = day.get("temperature_min", 20)
                    temp_max = day.get("temperature_max", 20)
                    precip = day.get("precipitation_sum", 0)
                    
                    # Temperature stress
                    if temp_min < 5 or temp_max > 38:
                        risk_score += 10
                        if "Temperature stress" not in risk_factors:
                            risk_factors.append("Temperature stress")
                    
                    # Drought risk
                    if precip == 0 and day == forecast[0]:
                        risk_score += 5
                        if "No precipitation expected" not in risk_factors:
                            risk_factors.append("No precipitation expected")
                    
                    # Excessive rain
                    if precip > 50:
                        risk_score += 10
                        if "Excessive rainfall" not in risk_factors:
                            risk_factors.append("Excessive rainfall")
            
            # Save risk score
            self.repo.save_risk_score({
                "field_id": field_id,
                "crop_cycle_id": field.get("active_crop", {}).get("id") if field.get("active_crop") else None,
                "score_date": date.today(),
                "overall_score": min(100, risk_score),
                "risk_trend": "stable" if risk_score < 30 else "increasing",
                "metadata": {
                    "risk_factors": risk_factors,
                    "forecast_days": len(forecast) if forecast else 0
                }
            })
            self.repo.commit()
            
            return {
                "field_id": field_id,
                "risk_score": min(100, risk_score),
                "risk_level": "low" if risk_score < 30 else "medium" if risk_score < 60 else "high",
                "risk_factors": risk_factors
            }
        except Exception as e:
            logger.error(f"Error generating risk scores for field {field_id}: {e}")
            self.repo.rollback()
            raise WeatherServiceError(f"Failed to generate risk scores: {str(e)}")
    
    # ============== API Methods with Retry Logic ==============
    
    async def _fetch_with_retry(
        self, 
        latitude: float, 
        longitude: float,
        max_retries: int = MAX_RETRIES
    ) -> Dict[str, Any]:
        """Fetch current weather with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await self._fetch_current_weather(latitude, longitude)
            except httpx.HTTPStatusError as e:
                last_exception = e
                if e.response.status_code >= 500:
                    # Server error, retry
                    wait_time = RETRY_BACKOFF_FACTOR ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
                    await self._sleep(wait_time)
                else:
                    # Client error, don't retry
                    raise WeatherServiceError(f"HTTP error: {e.response.status_code}")
            except httpx.RequestError as e:
                last_exception = e
                wait_time = RETRY_BACKOFF_FACTOR ** attempt
                logger.warning(f"Network error on attempt {attempt + 1}, retrying in {wait_time}s")
                await self._sleep(wait_time)
        
        raise WeatherServiceUnavailable(f"Failed after {max_retries} attempts: {last_exception}")
    
    async def _sleep(self, seconds: float):
        """Async sleep for retry backoff."""
        import asyncio
        await asyncio.sleep(seconds)
    
    async def _fetch_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch current weather from Open-Meteo."""
        url = f"{OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
                       "rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,"
                       "surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            
            return {
                "temperature": current.get("temperature_2m", 0),
                "feels_like": current.get("apparent_temperature", 0),
                "humidity": current.get("relative_humidity_2m", 0),
                "pressure": current.get("pressure_msl", 0),
                "wind_speed": current.get("wind_speed_10m", 0),
                "wind_direction": current.get("wind_direction_10m", 0),
                "cloud_cover": current.get("cloud_cover", 0),
                "rainfall": current.get("precipitation", 0),
                "weather_code": current.get("weather_code", 0),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _fetch_forecast_async(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Dict[str, Any]:
        """Fetch weather forecast from Open-Meteo."""
        url = f"{OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,"
                     "showers_sum,snowfall_sum,precipitation_probability_max,"
                     "wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,"
                     "sunrise,sunset,uv_index_max,weather_code,et0_fao_evapotranspiration",
            "timezone": "auto",
            "forecast_days": days
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            return {"daily": self._format_daily_forecast(daily)}
    
    async def _fetch_historical_async(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get historical weather data from Open-Meteo archive."""
        # Limit to 30 days max
        if (end_date - start_date).days > 30:
            end_date = start_date + timedelta(days=30)
        
        url = f"{OPEN_METEO_BASE_URL}/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                     "wind_speed_10m_max,weather_code",
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            return {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "daily": self._format_daily_forecast(daily)
            }
    
    def _parse_date(self, date_str) -> date:
        """Parse date string to date object."""
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, str):
            return datetime.fromisoformat(date_str).date()
        return date.today()
    
    def _format_daily_forecast(self, daily: Dict) -> List[Dict[str, Any]]:
        """Format daily forecast data from Open-Meteo response."""
        dates = daily.get("time", [])
        result = []
        
        for i, date_str in enumerate(dates):
            result.append({
                "date": date_str,
                "temperature_max": daily.get("temperature_2m_max", [None]*len(dates))[i],
                "temperature_min": daily.get("temperature_2m_min", [None]*len(dates))[i],
                "temperature_avg": (
                    (daily.get("temperature_2m_max", [0]*len(dates))[i] or 0) +
                    (daily.get("temperature_2m_min", [0]*len(dates))[i] or 0)
                ) / 2 if daily.get("temperature_2m_max") else None,
                "precipitation_probability": daily.get("precipitation_probability_max", [None]*len(dates))[i],
                "precipitation_sum": daily.get("precipitation_sum", [None]*len(dates))[i],
                "rainfall": daily.get("rain_sum", [None]*len(dates))[i],
                "snowfall": daily.get("snowfall_sum", [None]*len(dates))[i],
                "wind_speed_max": daily.get("wind_speed_10m_max", [None]*len(dates))[i],
                "wind_gusts_max": daily.get("wind_gusts_10m_max", [None]*len(dates))[i],
                "wind_direction": daily.get("wind_direction_10m_dominant", [None]*len(dates))[i],
                "sunrise": daily.get("sunrise", [None]*len(dates))[i],
                "sunset": daily.get("sunset", [None]*len(dates))[i],
                "uv_index_max": daily.get("uv_index_max", [None]*len(dates))[i],
                "weather_code": daily.get("weather_code", [None]*len(dates))[i],
                "evapotranspiration": daily.get("et0_fao_evapotranspiration", [None]*len(dates))[i]
            })
        
        return result
    
    def _format_forecast(self, forecast_orm) -> Dict[str, Any]:
        """Format forecast ORM to dict."""
        return {
            "id": forecast_orm.id,
            "forecast_date": forecast_orm.forecast_date.isoformat() if forecast_orm.forecast_date else None,
            "temperature_min": float(forecast_orm.temperature_min_c) if forecast_orm.temperature_min_c else None,
            "temperature_max": float(forecast_orm.temperature_max_c) if forecast_orm.temperature_max_c else None,
            "temperature_avg": float(forecast_orm.temperature_avg_c) if forecast_orm.temperature_avg_c else None,
            "precipitation_probability": float(forecast_orm.precipitation_probability_pct) if forecast_orm.precipitation_probability_pct else None,
            "precipitation_sum": float(forecast_orm.precipitation_mm) if forecast_orm.precipitation_mm else None,
            "wind_speed_max": float(forecast_orm.wind_speed_max_mps) if forecast_orm.wind_speed_max_mps else None,
            "wind_direction": forecast_orm.wind_direction_deg,
            "humidity_avg": float(forecast_orm.humidity_avg_pct) if forecast_orm.humidity_avg_pct else None,
            "risk_type": forecast_orm.risk_type,
            "risk_level": forecast_orm.risk_level,
        }
    
    def _format_snapshot(self, snapshot_orm) -> Dict[str, Any]:
        """Format snapshot ORM to dict."""
        return {
            "id": snapshot_orm.id,
            "recorded_at": snapshot_orm.recorded_at.isoformat() if snapshot_orm.recorded_at else None,
            "temperature": float(snapshot_orm.temperature_c) if snapshot_orm.temperature_c else None,
            "feels_like": float(snapshot_orm.feels_like_c) if snapshot_orm.feels_like_c else None,
            "humidity": float(snapshot_orm.humidity_pct) if snapshot_orm.humidity_pct else None,
            "pressure": float(snapshot_orm.pressure_hpa) if snapshot_orm.pressure_hpa else None,
            "wind_speed": float(snapshot_orm.wind_speed_mps) if snapshot_orm.wind_speed_mps else None,
            "wind_direction": snapshot_orm.wind_direction_deg,
            "rainfall": float(snapshot_orm.rainfall_mm) if snapshot_orm.rainfall_mm else None,
            "cloud_cover": float(snapshot_orm.cloud_cover_pct) if snapshot_orm.cloud_cover_pct else None,
            "source": snapshot_orm.source,
        }
    
    # ============== Standalone Methods (no DB) ==============
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather (standalone, no DB)."""
        return await self._fetch_current_weather(latitude, longitude)
    
    async def get_forecast(
        self, 
        latitude: float, 
        longitude: float, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get weather forecast (standalone, no DB)."""
        return await self._fetch_forecast_async(latitude, longitude, days)
    
    async def get_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get historical weather (standalone, no DB)."""
        return await self._fetch_historical_async(latitude, longitude, start_date, end_date)
    
    async def calculate_gdd(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        base_temp: float = 10.0
    ) -> Dict[str, Any]:
        """Calculate Growing Degree Days."""
        historical = await self.get_historical(latitude, longitude, start_date, end_date)
        daily_data = historical.get("daily", []) if isinstance(historical, dict) else []
        
        total_gdd = 0
        daily_gdd = []
        
        for day in daily_data:
            temp_max = day.get("temperature_max", base_temp)
            temp_min = day.get("temperature_min", base_temp)
            
            avg_temp = (temp_max + temp_min) / 2
            gdd = max(0, avg_temp - base_temp)
            
            total_gdd += gdd
            daily_gdd.append({
                "date": day.get("date"),
                "gdd": round(gdd, 1),
                "avg_temp": avg_temp
            })
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "base_temperature": base_temp,
            "total_gdd": round(total_gdd, 1),
            "daily": daily_gdd
        }
    
    async def get_agricultural_advice(
        self,
        latitude: float,
        longitude: float,
        crop_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get agricultural weather advice."""
        try:
            forecast = await self.get_forecast(latitude, longitude, days=5)
            daily = forecast.get("daily", []) if isinstance(forecast, dict) else []
            
            advice = []
            for day_data in daily:
                date_str = day_data.get("date")
                temp_max = day_data.get("temperature_max", 20)
                temp_min = day_data.get("temperature_min", 10)
                precip = day_data.get("precipitation_sum", 0)
                wind_max = day_data.get("wind_speed_max", 0)
                
                daily_advice = []
                risk_level = "low"
                actions = []
                
                if temp_max > 35:
                    daily_advice.append("High temperature - ensure adequate irrigation")
                    risk_level = "medium"
                    actions.append("Water crops in early morning or evening")
                elif temp_max < 5:
                    daily_advice.append("Low temperature - monitor for frost risk")
                    risk_level = "medium"
                
                if precip > 20:
                    daily_advice.append("Heavy rain expected - avoid field work")
                    actions.append("Check drainage for waterlogging")
                elif precip == 0:
                    daily_advice.append("No rain expected - consider irrigation")
                    if crop_type in ["vegetables", "tomato", "pepper"]:
                        actions.append("Priority irrigation for vegetables")
                
                if wind_max > 50:
                    daily_advice.append("Strong winds - secure tall crops")
                    risk_level = "medium"
                    actions.append("Check stake/trellis support")
                
                if not daily_advice:
                    daily_advice.append("Favorable weather for field activities")
                
                advice.append({
                    "date": date_str,
                    "advice": daily_advice,
                    "risk_level": risk_level,
                    "recommended_actions": actions
                })
            
            return advice
            
        except Exception as e:
            logger.error(f"Error generating agricultural advice: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for weather service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{OPEN_METEO_BASE_URL}/forecast",
                    params={"latitude": 0, "longitude": 0, "current": "temperature_2m"},
                    timeout=5.0
                )
                status = "healthy" if response.status_code == 200 else "degraded"
        except Exception as e:
            status = "unhealthy"
        
        return {
            "status": status,
            "provider": "Open-Meteo",
            "api_url": OPEN_METEO_BASE_URL
        }
    
    # ============== NEW: Historical Weather & Farm Summaries ==============
    
    def get_field_historical_weather(
        self,
        field_id: str,
        start_date: date,
        end_date: date,
        page: int = 1,
        page_size: int = 100
    ) -> Tuple[List[Dict], Dict]:
        """
        Get historical weather data for a field from database.
        
        Returns stored weather snapshots (not live API data).
        """
        snapshots, pagination = self.repo.get_snapshots(
            field_id=field_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        # Convert to dict format
        results = []
        for snapshot in snapshots:
            results.append({
                'id': str(snapshot.id),
                'field_id': str(snapshot.field_id),
                'source': snapshot.source,
                'recorded_at': snapshot.recorded_at.isoformat() if snapshot.recorded_at else None,
                'temperature_c': float(snapshot.temperature_c) if snapshot.temperature_c else None,
                'humidity_pct': float(snapshot.humidity_pct) if snapshot.humidity_pct else None,
                'rainfall_mm': float(snapshot.rainfall_mm) if snapshot.rainfall_mm else None,
                'wind_speed_kmh': float(snapshot.wind_speed_mps) * 3.6 if snapshot.wind_speed_mps else None,
                'solar_radiation_wm2': None,  # Not in current schema
                'evapotranspiration_mm': float(snapshot.evapotranspiration_mm) if snapshot.evapotranspiration_mm else None,
            })
        
        return results, pagination
    
    def get_farm_weather_summary(self, farm_id: str) -> Dict[str, Any]:
        """
        Get weather summary for all fields in a farm.
        
        Optimizes API calls if fields are clustered together (<10km).
        """
        # Get farm and its fields
        from app.infrastructure.repositories.farm_repo import FarmRepository
        farm_repo = FarmRepository(self.db_session)
        
        farm = farm_repo.get_by_id(farm_id)
        if not farm:
            raise ValueError(f"Farm {farm_id} not found")
        
        fields = farm_repo.get_fields_by_farm_id(farm_id)
        
        if len(fields) == 0:
            return {"type": "empty", "fields": [], "weather": None}
        
        # Check if fields are clustered (within 10km)
        if self._fields_are_clustered(fields, max_distance_km=10):
            # Use single weather query at farm centroid
            centroid = self._calculate_centroid(fields)
            
            try:
                # Get current weather for farm centroid
                weather_forecast = self.get_field_forecast(fields[0].id, days=7)
                
                return {
                    "type": "aggregated",
                    "location": centroid,
                    "fields_count": len(fields),
                    "weather": weather_forecast,
                    "note": "Fields are clustered - using farm-level weather"
                }
            except Exception as e:
                logger.error(f"Failed to fetch farm weather: {e}")
                # Fallback to per-field
        
        # Fields are spread out - get weather for each
        field_weather = {}
        for field in fields:
            try:
                field_weather[str(field.id)] = self.get_field_current_weather(str(field.id))
            except Exception as e:
                logger.warning(f"Failed to fetch weather for field {field.id}: {e}")
                field_weather[str(field.id)] = None
        
        return {
            "type": "per_field",
            "fields_count": len(fields),
            "weather_by_field": field_weather
        }
    
    def validate_weather_data(self, data: Dict) -> List[str]:
        """
        Validate weather data is within reasonable ranges.
        
        Returns list of warning messages for out-of-range values.
        """
        warnings = []
        
        # Temperature validation (-60°C to 60°C)
        if 'temperature_c' in data and data['temperature_c'] is not None:
            temp = float(data['temperature_c'])
            if temp < -60 or temp > 60:
                warnings.append(f"Temperature {temp}°C outside valid range (-60 to 60)")
        
        # Rainfall validation (0 to 1000mm)
        if 'rainfall_mm' in data and data['rainfall_mm'] is not None:
            rain = float(data['rainfall_mm'])
            if rain < 0 or rain > 1000:
                warnings.append(f"Rainfall {rain}mm outside valid range (0 to 1000)")
        
        # Humidity validation (0 to 100%)
        if 'humidity_pct' in data and data['humidity_pct'] is not None:
            humidity = float(data['humidity_pct'])
            if humidity < 0 or humidity > 100:
                warnings.append(f"Humidity {humidity}% outside valid range (0 to 100)")
        
        # Wind speed validation (0 to 500 km/h)
        if 'wind_speed_kmh' in data and data['wind_speed_kmh'] is not None:
            wind = float(data['wind_speed_kmh'])
            if wind < 0 or wind > 500:
                warnings.append(f"Wind speed {wind}km/h outside valid range (0 to 500)")
        
        # Pressure validation (800 to 1100 hPa)
        if 'pressure_hpa' in data and data['pressure_hpa'] is not None:
            pressure = float(data['pressure_hpa'])
            if pressure < 800 or pressure > 1100:
                warnings.append(f"Pressure {pressure}hPa outside valid range (800 to 1100)")
        
        return warnings
    
    def _fields_are_clustered(self, fields: List, max_distance_km: float = 10) -> bool:
        """
        Check if all fields are within max_distance_km of each other.
        
        Uses Haversine formula for distance calculation.
        """
        if len(fields) <= 1:
            return True
        
        # Extract coordinates
        coords = []
        for field in fields:
            coord = self._extract_coordinates(field.centroid_geojson)
            if coord:
                coords.append(coord)  # (lng, lat)
        
        if len(coords) <= 1:
            return True
        
        # Check max distance between any two points
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate distance in km between two lat/lng points"""
            R = 6371  # Earth radius in km
            
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        for i in range(len(coords)):
            for j in range(i+1, len(coords)):
                distance = haversine_distance(
                    coords[i][1], coords[i][0],  # lat1, lon1
                    coords[j][1], coords[j][0]   # lat2, lon2
                )
                if distance > max_distance_km:
                    return False
        
        return True
    
    def _calculate_centroid(self, fields: List) -> Dict[str, float]:
        """
        Calculate geographic centroid of fields.
        
        Returns dict with 'lat' and 'lng' keys.
        """
        lats, lngs = [], []
        
        for field in fields:
            coords = self._extract_coordinates(field.centroid_geojson)
            if coords:
                lngs.append(coords[0])
                lats.append(coords[1])
        
        if not lats:
            raise ValueError("No valid coordinates found")
        
        return {
            'lat': sum(lats) / len(lats),
            'lng': sum(lngs) / len(lngs)
        }
