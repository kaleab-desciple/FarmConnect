"""
Monitoring API Routes - Complete Implementation
Farm Connect AgriManagement

Following the same architecture, patterns, and structure as the forum implementation.
Routes → Service → Repository pattern with proper authentication and authorization.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from app.core.database import get_db
from app.core.auth.dependencies import get_optional_user, require_auth, get_enriched_user
from app.domain.monitoring.entities import (
    SoilReadingCreate, SoilReadingUpdate,
    NDVISnapshotCreate,
    PestDiseaseReportCreate, PestDiseaseReportUpdate,
    TreatmentRecommendationCreate,
)

from .service import MonitoringService


router = APIRouter()


# ============ Soil Reading Routes ============

@router.post(
    "/soil-readings",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_soil_reading(
    field_id: str = Query(..., description="Field ID"),
    moisture_pct: Optional[float] = Query(None, ge=0, le=100, description="Moisture percentage"),
    temperature_c: Optional[float] = Query(None, description="Temperature in Celsius"),
    ph: Optional[float] = Query(None, ge=0, le=14, description="pH level"),
    nitrogen_ppm: Optional[float] = Query(None, description="Nitrogen in ppm"),
    phosphorus_ppm: Optional[float] = Query(None, description="Phosphorus in ppm"),
    potassium_ppm: Optional[float] = Query(None, description="Potassium in ppm"),
    organic_matter_pct: Optional[float] = Query(None, ge=0, le=100, description="Organic matter %"),
    source: str = Query(default="MANUAL_TEST", description="Data source"),
    sample_depth_cm: Optional[int] = Query(None, gt=0, description="Sample depth in cm"),
    recorded_at: Optional[datetime] = Query(None, description="Recording timestamp"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new soil reading for a field.
    
    Requires authentication. Users can only create readings for their own fields
    unless they have admin/agent role.
    """
    try:
        # Convert field_id to UUID
        try:
            field_uuid = UUID(field_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid field_id format")
        
        reading_data = SoilReadingCreate(
            field_id=field_uuid,
            moisture_pct=Decimal(str(moisture_pct)) if moisture_pct is not None else None,
            temperature_c=Decimal(str(temperature_c)) if temperature_c is not None else None,
            ph=Decimal(str(ph)) if ph is not None else None,
            nitrogen_ppm=Decimal(str(nitrogen_ppm)) if nitrogen_ppm is not None else None,
            phosphorus_ppm=Decimal(str(phosphorus_ppm)) if phosphorus_ppm is not None else None,
            potassium_ppm=Decimal(str(potassium_ppm)) if potassium_ppm is not None else None,
            organic_matter_pct=Decimal(str(organic_matter_pct)) if organic_matter_pct is not None else None,
            source=source,
            sample_depth_cm=sample_depth_cm,
            recorded_at=recorded_at or datetime.now(timezone.utc),
        )
        
        service = MonitoringService(db)
        created = service.create_soil_reading(reading_data, current_user)
        
        return {
            "id": str(created.id),
            "field_id": str(created.field_id),
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/soil-readings", response_model=Dict[str, Any])
async def list_soil_readings(
    field_id: str = Query(..., description="Field ID"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List soil readings for a field with filtering and pagination.
    """
    try:
        service = MonitoringService(db)
        return service.list_soil_readings(field_id, start_date, end_date, current_user, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/soil-readings/{field_id}/latest", response_model=Dict[str, Any])
async def get_latest_soil_reading(
    field_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Get the latest soil reading for a field.
    """
    try:
        service = MonitoringService(db)
        reading = service.get_latest_soil_reading(field_id, current_user)
        
        if not reading:
            raise HTTPException(status_code=404, detail="No soil readings found")
        
        return {
            "id": str(reading.id),
            "field_id": str(reading.field_id),
            "moisture_pct": str(reading.moisture_pct) if reading.moisture_pct else None,
            "temperature_c": str(reading.temperature_c) if reading.temperature_c else None,
            "ph": str(reading.ph) if reading.ph else None,
            "nitrogen_ppm": str(reading.nitrogen_ppm) if reading.nitrogen_ppm else None,
            "phosphorus_ppm": str(reading.phosphorus_ppm) if reading.phosphorus_ppm else None,
            "potassium_ppm": str(reading.potassium_ppm) if reading.potassium_ppm else None,
            "recorded_at": reading.recorded_at.isoformat() if reading.recorded_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ NDVI Snapshot Routes ============

@router.post(
    "/ndvi-snapshots",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_ndvi_snapshot(
    field_id: str = Query(..., description="Field ID"),
    ndvi_mean: float = Query(..., ge=-1, le=1, description="Mean NDVI value"),
    source: str = Query(default="MANUAL", description="Data source"),
    captured_at: Optional[datetime] = Query(None, description="Capture timestamp"),
    ndvi_min: Optional[float] = Query(None, ge=-1, le=1, description="Min NDVI value"),
    ndvi_max: Optional[float] = Query(None, ge=-1, le=1, description="Max NDVI value"),
    stress_level: Optional[str] = Query(None, description="Stress level"),
    cloud_cover_pct: Optional[float] = Query(None, ge=0, le=100, description="Cloud cover %"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new NDVI snapshot for a field.
    """
    try:
        try:
            field_uuid = UUID(field_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid field_id format")
        
        snapshot_data = NDVISnapshotCreate(
            field_id=field_uuid,
            ndvi_mean=Decimal(str(ndvi_mean)),
            ndvi_min=Decimal(str(ndvi_min)) if ndvi_min is not None else None,
            ndvi_max=Decimal(str(ndvi_max)) if ndvi_max is not None else None,
            source=source,
            captured_at=captured_at or datetime.now(timezone.utc),
            stress_level=stress_level,
            cloud_cover_pct=Decimal(str(cloud_cover_pct)) if cloud_cover_pct is not None else None,
        )
        
        service = MonitoringService(db)
        created = service.create_ndvi_snapshot(snapshot_data, current_user)
        
        return {
            "id": str(created.id),
            "field_id": str(created.field_id),
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ndvi-snapshots", response_model=Dict[str, Any])
async def list_ndvi_snapshots(
    field_id: str = Query(..., description="Field ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List NDVI snapshots for a field with pagination.
    """
    try:
        service = MonitoringService(db)
        return service.list_ndvi_snapshots(field_id, current_user, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Pest/Disease Report Routes ============

@router.post(
    "/pest-reports",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_pest_report(
    field_id: str = Query(..., description="Field ID"),
    report_type: str = Query(..., description="Report type: PEST or DISEASE"),
    pest_disease_name: str = Query(..., description="Name of pest or disease"),
    severity: str = Query(..., description="Severity level"),
    affected_area_pct: float = Query(..., ge=0, le=100, description="Affected area %"),
    observed_at: Optional[datetime] = Query(None, description="Observation timestamp"),
    description: Optional[str] = Query(None, description="Description"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)  # needs system_user_id for reported_by FK
):
    """
    Create a new pest/disease report for a field.
    """
    try:
        try:
            field_uuid = UUID(field_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid field_id format")
        
        report_data = PestDiseaseReportCreate(
            field_id=field_uuid,
            report_type=report_type,
            pest_disease_name=pest_disease_name,
            severity=severity,
            affected_area_pct=Decimal(str(affected_area_pct)),
            observed_at=observed_at or datetime.now(timezone.utc),
            description=description,
            reported_by=current_user.system_user_id,
        )
        
        service = MonitoringService(db)
        created = service.create_pest_report(report_data, current_user)
        
        return {
            "id": str(created.id),
            "field_id": str(created.field_id),
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pest-reports", response_model=Dict[str, Any])
async def list_pest_reports(
    field_id: str = Query(..., description="Field ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List pest/disease reports for a field with pagination.
    """
    try:
        service = MonitoringService(db)
        return service.list_pest_reports(field_id, current_user, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pest-reports/{report_id}", response_model=Dict[str, Any])
async def get_pest_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Get a specific pest/disease report by ID.
    """
    try:
        service = MonitoringService(db)
        report = service.get_pest_report(report_id, current_user)
        
        return {
            "id": str(report.id),
            "field_id": str(report.field_id),
            "report_type": report.report_type,
            "pest_disease_name": report.pest_disease_name,
            "severity": report.severity,
            "affected_area_pct": str(report.affected_area_pct),
            "observed_at": report.observed_at.isoformat() if report.observed_at else None,
            "description": report.description,
            "treatment_status": report.treatment_status,
            "image_urls": report.image_urls or [],
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Treatment Recommendation Routes ============

@router.post(
    "/treatment-recommendations",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_treatment_recommendation(
    report_id: str = Query(..., description="Pest/disease report ID"),
    product_name: str = Query(..., description="Product/recommendation name"),
    product_type: str = Query(..., description="Product type"),
    application_method: str = Query(..., description="Application method"),
    dosage: Optional[str] = Query(None, description="Dosage"),
    application_timing: Optional[str] = Query(None, description="Application timing"),
    estimated_cost_usd: Optional[float] = Query(None, ge=0, description="Estimated cost in USD"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new treatment recommendation for a pest/disease report.
    """
    try:
        treatment_data = TreatmentRecommendationCreate(
            report_id=report_id,
            product_name=product_name,
            product_type=product_type,
            application_method=application_method,
            dosage=dosage,
            application_timing=application_timing,
            estimated_cost_usd=Decimal(str(estimated_cost_usd)) if estimated_cost_usd is not None else None,
        )
        
        service = MonitoringService(db)
        created = service.create_treatment_recommendation(treatment_data, current_user)
        
        return {
            "id": str(created.id),
            "report_id": str(created.report_id),
            "status": "created"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/treatment-recommendations", response_model=List[Dict[str, Any]])
async def list_treatment_recommendations(
    report_id: str = Query(..., description="Pest/disease report ID"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    List treatment recommendations for a pest/disease report.
    """
    try:
        service = MonitoringService(db)
        return service.list_treatment_recommendations(report_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Placeholder Routes (for backward compatibility) ============

@router.post("/irrigation-schedules", response_model=dict)
async def create_irrigation_schedule(
    field_id: str = Query(..., description="Field ID"),
    duration_minutes: int = Query(..., gt=0, description="Duration in minutes"),
    water_volume_liters: float = Query(..., gt=0, description="Water volume in liters"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Create an irrigation schedule (placeholder)."""
    return {"id": str(UUID()), "status": "scheduled", "message": "Irrigation schedule created"}


@router.get("/irrigation-schedules/{field_id}", response_model=list)
async def get_field_irrigation(
    field_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Get irrigation schedules for a field (placeholder)."""
    return []


@router.post("/field-visits", response_model=dict)
async def create_field_visit_log(
    field_id: str = Query(..., description="Field ID"),
    visit_date: date = Query(..., description="Visit date"),
    visit_type: str = Query(..., description="Visit type"),
    visited_by: str = Query(..., description="Visited by"),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Create a field visit log (placeholder)."""
    return {"id": str(UUID()), "status": "created"}
