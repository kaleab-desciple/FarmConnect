"""Weather Data API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user
from app.core.auth.permission_helpers import check_resource_access
from app.core.auth.permissions import PERMISSIONS
from app.infrastructure.external.weather.open_meteo import OpenMeteoWeatherProvider
from app.domain.agriculture.enums import WeatherSource

router = APIRouter(prefix="/weather", tags=["weather"])


# Response Models
class CurrentWeatherResponse(BaseModel):
    """Current weather response"""
    field_id: UUID
    temperature_c: Optional[Decimal]
    feels_like_c: Optional[Decimal]
    humidity_pct: Optional[Decimal]
    pressure_hpa: Optional[Decimal]
    wind_speed_mps: Optional[Decimal]
    wind_direction_deg: Optional[int]
    wind_gust_mps: Optional[Decimal]
    rainfall_mm: Optional[Decimal]
    cloud_cover_pct: Optional[Decimal]
    recorded_at: str
    source: str


class ForecastResponse(BaseModel):
    """Weather forecast response"""
    field_id: UUID
    forecast_date: str
    temperature_min_c: Optional[Decimal]
    temperature_max_c: Optional[Decimal]
    precipitation_probability_pct: Optional[Decimal]
    precipitation_mm: Optional[Decimal]
    wind_speed_max_mps: Optional[Decimal]
    risk_type: Optional[str]
    risk_level: Optional[str]
    risk_description: Optional[str]
    issued_at: str


class WeatherRiskResponse(BaseModel):
    """Weather risk summary"""
    field_id: UUID
    current_risks: List[dict]
    forecast_risks: List[dict]
    recommendations: List[str]


# Endpoints

@router.get("/fields/{field_id}/current", response_model=CurrentWeatherResponse)
def get_current_weather(
    field_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current weather for field"""
    
    # Get field coordinates
    field_query = text("""
        SELECT f.*, fa.farmer_id, fa.assigned_agronomists
        FROM fields f
        JOIN farms fa ON f.farm_id = fa.id
        WHERE f.id = :field_id AND f.deleted_at IS NULL AND fa.deleted_at IS NULL
    """)
    
    result = db.execute(field_query, {"field_id": str(field_id)})
    field = result.fetchone()
    
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    # Check access using permission helper
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    assigned_agronomists = field.assigned_agronomists if field.assigned_agronomists else []
    
    check_resource_access(
        user_id=user_id,
        user_roles=user_roles,
        resource_owner_id=field.farmer_id,
        assigned_user_ids=assigned_agronomists,
        permission_base="weather:read",
        permissions_matrix=PERMISSIONS
    )
    
    # Use centroid or first coordinate from boundary
    try:
        # Try to extract coordinates from boundary_geojson
        if field.boundary_geojson and 'coordinates' in field.boundary_geojson:
            coords = field.boundary_geojson['coordinates'][0][0]
            longitude = Decimal(str(coords[0]))
            latitude = Decimal(str(coords[1]))
        else:
            # Fallback to farm coordinates
            farm_query = text("""
                SELECT location_lat, location_lng FROM farms WHERE id = :farm_id
            """)
            farm_result = db.execute(farm_query, {"farm_id": str(field.farm_id)})
            farm = farm_result.fetchone()
            latitude = farm.location_lat
            longitude = farm.location_lng
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field coordinates: {str(e)}"
        )
    
    # Fetch weather data
    weather_provider = OpenMeteoWeatherProvider()
    try:
        weather_data = weather_provider.get_current_weather(latitude, longitude)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weather service unavailable: {str(e)}"
        )
    
    # Store snapshot in database
    insert_query = text("""
        INSERT INTO weather_snapshots (
            field_id, source, temperature_c, feels_like_c, humidity_pct,
            pressure_hpa, wind_speed_mps, wind_direction_deg, wind_gust_mps,
            rainfall_mm, cloud_cover_pct, recorded_at
        ) VALUES (
            :field_id, :source, :temperature_c, :feels_like_c, :humidity_pct,
            :pressure_hpa, :wind_speed_mps, :wind_direction_deg, :wind_gust_mps,
            :rainfall_mm, :cloud_cover_pct, :recorded_at
        )
    """)
    
    db.execute(
        insert_query,
        {
            "field_id": str(field_id),
            "source": weather_data["source"],
            "temperature_c": weather_data.get("temperature_c"),
            "feels_like_c": weather_data.get("feels_like_c"),
            "humidity_pct": weather_data.get("humidity_pct"),
            "pressure_hpa": weather_data.get("pressure_hpa"),
            "wind_speed_mps": weather_data.get("wind_speed_mps"),
            "wind_direction_deg": weather_data.get("wind_direction_deg"),
            "wind_gust_mps": weather_data.get("wind_gust_mps"),
            "rainfall_mm": weather_data.get("rainfall_mm"),
            "cloud_cover_pct": weather_data.get("cloud_cover_pct"),
            "recorded_at": weather_data["recorded_at"]
        }
    )
    db.commit()
    
    return CurrentWeatherResponse(
        field_id=field_id,
        **weather_data,
        recorded_at=weather_data["recorded_at"].isoformat()
    )


