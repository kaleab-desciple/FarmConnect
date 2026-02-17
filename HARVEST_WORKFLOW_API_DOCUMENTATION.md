# Harvest to Product Workflow API Documentation
## Farm Connect - AgriManagement System

This document provides comprehensive API documentation for the Harvest-to-Product workflow in the Farm Connect application. This workflow allows farmers to record harvested quantities from fields and convert them into sellable products in the inventory.

---

## Table of Contents
1. [Record Harvest](#1-record-harvest---post-agriharvests)
2. [List Harvests for Crop Cycle](#2-list-harvests-for-crop-cycle---get-agriharvestscrop-cyclecycle_id)
3. [Convert Harvest to Product](#3-convert-harvest-to-product---post-agriharvestsharvest_idconvert-to-product)

---

## 1. Record Harvest - POST /api/v1/agri/harvests/

Record a new harvest event for a specific field and crop cycle.

### Request Body

```json
{
  "farmer_id": "aefc0e4b-8010-4c9a-bc7f-d1d02804795d",
  "crop_cycle_id": "b41a826b-5e66-4667-8256-f0f6a3b993b2",
  "field_id": "8e62ca44-c9db-4109-a42b-af18e1cfb67c",
  "harvest_date": "2026-02-17",
  "quantity_harvested": 1200.50,
  "unit": "KG",
  "quality_grade": "GRADE_A",
  "notes": "Excellent yield from the north section.",
  "metadata": {
    "weather_condition": "sunny",
    "labor_count": 5
  }
}
```

### Field Descriptions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `farmer_id` | string | Yes | Valid UUID | Identifier of the farmer |
| `crop_cycle_id` | string | No | Valid UUID | Associated crop cycle |
| `field_id` | string | Yes | Valid UUID | Field where harvest occurred |
| `harvest_date` | date | Yes | ISO date | Date of the harvest |
| `quantity_harvested` | decimal | Yes | > 0 | Amount harvested |
| `unit` | string | No | enum | KG, TON, UNIT, CRATE, BAG |
| `quality_grade` | string | No | enum | GRADE_A, GRADE_B, GRADE_C, PREMIUM, STANDARD |
| `notes` | string | No | - | Additional observations |
| `metadata` | object | No | - | Arbitrary JSON metadata |

### Response

```json
{
  "id": "c4d9e2f1-a6b7-4890-c1d2-e3f4a5b6c7d8",
  "status": "recorded",
  "harvest_date": "2026-02-17",
  "quantity": "1200.50"
}
```

---

## 2. List Harvests for Crop Cycle - GET /api/v1/agri/harvests/crop-cycle/{cycle_id}

Retrieve all harvest records associated with a specific crop cycle.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cycle_id` | string | Yes | UUID of the crop cycle |

### Response

```json
[
  {
    "id": "c4d9e2f1-a6b7-4890-c1d2-e3f4a5b6c7d8",
    "harvest_date": "2026-02-17",
    "quantity": "1200.50",
    "unit": "KG",
    "quality_grade": "GRADE_A"
  }
]
```

---

## 3. Convert Harvest to Product - POST /api/v1/agri/harvests/{harvest_id}/convert-to-product

Convert a recorded harvest into a sellable product in the inventory.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `harvest_id` | string | Yes | UUID of the harvest record |

### Request Body

```json
{
  "name": "Premium Basmati Rice",
  "description": "Organic long-grain basmati rice, freshly harvested.",
  "category": "GRAINS",
  "base_price": 2.50,
  "currency": "USD",
  "quantity": 1200.0,
  "metadata": {
    "packaging": "25kg bags"
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Name for the product (defaults to harvest info if empty) |
| `description` | string | No | Product description |
| `category` | string | Yes | Products category (e.g., GRAINS, VEGETABLES) |
| `base_price` | decimal | Yes | Price per unit |
| `currency` | string | No | Currency code (default: USD) |
| `quantity` | decimal | No | Quantity to list (defaults to harvest quantity) |
| `metadata` | object | No | Product-level metadata |

### Response

```json
{
  "id": "1616559f-747e-4067-8ced-c68a42727e33",
  "name": "Premium Basmati Rice",
  "quantity_available": "1200.0",
  "status": "converted"
}
```

---

## Business Rules & Logic

1.  **Status Transition**: Recording a harvest automatically updates the `CropCycle` status. If the total harvested quantity exceeds the expected yield, the status becomes `HARVESTED`. Otherwise, it remains `PARTIALLY_HARVESTED`.
2.  **Traceability**: Products created from this workflow carry a `harvest_id` and `crop_cycle_id`, allowing merchants and admins to trace produce back to the specific field and planting cycle.
3.  **Authorization**: Only the owner (farmer) of the farm or an administrator can record harvests or convert them to products.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-17 | Initial release of Harvest-to-Product workflow API |
