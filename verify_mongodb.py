#!/usr/bin/env python3
"""
MongoDB Verification Script for Farm Connect AI Diagnosis Service

This script verifies MongoDB connectivity and data storage for the AI Diagnosis Workflow.
Run this script to verify MongoDB integration.

Usage:
    # As standalone script
    python verify_mongodb.py
    
    # As pytest
    pytest verify_mongodb.py -v
"""

import sys
import json
from datetime import datetime, timezone
from uuid import uuid4

# Add the server directory to the path
sys.path.insert(0, '/home/kaleab/Downloads/Farm_Connect/server')

import pytest
from pymongo import MongoClient


# ============== TEST DATA ==============

def get_test_diagnosis():
    """Generate test diagnosis data."""
    return {
        "_id": str(uuid4()),
        "field_id": "FLD-TEST-001",
        "crop_type": "Wheat",
        "growth_stage": "flowering",
        "region": "Oromia",
        "issue_category": "disease",
        "suspected_issue": "fungal disease",
        "affected_area_pct": 35.0,
        "symptom_severity": "high",
        "symptoms": ["brown_spots", "yellowing"],
        "processing_status": "completed",
        "primary_diagnosis": "Septoria Leaf Blotch",
        "confidence_score": 0.89,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "treatment_recommendations": [],
        "farmer_feedback": None
    }


