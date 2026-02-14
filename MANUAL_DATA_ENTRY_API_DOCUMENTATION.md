# Manual Data Entry Workflow API Documentation
## Farm Connect - AgriManagement System

This document provides comprehensive API Request Bodies documentation for the Manual Data Entry Workflow in the Farm Connect application.

---

## Table of Contents
1. [Soil Reading Submission](#1-soil-reading-submission---post-agrisoil-readings)
2. [Field Visit Log](#2-field-visit-log---post-agrifield-visits)
3. [Irrigation Schedule](#3-irrigation-schedule---post-agriirrigation-schedules)
4. [NDVI Snapshot](#4-ndvi-snapshot---post-agrindvi-snapshots)
5. [Pest/Disease Report](#5-pestdisease-report---post-agripest-disease-reports)
6. [Treatment Recommendation](#6-treatment-recommendation---post-agritreatment-recommendations)
7. [Retrieve Soil Readings](#7-retrieve-soil-readings---get-agrisoil-readingsfield_id)
8. [Retrieve Field Visits](#8-retrieve-field-visits---get-agrifield-visitsfield_id)

---

## 1. Soil Reading Submission - POST /agri/soil-readings

Record manual soil readings from field visits.

### Request Body

```json
{
  "field_id": "FLD-2024-001",
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
  "lab_name": null,
  "lab_report_url": null,
  "recorded_by": "FAR-00002",
  "recorded_at": "2024-08-15T10:00:00Z",
  "weather_conditions": "Sunny",
  "days_since_rain": 3
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | 1-50 chars | Unique field identifier |
| `location_geojson` | object | No | Valid GeoJSON | GPS coordinates of sample location |
| `location_geojson.type` | string | No | "Point" | GeoJSON type |
| `location_geojson.coordinates` | array | No | [lng, lat] | Longitude and latitude |
| `sample_depth_cm` | integer | No | > 0 | Depth of soil sample in cm |
| `sample_depth_range` | string | No | - | Depth range description |
| `moisture_pct` | decimal | No | 0-100 | Soil moisture percentage |
| `temperature_c` | decimal | No | - | Soil temperature in Celsius |
| `ph` | decimal | No | 0-14 | Soil pH level |
| `nitrogen_ppm` | decimal | No | >= 0 | Nitrogen content in ppm |
| `phosphorus_ppm` | decimal | No | >= 0 | Phosphorus content in ppm |
| `potassium_ppm` | decimal | No | >= 0 | Potassium content in ppm |
| `organic_matter_pct` | decimal | No | 0-100 | Organic matter percentage |
| `source` | string | Yes | - | Data source (e.g., "MANUAL_TEST", "LAB") |
| `lab_name` | string | No | - | Laboratory name if applicable |
| `lab_report_url` | string | No | - | URL to lab report |
| `recorded_by` | string | No | - | User ID of person recording |
| `recorded_at` | datetime | No | ISO datetime | When reading was taken |
| `weather_conditions` | string | No | - | Weather during sampling |
| `days_since_rain` | integer | No | >= 0 | Days since last rain |

### Example Values (Ethiopian Context)

```json
{
  "field_id": "FLD-2024-ABB-042",
  "sample_depth_cm": 20,
  "sample_depth_range": "15-30cm",
  "moisture_pct": 28.5,
  "temperature_c": 24.0,
  "ph": 6.2,
  "nitrogen_ppm": 35.0,
  "phosphorus_ppm": 18.0,
  "potassium_ppm": 150.0,
  "organic_matter_pct": 2.8,
  "source": "MANUAL_FIELD_VISIT",
  "soil_type": "vertisol",
  "weather_conditions": "Partly cloudy",
  "days_since_rain": 5
}
```

### Ethiopian Soil Types

| Soil Type | Region | Characteristics |
|-----------|--------|-----------------|
| Vertisol | Oromia, Amhara | High clay content, swelling when wet |
| Cambisol | Highlands | Moderately fertile, good structure |
| Luvisol | SNNPR | Leached clay horizon |
| Nitisol | Tigray | Deep, well-drained volcanic soil |

### Response

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "created",
  "message": "Soil reading recorded successfully"
}
```

### Common Error Scenarios

| Error Code | Error Message | Correction |
|------------|---------------|------------|
| 422 | field_id required | Provide a valid field_id |
| 422 | moisture_pct must be between 0 and 100 | Ensure value is in range |
| 422 | ph must be between 0 and 14 | Ensure pH is in valid range |
| 404 | Field not found | Verify field_id exists |

---

## 2. Field Visit Log - POST /agri/field-visits

Record field visit observations and activities.

### Request Body

```json
{
  "field_id": "FLD-2024-001",
  "crop_cycle_id": "CC-2024-WHEAT-001",
  "visit_date": "2024-08-15",
  "visit_type": "REGULAR_MONITORING",
  "purpose": "Weekly crop health check",
  "visited_by": "FAR-00002",
  "weather_conditions": "Sunny",
  "temperature_c": 28.5,
  "humidity_pct": 65.0,
  "soil_conditions": "Moist",
  "observations": "Overall crop health looks good. No visible signs of disease. Some minor weed pressure in eastern section.",
  "issues_found": ["weed_pressure"],
  "photos": [
    "https://s3.amazonaws.com/farm-connect-images/visits/visit-001.jpg"
  ],
  "recommendations": ["Weed control needed within 7 days"],
  "follow_up_required": true,
  "follow_up_notes": "Monitor weed growth and plan herbicide application"
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | 1-50 chars | Unique field identifier |
| `crop_cycle_id` | string | No | - | Current crop cycle identifier |
| `visit_date` | date | Yes | ISO date | Date of visit |
| `visit_type` | string | Yes | - | Type: REGULAR_MONITORING, IRRIGATION_CHECK, PEST_INSPECTION, HARVEST_PREP, OTHER |
| `purpose` | string | No | - | Purpose of visit |
| `visited_by` | string | Yes | - | User ID of visitor |
| `weather_conditions` | string | No | - | Weather during visit |
| `temperature_c` | decimal | No | - | Temperature in Celsius |
| `humidity_pct` | decimal | No | 0-100 | Humidity percentage |
| `soil_conditions` | string | No | - | Soil condition: dry, moist, wet, waterlogged |
| `observations` | string | No | Max 2000 chars | General observations |
| `issues_found` | array | No | - | List of issues: pest, disease, nutrient_deficiency, weed, irrigation, none |
| `photos` | array | No | Valid URLs | Photo URLs from visit |
| `recommendations` | array | No | - | Recommended actions |
| `follow_up_required` | boolean | No | - | Whether follow-up is needed |
| `follow_up_notes` | string | No | - | Notes for follow-up |

### Ethiopian Visit Types

```json
{
  "visit_type": "REGULAR_MONITORING",
  "purpose": "Weekly crop health monitoring for Teff field"
}
```

### Response

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "status": "created",
  "message": "Field visit logged successfully"
}
```

---

## 3. Irrigation Schedule - POST /agri/irrigation-schedules

Schedule irrigation for a field.

### Request Body

```json
{
  "field_id": "FLD-2024-001",
  "crop_cycle_id": "CC-2024-WHEAT-001",
  "scheduled_date": "2024-08-20",
  "duration_minutes": 120,
  "water_volume_liters": 5000.0,
  "triggered_by": "manual",
  "notes": "Irrigate early morning for best water absorption"
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | 1-50 chars | Unique field identifier |
| `crop_cycle_id` | string | No | - | Current crop cycle identifier |
| `scheduled_date` | datetime | Yes | ISO datetime | When to irrigate |
| `duration_minutes` | integer | Yes | > 0 | Duration in minutes |
| `water_volume_liters` | decimal | Yes | > 0 | Water volume in liters |
| `triggered_by` | string | Yes | - | manual, weather_based, soil_moisture, schedule |
| `notes` | string | No | - | Additional notes |

### Response

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "status": "scheduled",
  "message": "Irrigation schedule created successfully"
}
```

---

## 4. NDVI Snapshot - POST /agri/ndvi-snapshots

Record NDVI (Normalized Difference Vegetation Index) data from satellite imagery.

### Request Body

```json
{
  "field_id": "FLD-2024-001",
  "crop_cycle_id": "CC-2024-WHEAT-001",
  "source": "SENTINEL_2",
  "captured_at": "2024-08-15T10:00:00Z",
  "ndvi_mean": 0.65,
  "ndvi_min": 0.42,
  "ndvi_max": 0.85,
  "ndvi_stddev": 0.08,
  "stress_level": "low",
  "cloud_cover_pct": 5.0
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | 1-50 chars | Unique field identifier |
| `crop_cycle_id` | string | No | - | Current crop cycle identifier |
| `source` | string | Yes | - | Data source: SENTINEL_2, LANDSAT, DRONE, MANUAL |
| `captured_at` | datetime | Yes | ISO datetime | When imagery was captured |
| `ndvi_mean` | decimal | Yes | -1 to 1 | Mean NDVI value |
| `ndvi_min` | decimal | No | -1 to 1 | Minimum NDVI value |
| `ndvi_max` | decimal | No | -1 to 1 | Maximum NDVI value |
| `ndvi_stddev` | decimal | No | - | Standard deviation of NDVI |
| `stress_level` | string | No | none, low, moderate, high, severe | Stress level |
| `cloud_cover_pct` | decimal | No | 0-100 | Cloud cover percentage |

### NDVI Interpretation

| NDVI Range | Interpretation | Action |
|------------|----------------|--------|
| < 0.2 | Bare soil/water | Normal for non-growing season |
| 0.2-0.5 | Sparse vegetation | May need attention |
| 0.5-0.7 | Healthy vegetation | Good crop condition |
| 0.7-0.9 | Very healthy | Optimal growth |
| > 0.9 | Dense vegetation | May indicate over-fertilization |

### Response

```json
{
  "id": "d4e5f6a7-b8c9-0123-def0-123456789012",
  "status": "created",
  "ndvi_mean": 0.65,
  "stress_level": "low"
}
```

---

## 5. Pest/Disease Report - POST /agri/pest-disease-reports

Report pest or disease issues in a field.

### Request Body

```json
{
  "field_id": "FLD-2024-001",
  "crop_cycle_id": "CC-2024-WHEAT-001",
  "reported_by": "FAR-00002",
  "location_geojson": {
    "type": "Point",
    "coordinates": [40.489, 9.145]
  },
  "image_urls": [
    "https://s3.amazonaws.com/farm-connect-images/pests/affected-leaves.jpg"
  ],
  "suspected_issue": "Early Blight",
  "issue_type": "DISEASE",
  "scientific_name": "Alternaria solani",
  "common_names": ["Early blight", "Target spot"],
  "severity": "MEDIUM",
  "affected_area_ha": 2.5,
  "affected_plant_count": 150,
  "symptoms": "Dark brown spots with concentric rings on lower leaves, progressing upward",
  "spread_pattern": "Scattered",
  "first_observed_date": "2024-08-10",
  "detected_at": "2024-08-15T14:00:00Z"
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | 1-50 chars | Unique field identifier |
| `crop_cycle_id` | string | No | - | Current crop cycle identifier |
| `reported_by` | string | Yes | - | User ID of reporter |
| `location_geojson` | object | No | Valid GeoJSON | GPS location of issue |
| `image_urls` | array | No | Valid URLs | Photos of the issue |
| `suspected_issue` | string | Yes | - | Name of suspected pest/disease |
| `issue_type` | string | Yes | - | PEST or DISEASE |
| `scientific_name` | string | No | - | Scientific name if known |
| `common_names` | array | No | - | Alternative names |
| `severity` | string | Yes | LOW, MEDIUM, HIGH, SEVERE | Severity level |
| `affected_area_ha` | decimal | No | > 0 | Area affected in hectares |
| `affected_plant_count` | integer | No | >= 0 | Number of affected plants |
| `symptoms` | string | No | Max 1000 chars | Description of symptoms |
| `spread_pattern` | string | No | - | scattered, clustered, uniform, spreading |
| `first_observed_date` | string | No | ISO date | When issue was first noticed |
| `detected_at` | datetime | Yes | ISO datetime | When report was created |

### Ethiopian Common Pests

```json
{
  "suspected_issue": "African Armyworm",
  "scientific_name": "Spodoptera exempta",
  "issue_type": "PEST",
  "severity": "HIGH"
}
```

### Response

```json
{
  "id": "e5f6a7b8-c9d0-1234-ef01-234567890123",
  "status": "created",
  "message": "Pest/disease report submitted successfully"
}
```

---

## 6. Treatment Recommendation - POST /agri/treatment-recommendations

Create treatment recommendations for pest/disease reports.

### Request Body

```json
{
  "report_id": "e5f6a7b8-c9d0-1234-ef01-234567890123",
  "recommended_by": "AGR-00001",
  "recommendation_source": "AI_DIAGNOSIS",
  "description": "Apply copper-based fungicide for early blight control",
  "treatment_type": "chemical",
  "chemical_name": "Copper Oxychloride 50% WP",
  "active_ingredient": "Copper Oxychloride",
  "dosage_per_ha": "2.5 kg/ha",
  "application_method": "foliar_spray",
  "application_timing": "early_morning",
  "organic": false,
  "restricted_use": false,
  "required_ppe": ["gloves", "mask", "eye_protection"],
  "reentry_interval_hours": 24,
  "pre_harvest_interval_days": 7,
  "estimated_cost_per_ha_usd": 45.00,
  "effectiveness_rating": 4.5,
  "expected_results_days": 5
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `report_id` | string | Yes | Valid UUID | Associated pest/disease report |
| `recommended_by` | string | Yes | - | User ID of recommender |
| `recommendation_source` | string | Yes | - | AI_DIAGNOSIS, EXPERT, MANUAL, KNOWLEDGE_BASE |
| `description` | string | Yes | - | Treatment description |
| `treatment_type` | string | Yes | - | chemical, biological, cultural, mechanical |
| `chemical_name` | string | No | - | Product name |
| `active_ingredient` | string | No | - | Active ingredient |
| `dosage_per_ha` | string | No | - | Recommended dosage per hectare |
| `application_method` | string | No | - | foliar_spray, soil_drench, seed_treatment, etc. |
| `application_timing` | string | No | - | early_morning, late_afternoon, evening |
| `organic` | boolean | No | - | Is treatment organic |
| `restricted_use` | boolean | No | - | Is restricted use pesticide |
| `required_ppe` | array | No | - | Required PPE: gloves, mask, goggles, apron |
| `reentry_interval_hours` | integer | No | >= 0 | Hours before re-entry allowed |
| `pre_harvest_interval_days` | integer | No | >= 0 | Days before harvest |
| `estimated_cost_per_ha_usd` | decimal | No | >= 0 | Cost per hectare in USD |
| `effectiveness_rating` | decimal | No | 0-5 | Effectiveness rating |
| `expected_results_days` | integer | No | >= 0 | Expected days to see results |

### Response

```json
{
  "id": "f6a7b8c9-d0e1-2345-f012-345678901234",
  "status": "created",
  "message": "Treatment recommendation created successfully"
}
```

---

## 7. Retrieve Soil Readings - GET /agri/soil-readings/{field_id}

Get historical soil readings for a field.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `field_id` | string | Yes | Field identifier |
| `start_date` | date | No | Filter by start date |
| `end_date` | date | No | Filter by end date |

### Response

```json
{
  "count": 5,
  "readings": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "field_id": "FLD-2024-001",
      "moisture_pct": "35.50",
      "temperature_c": "22.50",
      "ph": "6.80",
      "nitrogen_ppm": "45.00",
      "recorded_at": "2024-08-15T10:00:00Z"
    }
  ]
}
```

---

## 8. Retrieve Field Visits - GET /agri/field-visits/{field_id}

Get field visit history for a field.

### Response

```json
{
  "count": 3,
  "visits": [
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "field_id": "FLD-2024-001",
      "visit_date": "2024-08-15",
      "visit_type": "REGULAR_MONITORING",
      "weather_conditions": "Sunny",
      "issues_found": ["weed_pressure"],
      "follow_up_required": true
    }
  ]
}
```

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

## Ethiopian Agriculture Reference

### Common Crops

| Crop | Amharic | Growing Regions |
|------|---------|-----------------|
| Teff | ጤፍ | Highlands (Amhara, Oromia) |
| Wheat | ስንዴ | Highlands (Oromia, Amhara) |
| Maize | ድንች | Lowlands (Oromia, SNNPR) |
| Barley | አተር | Highlands |
| Sorghum | ገብስ | Lowlands |

### Soil Types by Region

| Region | Common Soil Types |
|--------|------------------|
| Oromia | Vertisol, Cambisol, Nitisol |
| Amhara | Vertisol, Cambisol, Luvisol |
| SNNPR | Nitisol, Andosol |
| Tigray | Cambisol, Luvisol |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-08-15 | Initial release |
| 1.1.0 | 2024-08-20 | Added NDVI and irrigation endpoints |

---

## Support

For questions or issues:
- Extension Officer: +251-XX-XXX-XXXX
- Email: support@farmconnect.et
- Documentation: docs.farmconnect.et