@router.get("/fields/{field_id}/forecast", response_model=List[ForecastResponse])
def get_weather_forecast(
    field_id: UUID,
    days: int = Query(7, ge=1, le=14),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weather forecast for field"""
    
    # Get field coordinates
    field_query = text("""
        SELECT f.*, fa.farmer_id
        FROM fields f
        JOIN farms fa ON f.farm_id = fa.id
        WHERE f.id = :field_id AND f.deleted_at IS NULL AND fa.deleted_at IS NULL
    """)
    
    result = db.execute(field_query, {"field_id": str(field_id)})
    field = result.fetchone()
    
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    # Check access
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if field.farmer_id != user_id and "ADMIN" not in user_roles and "AGRONOMIST" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view weather for this field"
        )
    
    # Extract coordinates
    try:
        if field.boundary_geojson and 'coordinates' in field.boundary_geojson:
            coords = field.boundary_geojson['coordinates'][0][0]
            longitude = Decimal(str(coords[0]))
            latitude = Decimal(str(coords[1]))
        else:
            farm_query = text("""
                SELECT location_lat, location_lng FROM farms WHERE id = :farm_id
            """)
            farm_result = db.execute(farm_query, {"farm_id": str(field.farm_id)})
            farm = farm_result.fetchone()
            latitude = farm.location_lat
            longitude = farm.location_lng
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field coordinates: {str(e)}"
        )
    
    # Fetch forecast data
    weather_provider = OpenMeteoWeatherProvider()
    try:
        forecast_data = weather_provider.get_forecast(latitude, longitude, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weather service unavailable: {str(e)}"
        )
    
    # Store forecasts in database
    for forecast in forecast_data:
        insert_query = text("""
            INSERT INTO weather_forecasts (
                field_id, source, forecast_date, temperature_min_c, temperature_max_c,
                precipitation_probability_pct, precipitation_mm, wind_speed_max_mps,
                risk_type, risk_level, risk_description, issued_at
            ) VALUES (
                :field_id, :source, :forecast_date, :temperature_min_c, :temperature_max_c,
                :precipitation_probability_pct, :precipitation_mm, :wind_speed_max_mps,
                :risk_type, :risk_level, :risk_description, :issued_at
            )
            ON CONFLICT DO NOTHING
        """)
        
        db.execute(
            insert_query,
            {
                "field_id": str(field_id),
                "source": forecast["source"],
                "forecast_date": forecast["forecast_date"],
                "temperature_min_c": forecast.get("temperature_min_c"),
                "temperature_max_c": forecast.get("temperature_max_c"),
                "precipitation_probability_pct": forecast.get("precipitation_probability_pct"),
                "precipitation_mm": forecast.get("precipitation_mm"),
                "wind_speed_max_mps": forecast.get("wind_speed_max_mps"),
                "risk_type": forecast.get("risk_type"),
                "risk_level": forecast.get("risk_level"),
                "risk_description": forecast.get("risk_description"),
                "issued_at": forecast["issued_at"]
            }
        )
    
    db.commit()
    
    return [
        ForecastResponse(
            field_id=field_id,
            forecast_date=f["forecast_date"].isoformat(),
            temperature_min_c=f.get("temperature_min_c"),
            temperature_max_c=f.get("temperature_max_c"),
            precipitation_probability_pct=f.get("precipitation_probability_pct"),
            precipitation_mm=f.get("precipitation_mm"),
            wind_speed_max_mps=f.get("wind_speed_max_mps"),
            risk_type=f.get("risk_type"),
            risk_level=f.get("risk_level"),
            risk_description=f.get("risk_description"),
            issued_at=f["issued_at"].isoformat()
        )
        for f in forecast_data
    ]


@router.get("/fields/{field_id}/history")
def get_weather_history(
    field_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical weather data for field"""
    
    # Check field access
    field_query = text("""
        SELECT f.*, fa.farmer_id
        FROM fields f
        JOIN farms fa ON f.farm_id = fa.id
        WHERE f.id = :field_id AND f.deleted_at IS NULL AND fa.deleted_at IS NULL
    """)
    
    result = db.execute(field_query, {"field_id": str(field_id)})
    field = result.fetchone()
    
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if field.farmer_id != user_id and "ADMIN" not in user_roles and "AGRONOMIST" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view weather for this field"
        )
    
    # Get historical data from database
    history_query = text("""
        SELECT * FROM weather_snapshots
        WHERE field_id = :field_id
        AND DATE(recorded_at) BETWEEN :start_date AND :end_date
        ORDER BY recorded_at ASC
    """)
    
    result = db.execute(
        history_query,
        {
            "field_id": str(field_id),
            "start_date": start_date,
            "end_date": end_date
        }
    )
    
    history = result.fetchall()
    return [dict(row._mapping) for row in history]


