"""
Weather Service API Routes
Farm Connect AgriManagement

Provides weather forecasting, historical data, and agricultural risk alerts.
Integrates with Open-Meteo API for free weather data.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth.dependencies import get_enriched_user, get_optional_user, get_enriched_user, require_auth
from app.core.config import settings


router = APIRouter()


# ============== Request/Response Models ==============

class WeatherForecastRequest(BaseModel):
    """Request for weather forecast"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    forecast_days: int = Field(default=7, ge=1, le=16)
    hourly: bool = Field(default=False)


class WeatherHistoricalRequest(BaseModel):
    """Request for historical weather data"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: date
    end_date: date


class LocationQuery(BaseModel):
    """Query weather by location"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    field_id: Optional[str] = None


class CurrentWeatherResponse(BaseModel):
    """Current weather response"""
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    cloud_cover: int
    rainfall: float
    visibility: float
    uv_index: float
    timestamp: datetime


class DailyForecastResponse(BaseModel):
    """Daily forecast response"""
    date: date
    temperature_max: float
    temperature_min: float
    precipitation_probability: int
    precipitation_sum: float
    rainfall: float
    snowfall: float
    wind_speed_max: float
    wind_gusts_max: float
    wind_direction: int
    sunrise: datetime
    sunset: datetime
    uv_index_max: float
    weather_code: int


class HourlyForecastResponse(BaseModel):
    """Hourly forecast response"""
    time: datetime
    temperature: float
    humidity: int
    precipitation_probability: int
    precipitation: float
    weather_code: int
    wind_speed: float
    wind_direction: int
    cloud_cover: int


class WeatherAlertResponse(BaseModel):
    """Weather alert response"""
    id: str
    alert_type: str
    severity: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    affected_fields: List[str]


class AgriculturalAdviceResponse(BaseModel):
    """Agricultural weather advice"""
    date: date
    advice: List[str]
    risk_level: str
    recommended_actions: List[str]


# ============== Weather API Routes ==============

@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get current weather conditions for a location.
    
    Uses Open-Meteo API for real-time weather data.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    weather = await service.get_current_weather(latitude, longitude)
    
    return weather


