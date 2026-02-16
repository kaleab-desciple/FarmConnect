import sys
import os
from uuid import UUID
from datetime import datetime, timezone

# Adjust path to find app modules
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR)

from app.core.database import SessionLocal
from app.infrastructure.repositories.monitoring_repo import PestDiseaseReportRepository
from app.domain.monitoring.entities import PestDiseaseReportCreate

def test_persistence():
    print("Testing data persistence in PestDiseaseReportRepository...")
    db = SessionLocal()
    try:
        repo = PestDiseaseReportRepository(db)
        
        report_data = PestDiseaseReportCreate(
            field_id=UUID("259df240-cef5-450b-b54d-ccff2d56c5c8"),
            crop_cycle_id=UUID("b41a826b-5e66-4667-8256-f0f6a3b993b2"),
            reported_by="FAR-00001",
            location_geojson={"type": "Point", "coordinates": [0, 0]},
            image_urls=["test1.jpg"],
            suspected_issue="Verifying persistence fix",
            severity="MEDIUM",
            affected_area_ha=1.0,
            affected_plant_count=10,
            detected_at=datetime.now(timezone.utc)
        )
        
        print("Creating report...")
        created = repo.create(report_data)
        print(f"Report created with ID: {created.id}")
        
        # Now verify it's actually in the database by starting a NEW session
        db.close()
        
        print("Verifying in a new session...")
        db2 = SessionLocal()
        repo2 = PestDiseaseReportRepository(db2)
        retrieved = repo2.get_by_id(str(created.id))
        
        if retrieved:
            print(f"SUCCESS: Found report {retrieved.id} in database!")
        else:
            print("FAILURE: Report not found in database!")
            
        db2.close()
    except Exception as e:
        print(f"Error during test: {e}")
        db.close()

if __name__ == "__main__":
    test_persistence()