@router.get("/fields/{field_id}/risks", response_model=WeatherRiskResponse)
def get_weather_risks(
    field_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weather risk summary for field"""
    
    # Check field access
    field_query = text("""
        SELECT f.*, fa.farmer_id
        FROM fields f
        JOIN farms fa ON f.farm_id = fa.id
        WHERE f.id = :field_id AND f.deleted_at IS NULL AND fa.deleted_at IS NULL
    """)
    
    result = db.execute(field_query, {"field_id": str(field_id)})
    field = result.fetchone()
    
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if field.farmer_id != user_id and "ADMIN" not in user_roles and "AGRONOMIST" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view weather for this field"
        )
    
    # Get forecast risks
    risk_query = text("""
        SELECT * FROM weather_forecasts
        WHERE field_id = :field_id
        AND forecast_date >= CURRENT_DATE
        AND risk_level IN ('HIGH', 'CRITICAL')
        ORDER BY forecast_date ASC
    """)
    
    result = db.execute(risk_query, {"field_id": str(field_id)})
    risks = result.fetchall()
    
    forecast_risks = [
        {
            "date": str(risk.forecast_date),
            "type": risk.risk_type,
            "level": risk.risk_level,
            "description": risk.risk_description
        }
        for risk in risks
    ]
    
    # Generate recommendations
    recommendations = []
    for risk in risks:
        if risk.risk_type == "FROST":
            recommendations.append("Consider frost protection measures for sensitive crops")
        elif risk.risk_type == "HEAVY_RAIN":
            recommendations.append("Ensure proper drainage and delay irrigation")
        elif risk.risk_type == "HEAT_STRESS":
            recommendations.append("Increase irrigation frequency and provide shade if possible")
        elif risk.risk_type == "STRONG_WIND":
            recommendations.append("Secure equipment and check crop support structures")
    
    return WeatherRiskResponse(
        field_id=field_id,
        current_risks=[],
        forecast_risks=forecast_risks,
        recommendations=list(set(recommendations))
    )