@router.get("/forecast", response_model=Dict[str, Any])
async def get_weather_forecast(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(default=7, ge=1, le=16),
    hourly: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get weather forecast for a location.
    
    - **latitude/longitude**: Location coordinates
    - **days**: Number of days (1-16)
    - **hourly**: Include hourly data (increases response size)
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    forecast = await service.get_forecast(latitude, longitude, days, hourly)
    
    return forecast


@router.get("/forecast/daily", response_model=List[DailyForecastResponse])
async def get_daily_forecast(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(default=7, ge=1, le=16),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get daily weather forecast.
    
    Returns daily summaries with high/low temps, precipitation, etc.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    forecast = await service.get_daily_forecast(latitude, longitude, days)
    
    return forecast


@router.get("/forecast/hourly", response_model=List[HourlyForecastResponse])
async def get_hourly_forecast(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    hours: int = Query(default=24, ge=1, le=48),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get hourly weather forecast.
    
    Returns detailed hourly data for the specified number of hours.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    forecast = await service.get_hourly_forecast(latitude, longitude, hours)
    
    return forecast


@router.post("/historical", response_model=Dict[str, Any])
async def get_historical_weather(
    request: WeatherHistoricalRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get historical weather data for a location.
    
    - **start_date/end_date**: Date range (max 30 days)
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    historical = await service.get_historical(
        request.latitude, 
        request.longitude,
        request.start_date,
        request.end_date
    )
    
    return historical


@router.get("/alerts", response_model=List[WeatherAlertResponse])
async def get_weather_alerts(
    field_id: Optional[str] = Query(None, description="Filter by field ID"),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get weather alerts for fields.
    
    Returns active weather alerts that may affect crops.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    alerts = await service.get_alerts(
        field_id=field_id,
        latitude=latitude,
        longitude=longitude
    )
    
    return alerts


@router.get("/alerts/active", response_model=List[WeatherAlertResponse])
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)  # needs system_user_id for alert FK
):
    """
    Get all active weather alerts for user's fields.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    alerts = await service.get_active_alerts(current_user.system_user_id)
    
    return alerts


@router.post("/alerts/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_alerts(
    field_id: str = Query(..., description="Field ID to subscribe"),
    alert_types: List[str] = Query(default=["frost", "heat", "drought", "heavy_rain"]),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)  # needs system_user_id for subscription FK
):
    """
    Subscribe to weather alerts for a field.
    
    - **alert_types**: Types of alerts to receive (frost, heat, drought, heavy_rain, wind, hail)
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    result = await service.subscribe_to_alerts(
        field_id, 
        alert_types,
        current_user.system_user_id
    )
    
    return result


@router.delete("/alerts/subscribe")
async def unsubscribe_from_alerts(
    field_id: str = Query(..., description="Field ID to unsubscribe"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)  # needs system_user_id for subscription FK
):
    """
    Unsubscribe from weather alerts for a field.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    result = await service.unsubscribe_from_alerts(field_id, current_user.system_user_id)
    
    return result


@router.get("/agricultural-advice", response_model=List[AgriculturalAdviceResponse])
async def get_agricultural_advice(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    crop_type: Optional[str] = Query(None, description="Crop type for specific advice"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get agricultural weather advice.
    
    Returns weather-based recommendations for farming activities.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    advice = await service.get_agricultural_advice(latitude, longitude, crop_type)
    
    return advice


@router.get("/growing-degree-days", response_model=Dict[str, Any])
async def get_growing_degree_days(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    base_temp: float = Query(default=10.0, description="Base temperature in Celsius"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Calculate growing degree days (GDD).
    
    Agricultural metric for predicting crop development.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    gdd = await service.calculate_gdd(
        latitude, longitude, start_date, end_date, base_temp
    )
    
    return gdd


@router.get("/evapotranspiration", response_model=Dict[str, Any])
async def get_evapotranspiration(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    date: date = Query(default=None),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get reference evapotranspiration (ET0) data.
    
    Used for irrigation scheduling.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    et0 = await service.get_evapotranspiration(latitude, longitude, date or date.today())
    
    return et0


@router.get("/field/{field_id}/weather", response_model=Dict[str, Any])
async def get_field_weather(
    field_id: str,
    days: int = Query(default=7, ge=1, le=16),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get weather forecast for a specific field.
    
    Uses field's registered GPS coordinates.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    weather = await service.get_field_weather(field_id, days)
    
    return weather


@router.get("/field/{field_id}/history")
async def get_field_weather_history(
    field_id: str,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get historical weather data for a field.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    history = await service.get_field_weather_history(field_id, start_date, end_date)
    
    return history


@router.post("/manual-observation", status_code=status.HTTP_201_CREATED)
async def create_manual_observation(
    field_id: str = Query(..., description="Field ID"),
    temperature: float = Query(..., description="Temperature in Celsius"),
    humidity: Optional[float] = Query(None, ge=0, le=100, description="Humidity %"),
    rainfall: Optional[float] = Query(None, ge=0, description="Rainfall in mm"),
    wind_speed: Optional[float] = Query(None, ge=0, description="Wind speed m/s"),
    notes: Optional[str] = None,
    observed_at: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)  # needs system_user_id for observation FK
):
    """
    Record manual weather observation.
    
    Farmers can log weather observations from local sensors or manual readings.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    observation = await service.create_manual_observation(
        field_id, temperature, humidity, rainfall, wind_speed, 
        notes, observed_at, current_user.system_user_id
    )
    
    return observation


@router.get("/stations/nearby")
async def get_nearby_stations(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get nearby weather stations.
    
    Returns weather stations within specified radius.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db)
    stations = await service.get_nearby_stations(latitude, longitude, radius_km)
    
    return stations


@router.get("/health")
async def weather_health_check():
    """
    Health check for weather service.
    
    Returns status of external weather API connections.
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(None)
    health = await service.health_check()
    
    return health


# ============== Enhanced Farm/Field-Specific Weather Endpoints ==============


@router.get("/fields/{field_id}", response_model=Dict[str, Any])
async def get_field_weather_complete(
    field_id: str,
    days: int = Query(default=7, ge=1, le=14, description="Number of forecast days (1-14)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get complete weather data for a specific field.
    
    Returns current weather, forecast, alerts, and field information.
    Uses field centroid coordinates for weather lookup.
    Includes active crop information for crop-specific alerts.
    
    ## Response Example
    
    ```json
    {
      "field_id": "field_001",
      "field_name": "North Field",
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "current_weather": {
        "temperature": 22.5,
        "humidity": 65,
        "wind_speed": 12.3,
        "precipitation": 0.0,
        "condition": "sunny",
        "timestamp": "2024-01-15T14:30:00Z"
      },
      "forecast": [...],
      "alerts": [...],
      "active_crop": {
        "crop_name": "wheat",
        "variety": "winter",
        "status": "GROWING"
      }
    }
    ```
    
    ## Query Parameters
    - **field_id**: Unique identifier of the field (required)
    - **days**: Number of forecast days, 1-14 (default: 7)
    
    ## Responses
    - **200**: Successfully retrieved weather data
    - **404**: Field not found or has no location coordinates
    - **500**: Internal server error
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db_session=db)
    weather_data = service.get_field_weather_data(field_id)
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found or has no location coordinates"
        )
    
    return weather_data


@router.get("/fields/{field_id}/current", response_model=Dict[str, Any])
async def get_field_current_weather(
    field_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get current weather for a specific field.
    
    Returns cached or fresh current weather data from Open-Meteo API.
    
    ## Response Example
    
    ```json
    {
      "temperature": 22.5,
      "humidity": 65,
      "wind_speed": 12.3,
      "wind_direction": 180,
      "precipitation": 0.0,
      "cloud_cover": 20,
      "pressure": 1013.25,
      "uv_index": 5.0,
      "visibility": 10.0,
      "condition": "sunny",
      "condition_code": 0,
      "is_day": true,
      "timestamp": "2024-01-15T14:30:00Z",
      "source": "open_meteo"
    }
    ```
    
    ## Weather Condition Codes
    - 0: Clear sky
    - 1-3: Mainly clear, partly cloudy, overcast
    - 45-48: Fog
    - 51-67: Drizzle and rain
    - 71-77: Snow
    - 80-82: Rain showers
    - 95-99: Thunderstorm
    
    ## Responses
    - **200**: Successfully retrieved current weather
    - **404**: Field not found or has no location coordinates
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db_session=db)
    weather = service.get_field_current_weather(field_id)
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found or has no location coordinates"
        )
    
    return weather


@router.get("/fields/{field_id}/forecast", response_model=List[Dict[str, Any]])
async def get_field_forecast_weather(
    field_id: str,
    days: int = Query(default=7, ge=1, le=14, description="Forecast days (1-14)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get weather forecast for a specific field.
    
    Returns daily forecast with temperature, precipitation, and risk indicators.
    
    ## Response Example
    
    ```json
    [
      {
        "date": "2024-01-15",
        "temperature": {
          "max": 25.3,
          "min": 18.1,
          "avg": 21.5
        },
        "precipitation": {
          "probability": 30,
          "amount": 2.5,
          "unit": "mm"
        },
        "humidity": 65,
        "wind_speed": 15.2,
        "uv_index": 6.0,
        "sunrise": "06:45",
        "sunset": "18:30",
        "condition": "partly_cloudy",
        "condition_code": 2,
        "risk_indicators": {
          "frost_risk": false,
          "heat_stress_risk": false,
          "rain_risk": true,
          "wind_risk": false
        }
      }
    ]
    ```
    
    ## Query Parameters
    - **field_id**: Unique identifier of the field (required)
    - **days**: Number of forecast days, 1-14 (default: 7)
    
    ## Risk Indicators
    - **frost_risk**: True if min temp < 0°C
    - **heat_stress_risk**: True if max temp > 35°C
    - **rain_risk**: True if precipitation probability > 50%
    - **wind_risk**: True if wind speed > 40 km/h
    
    ## Responses
    - **200**: Successfully retrieved forecast
    - **404**: Field not found or has no location coordinates
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db_session=db)
    forecast = service.get_field_forecast(field_id, days)
    
    if forecast is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found or has no location coordinates"
        )
    
    return forecast


@router.get("/fields/{field_id}/historical", response_model=Dict[str, Any])
async def get_field_historical_weather(
    field_id: str,
    start_date: date = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (max 30 days from start)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get historical weather data for a specific field.
    
    Returns historical weather data with caching for performance.
    Data is cached for 24 hours to reduce API calls.
    
    ## Response Example
    
    ```json
    {
      "field_id": "field_001",
      "start_date": "2024-01-01",
      "end_date": "2024-01-07",
      "daily_data": [
        {
          "date": "2024-01-01",
          "temperature": {
            "max": 22.1,
            "min": 15.3,
            "avg": 18.5
          },
          "precipitation": {
            "amount": 5.2,
            "unit": "mm"
          },
          "humidity": 72,
          "wind_speed": 10.5,
          "sunshine_hours": 8.5,
          "uv_index_max": 4.2
        }
      ],
      "summary": {
        "total_precipitation": 25.3,
        "avg_temperature": 19.2,
        "avg_humidity": 68,
        "sunshine_hours": 52.3
      },
      "cached_at": "2024-01-15T10:00:00Z"
    }
    ```
    
    ## Query Parameters
    - **field_id**: Unique identifier of the field (required)
    - **start_date**: Start date in ISO format (required)
    - **end_date**: End date in ISO format, max 30 days from start (required)
    
    ## Responses
    - **200**: Successfully retrieved historical data
    - **400**: Invalid date range (more than 30 days apart)
    - **404**: Field not found or has no location coordinates
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db_session=db)
    historical = service.get_field_historical(field_id, start_date, end_date)
    
    if historical is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found or has no location coordinates"
        )
    
    return historical


@router.get("/fields/{field_id}/alerts", response_model=List[Dict[str, Any]])
async def get_field_weather_alerts(
    field_id: str,
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of alerts to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get weather alerts for a specific field.
    
    Alerts are generated based on current conditions and forecast,
    considering the crop planted in the field.
    
    ## Response Example
    
    ```json
    [
      {
        "id": "alert_001",
        "alert_type": "FROST_WARNING",
        "severity": "high",
        "title": "Frost Risk Tomorrow",
        "description": "Temperature expected to drop below 0°C",
        "start_time": "2024-01-15T06:00:00Z",
        "end_time": "2024-01-15T09:00:00Z",
        "recommendation": "Cover sensitive crops or delay planting"
      }
    ]
    ```
    
    ## Severity Levels
    - **low**: Minor impact, monitor conditions
    - **medium**: Moderate risk, take preventive measures
    - **high**: Significant risk, immediate action recommended
    - **critical**: Severe risk, urgent action required
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db_session=db)
    alerts = service.get_field_alerts(field_id, limit=limit)
    
    return alerts


@router.get("/fields/{field_id}/risk-score", response_model=Dict[str, Any])
async def get_field_risk_score(
    field_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get weather risk score for a field.
    
    Returns a risk score (0-100) based on weather conditions
    and crop-specific thresholds.
    
    ## Response Example
    
    ```json
    {
      "field_id": "field_001",
      "crop_name": "wheat",
      "overall_risk_score": 35,
      "risk_level": "low",
      "risk_factors": [
        {
          "factor": "precipitation",
          "score": 25,
          "status": "optimal",
          "details": "Recent rainfall is adequate"
        },
        {
          "factor": "temperature",
          "score": 30,
          "status": "optimal",
          "details": "Temperature within crop range"
        },
        {
          "factor": "wind",
          "score": 45,
          "status": "moderate",
          "details": "Wind speed elevated, monitor spray operations"
        }
      ],
      "recommendations": [
        "Monitor wind conditions before pesticide application",
        "Continue regular irrigation schedule"
      ],
      "generated_at": "2024-01-15T14:30:00Z"
    }
    ```
    
    ## Risk Score Interpretation
    - **0-25 (low)**: Favorable conditions, minimal risk
    - **26-50 (moderate)**: Some concerns, monitor conditions
    - **51-75 (high)**: Elevated risk, take preventive measures
    - **76-100 (critical)**: Severe risk, immediate action required
    
    ## Risk Factors
    - **precipitation**: Rainfall adequacy
    - **temperature**: Temperature stress
    - **humidity**: Disease risk
    - **wind**: Spray and physical damage risk
    - **uv**: UV stress
    
    ## Responses
    - **200**: Successfully retrieved risk score
    - **404**: Field not found
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db_session=db)
    risk = service.generate_field_risk_scores(field_id)
    
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found"
        )
    
    return risk


@router.get("/farms/{farm_id}/weather", response_model=Dict[str, Any])
async def get_farm_weather_summary(
    farm_id: str,
    page: int = Query(default=1, ge=1, description="Page number for pagination"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of fields per page"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get weather summary for all fields in a farm.
    
    Returns weather data and alerts for each field in the farm.
    Useful for overview dashboards and farm-wide alerts.
    
    Supports pagination:
    - **page**: Page number (default: 1)
    - **page_size**: Number of fields per page (default: 10, max: 100)
    
    Returns:
        - **fields**: List of field weather data
        - **pagination**: Page info (current_page, page_size, total_pages, total_fields)
    """
    from app.application.weather.service import WeatherService
    
    service = WeatherService(db_session=db)
    farm_weather = service.get_farm_weather_summary(farm_id, page=page, page_size=page_size)
    
    return farm_weather
# ============== NEW ENDPOINTS: Historical Weather & Farm Summaries ==============

@router.get("/fields/{field_id}/history")
async def get_field_weather_history(
    field_id: str,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=365, description="Items per page"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get historical weather data for a field.
    
    Returns actual recorded weather data from the database.
    Maximum 365 days of history per request.
    
    **Parameters:**
    - field_id: UUID of the field
    - start_date: Beginning of date range
    - end_date: End of date range
    - page: Page number for pagination
    - page_size: Number of records per page (max 365)
    
    **Returns:**
    - List of historical weather snapshots with pagination info
    """
    # Validate date range
    if (end_date - start_date).days > 365:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 365 days"
        )
    
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before or equal to end date"
        )
    
    # Check if field exists and user has access
    from app.infrastructure.repositories.farm_repo import FieldRepository
    field_repo = FieldRepository(db)
    field = field_repo.get_by_id(field_id)
    
    if not field:
        raise HTTPException(
            status_code=404,
            detail=f"Field {field_id} not found"
        )
    
    # Get historical weather data
    from app.application.weather.service import WeatherService
    service = WeatherService(db_session=db)
    
    try:
        snapshots, pagination = service.get_field_historical_weather(
            field_id=field_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        return {
            "field_id": field_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "count": len(snapshots),
            "data": snapshots,
            "pagination": pagination
        }
    except Exception as e:
        logger.error(f"Error fetching historical weather: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch historical weather data"
        )


@router.get("/farms/{farm_id}/weather-summary")
async def get_farm_weather_summary(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get current weather summary for all fields in a farm.
    
    If fields are clustered together (<10km), uses single API call.
    Otherwise returns weather for each field individually.
    
    **Parameters:**
    - farm_id: UUID of the farm
    
    **Returns:**
    - Weather summary with type indicator (aggregated or per_field)
    - For aggregated: single weather object for farm centroid
    - For per_field: weather object for each field
    """
    # Check if farm exists
    from app.infrastructure.repositories.farm_repo import FarmRepository
    farm_repo = FarmRepository(db)
    farm = farm_repo.get_by_id(farm_id)
    
    if not farm:
        raise HTTPException(
            status_code=404,
            detail=f"Farm {farm_id} not found"
        )
    
    # Get farm weather summary
    from app.application.weather.service import WeatherService
    service = WeatherService(db_session=db)
    
    try:
        summary = service.get_farm_weather_summary(farm_id)
        
        return {
            "farm_id": farm_id,
            "weather_summary": summary,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching farm weather summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch farm weather summary"
        )


@router.get("/fields/{field_id}/weather-export")
async def export_field_weather(
    field_id: str,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    format: str = Query("json", pattern="^(json|csv)$", description="Export format (json or csv)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Export weather data in JSON or CSV format.
    
    Useful for downloading weather data for external analysis.
    
    **Parameters:**
    - field_id: UUID of the field
    - start_date: Beginning of date range
    - end_date: End of date range
    - format: Export format ("json" or "csv")
    
    **Returns:**
    - JSON array or CSV file download
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    # Validate date range
    if (end_date - start_date).days > 730:  # 2 years max for export
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 730 days for export"
        )
    
    # Get historical weather
    from app.application.weather.service import WeatherService
    service = WeatherService(db_session=db)
    
    try:
        snapshots, _ = service.get_field_historical_weather(
            field_id=field_id,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=10000  # Large page size for export
        )
        
        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            if len(snapshots) > 0:
                # Define CSV columns
                fieldnames = [
                    'recorded_at', 'temperature_c', 'temperature_min_c', 'temperature_max_c',
                    'humidity_pct', 'rainfall_mm', 'wind_speed_kmh',
                    'solar_radiation_wm2', 'evapotranspiration_mm', 'source'
                ]
                
                writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(snapshots)
            
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=weather_{field_id}_{start_date}_{end_date}.csv"
                }
            )
        else:
            # Return JSON
            return {
                "field_id": field_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "format": "json",
                "count": len(snapshots),
                "data": snapshots
            }
    
    except Exception as e:
        logger.error(f"Error exporting weather data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to export weather data"
        )
