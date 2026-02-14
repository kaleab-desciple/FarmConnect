# Field Management Workflow API Documentation
## Farm Connect - AgriManagement System

This document provides comprehensive API Request Bodies documentation for the Field Management Workflow in the Farm Connect application.

---

## Table of Contents
1. [Farm Operations](#1-farm-operations---post-apifarms)
2. [Field Operations](#2-field-operations---post-apifields)
3. [Crop Cycle Management](#3-cycle-management---post-apicrop-cycles)
4. [Task/Work Order Management](#4-taskwork-order-management---post-apitasks)
5. [Task Status Updates](#5-task-status-updates---put-apitaskstask_id)
6. [Harvest Records](#6-harvest-records---post-apiharvests)
7. [Inventory Management](#7-inventory-operations---post-apiinventory)
8. [Equipment Management](#8-equipment-management---post-apiequipment)

---

## 1. Farm Operations - POST /api/farms

Create and manage farm operations.

### Request Body

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
    "irrigation_source": "Well",
    "elevation_m": 1500,
    "farm_type": "mixed_farming"
  }
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `farmer_id` | string | Yes | 1-50 chars | Unique farmer/owner identifier |
| `name` | string | Yes | 1-200 chars | Farm name |
| `location_lat` | decimal | Yes | -90 to 90 | Latitude of farm center |
| `location_lng` | decimal | Yes | -180 to 180 | Longitude of farm center |
| `location_address` | string | No | Max 500 chars | Physical address |
| `total_area_ha` | decimal | Yes | > 0 | Total farm area in hectares |
| `boundary_geojson` | object | No | Valid GeoJSON Polygon | Farm boundary |
| `metadata` | object | No | - | Additional metadata |
| `metadata.soil_type` | string | No | - | Primary soil type |
| `metadata.irrigation_source` | string | No | - | Well, river, rainfed, etc. |
| `metadata.elevation_m` | integer | No | > 0 | Elevation in meters |
| `metadata.farm_type` | string | No | - | crop_only, livestock, mixed_farming |

### Example Values (Ethiopian Context)

```json
{
  "farmer_id": "FAR-ABB-2024-001",
  "name": "Bako Agricultural Cooperative",
  "location_lat": 9.1333,
  "location_lng": 37.0667,
  "location_address": "Bako, Oromia Region, Ethiopia",
  "total_area_ha": 500.0,
  "metadata": {
    "soil_type": "Vertisol",
    "irrigation_source": "Irrigated",
    "elevation_m": 1650,
    "farm_type": "crop_only",
    "year_established": 2015
  }
}
```

### Ethiopian Regions

| Region | Primary Crops | Elevation Range |
|--------|---------------|----------------|
| Oromia | Teff, Wheat, Maize | 1500-3000m |
| Amhara | Wheat, Barley, Teff | 2000-3500m |
| SNNPR | Coffee, Enset, Maize | 1000-2500m |
| Tigray | Sorghum, Millet | 1500-2500m |
| Somali | Livestock, Sorghum | 500-1500m |

### Response

```json
{
  "id": "aefc0e4b-8010-4c9a-bc7f-d1d02804795d",
  "status": "created",
  "message": "Farm created successfully"
}
```

### Common Error Scenarios

| Error Code | Error Message | Correction |
|------------|---------------|------------|
| 422 | farmer_id required | Provide a valid farmer_id |
| 422 | name required | Provide a farm name |
| 422 | total_area_ha must be greater than 0 | Ensure area is positive |
| 400 | Invalid GeoJSON format | Verify boundary coordinates |

---

## 2. Field Operations - POST /api/fields

Create and manage individual fields within a farm.

### Request Body

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
  "elevation_m": 1520,
  "slope_pct": 5.0,
  "previous_crop": "Wheat",
  "metadata": {
    "soil_ph": 6.5,
    "drainage": "good",
    "flood_risk": "low"
  }
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `farm_id` | string | Yes | Valid UUID | Parent farm identifier |
| `name` | string | Yes | 1-200 chars | Field name |
| `area_ha` | decimal | Yes | > 0 | Field area in hectares |
| `boundary_geojson` | object | Yes | Valid GeoJSON Polygon | Field boundary |
| `soil_type` | string | No | - | Soil classification |
| `irrigation_type` | string | No | - | rainfed, drip, sprinkler, flood, none |
| `elevation_m` | integer | No | > 0 | Elevation in meters |
| `slope_pct` | decimal | No | 0-100 | Slope percentage |
| `previous_crop` | string | No | - | Previous season's crop |
| `metadata` | object | No | - | Additional field data |

### Field Sizes by Region

| Region | Typical Field Size | Common Crops |
|--------|-------------------|--------------|
| Oromia | 1-10 ha | Teff, Wheat |
| Amhara | 0.5-5 ha | Barley, Wheat |
| SNNPR | 0.25-2 ha | Enset, Coffee |
| Tigray | 1-5 ha | Sorghum, Millet |

### Response

```json
{
  "id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "status": "created",
  "area_ha": 50.5,
  "message": "Field created successfully"
}
```

---

## 3. Crop Cycle Management - POST /api/crop-cycles

Create and manage crop growing cycles for fields.

### Request Body

```json
{
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "product_category": "VEGETABLES",
  "crop_name": "Tomato",
  "variety": "Roma",
  "planting_date": "2024-01-15",
  "expected_harvest_date": "2024-06-15",
  "status": "PLANTED",
  "expected_yield_kg": 5000,
  "actual_yield_kg": null,
  "seed_source": "Certified Seed",
  "seed_rate_kg_ha": 0.5,
  "row_spacing_cm": 60,
  "plant_spacing_cm": 40,
  "planting_method": "transplant",
  "notes": "Healthy germination observed"
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | Valid UUID | Field identifier |
| `product_category` | string | Yes | - | CEREALS, VEGETABLES, LEGUMES, OILSEEDS, FRUIT, OTHER |
| `crop_name` | string | Yes | 1-100 chars | Crop species name |
| `variety` | string | No | - | Crop variety/cultivar |
| `planting_date` | date | Yes | ISO date | Date of planting |
| `expected_harvest_date` | date | No | ISO date | Expected harvest date |
| `status` | string | Yes | - | PLANNED, PLANTED, GROWING, HARVESTING, COMPLETED, FAILED |
| `expected_yield_kg` | decimal | No | > 0 | Expected yield in kg |
| `actual_yield_kg` | decimal | No | > 0 | Actual yield after harvest |
| `seed_source` | string | No | - | Source of seeds |
| `seed_rate_kg_ha` | decimal | No | > 0 | Seeding rate per hectare |
| `row_spacing_cm` | integer | No | > 0 | Distance between rows |
| `plant_spacing_cm` | integer | No | > 0 | Distance between plants |
| `planting_method` | string | No | - | direct_seeding, transplant, broadcast |
| `notes` | string | No | Max 1000 chars | Additional notes |

### Growth Stages

| Stage | Description |
|-------|-------------|
| PLANNED | Scheduled but not yet planted |
| PLANTED | Seeds sown/transplanted |
| GROWING | Actively growing |
| FLOWERING | Crop is flowering |
| GRAIN_FILLING | Grain/fruit development |
| HARVESTING | Ready or being harvested |
| COMPLETED | Harvest complete |
| FAILED | Crop failed |

### Ethiopian Crop Varieties

```json
{
  "crop_name": "Teff",
  "variety": "Qusso",
  "product_category": "CEREALS"
}
```

### Response

```json
{
  "id": "b41a826b-5e66-4667-8256-f0f6a3b993b2",
  "status": "created",
  "message": "Crop cycle created successfully"
}
```

---

## 4. Task/Work Order Management - POST /api/tasks

Create farm tasks and work orders.

### Request Body

```json
{
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "crop_cycle_id": "b41a826b-5e66-4667-8256-f0f6a3b993b2",
  "task_type": "IRRIGATION",
  "title": "Morning Drip Irrigation",
  "description": "Drip irrigation for 2 hours - check all emitters for blockages",
  "status": "PENDING",
  "priority": "HIGH",
  "scheduled_date": "2024-02-01",
  "duration_estimate_hours": 2.0,
  "assigned_to": "FAR-00002",
  "labor_count": 2,
  "equipment_needed": ["drip_system", "water_pump"],
  "estimated_cost_usd": 50.00,
  "materials_needed": [],
  "safety_requirements": "Check water pressure before starting"
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `field_id` | string | Yes | Valid UUID | Associated field |
| `crop_cycle_id` | string | No | Valid UUID | Associated crop cycle |
| `task_type` | string | Yes | - | IRRIGATION, FERTILIZATION, PEST_CONTROL, WEEDING, HARVESTING, MONITORING, MAINTENANCE, OTHER |
| `title` | string | Yes | 1-200 chars | Task title |
| `description` | string | No | Max 1000 chars | Detailed description |
| `status` | string | Yes | - | PENDING, IN_PROGRESS, COMPLETED, CANCELLED, ON_HOLD |
| `priority` | string | No | - | LOW, NORMAL, HIGH, URGENT, EMERGENCY |
| `scheduled_date` | date | Yes | ISO date | Planned date |
| `duration_estimate_hours` | decimal | No | > 0 | Estimated duration |
| `assigned_to` | string | No | - | Assigned worker/farmer ID |
| `labor_count` | integer | No | >= 1 | Number of laborers |
| `equipment_needed` | array | No | - | Required equipment |
| `estimated_cost_usd` | decimal | No | >= 0 | Estimated cost in USD |
| `materials_needed` | array | No | - | Required materials |
| `safety_requirements` | string | No | - | Safety instructions |

### Task Types

| Task Type | Description |
|-----------|-------------|
| IRRIGATION | Water application |
| FERTILIZATION | Fertilizer application |
| PEST_CONTROL | Pesticide/herbicide application |
| WEEDING | Weed control activities |
| HARVESTING | Harvest operations |
| MONITORING | Field scouting/observation |
| MAINTENANCE | Equipment/structure maintenance |
| PLANTING | Planting activities |
| PRUNING | Pruning/grooming |
| OTHER | Miscellaneous tasks |

### Response

```json
{
  "id": "ab7c8d1a-4727-4b3e-8fbe-c3f8d3c99583",
  "status": "created",
  "message": "Task created successfully"
}
```

---

## 5. Task Status Updates - PUT /api/tasks/{task_id}

Update task status and add completion details.

### Request Body

```json
{
  "status": "IN_PROGRESS",
  "started_at": "2024-02-01T08:00:00Z",
  "notes": "Started irrigation - all emitters checked and clear"
}
```

### Complete Task

```json
{
  "status": "COMPLETED",
  "completed_date": "2024-02-01",
  "completed_by": "FAR-00002",
  "started_at": "2024-02-01T08:00:00Z",
  "ended_at": "2024-02-01T09:45:00Z",
  "duration_actual_hours": 1.75,
  "completion_notes": "All emitters checked and cleared. No blockages found.",
  "actual_cost_usd": 45.00,
  "labor_hours": 3.5,
  "materials_used": [],
  "outcomes": {
    "area_irrigated_ha": 50.5,
    "water_used_liters": 5000
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | New status |
| `completed_date` | date | For completion | Actual completion date |
| `completed_by` | string | For completion | Worker ID |
| `started_at` | datetime | For in-progress | Start time |
| `ended_at` | datetime | For completion | End time |
| `duration_actual_hours` | decimal | For completion | Actual hours spent |
| `completion_notes` | string | For completion | Completion details |
| `actual_cost_usd` | decimal | For completion | Actual cost |
| `labor_hours` | decimal | For completion | Total labor hours |
| `outcomes` | object | For completion | Task-specific outcomes |

### Status Transition Flow

```
PENDING → IN_PROGRESS → COMPLETED
PENDING → CANCELLED
PENDING → ON_HOLD → (PENDING | CANCELLED)
```

### Response

```json
{
  "id": "ab7c8d1a-4727-4b3e-8fbe-c3f8d3c99583",
  "status": "COMPLETED",
  "message": "Task completed successfully"
}
```

---

## 6. Harvest Records - POST /api/harvests

Record harvest data.

### Request Body

```json
{
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "crop_cycle_id": "b41a826b-5e66-4667-8256-f0f6a3b993b2",
  "harvest_date": "2024-06-15",
  "harvest_method": "manual",
  "area_harvested_ha": 48.5,
  "total_yield_kg": 24250,
  "yield_per_ha_kg": 500,
  "quality_grade": "A",
  "moisture_content_pct": 12.5,
  "storage_location": "Farm Warehouse A",
  "market_destination": "Addis Ababa Market",
  "price_per_kg_usd": 0.45,
  "labor_hours": 120,
  "labor_cost_usd": 240,
  "notes": "Good quality harvest, no significant losses"
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `field_id` | string | Yes | Field identifier |
| `crop_cycle_id` | string | Yes | Crop cycle identifier |
| `harvest_date` | date | Yes | Date of harvest |
| `harvest_method` | string | - | manual, mechanical, combined |
| `area_harvested_ha` | decimal | > 0 | Area actually harvested |
| `total_yield_kg` | decimal | > 0 | Total yield in kg |
| `yield_per_ha_kg` | decimal | > 0 | Calculated yield per hectare |
| `quality_grade` | string | - | A, B, C, reject |
| `moisture_content_pct` | decimal | 0-100 | Grain moisture percentage |
| `storage_location` | string | - | Where produce is stored |
| `market_destination` | string | - | Where produce will be sold |
| `price_per_kg_usd` | decimal | >= 0 | Selling price per kg |
| `labor_hours` | decimal | >= 0 | Hours of labor used |
| `labor_cost_usd` | decimal | >= 0 | Cost of labor |
| `notes` | string | - | Additional notes |

### Response

```json
{
  "id": "c4d9e2f1-a6b7-4890-c1d2-e3f4a5b6c7d8",
  "status": "created",
  "total_yield_kg": 24250,
  "yield_per_ha_kg": 500,
  "message": "Harvest record created successfully"
}
```

---

## 7. Inventory Management - POST /api/inventory

Manage farm inventory (seeds, fertilizers, pesticides).

### Request Body

```json
{
  "item_name": "Urea Fertilizer",
  "item_type": "fertilizer",
  "quantity": 500,
  "unit": "kg",
  "supplier": "Ethiopian Agricultural Inputs",
  "purchase_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "unit_cost_usd": 0.80,
  "total_cost_usd": 400,
  "storage_location": "Farm Shed B",
  "batch_number": "BATCH-2024-001",
  "notes": "Stored in cool, dry place"
}
```

### Item Types

| Type | Examples |
|------|----------|
| seed | Seeds, seedlings, cuttings |
| fertilizer | Urea, DAP, compost |
| pesticide | Insecticides, fungicides, herbicides |
| equipment | Tools, machinery |
| fuel | Diesel, petrol |
| other | Miscellaneous |

### Response

```json
{
  "id": "d5e0f3a2-b7c8-5901-d2e3-f4a5b6c7d8e9",
  "status": "created",
  "current_stock": 500,
  "unit": "kg",
  "message": "Inventory item added successfully"
}
```

---

## 8. Equipment Management - POST /api/equipment

Manage farm equipment.

### Request Body

```json
{
  "name": "Water Pump",
  "equipment_type": "pump",
  "model": "Centrifugal Pump X200",
  "serial_number": "SN-2023-001234",
  "purchase_date": "2023-06-15",
  "purchase_cost_usd": 2500,
  "current_condition": "good",
  "last_maintenance_date": "2024-01-15",
  "next_maintenance_date": "2024-04-15",
  "storage_location": "Equipment Shed",
  "operator_manual_url": "https://storage.example.com/manuals/pump-x200.pdf"
}
```

### Equipment Types

| Type | Examples |
|------|----------|
| tractor | Two-wheel, four-wheel tractors |
| irrigation | Pumps, sprinklers, drip systems |
| sprayer | Backpack, motorized, tractor-mounted |
| harvester | Combine harvesters, reapers |
| trailer | Transport trailers |
| tools | Plows, cultivators, seeders |
| other | Miscellaneous equipment |

### Response

```json
{
  "id": "e6f1a4b3-c8d9-6012-e3f4-b5c6d7e8f9a0",
  "status": "created",
  "message": "Equipment added successfully"
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

### Growing Calendar

| Month | Main Activities |
|-------|----------------|
| June-August | Planting (Meher season) |
| September-October | Weeding, fertilization |
| November-December | Late weeding, pest control |
| January-March | Harvesting (Teff, Wheat) |
| February-April | Harvesting (Maize) |
| May | Land preparation (Belg season) |

### Common Crop Yield Estimates

| Crop | Expected Yield (kg/ha) |
|------|----------------------|
| Teff | 1500-2500 |
| Wheat | 2500-4000 |
| Maize | 3000-5000 |
| Barley | 2000-3500 |
| Sorghum | 2000-4000 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-08-15 | Initial release |
| 1.1.0 | 2024-08-20 | Added harvest and inventory endpoints |

---

## Support

For questions or issues:
- Extension Officer: +251-XX-XXX-XXXX
- Email: support@farmconnect.et
- Documentation: docs.farmconnect.et
