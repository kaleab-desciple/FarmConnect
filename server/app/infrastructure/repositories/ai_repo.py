from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from dataclasses import asdict
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.domain.ai.models import DiagnosisSession, ImageAnalysisResult, TreatmentOption

class AiRepository:
    def __init__(self, db: Database):
        self.collection = db["ai_diagnoses"]

    def create_session(self, session: DiagnosisSession) -> DiagnosisSession:
        """Create a new diagnosis session in MongoDB."""
        # Convert dataclass to dict
        # We need a custom conversion because standard asdict doesn't handle nested dataclasses 
        # for MongoDB serialization perfectly if we want specific field names or types (like _id)
        # However, for simplicity allowing pymongo to handle dict conversion is standard.
        # We just need to make sure we don't have non-serializable objects.
        
        session_dict = asdict(session)
        session_dict["_id"] = session.id
        del session_dict["id"] # Use _id as primary key
        
        self.collection.insert_one(session_dict)
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a diagnosis session by ID."""
        # We return a dict for now to be flexible, the service layer can reconstruct the entity
        # or we can do it here. Given the complexity of nested dataclasses, returning dict 
        # and letting service handle domain logic is often easier for rapid dev, 
        # but reconstructing is cleaner architecture.
        # Let's return the dict from Mongo for now as the Pydantic models in API layer expect dicts/attributes.
        
        doc = self.collection.find_one({"_id": session_id})
        if not doc:
            return None
        
        # Map _id back to id
        doc["id"] = doc["_id"]
        # del doc["_id"] # Optional, dependent on how downstream uses it
        return doc

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update a diagnosis session."""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = self.collection.update_one(
            {"_id": session_id},
            {"$set": updates}
        )
        return result.modified_count > 0

    def list_sessions(self, field_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List diagnosis sessions."""
        query = {}
        if field_id:
            query["field_id"] = field_id
            
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        results = []
        for doc in cursor:
            doc["id"] = doc["_id"]
            results.append(doc)
        return results
