from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class GeoLocation:
    latitude: float
    longitude: float
    altitude_m: Optional[float] = None
    accuracy_m: Optional[float] = None

@dataclass
class SymptomDetail:
    symptom_type: str
    location_on_plant: str
    pattern: Optional[str] = None
    progression: Optional[str] = None
    description: Optional[str] = None

@dataclass
class AnalysisDetection:
    detection_type: str
    name: str
    scientific_name: Optional[str]
    confidence: float
    bbox: Optional[List[int]] = None
    severity: Optional[str] = None
    affected_area_pct: Optional[float] = None

@dataclass
class ImageAnalysisResult:
    analysis_id: str
    image_url: str
    analysis_type: str
    detections: List[AnalysisDetection]
    overall_health_score: float
    primary_issue: Optional[str]
    confidence_score: float
    model_used: str
    processing_time_ms: int
    recommendations: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class TreatmentOption:
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

@dataclass
class DiagnosisSession:
    id: str
    field_id: str
    crop_cycle_id: Optional[str]
    location: Optional[GeoLocation]
    region: Optional[str]
    crop_type: str
    growth_stage: str
    planting_date: Optional[str]
    
    # Issue details
    suspected_issue: Optional[str]
    issue_category: str
    affected_area_pct: float
    symptoms_list: List[str]
    symptom_onset_days: Optional[int]
    symptom_severity: str
    
    # Context
    weather_recent: Optional[str]
    irrigation_type: Optional[str]
    soil_type: Optional[str]
    
    # Assets
    image_urls: List[str]
    
    # Metadata
    priority: str
    farmer_notes: Optional[str]
    status: str  # processing, diagnosed, completed, failed
    
    # Results
    confidence_score: Optional[float] = None
    primary_diagnosis: Optional[str] = None
    
    # Progress
    symptom_details: List[SymptomDetail] = field(default_factory=list)
    image_analyses: List[ImageAnalysisResult] = field(default_factory=list)
    treatments_recommended: List[TreatmentOption] = field(default_factory=list)
    treatments_applied: List[Dict[str, Any]] = field(default_factory=list) # simplified for now
    follow_ups: List[Dict[str, Any]] = field(default_factory=list)
    farmer_feedback: Optional[Dict[str, Any]] = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, **kwargs):
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid4()),
            created_at=now,
            updated_at=now,
            status="processing",
            symptom_details=[],
            image_analyses=[],
            treatments_recommended=[],
            treatments_applied=[],
            follow_ups=[],
            **kwargs
        )

    def to_dict(self):
        # Helper to convert nested dataclasses to dicts for MongoDB
        # simpler than full serialization lib
        # In a real app we might use Pydantic directly or a proper ODM
        # For now, we'll rely on the fact that standard types are JSON serializable
        # and we need to handle nested dataclasses carefully if we use pymongo directly.
        # Ideally, we should use Pydantic models in the Domain layer if usage is heavy,
        # but adhering to the pattern: this is a pure python entity.
        # We will map it in the Repository.
        pass 
