# AgriManagement Workflow Verification API Documentation

## Complete Step-by-Step API Testing Guide

---

## Table of Contents
1. [Field Management Workflow](#workflow-1-field-management-api-tests)
2. [Manual Data Entry Workflow](#workflow-2-manual-data-entry-api-tests)
3. [AI Diagnosis Workflow](#workflow-3-ai-diagnosis-api-tests)

---

## Workflow 1: Field Management API Tests

### Request #1: Create a Farm
**Endpoint:** `POST http://localhost:8000/api/v1/agri/farms`

```json
{
  "farmer_id": "FAR-00002",
  "name": "Green Valley Farm",
  "location_lat": 9.145,
  "location_lng": 40.489,
  "location_address": "Oromia Region, Ethiopia",
  "total_area_ha": 150.5,
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [
      [
        [40.485, 9.140],
        [40.495, 9.140],
        [40.495, 9.150],
        [40.485, 9.150],
        [40.485, 9.140]
      ]
    ]
  },
  "metadata": {
    "soil_type": "Loam",
    "irrigation_source": "Well"
  }
}
```

**Response:**
```json
{
  "id": "aefc0e4b-8010-4c9a-bc7f-d1d02804795d",
  "status": "created"
}
```

---

### Request #2: Create a Field
**Endpoint:** `POST http://localhost:8000/api/v1/agri/fields`

```json
{
  "farm_id": "aefc0e4b-8010-4c9a-bc7f-d1d02804795d",
  "name": "North Field",
  "area_ha": 50.5,
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [
      [
        [40.485, 9.140],
        [40.490, 9.140],
        [40.490, 9.145],
        [40.485, 9.145],
        [40.485, 9.140]
      ]
    ]
  },
  "soil_type": "Loam",
  "irrigation_type": "Drip",
  "elevation_m": 1500
}
```

---

### Request #3: Create a Crop Cycle
**Endpoint:** `POST http://localhost:8000/api/v1/agri/crop-cycles`

```json
{
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "product_category": "VEGETABLES",
  "crop_name": "Tomato",
  "variety": "Roma",
  "planting_date": "2024-01-15",
  "expected_harvest_date": "2024-06-15",
  "status": "PLANTED",
  "expected_yield_kg": 5000
}
```

---

### Request #4: Create a Farm Task (Work Order)
**Endpoint:** `POST http://localhost:8000/api/v1/agri/tasks`

```json
{
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "crop_cycle_id": "b41a826b-5e66-4667-8256-f0f6a3b993b2",
  "task_type": "IRRIGATION",
  "title": "Morning Drip Irrigation",
  "description": "Drip irrigation for 2 hours - check all emitters",
  "status": "PENDING",
  "priority": "HIGH",
  "scheduled_date": "2024-02-01",
  "duration_estimate_hours": 2.0,
  "assigned_to": "FAR-00002",
  "labor_count": 2,
  "equipment_needed": ["drip_system", "water_pump"],
  "estimated_cost_usd": 50.00
}
```

---

### Request #5: Update Task Status to IN_PROGRESS
**Endpoint:** `PUT http://localhost:8000/api/v1/agri/tasks/{task_id}`

```json
{
  "status": "IN_PROGRESS"
}
```

---

### Request #6: Complete Task
**Endpoint:** `PUT http://localhost:8000/api/v1/agri/tasks/{task_id}`

```json
{
  "status": "COMPLETED",
  "completed_date": "2024-02-01",
  "completed_by": "FAR-00002",
  "duration_actual_hours": 1.75,
  "completion_notes": "All emitters checked and cleared."
}
```

---

## Workflow 2: Manual Data Entry API Tests

### Request #7: Create Soil Reading
**Endpoint:** `POST http://localhost:8000/api/v1/agri/soil-readings`

```json
{
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "location_geojson": {
    "type": "Point",
    "coordinates": [40.489, 9.145]
  },
  "sample_depth_cm": 15,
  "sample_depth_range": "0-15cm",
  "moisture_pct": 35.5,
  "temperature_c": 22.5,
  "ph": 6.8,
  "nitrogen_ppm": 45.0,
  "phosphorus_ppm": 25.0,
  "potassium_ppm": 180.0,
  "organic_matter_pct": 3.2,
  "source": "MANUAL_TEST",
  "recorded_by": "FAR-00002",
  "recorded_at": "2024-02-01T10:00:00Z",
  "weather_conditions": "Sunny",
  "days_since_rain": 3
}
```

**Validation Rules:**
- `moisture_pct`: 0-100
- `ph`: 0-14
- `sample_depth_cm`: > 0

---

### Request #8: Create Pest/Disease Report
**Endpoint:** `POST http://localhost:8000/api/v1/agri/pest-disease-reports`

```json
{
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "crop_cycle_id": "b41a826b-5e66-4667-8256-f0f6a3b993b2",
  "reported_by": "FAR-00002",
  "location_geojson": {
    "type": "Point",
    "coordinates": [40.489, 9.145]
  },
  "image_urls": [
    "https://storage.example.com/images/affected_leaves.jpg"
  ],
  "suspected_issue": "Early Blight",
  "issue_type": "DISEASE",
  "scientific_name": "Alternaria solani",
  "common_names": ["Early blight", "Target spot"],
  "severity": "MEDIUM",
  "affected_area_ha": 2.5,
  "symptoms": "Dark brown spots with concentric rings on lower leaves",
  "spread_pattern": "Scattered",
  "detected_at": "2024-02-01T14:00:00Z"
}
```

---

## Workflow 3: AI Diagnosis API Tests (Step-by-Step)

### Step 1: Initial Diagnosis Request
**Endpoint:** `POST http://localhost:8000/api/v1/agri/ai/diagnose`

```json
{
  "field_id": "FLD-2024-001",
  "crop_cycle_id": "CC-2024-WHEAT-001",
  "location": {
    "latitude": 9.145,
    "longitude": 40.489,
    "altitude_m": 2080,
    "accuracy_m": 5.0
  },
  "region": "Oromia",
  "crop_type": "Wheat",
  "growth_stage": "flowering",
  "planting_date": "2024-06-15",
  "suspected_issue": "fungal disease",
  "issue_category": "disease",
  "affected_area_pct": 35.0,
  "symptoms": [
    "brown_spots_on_leaves",
    "yellowing",
    "premature_drying"
  ],
  "symptom_onset_days": 7,
  "symptom_severity": "high",
  "weather_recent": "heavy_rain_past_week",
  "irrigation_type": "rainfed",
  "soil_type": "vertisol",
  "image_urls": [
    "https://s3.amazonaws.com/farm-connect-images/diagnosis/wheat-001.jpg"
  ],
  "priority": "urgent",
  "farmer_notes": "Disease spreading rapidly after recent heavy rains"
}
```

**Response:**
```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "estimated_completion_seconds": 120,
  "priority_ack": "urgent",
  "message": "Diagnosis session created. You will receive results shortly."
}
```

---

### Step 2: Submit Symptom Details
**Endpoint:** `POST http://localhost:8000/api/v1/agri/ai/symptoms`

```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "symptoms": [
    {
      "symptom_type": "leaf_spots",
      "location_on_plant": "leaves",
      "pattern": "scattered",
      "progression": "spreading_from_lower_to_upper",
      "description": "Circular brown spots with concentric rings, approximately 5-10mm diameter"
    },
    {
      "symptom_type": "wilting",
      "location_on_plant": "whole_plant",
      "pattern": "clustered",
      "progression": "worsening_over_time",
      "description": "Plants showing midday wilting despite adequate soil moisture"
    }
  ],
  "plant_health_score": 4,
  "affected_plants_count": 150,
  "total_plants_observed": 500,
  "pest_presence": ["aphids", "whitefly"],
  "beneficial_insects": ["ladybug", "lacewing"],
  "weed_pressure": "medium",
  "treatments_applied": ["none"],
  "last_fertilizer_date": "2024-07-01",
  "last_irrigation_date": "2024-08-10",
  "additional_image_urls": [
    "https://s3.amazonaws.com/farm-connect-images/symptoms/detail-001.jpg"
  ]
}
```

**Response:**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "symptoms_received": 2,
  "updated_confidence": 0.82,
  "additional_recommendations": [
    "Take photos of unaffected plants for comparison",
    "Note any recent pesticide or fertilizer applications",
    "Check for pest presence on leaf undersides"
  ],
  "next_step": "Upload images for visual analysis if available"
}
```

---

### Step 3: Request Image Analysis
**Endpoint:** `POST http://localhost:8000/api/v1/agri/ai/analyze-image`

```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "image_url": "https://s3.amazonaws.com/farm-connect-images/uploaded/wheat-leaves.jpg",
  "image_metadata": {
    "width": 4032,
    "height": 3024,
    "format": "jpeg",
    "file_size_bytes": 2456789,
    "capture_device": "Samsung Galaxy A52"
  },
  "analysis_type": "disease",
  "analysis_mode": "detailed",
  "captured_at": "2024-08-15T14:30:00Z",
  "capture_conditions": {
    "lighting": "natural_daylight",
    "weather": "partly_cloudy",
    "time_of_day": "14:30"
  },
  "field_context": "middle_section_of_field",
  "plant_part": "leaf"
}
```

**Response:**
```json
{
  "analysis_id": "img-2024-001",
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "image_url": "https://s3.amazonaws.com/farm-connect-images/uploaded/wheat-leaves.jpg",
  "analysis_type": "disease",
  "detections": [
    {
      "detection_type": "disease",
      "name": "Septoria Leaf Blotch",
      "scientific_name": "Septoria tritici",
      "confidence": 0.89,
      "bbox": [120, 200, 350, 480],
      "severity": "moderate",
      "affected_area_pct": 15.2
    },
    {
      "detection_type": "disease",
      "name": "Leaf Rust",
      "scientific_name": "Puccinia triticina",
      "confidence": 0.67,
      "bbox": [500, 300, 200, 250],
      "severity": "low",
      "affected_area_pct": 5.0
    }
  ],
  "overall_health_score": 0.65,
  "primary_issue": "Septoria Leaf Blotch (Septoria tritici)",
  "confidence_score": 0.89,
  "model_used": "disease_classifier_v1.2",
  "processing_time_ms": 245,
  "recommendations": [
    "Apply fungicide at first sign of infection",
    "Remove and destroy infected plant material",
    "Improve air circulation between plants",
    "Avoid overhead irrigation"
  ]
}
```

---

### Step 4: Request Treatment Recommendations
**Endpoint:** `POST http://localhost:8000/api/v1/agri/ai/treatment`

```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "treatment_type_preference": "all",
  "budget_constraint": {
    "max_cost_per_ha": 50.0,
    "currency": "ETB"
  },
  "time_to_harvest_days": 45,
  "water_source_proximity": true,
  "organic_certified": false,
  "pollinator_present": true,
  "equipment_available": [
    "backpack_sprayer",
    "motorized_sprayer"
  ],
  "labor_availability": "adequate",
  "treatments_last_30_days": ["urea_fertilizer"],
  "known_resistance": []
}
```

**Response:**
```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "primary_diagnosis": "Septoria Leaf Blotch",
  "severity": "moderate",
  "treatment_options": [
    {
      "treatment_id": "TR-2024-001",
      "type": "chemical",
      "name": "Copper Oxychloride 50% WP",
      "active_ingredient": "Copper Oxychloride",
      "efficacy_score": 0.85,
      "cost_per_ha": 45.00,
      "application_method": "foliar_spray",
      "pre_harvest_interval_days": 7,
      "reentry_interval_hours": 24,
      "restrictions": ["Do not apply during bloom", "Rotate with different mode"],
      "safety_ppe": ["gloves", "mask", "eye_protection"],
      "environmental_warnings": ["toxic_to_fish", "avoid_near_waterways"],
      "application_instructions": "Apply at 2-3 g/L water, spray thoroughly on both leaf surfaces"
    },
    {
      "treatment_id": "TR-2024-002",
      "type": "biological",
      "name": "Bacillus subtilis QST 713",
      "active_ingredient": "Bacillus subtilis",
      "efficacy_score": 0.78,
      "cost_per_ha": 35.00,
      "application_method": "foliar_spray",
      "pre_harvest_interval_days": 0,
      "reentry_interval_hours": 4,
      "restrictions": ["Store below 30C", "Use within 6 months"],
      "safety_ppe": ["gloves"],
      "environmental_warnings": [],
      "application_instructions": "Apply at 5 ml/L water, ensure good coverage"
    }
  ],
  "recommended_options": ["TR-2024-001"],
  "cultural_controls": [
    "Remove infected leaves immediately",
    "Practice crop rotation with non-host crops",
    "Sanitize tools between plants",
    "Avoid working with wet plants"
  ],
  "prevention_measures": [
    "Use disease-free seeds",
    "Maintain proper plant spacing",
    "Water at base, avoid wetting leaves",
    "Monitor fields weekly"
  ],
  "follow_up_interval_days": 7,
  "success_indicators": [
    "No new lesions after 5-7 days",
    "Existing lesions stop expanding",
    "New growth appears healthy"
  ],
  "extension_contacts": [
    {"name": "Oromia Agriculture Bureau", "phone": "+251-11-123-4567"},
    {"name": "Ethiopian Institute of Agriculture", "phone": "+251-11-234-5678"}
  ]
}
```

---

### Step 5: Submit Follow-up Query
**Endpoint:** `POST http://localhost:8000/api/v1/agri/ai/follow-up`

```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "question_type": "application_guidance",
  "question": "How long should I wait after applying the copper fungicide before I can safely harvest the wheat? Also, can I apply it together with the urea fertilizer I'm planning to use?",
  "treatment_applied": "Copper Oxychloride 50% WP",
  "application_date": "2024-08-15",
  "observed_results": "Some improvement visible after 3 days, but new small spots still appearing on upper leaves",
  "follow_up_image_urls": [
    "https://s3.amazonaws.com/farm-connect-images/followup/status-001.jpg"
  ]
}
```

**Response:**
```json
{
  "query_id": "Q-2024-001",
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "question_type": "application_guidance",
  "answer": "Wait at least 7 days after the final fungicide application before harvesting wheat. Do NOT mix copper fungicide with urea fertilizer as this can cause phytotoxicity and reduce efficacy. Apply them at least 3 days apart.",
  "recommendations": [
    "Apply fungicide in early morning for best results",
    "Ensure complete coverage of both leaf surfaces",
    "Reapply after 7-10 days if disease continues to spread"
  ],
  "urgency_level": "normal",
  "immediate_actions": [
    "Do not mix copper with urea",
    "Schedule fungicide application 3 days before or after fertilizer",
    "Monitor for improvement over next 5 days"
  ],
  "monitor_for": [
    "New lesion development",
    "Spread to previously healthy plants",
    "Any adverse plant reactions"
  ],
  "escalation_contact": {
    "name": "Extension Officer",
    "phone": "+251-XX-XXX-XXXX"
  }
}
```

---

### Step 6: Retrieve Diagnosis History
**Endpoint:** `GET http://localhost:8000/api/v1/agri/ai/diagnosis/{diagnosis_id}`

**No body required**

**Response:**
```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "field_id": "FLD-2024-001",
  "crop_type": "Wheat",
  "growth_stage": "flowering",
  "created_at": "2024-08-15T10:00:00Z",
  "last_updated": "2024-08-15T14:30:00Z",
  "status": "completed",
  "primary_diagnosis": "Septoria Leaf Blotch",
  "diagnosis_confidence": 0.89,
  "severity": "moderate",
  "affected_area_pct": 15.2,
  "symptoms_recorded": [
    {
      "symptom_type": "leaf_spots",
      "location_on_plant": "leaves",
      "pattern": "scattered"
    }
  ],
  "images_analyzed": [
    {
      "analysis_id": "img-2024-001",
      "image_url": "https://s3.amazonaws.com/farm-connect-images/wheat-leaves.jpg"
    }
  ],
  "treatments_recommended": [
    {
      "treatment_id": "TR-2024-001",
      "name": "Copper Oxychloride 50% WP",
      "type": "chemical"
    }
  ],
  "treatments_applied": [
    {
      "treatment_id": "TR-2024-001",
      "name": "Copper Oxychloride 50% WP",
      "applied_date": "2024-08-15"
    }
  ],
  "farmer_feedback": {
    "validated": true,
    "actual_issue": "Septoria Leaf Blotch",
    "treatment_efficacy": 4.5,
    "comments": "Treatment worked well"
  },
  "final_outcome": "successful_treatment",
  "outcome_rating": 5,
  "follow_up_count": 1
}
```

---

### Step 7: Batch Diagnosis Status Check
**Endpoint:** `GET http://localhost:8000/api/v1/agri/ai/batch-status`

**Query Parameters:**
```
?session_ids=id1,id2,id3&include_details=true
```

**Response:**
```json
{
  "total_requested": 3,
  "completed": 2,
  "pending": 1,
  "failed": 0,
  "statuses": [
    {
      "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "status": "completed",
      "field_id": "FLD-2024-001",
      "crop_type": "Wheat",
      "created_at": "2024-08-15T10:00:00Z",
      "primary_diagnosis": "Septoria Leaf Blotch",
      "confidence": 0.89
    },
    {
      "diagnosis_session_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "status": "processing",
      "field_id": "FLD-2024-002",
      "crop_type": "Teff",
      "created_at": "2024-08-15T11:00:00Z"
    },
    {
      "diagnosis_session_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "status": "completed",
      "field_id": "FLD-2024-003",
      "crop_type": "Maize",
      "created_at": "2024-08-15T12:00:00Z",
      "primary_diagnosis": "Fall Armyworm",
      "confidence": 0.95
    }
  ]
}
```

---

### Bonus: Verify Diagnosis (Farmer Feedback)
**Endpoint:** `POST http://localhost:8000/api/v1/agri/ai/diagnosis/{diagnosis_id}/verify`

```json
{
  "actual_issue": "AI diagnosis was correct",
  "treatment_efficacy": 4.5,
  "comments": "Treatment worked well, saw improvement in 3 days"
}
```

**Response:**
```json
{
  "diagnosis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "validated": true,
  "message": "Diagnosis verified successfully"
}
```

---

## Quick Test Script (cURL)

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1/agri"

echo "=== Step 1: Initial Diagnosis Request ==="
curl -X POST "$BASE_URL/ai/diagnose" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FLD-2024-001",
    "crop_type": "Wheat",
    "growth_stage": "flowering",
    "issue_category": "disease",
    "affected_area_pct": 35.0,
    "symptom_severity": "high",
    "symptoms": ["brown_spots", "yellowing"],
    "region": "Oromia",
    "priority": "urgent"
  }' | jq .

echo ""
echo "=== Step 2: Get Diagnosis History ==="
curl -X GET "$BASE_URL/ai/diagnoses" | jq .

echo ""
echo "=== Step 3: List Available AI Models ==="
curl -X GET "$BASE_URL/ai/models" | jq .
```

---

## Summary of All Requests

| # | Workflow | Endpoint | Method | Status |
|---|----------|----------|--------|--------|
| 1 | Field | Create Farm | POST | ✅ |
| 2 | Field | Create Field | POST | ✅ |
| 3 | Field | Create Crop Cycle | POST | ✅ |
| 4 | Field | Create Task | POST | ✅ |
| 5 | Field | Update Task | PUT | ✅ |
| 6 | Field | Complete Task | PUT | ✅ |
| 7 | Manual | Soil Reading | POST | ✅ |
| 8 | Manual | Pest/Disease Report | POST | ✅ |
| 9 | AI | Initial Diagnosis | POST | ✅ |
| 10 | AI | Submit Symptoms | POST | ✅ |
| 11 | AI | Image Analysis | POST | ✅ |
| 12 | AI | Treatment Recommendations | POST | ✅ |
| 13 | AI | Follow-up Query | POST | ✅ |
| 14 | AI | Diagnosis History | GET | ✅ |
| 15 | AI | Batch Status | GET | ✅ |
| 16 | AI | Verify Diagnosis | POST | ✅ |
| 17 | AI | List Models | GET | ✅ |

**Note:** Restart the API server to load the new AI routes before testing.
