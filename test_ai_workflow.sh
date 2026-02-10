#!/bin/bash
# Complete AI Diagnosis Workflow Test Script
# Run this after starting the API server

BASE_URL="http://localhost:8000/api/v1/agri"

# Use the diagnosis ID from Step 1
DIAGNOSIS_ID="f8b37582-2759-4c4b-aecb-a745f40b2e27"

echo "=========================================="
echo "AI Diagnosis Workflow - Complete Test"
echo "=========================================="

# Step 1: Check Diagnosis Status
echo ""
echo "=== Step 1: Get Diagnosis Status ==="
curl -s -X GET "$BASE_URL/ai/diagnosis/$DIAGNOSIS_ID" | jq .

# Step 2: Submit Symptom Details
echo ""
echo "=== Step 2: Submit Symptoms ==="
curl -s -X POST "$BASE_URL/ai/symptoms" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis_session_id": "'"$DIAGNOSIS_ID"'",
    "symptoms": [
      {
        "symptom_type": "leaf_spots",
        "location_on_plant": "leaves",
        "pattern": "scattered",
        "progression": "spreading_from_lower_to_upper",
        "description": "Circular brown spots with concentric rings"
      },
      {
        "symptom_type": "wilting",
        "location_on_plant": "whole_plant",
        "pattern": "clustered",
        "description": "Plants showing midday wilting"
      }
    ],
    "plant_health_score": 4,
    "affected_plants_count": 150,
    "total_plants_observed": 500,
    "pest_presence": ["aphids", "whitefly"],
    "beneficial_insects": ["ladybug"],
    "weed_pressure": "medium"
  }' | jq .

# Step 3: Image Analysis
echo ""
echo "=== Step 3: Image Analysis ==="
curl -s -X POST "$BASE_URL/ai/analyze-image" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis_session_id": "'"$DIAGNOSIS_ID"'",
    "image_url": "https://s3.amazonaws.com/farm-connect-images/wheat-leaves.jpg",
    "image_metadata": {
      "width": 4032,
      "height": 3024,
      "format": "jpeg"
    },
    "analysis_type": "disease",
    "analysis_mode": "detailed",
    "plant_part": "leaf"
  }' | jq .

# Step 4: Treatment Recommendations
echo ""
echo "=== Step 4: Treatment Recommendations ==="
curl -s -X POST "$BASE_URL/ai/treatment" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis_session_id": "'"$DIAGNOSIS_ID"'",
    "treatment_type_preference": "all",
    "budget_constraint": {
      "max_cost_per_ha": 50.0,
      "currency": "ETB"
    },
    "time_to_harvest_days": 45,
    "water_source_proximity": true,
    "organic_certified": false,
    "pollinator_present": true,
    "equipment_available": ["backpack_sprayer", "motorized_sprayer"],
    "labor_availability": "adequate"
  }' | jq .

# Step 5: Follow-up Query
echo ""
echo "=== Step 5: Follow-up Query ==="
curl -s -X POST "$BASE_URL/ai/follow-up" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis_session_id": "'"$DIAGNOSIS_ID"'",
    "question_type": "application_guidance",
    "question": "How long should I wait after applying copper fungicide before harvesting wheat?",
    "treatment_applied": "Copper Oxychloride 50% WP"
  }' | jq .

# Step 6: Verify Diagnosis
echo ""
echo "=== Step 6: Verify Diagnosis (Farmer Feedback) ==="
curl -s -X POST "$BASE_URL/ai/diagnosis/$DIAGNOSIS_ID/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_issue": "AI diagnosis was correct",
    "treatment_efficacy": 4.5,
    "comments": "Treatment worked well, saw improvement in 3 days"
  }' | jq .

# Step 7: Batch Status Check
echo ""
echo "=== Step 7: Batch Status Check ==="
curl -s -X GET "$BASE_URL/ai/batch-status?session_ids=$DIAGNOSIS_ID&include_details=true" | jq .

# Step 8: List All Diagnoses
echo ""
echo "=== Step 8: List All Diagnoses ==="
curl -s -X GET "$BASE_URL/ai/diagnoses" | jq .

# Step 9: List Available Models
echo ""
echo "=== Step 9: List Available AI Models ==="
curl -s -X GET "$BASE_URL/ai/models" | jq .

echo ""
echo "=========================================="
echo "Complete Workflow Test Finished"
echo "=========================================="
