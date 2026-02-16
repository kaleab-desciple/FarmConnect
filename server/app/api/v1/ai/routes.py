"""AI Diagnosis API routes with MongoDB storage for Farm Connect."""
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from dataclasses import asdict

from app.core.database import get_mongo_db
from app.infrastructure.repositories.ai_repo import AiRepository
from app.domain.ai.services import DiagnosisService
from app.domain.ai.models import DiagnosisSession

router = APIRouter()

# Dependency for DiagnosisService
def get_diagnosis_service(db=Depends(get_mongo_db)) -> DiagnosisService:
    repo = AiRepository(db)
    return DiagnosisService(repo)

# ============== COMMON MODELS (DTOs) ==============

class GeoLocation(BaseModel):
    """GPS location coordinates."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    altitude_m: Optional[float] = Field(None, description="Altitude in meters")
    accuracy_m: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")

# ============== 1. INITIAL DIAGNOSIS REQUEST ==============

class InitialDiagnosisRequest(BaseModel):
    """Initial AI diagnosis request for crop health issues."""
    field_id: str = Field(..., min_length=1, max_length=50, description="Unique field identifier")
    crop_cycle_id: Optional[str] = Field(None, description="Current crop cycle identifier")
    location: Optional[GeoLocation] = Field(None, description="GPS location of the issue")
    region: Optional[str] = Field(None, description="Agricultural region")
    crop_type: str = Field(..., description="Crop species")
    growth_stage: str = Field(..., description="Crop growth stage")
    planting_date: Optional[str] = Field(None, description="ISO date of planting")
    suspected_issue: Optional[str] = Field(None, description="Farmer's initial suspicion")
    issue_category: str = Field(..., description="Category: pest, disease, etc.")
    affected_area_pct: float = Field(..., ge=0, le=100, description="Percentage of field affected")
    symptoms: Optional[List[str]] = Field(None, description="Observed symptoms")
    symptom_onset_days: Optional[int] = Field(None, ge=0, description="Days since symptoms first appeared")
    symptom_severity: str = Field(..., description="Severity: low, medium, high, severe")
    weather_recent: Optional[str] = Field(None, description="Recent weather conditions")
    irrigation_type: Optional[str] = Field(None, description="Irrigation method used")
    soil_type: Optional[str] = Field(None, description="Soil type if known")
    image_urls: List[str] = Field(default_factory=list, description="URLs of images showing the issue")
    priority: str = Field("normal", description="Priority level")
    farmer_notes: Optional[str] = Field(None, description="Additional observations")

class InitialDiagnosisResponse(BaseModel):
    """Response for initial diagnosis request."""
    diagnosis_session_id: str
    status: str
    estimated_completion_seconds: int
    priority_ack: str
    message: str

# ============== 2. SYMPTOM DESCRIPTION SUBMISSION ==============

class SymptomDetailDTO(BaseModel):
    """Detailed symptom information."""
    symptom_type: str
    location_on_plant: str
    pattern: Optional[str] = None
    progression: Optional[str] = None
    description: Optional[str] = None

class SymptomSubmissionRequest(BaseModel):
    """Submit detailed symptom descriptions."""
    diagnosis_session_id: str = Field(..., description="Session ID from initial diagnosis")
    symptoms: List[SymptomDetailDTO] = Field(..., min_length=1, description="Detailed symptom list")
    plant_health_score: int = Field(..., ge=1, le=10, description="Overall plant health 1-10")
    affected_plants_count: Optional[int] = Field(None, ge=0, description="Number of affected plants")
    total_plants_observed: Optional[int] = Field(None, ge=1, description="Total plants checked")
    pest_presence: Optional[List[str]] = Field(None, description="Pests observed")
    beneficial_insects: Optional[List[str]] = Field(None, description="Beneficial insects seen")
    weed_pressure: Optional[str] = Field(None, description="Weed competition level")
    treatments_applied: Optional[List[str]] = Field(None, description="Recent treatments")
    last_fertilizer_date: Optional[str] = Field(None, description="Last fertilizer application")
    last_irrigation_date: Optional[str] = Field(None, description="Last irrigation date")
    additional_image_urls: Optional[List[str]] = Field(None, description="Additional images")

class SymptomSubmissionResponse(BaseModel):
    """Response for symptom submission."""
    session_id: str
    symptoms_received: int
    updated_confidence: float
    next_step: str

# ============== 3. IMAGE ANALYSIS REQUEST ==============

class ImageAnalysisRequest(BaseModel):
    """Request detailed AI analysis of crop images."""
    diagnosis_session_id: str = Field(..., description="Link to existing session")
    image_url: str = Field(..., description="URL of the image to analyze")
    analysis_type: str = Field(..., description="Type of analysis: disease, pest, nutrient_deficiency, general_health")
    # Additional metadata fields omitted for brevity but can be added back

class ImageAnalysisResponse(BaseModel):
    """Response for image analysis."""
    analysis_id: str
    diagnosis_session_id: Optional[str]
    image_url: str
    analysis_type: str
    detections: List[Dict[str, Any]]
    overall_health_score: float
    primary_issue: Optional[str]
    confidence_score: float
    recommendations: List[str]

# ============== 4. TREATMENT RECOMMENDATION REQUEST ==============

class TreatmentRecommendationRequest(BaseModel):
    """Request detailed treatment recommendations."""
    diagnosis_session_id: str = Field(..., description="Session ID with confirmed diagnosis")
    # Constraints can be added back

class TreatmentOptionDTO(BaseModel):
    """Individual treatment recommendation."""
    treatment_id: str
    type: str
    name: str
    active_ingredient: Optional[str]
    efficacy_score: float
    cost_per_ha: float
    application_method: str
    pre_harvest_interval_days: int
    reentry_interval_hours: int
    restrictions: List[str]
    safety_ppe: List[str]
    environmental_warnings: List[str]
    application_instructions: str

class TreatmentRecommendationResponse(BaseModel):
    """Response with treatment recommendations."""
    diagnosis_session_id: str
    primary_diagnosis: str
    treatment_options: List[TreatmentOptionDTO]

# ============== ENDPOINTS ==============

@router.post("/ai/diagnose", response_model=InitialDiagnosisResponse)
def request_initial_diagnosis(
    request: InitialDiagnosisRequest,
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    """Create a new AI diagnosis session."""
    # Map request to domain entity creation
    try:
        session = service.create_session(
            field_id=request.field_id,
            crop_cycle_id=request.crop_cycle_id,
            location=request.location.dict() if request.location else None,
            region=request.region,
            crop_type=request.crop_type,
            growth_stage=request.growth_stage,
            planting_date=request.planting_date,
            suspected_issue=request.suspected_issue,
            issue_category=request.issue_category,
            affected_area_pct=request.affected_area_pct,
            symptoms_list=request.symptoms or [],
            symptom_onset_days=request.symptom_onset_days,
            symptom_severity=request.symptom_severity,
            weather_recent=request.weather_recent,
            irrigation_type=request.irrigation_type,
            soil_type=request.soil_type,
            image_urls=request.image_urls,
            priority=request.priority,
            farmer_notes=request.farmer_notes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return InitialDiagnosisResponse(
        diagnosis_session_id=session.id,
        status=session.status,
        estimated_completion_seconds=300, # Mock estimation
        priority_ack=request.priority,
        message="Diagnosis session created."
    )

@router.post("/ai/symptoms", response_model=SymptomSubmissionResponse)
def submit_symptom_details(
    request: SymptomSubmissionRequest,
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    """Submit detailed symptom descriptions."""
    # Convert DTOs to dicts for service
    symptoms_data = [s.dict() for s in request.symptoms]
    updated_session = service.add_symptoms(request.diagnosis_session_id, symptoms_data)
    
    if not updated_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return SymptomSubmissionResponse(
        session_id=request.diagnosis_session_id,
        symptoms_received=len(request.symptoms),
        updated_confidence=updated_session.get("confidence_score", 0.0) or 0.0,
        next_step="Upload images"
    )

@router.post("/ai/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_crop_image(
    request: ImageAnalysisRequest,
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    """Request detailed AI analysis of crop images."""
    try:
        result = await service.run_image_analysis(
            request.diagnosis_session_id,
            request.image_url,
            request.analysis_type
        )
    except ValueError as e:
         raise HTTPException(status_code=404, detail=str(e))

    # Convert domain result to response model
    # Note: result.detections is a list of AnalysisDetection objects
    detections_dict = [asdict(d) for d in result.detections]
    
    return ImageAnalysisResponse(
        analysis_id=result.analysis_id,
        diagnosis_session_id=request.diagnosis_session_id,
        image_url=result.image_url,
        analysis_type=result.analysis_type,
        detections=detections_dict,
        overall_health_score=result.overall_health_score,
        primary_issue=result.primary_issue,
        confidence_score=result.confidence_score,
        recommendations=result.recommendations
    )

@router.post("/ai/treatment", response_model=TreatmentRecommendationResponse)
def request_treatment_recommendations(
    request: TreatmentRecommendationRequest,
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    """Get detailed treatment recommendations."""
    try:
        treatments = service.get_treatments(request.diagnosis_session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    treatment_dtos = [TreatmentOptionDTO(**asdict(t)) for t in treatments]
    
    # We need to fetch the session to get the primary diagnosis name for the response
    session = service.get_session(request.diagnosis_session_id)
    primary_diag = session.get("primary_diagnosis", "Unknown") if session else "Unknown"
    
    return TreatmentRecommendationResponse(
        diagnosis_session_id=request.diagnosis_session_id,
        primary_diagnosis=primary_diag,
        treatment_options=treatment_dtos
    )
