"""AI Diagnosis API routes with MongoDB storage for Farm Connect."""
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal

from app.core.database import get_mongo_db

router = APIRouter()


# ============== COMMON MODELS ==============

class GeoLocation(BaseModel):
    """GPS location coordinates."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    altitude_m: Optional[float] = Field(None, description="Altitude in meters")
    accuracy_m: Optional[float] = Field(None, ge=0, description="GPS accuracy in meters")


# ============== 1. INITIAL DIAGNOSIS REQUEST ==============

class InitialDiagnosisRequest(BaseModel):
    """
    Initial AI diagnosis request for crop health issues.
    
    This is the primary endpoint for farmers to request AI-based diagnosis
    of crop health problems.
    """
    # Field Identification
    field_id: str = Field(..., min_length=1, max_length=50, description="Unique field identifier")
    crop_cycle_id: Optional[str] = Field(None, description="Current crop cycle identifier")
    
    # Location Context
    location: Optional[GeoLocation] = Field(None, description="GPS location of the issue")
    region: Optional[str] = Field(None, description="Agricultural region (e.g., Oromia, Amhara)")
    
    # Crop Information
    crop_type: str = Field(..., description="Crop species (e.g., Teff, Wheat, Maize)")
    growth_stage: str = Field(..., description="Crop growth stage")
    planting_date: Optional[str] = Field(None, description="ISO date of planting")
    
    # Issue Description
    suspected_issue: Optional[str] = Field(None, description="Farmer's initial suspicion")
    issue_category: str = Field(..., description="Category: pest, disease, nutrient_deficiency, abiotic_stress")
    affected_area_pct: float = Field(..., ge=0, le=100, description="Percentage of field affected")
    
    # Symptoms (if available)
    symptoms: Optional[List[str]] = Field(None, description="Observed symptoms")
    symptom_onset_days: Optional[int] = Field(None, ge=0, description="Days since symptoms first appeared")
    symptom_severity: str = Field(..., description="Severity: low, medium, high, severe")
    
    # Environmental Context
    weather_recent: Optional[str] = Field(None, description="Recent weather conditions")
    irrigation_type: Optional[str] = Field(None, description="Irrigation method used")
    soil_type: Optional[str] = Field(None, description="Soil type if known")
    
    # Image Reference
    image_urls: Optional[List[str]] = Field(None, description="URLs of images showing the issue")
    
    # Request Metadata
    priority: str = Field("normal", description="Priority level: low, normal, urgent, emergency")
    farmer_notes: Optional[str] = Field(None, description="Additional observations by farmer")


class SymptomDetail(BaseModel):
    """Detailed symptom information."""
    symptom_type: str = Field(..., description="Type of symptom")
    location_on_plant: str = Field(..., description="Where on the plant")
    pattern: Optional[str] = Field(None, description="Distribution pattern")
    progression: Optional[str] = Field(None, description="How symptoms are spreading")
    description: Optional[str] = Field(None, description="Free-text description")


class InitialDiagnosisResponse(BaseModel):
    """Response for initial diagnosis request."""
    diagnosis_session_id: str
    status: str
    estimated_completion_seconds: int
    priority_ack: str
    message: str


# ============== 2. SYMPTOM DESCRIPTION SUBMISSION ==============

class SymptomSubmissionRequest(BaseModel):
    """
    Submit detailed symptom descriptions for enhanced diagnosis.
    
    Farmers or agronomists can add detailed symptom information
    after the initial diagnosis request.
    """
    diagnosis_session_id: str = Field(..., description="Session ID from initial diagnosis")
    
    # Detailed Symptoms
    symptoms: List[SymptomDetail] = Field(..., min_length=1, description="Detailed symptom list")
    
    # Plant Observations
    plant_health_score: int = Field(..., ge=1, le=10, description="Overall plant health 1-10")
    affected_plants_count: Optional[int] = Field(None, ge=0, description="Number of affected plants")
    total_plants_observed: Optional[int] = Field(None, ge=1, description="Total plants checked")
    
    # Additional Observations
    pest_presence: Optional[List[str]] = Field(None, description="Pests observed")
    beneficial_insects: Optional[List[str]] = Field(None, description="Beneficial insects seen")
    weed_pressure: Optional[str] = Field(None, description="Weed competition level")
    
    # Management History
    treatments_applied: Optional[List[str]] = Field(None, description="Recent treatments")
    last_fertilizer_date: Optional[str] = Field(None, description="Last fertilizer application")
    last_irrigation_date: Optional[str] = Field(None, description="Last irrigation date")
    
    # Additional Images
    additional_image_urls: Optional[List[str]] = Field(None, description="Additional images")


class SymptomSubmissionResponse(BaseModel):
    """Response for symptom submission."""
    session_id: str
    symptoms_received: int
    updated_confidence: float
    additional_recommendations: List[str]
    next_step: str


# ============== 3. IMAGE ANALYSIS REQUEST ==============

class ImageAnalysisRequest(BaseModel):
    """
    Request detailed AI analysis of crop images.
    
    This endpoint processes individual images for disease detection,
    pest identification, and overall crop health assessment.
    """
    diagnosis_session_id: Optional[str] = Field(None, description="Link to existing session")
    
    # Image Information
    image_url: str = Field(..., description="URL of the image to analyze")
    image_metadata: Optional[Dict[str, Any]] = Field(None, description="Image EXIF/metadata")
    
    # Analysis Type
    analysis_type: str = Field(..., description="Type of analysis: disease, pest, nutrient_deficiency, general_health")
    analysis_mode: str = Field("standard", description="Analysis depth: quick, standard, detailed")
    
    # Image Context
    captured_at: Optional[datetime] = Field(None, description="When image was captured")
    capture_conditions: Optional[Dict[str, Any]] = Field(None, description="Lighting, angle, etc.")
    field_context: Optional[str] = Field(None, description="Where in field image was taken")
    
    # Plant Part (if applicable)
    plant_part: Optional[str] = Field(None, description="Plant part visible: leaf, stem, root, flower, fruit, whole_plant")


class ImageAnalysisResponse(BaseModel):
    """Response for image analysis."""
    analysis_id: str
    diagnosis_session_id: Optional[str]
    image_url: str
    analysis_type: str
    
    # Detection Results
    detections: List[Dict[str, Any]]  # Detected issues with confidence
    overall_health_score: float
    primary_issue: Optional[str]
    confidence_score: float
    
    # Analysis Details
    model_used: str
    processing_time_ms: int
    recommendations: List[str]


# ============== 4. TREATMENT RECOMMENDATION REQUEST ==============

class TreatmentRecommendationRequest(BaseModel):
    """
    Request detailed treatment recommendations.
    
    After diagnosis, this endpoint provides specific treatment
    options including chemical, biological, and cultural controls.
    """
    diagnosis_session_id: str = Field(..., description="Session ID with confirmed diagnosis")
    
    # Treatment Preferences
    treatment_type_preference: str = Field("all", description="Preferred type: all, chemical, biological, organic")
    budget_constraint: Optional[Dict[str, Any]] = Field(None, description="Budget limits")
    time_to_harvest_days: Optional[int] = Field(None, ge=0, description="Days until harvest")
    
    # Environmental Constraints
    water_source_proximity: Optional[bool] = Field(None, description="Near water body")
    organic_certified: bool = Field(False, description="Field is organic certified")
    pollinator_present: bool = Field(False, description="Bees/pollinators active in area")
    
    # Applicator Constraints
    equipment_available: Optional[List[str]] = Field(None, description="Available equipment")
    labor_availability: Optional[str] = Field(None, description="Labor constraints")
    
    # Previous Treatments (to avoid resistance)
    treatments_last_30_days: Optional[List[str]] = Field(None, description="Recently applied treatments")
    known_resistance: Optional[List[str]] = Field(None, description="Known resistance issues")


class TreatmentOption(BaseModel):
    """Individual treatment recommendation."""
    treatment_id: str
    type: str  # chemical, biological, cultural, mechanical
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
    severity: str
    
    treatment_options: List[TreatmentOption]
    recommended_options: List[str]  # IDs of top recommendations
    
    # Cultural Recommendations
    cultural_controls: List[str]
    prevention_measures: List[str]
    
    # Monitoring
    follow_up_interval_days: int
    success_indicators: List[str]
    
    # External Resources
    extension_contacts: List[Dict[str, str]]
    additional_resources: List[str]


# ============== 5. FOLLOW-UP QUERY ==============

class FollowUpQueryRequest(BaseModel):
    """
    Submit follow-up questions about a diagnosis.
    
    Farmers can ask clarifying questions about treatments,
    application methods, or expected outcomes.
    """
    diagnosis_session_id: str = Field(..., description="Original diagnosis session")
    
    # Query
    question_type: str = Field(..., description="Type: application_guidance, efficacy, safety, alternative, general")
    question: str = Field(..., min_length=10, max_length=1000, description="Follow-up question")
    
    # Context
    treatment_applied: Optional[str] = Field(None, description="Treatment that was applied")
    application_date: Optional[str] = Field(None, description="When treatment was applied")
    observed_results: Optional[str] = Field(None, description="What farmer observed since application")
    
    # Attachments
    follow_up_image_urls: Optional[List[str]] = Field(None, description="Images showing current status")


class FollowUpResponse(BaseModel):
    """Response to follow-up query."""
    query_id: str
    diagnosis_session_id: str
    question_type: str
    
    answer: str
    recommendations: List[str]
    urgency_level: str
    
    # Suggested Actions
    immediate_actions: List[str]
    monitor_for: List[str]
    escalation_contact: Optional[Dict[str, str]]


# ============== 6. DIAGNOSIS HISTORY RETRIEVAL ==============

class DiagnosisHistoryResponse(BaseModel):
    """Complete diagnosis history record."""
    diagnosis_session_id: str
    field_id: str
    crop_type: str
    growth_stage: str
    
    # Timeline
    created_at: datetime
    last_updated: datetime
    status: str
    
    # Diagnosis
    primary_diagnosis: Optional[str]
    diagnosis_confidence: Optional[float]
    severity: Optional[str]
    affected_area_pct: float
    
    # Symptoms Recorded
    symptoms_recorded: List[Dict[str, Any]]
    
    # Images Analyzed
    images_analyzed: List[Dict[str, Any]]
    
    # Treatments
    treatments_recommended: List[Dict[str, Any]]
    treatments_applied: List[Dict[str, Any]]
    
    # Outcomes
    farmer_feedback: Optional[Dict[str, Any]]
    final_outcome: Optional[str]
    outcome_rating: Optional[int]
    
    # Follow-ups
    follow_up_count: int
    follow_up_questions: List[Dict[str, Any]]


# ============== 7. BATCH DIAGNOSIS STATUS ==============

class BatchStatusRequest(BaseModel):
    """Request status for multiple diagnoses."""
    diagnosis_session_ids: List[str] = Field(..., min_length=1, max_length=100)
    include_details: bool = Field(True, description="Include full details in response")


class BatchStatusResponse(BaseModel):
    """Response with status of multiple diagnoses."""
    total_requested: int
    completed: int
    pending: int
    failed: int
    
    statuses: List[Dict[str, Any]]


# ============== MONGODB HELPER FUNCTIONS ==============

def store_diagnosis_mongodb(diagnosis_data: dict) -> str:
    """Store AI diagnosis in MongoDB."""
    mongo_db = get_mongo_db()
    collection = mongo_db["ai_diagnoses"]
    
    # Add timestamps
    diagnosis_data["created_at"] = datetime.now(timezone.utc)
    diagnosis_data["updated_at"] = datetime.now(timezone.utc)
    diagnosis_data["processing_status"] = "processing"
    
    result = collection.insert_one(diagnosis_data)
    return str(result.inserted_id)


def update_diagnosis_mongodb(diagnosis_id: str, updates: dict) -> bool:
    """Update AI diagnosis in MongoDB."""
    mongo_db = get_mongo_db()
    collection = mongo_db["ai_diagnoses"]
    
    # Try to find by string _id first (since we store UUID as string)
    result = collection.update_one({"_id": diagnosis_id}, {"$set": updates})
    
    # If not found, try ObjectId (for backward compatibility)
    if result.matched_count == 0:
        from bson import ObjectId
        try:
            result = collection.update_one({"_id": ObjectId(diagnosis_id)}, {"$set": updates})
        except Exception:
            return False
    
    return result.modified_count > 0 or result.matched_count > 0


def get_diagnosis_mongodb(diagnosis_id: str) -> Optional[dict]:
    """Get AI diagnosis from MongoDB."""
    mongo_db = get_mongo_db()
    collection = mongo_db["ai_diagnoses"]
    
    # Try to find by string _id first (since we store UUID as string)
    diagnosis = collection.find_one({"_id": diagnosis_id})
    
    # If not found, try ObjectId (for backward compatibility)
    if not diagnosis:
        from bson import ObjectId
        try:
            diagnosis = collection.find_one({"_id": ObjectId(diagnosis_id)})
        except Exception:
            pass
    
    return diagnosis


def list_diagnoses_mongodb(field_id: Optional[str] = None, limit: int = 20) -> List[dict]:
    """List diagnoses from MongoDB."""
    mongo_db = get_mongo_db()
    collection = mongo_db["ai_diagnoses"]
    
    query = {}
    if field_id:
        query["field_id"] = field_id
    
    diagnoses = list(collection.find(query).limit(limit))
    
    # Convert ObjectId to string
    for d in diagnoses:
        if "_id" in d:
            d["id"] = str(d["_id"])
            del d["_id"]
    
    return diagnoses


# ============== ENDPOINT 1: INITIAL DIAGNOSIS REQUEST ==============

@router.post("/ai/diagnose", response_model=InitialDiagnosisResponse)
def request_initial_diagnosis(request: InitialDiagnosisRequest):
    """
    Create a new AI diagnosis session for crop health issues.
    
    This is the entry point for farmers to get AI-powered diagnosis
    of crop problems.
    """
    session_id = str(uuid4())
    
    # Create MongoDB document
    mongo_doc = {
        "_id": session_id,
        "field_id": request.field_id,
        "crop_cycle_id": request.crop_cycle_id,
        "location": request.location.model_dump() if request.location else None,
        "region": request.region,
        "crop_type": request.crop_type,
        "growth_stage": request.growth_stage,
        "planting_date": request.planting_date,
        "suspected_issue": request.suspected_issue,
        "issue_category": request.issue_category,
        "affected_area_pct": request.affected_area_pct,
        "symptoms": request.symptoms,
        "symptom_onset_days": request.symptom_onset_days,
        "symptom_severity": request.symptom_severity,
        "weather_recent": request.weather_recent,
        "irrigation_type": request.irrigation_type,
        "soil_type": request.soil_type,
        "image_urls": request.image_urls,
        "priority": request.priority,
        "farmer_notes": request.farmer_notes,
        "processing_status": "processing",
        "confidence_score": None,
        "primary_diagnosis": None,
        "treatments_recommended": [],
        "farmer_feedback": None
    }
    
    # Store in MongoDB
    store_diagnosis_mongodb(mongo_doc)
    
    # Estimate completion time based on priority
    priority_times = {
        "emergency": 60,
        "urgent": 120,
        "normal": 300,
        "low": 600
    }
    estimated_seconds = priority_times.get(request.priority, 300)
    
    return InitialDiagnosisResponse(
        diagnosis_session_id=session_id,
        status="processing",
        estimated_completion_seconds=estimated_seconds,
        priority_ack=request.priority,
        message="Diagnosis session created. You will receive results shortly."
    )


# ============== ENDPOINT 2: SYMPTOM DESCRIPTION SUBMISSION ==============

@router.post("/ai/symptoms", response_model=SymptomSubmissionResponse)
def submit_symptom_details(request: SymptomSubmissionRequest):
    """
    Submit detailed symptom descriptions for enhanced diagnosis accuracy.
    """
    # Verify diagnosis exists
    diagnosis = get_diagnosis_mongodb(request.diagnosis_session_id)
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis session not found")
    
    # Update MongoDB with symptom details
    symptom_data = [s.model_dump() for s in request.symptoms]
    
    updates = {
        "symptom_details": symptom_data,
        "plant_health_score": request.plant_health_score,
        "affected_plants_count": request.affected_plants_count,
        "total_plants_observed": request.total_plants_observed,
        "pest_presence": request.pest_presence,
        "beneficial_insects": request.beneficial_insects,
        "weed_pressure": request.weed_pressure,
        "treatments_applied": request.treatments_applied,
        "last_fertilizer_date": request.last_fertilizer_date,
        "last_irrigation_date": request.last_irrigation_date,
        "additional_images": request.additional_image_urls
    }
    
    update_diagnosis_mongodb(request.diagnosis_session_id, updates)
    
    # Mock confidence update based on symptom detail
    confidence_boost = min(len(request.symptoms) * 0.05, 0.20)
    current_confidence = diagnosis.get("confidence_score") or 0.5
    new_confidence = min(current_confidence + confidence_boost, 0.95)
    
    return SymptomSubmissionResponse(
        session_id=request.diagnosis_session_id,
        symptoms_received=len(request.symptoms),
        updated_confidence=new_confidence,
        additional_recommendations=[
            "Take photos of unaffected plants for comparison",
            "Note any recent pesticide or fertilizer applications",
            "Check for pest presence on leaf undersides"
        ],
        next_step="Upload images for visual analysis if available"
    )


# ============== ENDPOINT 3: IMAGE ANALYSIS REQUEST ==============

@router.post("/ai/analyze-image", response_model=ImageAnalysisResponse)
def analyze_crop_image(request: ImageAnalysisRequest):
    """
    Request detailed AI analysis of crop images.
    
    Analyzes images for diseases, pests, nutrient deficiencies,
    and overall plant health assessment.
    """
    analysis_id = str(uuid4())
    
    # Mock detection results (in production, this calls ML models)
    mock_detections = [
        {
            "detection_type": "disease",
            "name": "Early Blight",
            "scientific_name": "Alternaria solani",
            "confidence": 0.87,
            "bbox": [120, 200, 150, 280],
            "severity": "moderate",
            "affected_area_pct": 12.5
        }
    ]
    
    mock_response = ImageAnalysisResponse(
        analysis_id=analysis_id,
        diagnosis_session_id=request.diagnosis_session_id,
        image_url=request.image_url,
        analysis_type=request.analysis_type,
        detections=mock_detections,
        overall_health_score=0.68,
        primary_issue="Early Blight (Alternaria solani)",
        confidence_score=0.87,
        model_used="disease_classifier_v1.2",
        processing_time_ms=245,
        recommendations=[
            "Apply copper-based fungicide at first sign of infection",
            "Remove and destroy infected plant material",
            "Improve air circulation between plants",
            "Avoid overhead irrigation"
        ]
    )
    
    # Store analysis result if session exists
    if request.diagnosis_session_id:
        update_diagnosis_mongodb(request.diagnosis_session_id, {
            "image_analysis": {
                "analysis_id": analysis_id,
                "image_url": request.image_url,
                "analysis_type": request.analysis_type,
                "detections": mock_detections,
                "confidence": 0.87,
                "recommendations": mock_response.recommendations
            }
        })
    
    return mock_response


# ============== ENDPOINT 4: TREATMENT RECOMMENDATION REQUEST ==============

@router.post("/ai/treatment", response_model=TreatmentRecommendationResponse)
def request_treatment_recommendations(request: TreatmentRecommendationRequest):
    """
    Get detailed treatment recommendations for confirmed diagnosis.
    
    Returns chemical, biological, and cultural control options
    with application guidance and safety information.
    """
    # Verify diagnosis exists
    diagnosis = get_diagnosis_mongodb(request.diagnosis_session_id)
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis session not found")
    
    # Mock treatment options
    treatments = [
        TreatmentOption(
            treatment_id=str(uuid4()),
            type="chemical",
            name="Copper Oxychloride 50% WP",
            active_ingredient="Copper Oxychloride",
            efficacy_score=0.85,
            cost_per_ha=45.00,
            application_method="foliar_spray",
            pre_harvest_interval_days=7,
            reentry_interval_hours=24,
            restrictions=["Do not apply during bloom", "Rotate with different mode of action"],
            safety_ppe=["gloves", "mask", "eye_protection"],
            environmental_warnings=["toxic_to_fish", "avoid_near_waterways"],
            application_instructions="Apply at 2-3 g/L water, spray thoroughly on both leaf surfaces"
        ),
        TreatmentOption(
            treatment_id=str(uuid4()),
            type="biological",
            name="Bacillus subtilis QST 713",
            active_ingredient="Bacillus subtilis",
            efficacy_score=0.78,
            cost_per_ha=35.00,
            application_method="foliar_spray",
            pre_harvest_interval_days=0,
            reentry_interval_hours=4,
            restrictions=["Store below 30C", "Use within 6 months of opening"],
            safety_ppe=["gloves"],
            environmental_warnings=["none"],
            application_instructions="Apply at 5 ml/L water, ensure good coverage"
        )
    ]
    
    # Get primary diagnosis from image analysis if available
    image_analysis = diagnosis.get("image_analysis")
    if image_analysis and image_analysis.get("detections"):
        primary_diag = image_analysis["detections"][0].get("name", "Unknown")
    else:
        primary_diag = diagnosis.get("primary_diagnosis") or "Pending Diagnosis"
    
    severity = diagnosis.get("symptom_severity") or "unknown"
    
    response = TreatmentRecommendationResponse(
        diagnosis_session_id=request.diagnosis_session_id,
        primary_diagnosis=primary_diag,
        severity=severity,
        treatment_options=treatments,
        recommended_options=[str(t.treatment_id) for t in treatments[:1]],
        cultural_controls=[
            "Remove infected leaves immediately",
            "Practice crop rotation with non-host crops",
            "Sanitize tools between plants",
            "Avoid working with wet plants"
        ],
        prevention_measures=[
            "Use disease-free seeds and transplants",
            "Maintain proper plant spacing for air circulation",
            "Water at base of plants, avoid wetting leaves",
            "Monitor fields weekly for early detection"
        ],
        follow_up_interval_days=7,
        success_indicators=[
            "No new lesions appearing after 5-7 days",
            "Existing lesions stop expanding",
            "New growth appears healthy"
        ],
        extension_contacts=[
            {"name": "Oromia Agriculture Bureau", "phone": "+251-11-123-4567"},
            {"name": "Ethiopian Institute of Agriculture", "phone": "+251-11-234-5678"}
        ],
        additional_resources=[
            "FAO Plant Protection Guidelines",
            "Ethiopian Ministry of Agriculture Pest Management Guide"
        ]
    )
    
    # Store recommendations
    update_diagnosis_mongodb(request.diagnosis_session_id, {
        "treatments_recommended": [t.model_dump() for t in treatments]
    })
    
    return response


# ============== ENDPOINT 5: FOLLOW-UP QUERY ==============

@router.post("/ai/follow-up", response_model=FollowUpResponse)
def submit_follow_up_query(request: FollowUpQueryRequest):
    """
    Submit follow-up questions about a diagnosis or treatment.
    
    Farmers can ask for clarification on application methods,
    expected results, or report observed outcomes.
    """
    # Verify diagnosis exists
    diagnosis = get_diagnosis_mongodb(request.diagnosis_session_id)
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis session not found")
    
    query_id = str(uuid4())
    
    # Mock response based on question type
    answers = {
        "application_guidance": "Apply the fungicide in early morning or late evening to avoid peak sun hours. Ensure complete coverage of both upper and lower leaf surfaces. Reapply after 7-10 days or after heavy rain.",
        "efficacy": "You should see initial results within 3-5 days. Complete control typically achieved after 2-3 applications spaced 7-10 days apart.",
        "safety": "Wait at least 24 hours before re-entering the treated area. Wear protective equipment during application. Do not spray when bees are actively foraging.",
        "alternative": "Consider biological options like Bacillus subtilis for organic systems. Cultural controls include removing infected material and improving air circulation.",
        "general": "Continue monitoring the field weekly. Document any changes in symptom progression. Contact extension services if symptoms worsen despite treatment."
    }
    
    answer = answers.get(request.question_type, answers["general"])
    
    response = FollowUpResponse(
        query_id=query_id,
        diagnosis_session_id=request.diagnosis_session_id,
        question_type=request.question_type,
        answer=answer,
        recommendations=[
            "Monitor treated areas for next 7 days",
            "Document any side effects",
            "Schedule follow-up inspection"
        ],
        urgency_level="normal",
        immediate_actions=[
            "Apply treatment according to instructions",
            "Mark treated areas for follow-up"
        ],
        monitor_for=[
            "New lesion development",
            "Leaf yellowing or wilting",
            "Pest return"
        ],
        escalation_contact={"name": "Extension Officer", "phone": "+251-XX-XXX-XXXX"}
    )
    
    # Store follow-up
    update_diagnosis_mongodb(request.diagnosis_session_id, {
        "follow_up_" + query_id: {
            "query_id": query_id,
            "question": request.question,
            "question_type": request.question_type,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    
    return response


# ============== ENDPOINT 6: DIAGNOSIS HISTORY RETRIEVAL ==============

@router.get("/ai/diagnosis/{diagnosis_id}", response_model=DiagnosisHistoryResponse)
def get_diagnosis_history(diagnosis_id: str):
    """
    Retrieve complete diagnosis history for a session.
    
    Returns all details including symptoms, images, treatments,
    and farmer feedback.
    """
    diagnosis = get_diagnosis_mongodb(diagnosis_id)
    
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    
    return DiagnosisHistoryResponse(
        diagnosis_session_id=diagnosis_id,
        field_id=diagnosis.get("field_id", ""),
        crop_type=diagnosis.get("crop_type", ""),
        growth_stage=diagnosis.get("growth_stage", ""),
        created_at=diagnosis.get("created_at", datetime.now(timezone.utc)),
        last_updated=diagnosis.get("updated_at", datetime.now(timezone.utc)),
        status=diagnosis.get("processing_status", "completed"),
        primary_diagnosis=diagnosis.get("primary_diagnosis"),
        diagnosis_confidence=diagnosis.get("confidence_score"),
        severity=diagnosis.get("symptom_severity"),
        affected_area_pct=diagnosis.get("affected_area_pct", 0),
        symptoms_recorded=diagnosis.get("symptom_details", []),
        images_analyzed=diagnosis.get("image_analysis", []),
        treatments_recommended=diagnosis.get("treatments_recommended", []),
        treatments_applied=diagnosis.get("treatments_applied", []),
        farmer_feedback=diagnosis.get("farmer_feedback"),
        final_outcome=diagnosis.get("outcome"),
        outcome_rating=diagnosis.get("outcome_rating"),
        follow_up_count=diagnosis.get("follow_up_count", 0),
        follow_up_questions=diagnosis.get("follow_ups", [])
    )


# ============== ENDPOINT 7: BATCH DIAGNOSIS STATUS ==============

@router.get("/ai/batch-status", response_model=BatchStatusResponse)
def check_batch_diagnosis_status(
    session_ids: str = Query(..., description="Comma-separated list of session IDs"),
    include_details: bool = Query(True, description="Include full details")
):
    """
    Check status of multiple diagnosis sessions.
    
    Useful for agronomists managing multiple cases or
    for dashboard refresh.
    """
    # Parse session IDs
    ids = [s.strip() for s in session_ids.split(",")]
    
    completed = 0
    pending = 0
    failed = 0
    statuses = []
    
    for session_id in ids:
        diagnosis = get_diagnosis_mongodb(session_id)
        
        if diagnosis:
            status_info = {
                "diagnosis_session_id": session_id,
                "status": diagnosis.get("processing_status", "unknown"),
                "field_id": diagnosis.get("field_id"),
                "crop_type": diagnosis.get("crop_type"),
                "created_at": diagnosis.get("created_at").isoformat() if diagnosis.get("created_at") else None
            }
            
            if include_details:
                status_info["primary_diagnosis"] = diagnosis.get("primary_diagnosis")
                status_info["confidence"] = diagnosis.get("confidence_score")
            
            statuses.append(status_info)
            
            if diagnosis.get("processing_status") == "completed":
                completed += 1
            else:
                pending += 1
        else:
            status_info = {
                "diagnosis_session_id": session_id,
                "status": "not_found",
                "error": "Diagnosis session not found"
            }
            statuses.append(status_info)
            failed += 1
    
    return BatchStatusResponse(
        total_requested=len(ids),
        completed=completed,
        pending=pending,
        failed=failed,
        statuses=statuses
    )


# ============== ADDITIONAL UTILITY ENDPOINTS ==============

@router.get("/ai/diagnoses")
def list_diagnoses(field_id: Optional[str] = None, limit: int = 20):
    """List all diagnoses, optionally filtered by field_id."""
    diagnoses = list_diagnoses_mongodb(field_id, limit)
    
    return {
        "count": len(diagnoses),
        "diagnoses": diagnoses
    }


@router.delete("/ai/diagnosis/{diagnosis_id}")
def delete_diagnosis(diagnosis_id: str):
    """Delete a diagnosis from MongoDB (for testing)."""
    mongo_db = get_mongo_db()
    collection = mongo_db["ai_diagnoses"]
    
    from bson import ObjectId
    try:
        object_id = ObjectId(diagnosis_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid diagnosis ID")
    
    result = collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    
    return {"message": "Diagnosis deleted successfully"}


@router.post("/ai/diagnosis/{diagnosis_id}/verify")
def verify_diagnosis(diagnosis_id: str, verification: dict):
    """
    Verify or correct AI diagnosis (farmer feedback endpoint).
    """
    update_result = update_diagnosis_mongodb(diagnosis_id, {
        "farmer_feedback": {
            "validated": True,
            "actual_issue": verification.get("actual_issue", "AI diagnosis correct"),
            "treatment_efficacy": verification.get("treatment_efficacy", 4.5),
            "comments": verification.get("comments"),
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
    })
    
    if not update_result:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    
    return {
        "diagnosis_id": diagnosis_id,
        "validated": True,
        "message": "Diagnosis verified successfully"
    }


@router.get("/ai/models")
def list_available_models():
    """List available AI models for diagnosis."""
    return {
        "models": [
            {
                "model_id": "pest_classifier_v2.4",
                "name": "Pest Classifier",
                "version": "2.4.1",
                "type": "classification",
                "accuracy": 0.94,
                "classes_count": 156,
                "status": "active"
            },
            {
                "model_id": "disease_classifier_v1.2",
                "name": "Disease Classifier",
                "version": "1.2.0",
                "type": "classification",
                "accuracy": 0.91,
                "classes_count": 89,
                "status": "active"
            },
            {
                "model_id": "crop_health_v1.0",
                "name": "Crop Health Assessment",
                "version": "1.0.0",
                "type": "segmentation",
                "accuracy": 0.88,
                "classes_count": 5,
                "status": "active"
            }
        ]
    }
