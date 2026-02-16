import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

# Define root path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add shared/py to path - PREPEND to override installed package
sys.path.insert(0, os.path.join(ROOT_DIR, "shared", "py"))

# Adjust path to find app modules
sys.path.append(ROOT_DIR)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Add venv site-packages
# NOTE: The venv in Downloads seems to point to Desktop installation
desktop_venv_path = "/home/kaleab/Desktop/Farm_Connect/venv/lib/python3.12/site-packages"
if os.path.exists(desktop_venv_path):
    sys.path.append(desktop_venv_path)

venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "lib", "python3.12", "site-packages")
if os.path.exists(venv_path):
    sys.path.append(venv_path)


# Mock pymongo
class MockCollection:
    def __init__(self):
        self.data = {}
        
    def insert_one(self, doc):
        _id = doc.get("_id")
        self.data[_id] = doc
        return MagicMock(inserted_id=_id)
        
    def find_one(self, query):
        _id = query.get("_id")
        return self.data.get(_id)
        
    def update_one(self, query, update):
        _id = query.get("_id")
        if _id in self.data:
            changes = update.get("$set", {})
            self.data[_id].update(changes)
            return MagicMock(modified_count=1)
        return MagicMock(modified_count=0)

class MockDB:
    def __init__(self):
        self.collection = MockCollection()
        
    def __getitem__(self, name):
        return self.collection

# Mock deps
sys.modules["app.core.database"] = MagicMock()
from app.core.database import get_mongo_db

from app.domain.ai.services import DiagnosisService, ImageAnalysisService, TreatmentService
from app.infrastructure.repositories.ai_repo import AiRepository
from app.domain.ai.models import DiagnosisSession

async def test_ai_flow():
    print("Starting AI Diagnosis Flow Verification...")
    
    # Setup Mocks
    mock_db = MockDB()
    repo = AiRepository(mock_db)
    service = DiagnosisService(repo)
    
    # 1. Start Diagnosis Session
    print("\n1. Creating Diagnosis Session...")
    session = service.create_session(
        field_id="FLD-123",
        crop_type="Tomato",
        growth_stage="Flowering",
        issue_category="Disease",
        priority="high",
        affected_area_pct=20.0,
        symptom_severity="medium",
        image_urls=[],
        symptoms_list=["Spots"],
        # Mocking generic optional fields 
        crop_cycle_id=None, location=None, region=None, planting_date=None, 
        suspected_issue=None, symptom_onset_days=None, weather_recent=None,
        irrigation_type=None, soil_type=None, farmer_notes=None
    )
    
    print(f"   Session Created: {session.id}")
    assert session.status == "processing"
    
    # 2. Add Symptoms
    print("\n2. Adding Detailed Symptoms...")
    symptoms_data = [{
        "symptom_type": "Leaf Spot",
        "location_on_plant": "Leaves",
        "description": "Dark concentric rings"
    }]
    updated_session_dict = service.add_symptoms(session.id, symptoms_data)
    print(f"   Symptoms added. Current status: {updated_session_dict.get('status')}")
    
    # 3. Running Image Analysis
    print("\n3. Running Image Analysis...")
    # Using a URL that triggers the "blight" mock path
    image_url = "http://example.com/tomato_early_blight.jpg"
    result = await service.run_image_analysis(session.id, image_url, "disease")
    
    print(f"   Analysis Type: {result.analysis_type}")
    print(f"   Confidence: {result.confidence_score}")
    print(f"   Primary Issue: {result.primary_issue}")
    
    assert result.primary_issue == "Early Blight"
    assert result.confidence_score > 0.8
    
    # Verify session update
    session_data = service.get_session(session.id)
    print(f"   Session Primary Diagnosis: {session_data.get('primary_diagnosis')}")
    assert session_data.get("primary_diagnosis") == "Early Blight"
    
    # 4. Get Treatments
    print("\n4. Getting Recommendations...")
    treatments = service.get_treatments(session.id)
    
    print(f"   Recommendations found: {len(treatments)}")
    for t in treatments:
        print(f"   - {t.name} ({t.type})")
        
    assert len(treatments) > 0
    assert treatments[0].name == "Copper Fungicide"
    
    print("\n✅ AI Diagnosis Flow Verified Successfully!")

if __name__ == "__main__":
    asyncio.run(test_ai_flow())
