"""Weather repository for database operations with pagination support."""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone, date, timedelta
from uuid import uuid4
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.infrastructure.db.models.weather import WeatherForecastORM, WeatherSnapshotORM, AlertORM, FieldRiskScoreORM
from app.infrastructure.db.models.farm import FieldORM, CropCycleORM


class WeatherRepository:
    """Repository for weather data operations with pagination and error handling."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # ============== Field Operations ==============
    
    def get_field_by_id(self, field_id: str) -> Optional[Dict[str, Any]]:
        """Get field with its farm and crop cycle info."""
        try:
            orm = self.session.query(FieldORM).filter(
                and_(FieldORM.id == field_id, FieldORM.deleted_at.is_(None))
            ).first()
            
            if not orm:
                return None
            
            # Get active crop cycle
            crop_cycle = self.session.query(CropCycleORM).filter(
                and_(
                    CropCycleORM.field_id == field_id,
                    CropCycleORM.status.in_(['PLANTED', 'GROWING']),
                    CropCycleORM.deleted_at.is_(None)
                )
            ).order_by(desc(CropCycleORM.planting_date)).first()
            
            return {
                "id": orm.id,
                "farm_id": orm.farm_id,
                "name": orm.name,
                "area_ha": float(orm.area_ha) if orm.area_ha else None,
                "boundary_geojson": orm.boundary_geojson,
                "centroid_geojson": orm.centroid_geojson,
                "latitude": self._extract_latitude(orm.centroid_geojson, orm.boundary_geojson),
                "longitude": self._extract_longitude(orm.centroid_geojson, orm.boundary_geojson),
                "soil_type": orm.soil_type,
                "irrigation_type": orm.irrigation_type,
                "active_crop": self._format_crop_cycle(crop_cycle) if crop_cycle else None
            }
        except Exception as e:
            self.session.rollback()
            raise
    
    def _extract_latitude(self, centroid: Optional[dict], boundary: Optional[dict] = None) -> Optional[float]:
        """Extract latitude from centroid geojson, or calculate from boundary if centroid is null."""
        # First try centroid
        if centroid and centroid.get("type") == "Point":
            coords = centroid.get("coordinates", [None, None])
            return coords[1] if len(coords) > 1 else None
        
        # Fall back to calculating from boundary polygon
        if boundary and boundary.get("type") == "Polygon":
            return self._calculate_centroid_from_polygon(boundary)
        
        return None
    
    def _extract_longitude(self, centroid: Optional[dict], boundary: Optional[dict] = None) -> Optional[float]:
        """Extract longitude from centroid geojson, or calculate from boundary if centroid is null."""
        # First try centroid
        if centroid and centroid.get("type") == "Point":
            coords = centroid.get("coordinates", [None, None])
            return coords[0] if len(coords) > 0 else None
        
        # Fall back to calculating from boundary polygon
        if boundary and boundary.get("type") == "Polygon":
            return self._calculate_centroid_from_polygon(boundary, longitude_only=True)
        
        return None
    
    def _calculate_centroid_from_polygon(self, polygon: dict, longitude_only: bool = False) -> Optional[float]:
        """
        Calculate centroid from a Polygon GeoJSON.
        Returns the latitude of the centroid by default, or longitude if longitude_only=True.
        
        The polygon coordinates are in [longitude, latitude] format per GeoJSON spec.
        """
        try:
            coordinates = polygon.get("coordinates", [])
            if not coordinates or len(coordinates) == 0:
                return None
            
            # Get the outer ring (first element of coordinates array)
            ring = coordinates[0]
            if not ring or len(ring) < 3:
                return None
            
            # Calculate simple centroid (average of all vertices)
            # GeoJSON Polygon coordinates are [longitude, latitude]
            total_lon = 0.0
            total_lat = 0.0
            count = 0
            
            for point in ring:
                if point and len(point) >= 2:
                    total_lon += float(point[0])
                    total_lat += float(point[1])
                    count += 1
            
            if count == 0:
                return None
            
            avg_lon = total_lon / count
            avg_lat = total_lat / count
            
            if longitude_only:
                return avg_lon
            return avg_lat
            
        except (ValueError, TypeError, KeyError, IndexError) as e:
            return None
    
    def _format_crop_cycle(self, crop_cycle: CropCycleORM) -> Dict[str, Any]:
        """Format crop cycle to dict."""
        return {
            "id": crop_cycle.id,
            "crop_name": crop_cycle.crop_name,
            "variety": crop_cycle.variety,
            "planting_date": crop_cycle.planting_date.isoformat() if crop_cycle.planting_date else None,
            "expected_harvest_date": crop_cycle.expected_harvest_date.isoformat() if crop_cycle.expected_harvest_date else None,
            "status": crop_cycle.status,
        }
    
    def get_fields_by_farm(
        self, 
        farm_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated fields for a farm with total count."""
        try:
            # Get total count
            total = self.session.query(func.count(FieldORM.id)).filter(
                and_(FieldORM.farm_id == farm_id, FieldORM.deleted_at.is_(None))
            ).scalar() or 0
            
            # Get paginated results
            orms = self.session.query(FieldORM).filter(
                and_(FieldORM.farm_id == farm_id, FieldORM.deleted_at.is_(None))
            ).order_by(FieldORM.name).offset(offset).limit(limit).all()
            
            fields = []
            for orm in orms:
                # Get active crop cycle for each field
                crop_cycle = self.session.query(CropCycleORM).filter(
                    and_(
                        CropCycleORM.field_id == orm.id,
                        CropCycleORM.status.in_(['PLANTED', 'GROWING']),
                        CropCycleORM.deleted_at.is_(None)
                    )
                ).order_by(desc(CropCycleORM.planting_date)).first()
                
                fields.append({
                    "id": orm.id,
                    "name": orm.name,
                    "area_ha": float(orm.area_ha) if orm.area_ha else None,
                    "centroid_geojson": orm.centroid_geojson,
                    "latitude": self._extract_latitude(orm.centroid_geojson),
                    "longitude": self._extract_longitude(orm.centroid_geojson),
                    "soil_type": orm.soil_type,
                    "active_crop": {
                        "crop_name": crop_cycle.crop_name,
                        "variety": crop_cycle.variety,
                        "status": crop_cycle.status,
                    } if crop_cycle else None
                })
            
            return fields, total
        except Exception as e:
            self.session.rollback()
            raise
    
    # ============== Weather Forecast Operations ==============
    
    def save_forecast(self, field_id: str, forecast_data: Dict[str, Any]) -> WeatherForecastORM:
        """Save weather forecast for a field."""
        try:
            orm = WeatherForecastORM(
                id=str(uuid4()),
                field_id=field_id,
                source=forecast_data.get("source", "OPEN_METEO"),
                forecast_date=forecast_data.get("forecast_date"),
                forecast_hour=forecast_data.get("forecast_hour"),
                forecast_horizon_hours=forecast_data.get("forecast_horizon_hours"),
                issued_at=forecast_data.get("issued_at", datetime.now(timezone.utc)),
                temperature_min_c=forecast_data.get("temperature_min_c"),
                temperature_max_c=forecast_data.get("temperature_max_c"),
                temperature_avg_c=forecast_data.get("temperature_avg_c"),
                precipitation_probability_pct=forecast_data.get("precipitation_probability_pct"),
                precipitation_mm=forecast_data.get("precipitation_mm"),
                precipitation_type=forecast_data.get("precipitation_type"),
                wind_speed_max_mps=forecast_data.get("wind_speed_max_mps"),
                wind_direction_deg=forecast_data.get("wind_direction_deg"),
                humidity_avg_pct=forecast_data.get("humidity_avg_pct"),
                pressure_hpa=forecast_data.get("pressure_hpa"),
                growing_degree_days_accumulated=forecast_data.get("growing_degree_days_accumulated"),
                evapotranspiration_mm=forecast_data.get("evapotranspiration_mm"),
                risk_type=forecast_data.get("risk_type"),
                risk_level=forecast_data.get("risk_level"),
                risk_description=forecast_data.get("risk_description"),
                risk_confidence_pct=forecast_data.get("risk_confidence_pct"),
                metadata_=forecast_data.get("metadata", {}),
            )
            self.session.add(orm)
            self.session.flush()
            return orm
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_forecasts(
        self,
        field_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[WeatherForecastORM], int]:
        """Get paginated weather forecasts for a field."""
        try:
            query = self.session.query(WeatherForecastORM).filter(
                WeatherForecastORM.field_id == field_id
            )
            
            # Get total count
            total = query.count()
            
            # Apply filters
            if start_date:
                query = query.filter(WeatherForecastORM.forecast_date >= start_date)
            if end_date:
                query = query.filter(WeatherForecastORM.forecast_date <= end_date)
            
            # Get paginated results
            forecasts = query.order_by(WeatherForecastORM.forecast_date).offset(offset).limit(limit).all()
            
            return forecasts, total
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_latest_forecast(self, field_id: str) -> Optional[WeatherForecastORM]:
        """Get the latest weather forecast for a field."""
        try:
            return self.session.query(WeatherForecastORM).filter(
                WeatherForecastORM.field_id == field_id
            ).order_by(desc(WeatherForecastORM.issued_at)).first()
        except Exception as e:
            self.session.rollback()
            raise
    
    # ============== Weather Snapshot Operations ==============
    
    def save_snapshot(self, field_id: str, snapshot_data: Dict[str, Any]) -> WeatherSnapshotORM:
        """Save weather snapshot (actual recorded weather)."""
        try:
            orm = WeatherSnapshotORM(
                id=str(uuid4()),
                field_id=field_id,
                source=snapshot_data.get("source", "OPEN_METEO"),
                source_station_id=snapshot_data.get("source_station_id"),
                source_station_distance_km=snapshot_data.get("source_station_distance_km"),
                recorded_at=snapshot_data.get("recorded_at", datetime.now(timezone.utc)),
                temperature_c=snapshot_data.get("temperature_c"),
                feels_like_c=snapshot_data.get("feels_like_c"),
                humidity_pct=snapshot_data.get("humidity_pct"),
                pressure_hpa=snapshot_data.get("pressure_hpa"),
                wind_speed_mps=snapshot_data.get("wind_speed_mps"),
                wind_direction_deg=snapshot_data.get("wind_direction_deg"),
                wind_gust_mps=snapshot_data.get("wind_gust_mps"),
                rainfall_mm=snapshot_data.get("rainfall_mm"),
                rainfall_intensity=snapshot_data.get("rainfall_intensity"),
                snowfall_mm=snapshot_data.get("snowfall_mm"),
                cloud_cover_pct=snapshot_data.get("cloud_cover_pct"),
                visibility_m=snapshot_data.get("visibility_m"),
                uv_index=snapshot_data.get("uv_index"),
                soil_temperature_c=snapshot_data.get("soil_temperature_c"),
                soil_moisture_pct=snapshot_data.get("soil_moisture_pct"),
                leaf_wetness_hours=snapshot_data.get("leaf_wetness_hours"),
                evapotranspiration_mm=snapshot_data.get("evapotranspiration_mm"),
                growing_degree_days=snapshot_data.get("growing_degree_days"),
                raw_data=snapshot_data.get("raw_data"),
                metadata_=snapshot_data.get("metadata", {}),
            )
            self.session.add(orm)
            self.session.flush()
            return orm
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_snapshots(
        self,
        field_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[WeatherSnapshotORM], int]:
        """Get paginated historical weather snapshots for a field."""
        try:
            query = self.session.query(WeatherSnapshotORM).filter(
                WeatherSnapshotORM.field_id == field_id
            )
            
            # Get total count
            total = query.count()
            
            # Apply filters
            if start_date:
                query = query.filter(func.date(WeatherSnapshotORM.recorded_at) >= start_date)
            if end_date:
                query = query.filter(func.date(WeatherSnapshotORM.recorded_at) <= end_date)
            
            # Get paginated results
            snapshots = query.order_by(desc(WeatherSnapshotORM.recorded_at)).offset(offset).limit(limit).all()
            
            return snapshots, total
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_latest_snapshot(self, field_id: str) -> Optional[WeatherSnapshotORM]:
        """Get the latest weather snapshot for a field."""
        try:
            return self.session.query(WeatherSnapshotORM).filter(
                WeatherSnapshotORM.field_id == field_id
            ).order_by(desc(WeatherSnapshotORM.recorded_at)).first()
        except Exception as e:
            self.session.rollback()
            raise
    
    # ============== Alert Operations ==============
    
    def create_alert(self, alert_data: Dict[str, Any]) -> AlertORM:
        """Create a new weather alert."""
        try:
            orm = AlertORM(
                id=str(uuid4()),
                user_id=alert_data.get("user_id"),
                field_id=alert_data.get("field_id"),
                alert_type=alert_data.get("alert_type", "WEATHER_WARNING"),
                severity=alert_data.get("severity", "WARNING"),
                title=alert_data.get("title"),
                message=alert_data.get("message"),
                acknowledged=alert_data.get("acknowledged", False),
                metadata_=alert_data.get("metadata", {}),
            )
            self.session.add(orm)
            self.session.flush()
            return orm
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_alerts(
        self,
        user_id: str,
        field_id: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        alert_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[AlertORM], int]:
        """Get paginated alerts for a user."""
        try:
            query = self.session.query(AlertORM).filter(
                AlertORM.user_id == user_id
            )
            
            # Get total count
            total = query.count()
            
            # Apply filters
            if field_id:
                query = query.filter(AlertORM.field_id == field_id)
            if acknowledged is not None:
                query = query.filter(AlertORM.acknowledged == acknowledged)
            if alert_type:
                query = query.filter(AlertORM.alert_type == alert_type)
            
            # Get paginated results
            alerts = query.order_by(desc(AlertORM.created_at)).offset(offset).limit(limit).all()
            
            return alerts, total
        except Exception as e:
            self.session.rollback()
            raise
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert."""
        try:
            alert = self.session.query(AlertORM).filter(
                and_(
                    AlertORM.id == alert_id,
                    AlertORM.user_id == user_id
                )
            ).first()
            
            if alert:
                alert.acknowledged = True
                self.session.flush()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_active_alerts(
        self,
        user_id: str,
        alert_types: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[AlertORM], int]:
        """Get paginated unacknowledged alerts for a user."""
        try:
            query = self.session.query(AlertORM).filter(
                and_(
                    AlertORM.user_id == user_id,
                    AlertORM.acknowledged == False
                )
            )
            
            # Get total count
            total = query.count()
            
            if alert_types:
                query = query.filter(AlertORM.alert_type.in_(alert_types))
            
            # Get paginated results
            alerts = query.order_by(desc(AlertORM.created_at)).offset(offset).limit(limit).all()
            
            return alerts, total
        except Exception as e:
            self.session.rollback()
            raise
    
    # ============== Risk Score Operations ==============
    
    def save_risk_score(self, risk_data: Dict[str, Any]) -> FieldRiskScoreORM:
        """Save field risk score."""
        try:
            orm = FieldRiskScoreORM(
                id=str(uuid4()),
                field_id=risk_data.get("field_id"),
                crop_cycle_id=risk_data.get("crop_cycle_id"),
                score_date=risk_data.get("score_date", date.today()),
                overall_score=risk_data.get("overall_score"),
                risk_trend=risk_data.get("risk_trend"),
                metadata_=risk_data.get("metadata", {}),
            )
            self.session.add(orm)
            self.session.flush()
            return orm
        except Exception as e:
            self.session.rollback()
            raise
    
    def get_risk_scores(
        self,
        field_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[FieldRiskScoreORM], int]:
        """Get paginated risk scores for a field."""
        try:
            query = self.session.query(FieldRiskScoreORM).filter(
                FieldRiskScoreORM.field_id == field_id
            )
            
            # Get total count
            total = query.count()
            
            # Apply filters
            if start_date:
                query = query.filter(FieldRiskScoreORM.score_date >= start_date)
            if end_date:
                query = query.filter(FieldRiskScoreORM.score_date <= end_date)
            
            # Get paginated results
            scores = query.order_by(desc(FieldRiskScoreORM.score_date)).offset(offset).limit(limit).all()
            
            return scores, total
        except Exception as e:
            self.session.rollback()
            raise
    
    # ============== Utility Methods ==============
    
    def commit(self):
        """Commit the transaction."""
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise
    
    def rollback(self):
        """Rollback the transaction."""
        self.session.rollback()
