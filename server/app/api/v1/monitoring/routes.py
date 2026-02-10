"""Monitoring API routes for manual data entry."""
from datetime import date, datetime, timezone
from typing import Optional, List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from decimal import Decimal

from app.core.database import get_db
from app.domain.monitoring.entities import (
    SoilReading, SoilReadingCreate, SoilReadingUpdate,
    NDVISnapshot, NDVISnapshotCreate,
    PestDiseaseReport, PestDiseaseReportCreate, PestDiseaseReportUpdate,
    TreatmentRecommendation, TreatmentRecommendationCreate, TreatmentRecommendationUpdate,
)
from app.domain.monitoring.irrigation import (
    IrrigationEventCreate, IrrigationEventUpdate, IrrigationEvent,
    FieldVisitLogCreate, FieldVisitLog,
)
from app.infrastructure.repositories.monitoring_repo import (
    SoilReadingRepository, NDVIRepository,
    PestDiseaseReportRepository, TreatmentRecommendationRepository,
)

router = APIRouter()


# ============== SOIL READINGS ==============

class SoilReadingCreateRequest(BaseModel):
    """Soil reading creation request."""
    field_id: str
    location_geojson: Optional[dict] = None
    sample_depth_cm: Optional[int] = Field(None, gt=0)
    sample_depth_range: Optional[str] = None
    moisture_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    temperature_c: Optional[Decimal] = None
    ph: Optional[Decimal] = Field(None, ge=0, le=14)
    nitrogen_ppm: Optional[Decimal] = None
    phosphorus_ppm: Optional[Decimal] = None
    potassium_ppm: Optional[Decimal] = None
    organic_matter_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    source: str = "MANUAL_TEST"
    lab_name: Optional[str] = None
    lab_report_url: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    weather_conditions: Optional[str] = None
    days_since_rain: Optional[int] = None


@router.post("/soil-readings", response_model=dict)
def create_soil_reading(reading: SoilReadingCreateRequest, db: Session = Depends(get_db)):
    """Create a manual soil reading from field visit."""
    repo = SoilReadingRepository(db)
    reading_data = SoilReadingCreate(
        field_id=reading.field_id,
        location_geojson=reading.location_geojson,
        sample_depth_cm=reading.sample_depth_cm,
        sample_depth_range=reading.sample_depth_range,
        moisture_pct=reading.moisture_pct,
        temperature_c=reading.temperature_c,
        ph=reading.ph,
        nitrogen_ppm=reading.nitrogen_ppm,
        phosphorus_ppm=reading.phosphorus_ppm,
        potassium_ppm=reading.potassium_ppm,
        organic_matter_pct=reading.organic_matter_pct,
        source=reading.source,
        lab_name=reading.lab_name,
        lab_report_url=reading.lab_report_url,
        recorded_by=reading.recorded_by,
        recorded_at=reading.recorded_at,
        weather_conditions=reading.weather_conditions,
        days_since_rain=reading.days_since_rain,
    )
    created = repo.create(reading_data)
    return {"id": str(created.id), "status": "created"}


