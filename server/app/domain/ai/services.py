from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
import asyncio

from app.domain.ai.models import (
    DiagnosisSession, 
    ImageAnalysisResult, 
    AnalysisDetection, 
    TreatmentOption,
    SymptomDetail
)
from app.infrastructure.repositories.ai_repo import AiRepository

class ImageAnalysisService:
    """
    Service to handle image analysis logic.
    In production, this would call an external ML Model Serving endpoint (e.g., TFServing, TorchServe).
    For now, it simulates analysis with heuristic logic based on the image URL or random seeds.
    """
    async def analyze_image(self, image_url: str, analysis_type: str) -> ImageAnalysisResult:
        # Simulate processing delay
        # await asyncio.sleep(0.5) 
        
        # Mock logic: deterministic "detection" based on URL hash or keywords
        # This is better than random for testing (reproducible)
        
        detections = []
        primary_issue = None
        confidence = 0.0
        
        if "blight" in image_url.lower() or "disease" in image_url.lower():
            detections.append(AnalysisDetection(
                detection_type="disease",
                name="Early Blight",
                scientific_name="Alternaria solani",
                confidence=0.88,
                severity="moderate",
                affected_area_pct=15.0
            ))
            primary_issue = "Early Blight"
            confidence = 0.88
        elif "pest" in image_url.lower() or "worm" in image_url.lower():
            detections.append(AnalysisDetection(
                detection_type="pest",
                name="Fall Armyworm",
                scientific_name="Spodoptera frugiperda",
                confidence=0.92,
                severity="high",
                affected_area_pct=40.0
            ))
            primary_issue = "Fall Armyworm"
            confidence = 0.92
        else:
            # Default fallback for generic images
            detections.append(AnalysisDetection(
                detection_type="unknown",
                name="Unidentified Issue",
                scientific_name=None,
                confidence=0.45,
                severity="low"
            ))
            primary_issue = "Unidentified Issue"
            confidence = 0.45
            
        return ImageAnalysisResult(
            analysis_id=str(uuid4()),
            image_url=image_url,
            analysis_type=analysis_type,
            detections=detections,
            overall_health_score=0.6,
            primary_issue=primary_issue,
            confidence_score=confidence,
            model_used="simulated_model_v1",
            processing_time_ms=250,
            recommendations=["Monitor closely", "Validate with field inspection"]
        )

class TreatmentService:
    """
    Service to generate treatment recommendations.
    Ideally links to Knowledge Base articles.
    """
    def generate_treatments(self, diagnosis: str, severity: str) -> List[TreatmentOption]:
        # Simple rule-based engine for now
        treatments = []
        
        if "Blight" in diagnosis:
            treatments.append(TreatmentOption(
                treatment_id=str(uuid4()),
                type="chemical",
                name="Copper Fungicide",
                active_ingredient="Copper Oxychloride",
                efficacy_score=0.85,
                cost_per_ha=45.0,
                application_method="spray",
                pre_harvest_interval_days=7,
                reentry_interval_hours=24,
                restrictions=["Do not apply in rain"],
                safety_ppe=["Gloves", "Mask"],
                environmental_warnings=["Toxic to fish"],
                application_instructions="Mix 2g/L and spray."
            ))
        elif "Armyworm" in diagnosis:
             treatments.append(TreatmentOption(
                treatment_id=str(uuid4()),
                type="biological",
                name="Neem Oil Extract",
                active_ingredient="Azadirachtin",
                efficacy_score=0.75,
                cost_per_ha=30.0,
                application_method="spray",
                pre_harvest_interval_days=0,
                reentry_interval_hours=4,
                restrictions=["Apply in evening"],
                safety_ppe=["Gloves"],
                environmental_warnings=["Safe for bees if applied at night"],
                application_instructions="Apply 5ml/L."
            ))
            
        return treatments

class DiagnosisService:
    """
    Main service orchestrating the diagnosis workflow.
    """
    def __init__(self, repo: AiRepository):
        self.repo = repo
        self.image_service = ImageAnalysisService()
        self.treatment_service = TreatmentService()

    def create_session(self, **kwargs) -> DiagnosisSession:
        session = DiagnosisSession.create(**kwargs)
        return self.repo.create_session(session)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_session(session_id)

    def add_symptoms(self, session_id: str, symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add detailed symptoms to a session."""
        # Validate session exists
        session_data = self.repo.get_session(session_id)
        if not session_data:
            return None
            
        # Update logic
        self.repo.update_session(session_id, {"symptom_details": symptoms})
        
        # Trigger re-evaluation logic here if needed
        # For now, just return updated session state mock
        return self.repo.get_session(session_id)

    async def run_image_analysis(self, session_id: str, image_url: str, analysis_type: str) -> ImageAnalysisResult:
        session_data = self.repo.get_session(session_id)
        if not session_data:
            raise ValueError("Session not found")
            
        # Run analysis
        result = await self.image_service.analyze_image(image_url, analysis_type)
        
        # Update session with result
        # We need to serialize the result to a dict for MongoDB storage
        current_analyses = session_data.get("image_analysis", [])
        if not isinstance(current_analyses, list):
            current_analyses = []
            
        # Convert dataclass to dict for storage
        from dataclasses import asdict
        result_dict = asdict(result)
        result_dict["created_at"] = result.created_at.isoformat()
        
        current_analyses.append(result_dict)
        
        # Update primary diagnosis based on highest confidence
        updates = {
            "image_analysis": current_analyses,
            "status": "diagnosed" if result.confidence_score > 0.7 else "processing"
        }
        
        current_score = session_data.get("confidence_score") or 0.0
        
        if result.confidence_score > current_score:
             updates["primary_diagnosis"] = result.primary_issue
             updates["confidence_score"] = result.confidence_score
             
        self.repo.update_session(session_id, updates)
        
        return result

    def get_treatments(self, session_id: str) -> List[TreatmentOption]:
        session_data = self.repo.get_session(session_id)
        if not session_data:
            raise ValueError("Session not found")
            
        diagnosis = session_data.get("primary_diagnosis")
        if not diagnosis:
            return []
            
        treatments = self.treatment_service.generate_treatments(diagnosis, "medium")
        
        # Store recommendations
        from dataclasses import asdict
        self.repo.update_session(session_id, {
            "treatments_recommended": [asdict(t) for t in treatments]
        })
        
        return treatments