def get_sample_diagnosis():
    """Generate sample diagnosis with realistic Ethiopian agriculture data."""
    return {
        "_id": str(uuid4()),
        "field_id": "FLD-2024-ABB-042",
        "crop_cycle_id": "CC-2024-WHEAT-001",
        "farm_id": "FARM-ABB-2024",
        "location": {
            "latitude": 9.145,
            "longitude": 40.489,
            "altitude_m": 2080,
            "region": "Oromia",
            "woreda": "Bako",
            "kebele": "Tibe"
        },
        "crop_type": "Wheat",
        "crop_variety": "ETBW 9397",
        "growth_stage": "flowering",
        "planting_date": "2024-06-15",
        "soil_type": "vertisol",
        "irrigation_type": "rainfed",
        "issue_category": "disease",
        "suspected_issue": "leaf_blotch",
        "affected_area_pct": 35.0,
        "symptom_onset_days": 7,
        "symptom_severity": "high",
        "symptoms": ["brown_spots", "yellowing", "premature_drying"],
        "weather_recent": "heavy_rain_past_week",
        "processing_status": "completed",
        "ensemble_result": {
            "primary_diagnosis": "Septoria Leaf Blotch",
            "scientific_name": "Septoria tritici",
            "confidence": 0.89,
            "severity": "moderate",
            "affected_area_estimate_pct": 15.2
        },
        "treatment_recommendations": [
            {
                "treatment_id": str(uuid4()),
                "type": "chemical",
                "name": "Copper Oxychloride 50% WP",
                "active_ingredient": "Copper Oxychloride",
                "cost_per_ha": 45.00,
                "pre_harvest_interval_days": 7
            },
            {
                "treatment_id": str(uuid4()),
                "type": "biological",
                "name": "Bacillus subtilis QST 713",
                "active_ingredient": "Bacillus subtilis",
                "cost_per_ha": 35.00,
                "pre_harvest_interval_days": 0
            }
        ],
        "cultural_controls": [
            "Remove infected plant material",
            "Improve air circulation"
        ],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


# ============== PYTEST TESTS ==============

class TestMongoDBConnection:
    """Test MongoDB connection and basic operations."""
    
    @pytest.fixture(scope="class")
    def mongo_client(self):
        """Create MongoDB client for testing."""
        MONGO_URI = "mongodb://localhost:27017/agri_db"
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        yield client
        client.close()
    
    @pytest.fixture(scope="class")
    def db(self, mongo_client):
        """Get database instance."""
        return mongo_client["agri_db"]
    
    @pytest.fixture(scope="class")
    def collection(self, db):
        """Get collection and cleanup after tests."""
        coll = db["ai_diagnoses"]
        yield coll
        # Cleanup: remove test documents
        coll.delete_many({"field_id": {"$in": ["FLD-TEST-001", "FLD-2024-ABB-042"]}})
    
    def test_mongodb_connection(self, mongo_client):
        """Test 1: Verify MongoDB connection."""
        mongo_client.admin.command('ping')
    
    def test_collection_exists(self, db):
        """Test 2: Verify collection exists."""
        collections = db.list_collection_names()
        assert "ai_diagnoses" in collections
    
    def test_create_diagnosis(self, collection):
        """Test 3: Create a diagnosis record."""
        diagnosis = get_test_diagnosis()
        result = collection.insert_one(diagnosis)
        assert result.inserted_id is not None
        assert result.acknowledged is True
    
    def test_retrieve_diagnosis(self, collection):
        """Test 4: Retrieve diagnosis record."""
        diagnosis = get_test_diagnosis()
        collection.insert_one(diagnosis)
        
        retrieved = collection.find_one({"_id": diagnosis["_id"]})
        assert retrieved is not None
        assert retrieved["primary_diagnosis"] == "Septoria Leaf Blotch"
        assert retrieved["confidence_score"] == 0.89
    
    def test_update_diagnosis(self, collection):
        """Test 5: Update diagnosis record."""
        diagnosis = get_test_diagnosis()
        collection.insert_one(diagnosis)
        
        update_result = collection.update_one(
            {"_id": diagnosis["_id"]},
            {"$set": {"farmer_feedback": {"validated": True}}}
        )
        assert update_result.modified_count == 1
        
        updated = collection.find_one({"_id": diagnosis["_id"]})
        assert updated["farmer_feedback"]["validated"] is True
    
    def test_index_creation(self, collection):
        """Test 6: Create and verify indexes."""
        collection.create_index("field_id")
        collection.create_index([("created_at", -1)])
        collection.create_index("primary_diagnosis")
        
        indexes = list(collection.list_indexes())
        index_names = [idx["name"] for idx in indexes]
        # MongoDB appends _1 for ascending, _-1 for descending
        assert "field_id_1" in index_names or "field_id" in index_names
        assert "created_at_-1" in index_names
    
    def test_list_diagnoses(self, collection):
        """Test 7: List all diagnoses."""
        diagnoses = list(collection.find())
        assert len(diagnoses) >= 0
    
    def test_delete_diagnosis(self, collection):
        """Test 8: Delete diagnosis record."""
        diagnosis = get_test_diagnosis()
        collection.insert_one(diagnosis)
        
        delete_result = collection.delete_one({"_id": diagnosis["_id"]})
        assert delete_result.deleted_count == 1
        
        retrieved = collection.find_one({"_id": diagnosis["_id"]})
        assert retrieved is None
    
    def test_sample_ethiopian_diagnosis(self, collection):
        """Test 9: Create sample diagnosis with Ethiopian context."""
        diagnosis = get_sample_diagnosis()
        result = collection.insert_one(diagnosis)
        
        assert result.inserted_id is not None
        
        retrieved = collection.find_one({"_id": diagnosis["_id"]})
        assert retrieved["location"]["region"] == "Oromia"
        assert retrieved["location"]["woreda"] == "Bako"
        assert retrieved["crop_type"] == "Wheat"
        assert len(retrieved["treatment_recommendations"]) == 2
    
    def test_diagnosis_with_treatments(self, collection):
        """Test 10: Verify treatment recommendations storage."""
        diagnosis = get_sample_diagnosis()
        collection.insert_one(diagnosis)
        
        retrieved = collection.find_one({"_id": diagnosis["_id"]})
        treatments = retrieved["treatment_recommendations"]
        
        assert len(treatments) == 2
        assert treatments[0]["type"] == "chemical"
        assert treatments[1]["type"] == "biological"
        assert treatments[0]["pre_harvest_interval_days"] == 7
        assert treatments[1]["pre_harvest_interval_days"] == 0


# ============== STANDALONE EXECUTION ==============

def verify_mongodb_connection():
    """Verify MongoDB connection and basic operations."""
    print("=" * 60)
    print("MongoDB Verification for Farm Connect AI Diagnosis Service")
    print("=" * 60)
    
    MONGO_URI = "mongodb://localhost:27017/agri_db"
    
    try:
        print("\n[1] Connecting to MongoDB...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("    ✓ MongoDB connection successful")
        
        db = client["agri_db"]
        collection = db["ai_diagnoses"]
        
        print("\n[2] Checking collections...")
        collections = db.list_collection_names()
        print(f"    ✓ Existing collections: {collections}")
        
        print("\n[3] Creating test diagnosis record...")
        test_diagnosis = get_test_diagnosis()
        result = collection.insert_one(test_diagnosis)
        print(f"    ✓ Created test diagnosis: {result.inserted_id}")
        
        print("\n[4] Verifying data retrieval...")
        retrieved = collection.find_one({"_id": test_diagnosis["_id"]})
        assert retrieved is not None
        print(f"    ✓ Retrieved: {retrieved['primary_diagnosis']}")
        
        print("\n[5] Creating indexes...")
        collection.create_index("field_id")
        collection.create_index([("created_at", -1)])
        print("    ✓ Indexes created")
        
        print("\n[6] Listing all diagnoses...")
        all_diagnoses = list(collection.find())
        print(f"    ✓ Total diagnoses: {len(all_diagnoses)}")
        
        print("\n[7] Cleaning up test data...")
        collection.delete_one({"_id": test_diagnosis["_id"]})
        print("    ✓ Test data cleaned up")
        
        print("\n[8] Creating sample Ethiopian diagnosis...")
        sample = get_sample_diagnosis()
        result = collection.insert_one(sample)
        print(f"    ✓ Sample created: {result.inserted_id}")
        print(f"    ✓ Region: {sample['location']['region']}")
        print(f"    ✓ Treatments: {len(sample['treatment_recommendations'])}")
        
        print("\n" + "=" * 60)
        print("MongoDB Verification Complete - All Tests Passed ✓")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure MongoDB is running: docker-compose up -d mongodb")
        print("2. Check MongoDB is accessible on port 27017")
        return False
    
    finally:
        try:
            client.close()
        except:
            pass


if __name__ == "__main__":
    success = verify_mongodb_connection()
    sys.exit(0 if success else 1)
