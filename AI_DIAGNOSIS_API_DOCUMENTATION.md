# AI Diagnosis Workflow API Documentation
## Farm Connect - AgriManagement System

This document provides comprehensive API Request Bodies documentation for the AI Diagnosis Workflow in the Farm Connect application.

---

## Table of Contents
1. [Initial Diagnosis Request](#1-initial-diagnosis-request---post-agriai-diagnose)
2. [Symptom Description Submission](#2-symptom-description-submission---post-agriai-symptoms)
3. [Image Analysis Request](#3-image-analysis-request---post-agriai-analyze-image)
4. [Treatment Recommendation Request](#4-treatment-recommendation-request---post-agriai-treatment)
5. [Follow-up Query](#5-follow-up-query---post-agriai-follow-up)
6. [Diagnosis History Retrieval](#6-diagnosis-history-retrieval---get-agriai-diagnosisid)
7. [Batch Diagnosis Status Check](#7-batch-diagnosis-status-check---get-agribatch-status)

---

## 1. Initial Diagnosis Request - POST /agri/ai/diagnose

Creates a new AI diagnosis session for crop health issues.

### Request Body

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
    "https://s3.amazonaws.com/farm-connect-images/diagnosis/image-001.jpg"
  ],
  "priority": "urgent",
  "farmer_notes": "Disease spreading rapidly after recent heavy rains. About 30% of plants showing symptoms."
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | 1-50 chars | Unique field identifier (e.g., "FLD-2024-001") |
| `crop_cycle_id` | string | No | - | Current crop cycle identifier |
| `location` | object | No | Valid GPS coords | GPS coordinates of the issue |
| `location.latitude` | float | No | -90 to 90 | Latitude in degrees |
| `location.longitude` | float | No | -180 to 180 | Longitude in degrees |
| `location.altitude_m` | float | No | - | Altitude in meters |
| `location.accuracy_m` | float | No | >= 0 | GPS accuracy in meters |
| `region` | string | No | - | Agricultural region (e.g., Oromia, Amhara, SNNPR) |
| `crop_type` | string | Yes | - | Crop species (Teff, Wheat, Maize, Barley, Sorghum) |
| `growth_stage` | string | Yes | - | seedling, vegetative, flowering, grain_filling, harvest |
| `planting_date` | string | No | ISO date | Date of planting (YYYY-MM-DD) |
| `suspected_issue` | string | No | - | Farmer's initial suspicion |
| `issue_category` | string | Yes | pest, disease, nutrient_deficiency, abiotic_stress | Category of issue |
| `affected_area_pct` | float | Yes | 0-100 | Percentage of field affected |
| `symptoms` | array | No | Max 20 items | List of observed symptoms |
| `symptom_onset_days` | integer | No | >= 0 | Days since symptoms first appeared |
| `symptom_severity` | string | Yes | low, medium, high, severe | Severity level |
| `weather_recent` | string | No | - | Recent weather conditions |
| `irrigation_type` | string | No | - | Irrigation method (rainfed, sprinkler, drip, flood) |
| `soil_type` | string | No | - | Soil type if known (vertisol, cambisol, luvisol) |
| `image_urls` | array | No | Valid URLs | URLs of images showing the issue |
| `priority` | string | No | low, normal, urgent, emergency | Priority level (default: normal) |
| `farmer_notes` | string | No | Max 1000 chars | Additional observations |

### Example Values (Ethiopian Agriculture Context)

```json
{
  "field_id": "FLD-2024-ABB-042",
  "region": "Amhara",
  "crop_type": "Teff",
  "growth_stage": "tillering",
  "issue_category": "pest",
  "suspected_issue": "armyworm",
  "soil_type": "cambisol",
  "irrigation_type": "rainfed"
}
```

### Response

```json
{
  "diagnosis_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "estimated_completion_seconds": 120,
  "priority_ack": "urgent",
  "message": "Diagnosis session created. You will receive results shortly."
}
```

### Common Error Scenarios

| Error Code | Error Message | Correction |
|------------|---------------|------------|
| 422 | field_id required | Provide a valid field_id string |
| 422 | crop_type required | Specify crop type (e.g., "Wheat", "Teff") |
| 422 | affected_area_pct must be between 0 and 100 | Ensure percentage is within valid range |
| 422 | symptom_severity must be low, medium, high, or severe | Use one of the valid values |

---

## 2. Symptom Description Submission - POST /agri/ai/symptoms

Submit detailed symptom descriptions for enhanced diagnosis accuracy.

### Request Body

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

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `diagnosis_session_id` | string | Yes | Valid UUID | Session ID from initial diagnosis |
| `symptoms` | array | Yes | Min 1 item | Detailed symptom list |
| `symptoms[].symptom_type` | string | Yes | - | Type: leaf_spots, wilting, yellowing, stunting, etc. |
| `symptoms[].location_on_plant` | string | Yes | - | leaves, stems, roots, fruit, flowers, whole_plant |
| `symptoms[].pattern` | string | No | - | scattered, clustered, uniform, progressive |
| `symptoms[].progression` | string | No | - | stable, spreading, worsening |
| `symptoms[].description` | string | No | Max 500 chars | Free-text description |
| `plant_health_score` | integer | Yes | 1-10 | Overall plant health rating |
| `affected_plants_count` | integer | No | >= 0 | Number of affected plants |
| `total_plants_observed` | integer | No | >= 1 | Total plants checked |
| `pest_presence` | array | No | - | Pests observed |
| `beneficial_insects` | array | No | - | Beneficial insects seen |
| `weed_pressure` | string | No | low, medium, high | Weed competition level |
| `treatments_applied` | array | No | - | Recently applied treatments |
| `last_fertilizer_date` | string | No | ISO date | Last fertilizer application |
| `last_irrigation_date` | string | No | ISO date | Last irrigation date |
| `additional_image_urls` | array | No | Valid URLs | Additional images |

### Ethiopian Agriculture Pest Examples

```json
{
  "pest_presence": [
    "african_armyworm",
    "stem_borer",
    "aphids",
    "termites",
    "locusts"
  ],
  "beneficial_insects": [
    "ladybug",
    "parasitic_wasp",
    "dragonfly"
  ]
}
```

### Response

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

### Common Error Scenarios

| Error Code | Error Message | Correction |
|------------|---------------|------------|
| 404 | Diagnosis session not found | Verify session_id is correct |
| 422 | symptoms must contain at least 1 item | Add symptom details |
| 422 | plant_health_score must be between 1 and 10 | Use valid rating |

---

## 3. Image Analysis Request - POST /agri/ai/analyze-image

Request detailed AI analysis of crop images for disease detection and health assessment.

### Request Body

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

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `diagnosis_session_id` | string | No | Valid UUID | Link to existing session |
| `image_url` | string | Yes | Valid URL | URL of image to analyze |
| `image_metadata` | object | No | - | Image EXIF/metadata |
| `image_metadata.width` | integer | No | > 0 | Image width in pixels |
| `image_metadata.height` | integer | No | > 0 | Image height in pixels |
| `image_metadata.format` | string | No | - | Image format (jpeg, png, webp) |
| `image_metadata.file_size_bytes` | integer | No | > 0 | File size |
| `image_metadata.capture_device` | string | No | - | Device used to capture |
| `analysis_type` | string | Yes | disease, pest, nutrient_deficiency, general_health | Type of analysis |
| `analysis_mode` | string | No | quick, standard, detailed | Analysis depth (default: standard) |
| `captured_at` | string | No | ISO datetime | When image was captured |
| `capture_conditions` | object | No | - | Environmental conditions |
| `capture_conditions.lighting` | string | No | - | natural_daylight, artificial, overcast |
| `capture_conditions.weather` | string | No | - | sunny, cloudy, overcast, rainy |
| `capture_conditions.time_of_day` | string | No | HH:MM | Time of capture |
| `field_context` | string | No | - | Where in field (edge, middle, random) |
| `plant_part` | string | No | leaf, stem, root, flower, fruit, whole_plant | Visible plant part |

### Response

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

### Common Error Scenarios

| Error Code | Error Message | Correction |
|------------|---------------|------------|
| 400 | Invalid image URL | Provide accessible image URL |
| 400 | Unsupported image format | Use jpeg, png, or webp |
| 404 | Diagnosis session not found | Verify session_id |

---

## 4. Treatment Recommendation Request - POST /agri/ai/treatment

Get detailed treatment recommendations for confirmed diagnosis.

### Request Body

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

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `diagnosis_session_id` | string | Yes | Valid UUID | Session ID with diagnosis |
| `treatment_type_preference` | string | No | all, chemical, biological, organic | Preferred type (default: all) |
| `budget_constraint` | object | No | - | Budget limits |
| `budget_constraint.max_cost_per_ha` | float | No | > 0 | Maximum cost per hectare |
| `budget_constraint.currency` | string | No | - | Currency code (ETB, USD) |
| `time_to_harvest_days` | integer | No | >= 0 | Days until harvest |
| `water_source_proximity` | boolean | No | - | Near water body |
| `organic_certified` | boolean | No | - | Field is organic certified |
| `pollinator_present` | boolean | No | - | Bees active in area |
| `equipment_available` | array | No | - | Available equipment |
| `labor_availability` | string | No | limited, adequate, abundant | Labor constraints |
| `treatments_last_30_days` | array | No | - | Recently applied treatments |
| `known_resistance` | array | No | - | Known resistance issues |

### Ethiopian Context Equipment Examples

```json
{
  "equipment_available": [
    "hand_press_pump",
    "motorized_mist_blower",
    "drip_irrigation_system",
    "trailed_sprayer"
  ]
}
```

### Response

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
  ],
  "additional_resources": [
    "FAO Plant Protection Guidelines",
    "Ethiopian Ministry of Agriculture Pest Management Guide"
  ]
}
```

### Common Error Scenarios

| Error Code | Error Message | Correction |
|------------|---------------|------------|
| 404 | Diagnosis session not found | Verify session_id |
| 422 | treatment_type_preference must be valid | Use all, chemical, biological, or organic |

---

## 5. Follow-up Query - POST /agri/ai/follow-up

Submit follow-up questions about a diagnosis or treatment.

### Request Body

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

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `diagnosis_session_id` | string | Yes | Valid UUID | Original diagnosis session |
| `question_type` | string | Yes | application_guidance, efficacy, safety, alternative, general | Type of question |
| `question` | string | Yes | 10-1000 chars | Follow-up question |
| `treatment_applied` | string | No | - | Treatment that was applied |
| `application_date` | string | No | ISO date | When treatment was applied |
| `observed_results` | string | No | - | What farmer observed |
| `follow_up_image_urls` | array | No | Valid URLs | Images showing current status |

### Response

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

### Question Types

| Type | Description |
|------|-------------|
| `application_guidance` | Questions about how to apply treatments |
| `efficacy` | Questions about expected results and timelines |
| `safety` | Questions about safety, PPE, re-entry intervals |
| `alternative` | Questions about alternative treatments |
| `general` | General questions about diagnosis |

---

## 6. Diagnosis History Retrieval - GET /agri/ai/diagnosis/:id

Retrieve complete diagnosis history for a session.

### Response

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
      "pattern": "scattered",
      "description": "Circular brown spots with concentric rings"
    }
  ],
  "images_analyzed": [
    {
      "analysis_id": "img-2024-001",
      "image_url": "https://s3.amazonaws.com/farm-connect-images/wheat-leaves.jpg",
      "detections": ["Septoria Leaf Blotch", "Leaf Rust"]
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
    "comments": "Treatment worked well, saw improvement within 3 days"
  },
  "final_outcome": "successful_treatment",
  "outcome_rating": 5,
  "follow_up_count": 1,
  "follow_up_questions": [
    {
      "query_id": "Q-2024-001",
      "question_type": "application_guidance",
      "answered": true
    }
  ]
}
```

---

## 7. Batch Diagnosis Status Check - GET /agri/ai/batch-status

Check status of multiple diagnosis sessions.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_ids` | string | Yes | Comma-separated list of session IDs |
| `include_details` | boolean | No | Include full details (default: true) |

### Example Request

```
GET /agri/ai/batch-status?session_ids=id1,id2,id3&include_details=true
```

### Response

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

## Ethiopian Agriculture Reference Data

### Crop Types
- **Teff** (Eragrostis tef) - Highland staple
- **Wheat** (Triticum aestivum) - Major cereal
- **Maize** (Zea mays) - Secondary staple
- **Barley** (Hordeum vulgable) - Highland crop
- **Sorghum** (Sorghum bicolor) - Lowland staple

### Common Pests
| Pest | Local Name | Affected Crops |
|------|------------|----------------|
| African Armyworm | Yedega Qime | Wheat, Teff, Maize |
| Stem Borer | Yeset Bere | Maize, Sorghum |
| Termites | Qiqe | All crops |
| Aphids | Zinjero | Vegetables, Pulses |

### Common Diseases
| Disease | Affected Crops |
|---------|----------------|
| Septoria Leaf Blotch | Wheat, Barley |
| Leaf Rust | Wheat, Barley |
| Blast (Magnaporthe oryzae) | Rice, Wheat |
| Faba Bean Chocolate Spot | Faba Bean |

### Regions
- **Oromia** - Largest region, diverse agriculture
- **Amhara** - Teff and wheat production
- **SNNPR** - Coffee and enset
- **Tigray** - Drought-resistant crops
- **Somali** - Pastoral and limited agriculture

---

## Error Handling Reference

### Standard Error Response

```json
{
  "detail": "Error message describing the issue"
}
```

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Invalid data in request body |
| 500 | Internal Server Error | Server-side error |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-08-15 | Initial release |
| 1.1.0 | 2024-08-20 | Added batch status endpoint |
| 1.2.0 | 2024-09-01 | Enhanced treatment recommendations |

---

## Support

For questions or issues:
- Extension Officer: +251-XX-XXX-XXXX
- Email: support@farmconnect.et
- Documentation: docs.farmconnect.et