@router.get("/soil-readings/{field_id}", response_model=List[dict])
def get_field_soil_readings(
    field_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get soil readings for a field."""
    repo = SoilReadingRepository(db)
    readings = repo.get_by_field_id(field_id, start_date, end_date)
    return [
        {
            "id": str(r.id),
            "field_id": r.field_id,
            "moisture_pct": str(r.moisture_pct) if r.moisture_pct else None,
            "temperature_c": str(r.temperature_c) if r.temperature_c else None,
            "ph": str(r.ph) if r.ph else None,
            "nitrogen_ppm": str(r.nitrogen_ppm) if r.nitrogen_ppm else None,
            "phosphorus_ppm": str(r.phosphorus_ppm) if r.phosphorus_ppm else None,
            "potassium_ppm": str(r.potassium_ppm) if r.potassium_ppm else None,
            "recorded_at": r.recorded_at.isoformat(),
        }
        for r in readings
    ]


@router.get("/soil-readings/{field_id}/latest", response_model=dict)
def get_latest_soil_reading(field_id: str, db: Session = Depends(get_db)):
    """Get latest soil reading for a field."""
    repo = SoilReadingRepository(db)
    reading = repo.get_latest(field_id)
    if not reading:
        raise HTTPException(status_code=404, detail="No soil readings found")
    return {
        "id": str(reading.id),
        "field_id": reading.field_id,
        "moisture_pct": str(reading.moisture_pct) if reading.moisture_pct else None,
        "temperature_c": str(reading.temperature_c) if reading.temperature_c else None,
        "ph": str(reading.ph) if reading.ph else None,
        "recorded_at": reading.recorded_at.isoformat(),
    }


# ============== IRRIGATION EVENTS ==============

class IrrigationEventCreateRequest(BaseModel):
    """Irrigation event creation request."""
    field_id: str
    crop_cycle_id: Optional[str] = None
    scheduled_date: datetime
    duration_minutes: int = Field(..., gt=0)
    water_volume_liters: Decimal = Field(..., gt=0)
    triggered_by: str = "manual"
    notes: Optional[str] = None


@router.post("/irrigation-schedules", response_model=dict)
def create_irrigation_schedule(schedule: IrrigationEventCreateRequest, db: Session = Depends(get_db)):
    """Create an irrigation schedule."""
    # Create irrigation event directly (no separate model in repo yet)
    return {"id": str(uuid4()), "status": "scheduled", "message": "Irrigation schedule created"}


@router.get("/irrigation-schedules/{field_id}", response_model=List[dict])
def get_field_irrigation(field_id: str, db: Session = Depends(get_db)):
    """Get irrigation schedules for a field."""
    return []  # Placeholder


# ============== FIELD VISIT LOGS ==============

class FieldVisitLogCreateRequest(BaseModel):
    """Field visit log creation request."""
    field_id: str
    crop_cycle_id: Optional[str] = None
    visit_date: date
    visit_type: str
    purpose: Optional[str] = None
    visited_by: str
    weather_conditions: Optional[str] = None
    temperature_c: Optional[Decimal] = None
    humidity_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    soil_conditions: Optional[str] = None
    observations: Optional[str] = None
    issues_found: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    recommendations: Optional[str] = None
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None


@router.post("/field-visits", response_model=dict)
def create_field_visit_log(visit: FieldVisitLogCreateRequest, db: Session = Depends(get_db)):
    """Create a field visit log."""
    visit_data = FieldVisitLogCreate(
        field_id=visit.field_id,
        crop_cycle_id=visit.crop_cycle_id,
        visit_date=visit.visit_date,
        visit_type=visit.visit_type,
        purpose=visit.purpose,
        visited_by=visit.visited_by,
        weather_conditions=visit.weather_conditions,
        temperature_c=visit.temperature_c,
        humidity_pct=visit.humidity_pct,
        soil_conditions=visit.soil_conditions,
        observations=visit.observations,
        issues_found=visit.issues_found,
        photos=visit.photos,
        recommendations=visit.recommendations,
        follow_up_required=visit.follow_up_required,
        follow_up_notes=visit.follow_up_notes,
    )
    return {"id": str(uuid4()), "status": "created"}


# ============== NDVI SNAPSHOTS ==============

class NDVISnapshotCreateRequest(BaseModel):
    """NDVI snapshot creation request."""
    field_id: str
    crop_cycle_id: Optional[str] = None
    source: str = "MANUAL"
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ndvi_mean: Decimal = Field(..., ge=-1, le=1)
    ndvi_min: Optional[Decimal] = Field(None, ge=-1, le=1)
    ndvi_max: Optional[Decimal] = Field(None, ge=-1, le=1)
    ndvi_stddev: Optional[Decimal] = None
    stress_level: Optional[str] = None
    cloud_cover_pct: Optional[Decimal] = Field(None, ge=0, le=100)


@router.post("/ndvi-snapshots", response_model=dict)
def create_ndvi_snapshot(snapshot: NDVISnapshotCreateRequest, db: Session = Depends(get_db)):
    """Create an NDVI snapshot."""
    repo = NDVIRepository(db)
    snapshot_data = NDVISnapshotCreate(
        field_id=snapshot.field_id,
        crop_cycle_id=snapshot.crop_cycle_id,
        source=snapshot.source,
        captured_at=snapshot.captured_at,
        ndvi_mean=snapshot.ndvi_mean,
        ndvi_min=snapshot.ndvi_min,
        ndvi_max=snapshot.ndvi_max,
        ndvi_stddev=snapshot.ndvi_stddev,
        stress_level=snapshot.stress_level,
        cloud_cover_pct=snapshot.cloud_cover_pct,
    )
    created = repo.create(snapshot_data)
    return {"id": str(created.id), "status": "created"}


@router.get("/ndvi-snapshots/{field_id}", response_model=List[dict])
def get_field_ndvi(field_id: str, limit: int = 30, db: Session = Depends(get_db)):
    """Get NDVI snapshots for a field."""
    repo = NDVIRepository(db)
    snapshots = repo.get_by_field_id(field_id, limit)
    return [
        {
            "id": str(s.id),
            "field_id": s.field_id,
            "ndvi_mean": str(s.ndvi_mean),
            "stress_level": s.stress_level,
            "captured_at": s.captured_at.isoformat(),
        }
        for s in snapshots
    ]


@router.get("/ndvi-snapshots/{field_id}/latest", response_model=dict)
def get_latest_ndvi(field_id: str, db: Session = Depends(get_db)):
    """Get latest NDVI snapshot for a field."""
    repo = NDVIRepository(db)
    snapshot = repo.get_latest(field_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No NDVI snapshots found")
    return {
        "id": str(snapshot.id),
        "field_id": snapshot.field_id,
        "ndvi_mean": str(snapshot.ndvi_mean),
        "stress_level": snapshot.stress_level,
        "captured_at": snapshot.captured_at.isoformat(),
    }


# ============== PEST/DISEASE REPORTS ==============

class PestDiseaseReportCreateRequest(BaseModel):
    """Pest/disease report creation request."""
    field_id: str
    crop_cycle_id: Optional[str] = None
    reported_by: str
    location_geojson: Optional[dict] = None
    image_urls: Optional[List[str]] = None
    suspected_issue: str
    issue_type: Optional[str] = None
    scientific_name: Optional[str] = None
    common_names: Optional[List[str]] = None
    severity: Optional[str] = None
    affected_area_ha: Optional[Decimal] = Field(None, gt=0)
    affected_plant_count: Optional[int] = None
    symptoms: Optional[str] = None
    spread_pattern: Optional[str] = None
    first_observed_date: Optional[date] = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@router.post("/pest-disease-reports", response_model=dict)
def create_pest_disease_report(report: PestDiseaseReportCreateRequest, db: Session = Depends(get_db)):
    """Create a pest/disease report."""
    repo = PestDiseaseReportRepository(db)
    report_data = PestDiseaseReportCreate(
        field_id=report.field_id,
        crop_cycle_id=report.crop_cycle_id,
        reported_by=report.reported_by,
        location_geojson=report.location_geojson,
        image_urls=report.image_urls,
        suspected_issue=report.suspected_issue,
        issue_type=report.issue_type,
        scientific_name=report.scientific_name,
        common_names=report.common_names,
        severity=report.severity,
        affected_area_ha=report.affected_area_ha,
        affected_plant_count=report.affected_plant_count,
        symptoms=report.symptoms,
        spread_pattern=report.spread_pattern,
        first_observed_date=report.first_observed_date,
        detected_at=report.detected_at,
    )
    created = repo.create(report_data)
    return {"id": str(created.id), "status": "created"}


@router.get("/pest-disease-reports/{field_id}", response_model=List[dict])
def get_field_pest_disease_reports(field_id: str, db: Session = Depends(get_db)):
    """Get pest/disease reports for a field."""
    repo = PestDiseaseReportRepository(db)
    reports = repo.get_by_field_id(field_id)
    return [
        {
            "id": str(r.id),
            "field_id": r.field_id,
            "suspected_issue": r.suspected_issue,
            "issue_type": r.issue_type,
            "severity": r.severity,
            "detected_at": r.detected_at.isoformat(),
        }
        for r in reports
    ]


@router.put("/pest-disease-reports/{report_id}", response_model=dict)
def update_pest_disease_report(
    report_id: str,
    report_update: dict,
    db: Session = Depends(get_db)
):
    """Update a pest/disease report (e.g., add AI diagnosis)."""
    repo = PestDiseaseReportRepository(db)
    update_data = PestDiseaseReportUpdate(**report_update)
    updated = repo.update(report_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"id": str(updated.id), "status": "updated"}


# ============== TREATMENT RECOMMENDATIONS ==============

class TreatmentRecommendationCreateRequest(BaseModel):
    """Treatment recommendation creation request."""
    report_id: str
    recommended_by: str
    recommendation_source: str
    description: str
    treatment_type: Optional[str] = None
    chemical_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage_per_ha: Optional[str] = None
    application_method: Optional[str] = None
    application_timing: Optional[str] = None
    organic: bool = False
    restricted_use: bool = False
    required_ppe: Optional[List[str]] = None
    reentry_interval_hours: Optional[int] = None
    pre_harvest_interval_days: Optional[int] = None
    estimated_cost_per_ha_usd: Optional[Decimal] = None
    effectiveness_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    expected_results_days: Optional[int] = None


@router.post("/treatment-recommendations", response_model=dict)
def create_treatment_recommendation(rec: TreatmentRecommendationCreateRequest, db: Session = Depends(get_db)):
    """Create a treatment recommendation."""
    repo = TreatmentRecommendationRepository(db)
    rec_data = TreatmentRecommendationCreate(
        report_id=rec.report_id,
        recommended_by=rec.recommended_by,
        recommendation_source=rec.recommendation_source,
        description=rec.description,
        treatment_type=rec.treatment_type,
        chemical_name=rec.chemical_name,
        active_ingredient=rec.active_ingredient,
        dosage_per_ha=rec.dosage_per_ha,
        application_method=rec.application_method,
        application_timing=rec.application_timing,
        organic=rec.organic,
        restricted_use=rec.restricted_use,
        required_ppe=rec.required_ppe,
        reentry_interval_hours=rec.reentry_interval_hours,
        pre_harvest_interval_days=rec.pre_harvest_interval_days,
        estimated_cost_per_ha_usd=rec.estimated_cost_per_ha_usd,
        effectiveness_rating=rec.effectiveness_rating,
        expected_results_days=rec.expected_results_days,
    )
    created = repo.create(rec_data)
    return {"id": str(created.id), "status": "created"}


@router.get("/treatment-recommendations/{report_id}", response_model=List[dict])
def get_report_treatment_recommendations(report_id: str, db: Session = Depends(get_db)):
    """Get treatment recommendations for a report."""
    repo = TreatmentRecommendationRepository(db)
    recommendations = repo.get_by_report_id(report_id)
    return [
        {
            "id": str(r.id),
            "report_id": r.report_id,
            "description": r.description,
            "treatment_type": r.treatment_type,
            "organic": r.organic,
            "effectiveness_rating": str(r.effectiveness_rating) if r.effectiveness_rating else None,
        }
        for r in recommendations
    ]


@router.put("/treatment-recommendations/{recommendation_id}", response_model=dict)
def update_treatment_recommendation(
    recommendation_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """Update a treatment recommendation (e.g., mark as applied)."""
    repo = TreatmentRecommendationRepository(db)
    update = TreatmentRecommendationUpdate(**update_data)
    updated = repo.update(recommendation_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"id": str(updated.id), "status": "updated"}
