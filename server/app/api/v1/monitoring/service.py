"""
Monitoring Service - Business Logic Layer
Farm Connect AgriManagement

Following the same architecture, patterns, and structure as the forum implementation.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timezone
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.auth.dependencies import TokenPayload
from app.domain.monitoring.entities import (
    SoilReading, SoilReadingCreate, SoilReadingUpdate,
    NDVISnapshot, NDVISnapshotCreate, NDVISnapshotUpdate,
    PestDiseaseReport, PestDiseaseReportCreate, PestDiseaseReportUpdate,
    TreatmentRecommendation, TreatmentRecommendationCreate, TreatmentRecommendationUpdate,
)
from app.infrastructure.repositories.monitoring_repo import (
    SoilReadingRepository, NDVIRepository,
    PestDiseaseReportRepository, TreatmentRecommendationRepository,
)
from app.infrastructure.repositories.farm_repo import FarmRepository, FieldRepository

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service layer for monitoring operations following clean architecture patterns"""
    
    # Constants for validation
    SOIL_SOURCES = ['IOT_SENSOR', 'MANUAL_TEST', 'LAB_ANALYSIS', 'ESTIMATED']
    NDVI_SOURCES = ['SENTINEL_2', 'LANDSAT_8', 'LANDSAT_9', 'MODIS', 'MANUAL']
    STRESS_LEVELS = ['NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    REPORT_TYPES = ['PEST', 'DISEASE']
    SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    TREATMENT_STATUSES = ['REPORTED', 'TREATMENT_RECOMMENDED', 'TREATMENT_APPLIED', 'RESOLVED', 'NO_ACTION']
    
    def __init__(self, session: Session):
        self.session = session
        self.soil_repo = SoilReadingRepository(session)
        self.ndvi_repo = NDVIRepository(session)
        self.pest_repo = PestDiseaseReportRepository(session)
        self.treatment_repo = TreatmentRecommendationRepository(session)
        self.farm_repo = FarmRepository(session)
        self.field_repo = FieldRepository(session)
    
    # ============ Field Access Control ============
    
    def _get_field_owner(self, field_id: str) -> Optional[str]:
        """Get the farmer_id who owns the field"""
        field = self.field_repo.get_by_id(field_id)
        if not field:
            return None
        farm = self.farm_repo.get_by_id(str(field.farm_id))
        if not farm:
            return None
        return farm.farmer_id
    
    def _can_access_field(self, field_id: str, current_user: TokenPayload) -> bool:
        """Check if user can access the field"""
        if not current_user:
            return False
        
        # Check if user has admin/agent role
        if (current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("AGENT") or
            current_user.is_service_account):
            return True
        
        # Check ownership — farm.farmer_id is an internal system user ID
        owner_id = self._get_field_owner(field_id)
        return bool(current_user.system_user_id) and owner_id == current_user.system_user_id
    
    def _can_edit_field(self, field_id: str, current_user: TokenPayload) -> bool:
        """Check if user can edit data for the field"""
        if not current_user:
            return False
        
        # Check if user has admin role
        if (current_user.has_realm_role("ADMIN") or 
            current_user.is_service_account):
            return True
        
        # Check ownership — farm.farmer_id is an internal system user ID
        owner_id = self._get_field_owner(field_id)
        return bool(current_user.system_user_id) and owner_id == current_user.system_user_id
    
    # ============ Soil Reading Operations ============
    
    def create_soil_reading(
        self,
        reading_data: SoilReadingCreate,
        current_user: TokenPayload
    ) -> SoilReading:
        """Create a new soil reading"""
        # Verify field exists and user has access
        field = self.field_repo.get_by_id(str(reading_data.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        if not self._can_access_field(str(reading_data.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate source
        if reading_data.source not in self.SOIL_SOURCES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source. Must be one of: {', '.join(self.SOIL_SOURCES)}"
            )
        
        created = self.soil_repo.create(reading_data)
        
        logger.info(f"Created soil reading: {created.id} for field: {reading_data.field_id}")
        
        return created
    
    def get_soil_reading(
        self,
        reading_id: str,
        current_user: TokenPayload
    ) -> SoilReading:
        """Get a soil reading by ID"""
        reading = self.soil_repo.get_by_id(reading_id)
        
        if not reading:
            raise HTTPException(status_code=404, detail="Soil reading not found")
        
        if not self._can_access_field(str(reading.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return reading
    
    def list_soil_readings(
        self,
        field_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        current_user: Optional[TokenPayload] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List soil readings for a field"""
        # Check access
        if current_user and not self._can_access_field(field_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        readings = self.soil_repo.get_by_field_id(field_id, start_date, end_date)
        
        # Apply pagination
        total = len(readings)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start = (page - 1) * page_size
        end = start + page_size
        paginated_readings = readings[start:end]
        
        return {
            "readings": [self._reading_to_response(r) for r in paginated_readings],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def get_latest_soil_reading(
        self,
        field_id: str,
        current_user: TokenPayload
    ) -> Optional[SoilReading]:
        """Get latest soil reading for a field"""
        if not self._can_access_field(field_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return self.soil_repo.get_latest(field_id)
    
    def update_soil_reading(
        self,
        reading_id: str,
        reading_data: SoilReadingUpdate,
        current_user: TokenPayload
    ) -> SoilReading:
        """Update a soil reading"""
        reading = self.soil_repo.get_by_id(reading_id)
        
        if not reading:
            raise HTTPException(status_code=404, detail="Soil reading not found")
        
        if not self._can_edit_field(str(reading.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return self.soil_repo.update(reading_id, reading_data)
    
    def delete_soil_reading(
        self,
        reading_id: str,
        current_user: TokenPayload
    ) -> bool:
        """Delete a soil reading"""
        reading = self.soil_repo.get_by_id(reading_id)
        
        if not reading:
            raise HTTPException(status_code=404, detail="Soil reading not found")
        
        if not self._can_edit_field(str(reading.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return self.soil_repo.delete(reading_id)
    
    def _reading_to_response(self, reading: SoilReading) -> Dict[str, Any]:
        """Convert soil reading to response dict"""
        return {
            "id": str(reading.id),
            "field_id": str(reading.field_id),
            "location_geojson": reading.location_geojson,
            "sample_depth_cm": reading.sample_depth_cm,
            "sample_depth_range": reading.sample_depth_range,
            "moisture_pct": str(reading.moisture_pct) if reading.moisture_pct else None,
            "temperature_c": str(reading.temperature_c) if reading.temperature_c else None,
            "ph": str(reading.ph) if reading.ph else None,
            "nitrogen_ppm": str(reading.nitrogen_ppm) if reading.nitrogen_ppm else None,
            "phosphorus_ppm": str(reading.phosphorus_ppm) if reading.phosphorus_ppm else None,
            "potassium_ppm": str(reading.potassium_ppm) if reading.potassium_ppm else None,
            "organic_matter_pct": str(reading.organic_matter_pct) if reading.organic_matter_pct else None,
            "source": reading.source,
            "recorded_at": reading.recorded_at.isoformat() if reading.recorded_at else None,
            "created_at": reading.created_at.isoformat() if reading.created_at else None,
        }
    
    # ============ NDVI Snapshot Operations ============
    
    def create_ndvi_snapshot(
        self,
        snapshot_data: NDVISnapshotCreate,
        current_user: TokenPayload
    ) -> NDVISnapshot:
        """Create a new NDVI snapshot"""
        field = self.field_repo.get_by_id(str(snapshot_data.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        if not self._can_access_field(str(snapshot_data.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate source
        if snapshot_data.source not in self.NDVI_SOURCES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source. Must be one of: {', '.join(self.NDVI_SOURCES)}"
            )
        
        created = self.ndvi_repo.create(snapshot_data)
        
        logger.info(f"Created NDVI snapshot: {created.id} for field: {snapshot_data.field_id}")
        
        return created
    
    def list_ndvi_snapshots(
        self,
        field_id: str,
        current_user: TokenPayload,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List NDVI snapshots for a field"""
        if not self._can_access_field(field_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        snapshots = self.ndvi_repo.get_by_field_id(field_id)
        
        # Apply pagination
        total = len(snapshots)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start = (page - 1) * page_size
        end = start + page_size
        paginated = snapshots[start:end]
        
        return {
            "snapshots": [self._ndvi_to_response(s) for s in paginated],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def _ndvi_to_response(self, snapshot: NDVISnapshot) -> Dict[str, Any]:
        """Convert NDVI snapshot to response dict"""
        return {
            "id": str(snapshot.id),
            "field_id": str(snapshot.field_id),
            "crop_cycle_id": str(snapshot.crop_cycle_id) if snapshot.crop_cycle_id else None,
            "source": snapshot.source,
            "captured_at": snapshot.captured_at.isoformat() if snapshot.captured_at else None,
            "ndvi_mean": str(snapshot.ndvi_mean) if snapshot.ndvi_mean else None,
            "ndvi_min": str(snapshot.ndvi_min) if snapshot.ndvi_min else None,
            "ndvi_max": str(snapshot.ndvi_max) if snapshot.ndvi_max else None,
            "stress_level": snapshot.stress_level,
            "cloud_cover_pct": str(snapshot.cloud_cover_pct) if snapshot.cloud_cover_pct else None,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        }
    
    # ============ Pest/Disease Report Operations ============
    
    def create_pest_report(
        self,
        report_data: PestDiseaseReportCreate,
        current_user: TokenPayload
    ) -> PestDiseaseReport:
        """Create a new pest/disease report"""
        field = self.field_repo.get_by_id(str(report_data.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        if not self._can_access_field(str(report_data.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate report type
        if report_data.report_type not in self.REPORT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report type. Must be one of: {', '.join(self.REPORT_TYPES)}"
            )
        
        # Validate severity
        if report_data.severity not in self.SEVERITIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {', '.join(self.SEVERITIES)}"
            )
        
        created = self.pest_repo.create(report_data)
        
        logger.info(f"Created pest/disease report: {created.id} for field: {report_data.field_id}")
        
        return created
    
    def list_pest_reports(
        self,
        field_id: str,
        current_user: TokenPayload,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List pest/disease reports for a field"""
        if not self._can_access_field(field_id, current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        reports = self.pest_repo.get_by_field_id(field_id)
        
        # Apply pagination
        total = len(reports)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start = (page - 1) * page_size
        end = start + page_size
        paginated = reports[start:end]
        
        return {
            "reports": [self._pest_to_response(r) for r in paginated],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def get_pest_report(
        self,
        report_id: str,
        current_user: TokenPayload
    ) -> PestDiseaseReport:
        """Get a pest/disease report by ID"""
        report = self.pest_repo.get_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Pest/disease report not found")
        
        if not self._can_access_field(str(report.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return report
    
    def update_pest_report(
        self,
        report_id: str,
        report_data: PestDiseaseReportUpdate,
        current_user: TokenPayload
    ) -> PestDiseaseReport:
        """Update a pest/disease report"""
        report = self.pest_repo.get_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Pest/disease report not found")
        
        if not self._can_edit_field(str(report.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate severity if provided
        if report_data.severity and report_data.severity not in self.SEVERITIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {', '.join(self.SEVERITIES)}"
            )
        
        return self.pest_repo.update(report_id, report_data)
    
    def _pest_to_response(self, report: PestDiseaseReport) -> Dict[str, Any]:
        """Convert pest/disease report to response dict"""
        return {
            "id": str(report.id),
            "field_id": str(report.field_id),
            "crop_cycle_id": str(report.crop_cycle_id) if report.crop_cycle_id else None,
            "report_type": report.report_type,
            "pest_disease_name": report.pest_disease_name,
            "severity": report.severity,
            "affected_area_pct": str(report.affected_area_pct) if report.affected_area_pct else None,
            "observed_at": report.observed_at.isoformat() if report.observed_at else None,
            "description": report.description,
            "treatment_status": report.treatment_status,
            "image_urls": report.image_urls or [],
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
    
    # ============ Treatment Recommendation Operations ============
    
    def create_treatment_recommendation(
        self,
        treatment_data: TreatmentRecommendationCreate,
        current_user: TokenPayload
    ) -> TreatmentRecommendation:
        """Create a new treatment recommendation"""
        # Verify report exists and user has access
        report = self.pest_repo.get_by_id(str(treatment_data.report_id))
        if not report:
            raise HTTPException(status_code=404, detail="Pest/disease report not found")
        
        if not self._can_access_field(str(report.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        created = self.treatment_repo.create(treatment_data)
        
        logger.info(f"Created treatment recommendation: {created.id} for report: {treatment_data.report_id}")
        
        return created
    
    def list_treatment_recommendations(
        self,
        report_id: str,
        current_user: TokenPayload
    ) -> List[Dict[str, Any]]:
        """List treatment recommendations for a report"""
        # Verify report exists
        report = self.pest_repo.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Pest/disease report not found")
        
        if not self._can_access_field(str(report.field_id), current_user):
            raise HTTPException(status_code=403, detail="Access denied")
        
        treatments = self.treatment_repo.get_by_report_id(report_id)
        
        return [self._treatment_to_response(t) for t in treatments]
    
    def _treatment_to_response(self, treatment: TreatmentRecommendation) -> Dict[str, Any]:
        """Convert treatment recommendation to response dict"""
        return {
            "id": str(treatment.id),
            "report_id": str(treatment.report_id),
            "product_name": treatment.product_name,
            "product_type": treatment.product_type,
            "application_method": treatment.application_method,
            "dosage": treatment.dosage,
            "application_timing": treatment.application_timing,
            "estimated_cost_usd": str(treatment.estimated_cost_usd) if treatment.estimated_cost_usd else None,
            "effectiveness_score": str(treatment.effectiveness_score) if treatment.effectiveness_score else None,
            "notes": treatment.notes,
            "created_at": treatment.created_at.isoformat() if treatment.created_at else None,
        }
