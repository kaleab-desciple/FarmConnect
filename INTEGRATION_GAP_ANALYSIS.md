# Integration Gap Analysis Report
## FarmConnect - Frontend vs Server API

---

## 1. Data Model Mismatches

### 1.1 Farm Interface

| Frontend (`farms-api.ts`) | Server (`shared_models/farm.py`) | Gap Type |
|---------------------------|----------------------------------|----------|
| `id: string` | `id: UUID` | Type mismatch (string vs UUID) |
| `location?: string` | `location_lat`, `location_lng`, `location_address` | Field doesn't exist - server uses separate lat/lng/address |
| `total_area_hectares?: number` | `total_area_ha: Optional[Decimal]` | Different field name + type (number vs Decimal) |
| `created_at: string` | `created_at: datetime` | Type mismatch (string vs datetime) |
| `updated_at?: string` | `updated_at: datetime` | Type mismatch |
| *(missing)* | `boundary_geojson: Optional[dict]` | Server has this field |
| *(missing)* | `centroid_geojson: Optional[dict]` | Server has this field |
| *(missing)* | `metadata: Optional[dict]` | Server has this field |
| *(missing)* | `deleted_at: Optional[datetime]` | Server has soft-delete field |

### 1.2 FarmListResponse

| Frontend (`farms-api.ts`) | Server (`FarmListResponse`) | Gap Type |
|---------------------------|-----------------------------|----------|
| `items: Farm[]` | `farms: List[Farm]` | **Critical**: Field name mismatch (`items` vs `farms`) |
| `total: number` | `total: int` | OK |
| `page: number` | `page: int` | OK |
| `page_size: number` | `page_size: int` | OK |
| *(missing)* | `total_pages: int` | Frontend missing this field |

**Impact**: `farmsData?.farms?.length` in FarmerDashboard.tsx (line 160) will be **undefined** because server returns `farms` not `items`.

### 1.3 Field Interface

| Frontend (`farms-api.ts`) | Server (`Field` in shared_models) | Gap Type |
|---------------------------|----------------------------------|----------|
| `id: string` | `id: UUID` | Type mismatch |
| `farm_id: string` | `farm_id: UUID` | Type mismatch |
| `name: string` | `name: str` | OK |
| `area_hectares: number` | `area_ha: Decimal` | **Field name mismatch** + type |
| `soil_type?: string` | `soil_type: Optional[str]` | OK |
| `location?: any` | *(not present)* | Frontend has extra field |
| `geometry?: any` | `boundary_geojson`, `centroid_geojson` | Different field names |
| `created_at: string` | `created_at: datetime` | Type mismatch |
| *(missing)* | `soil_classification: Optional[str]` | Server has extra field |
| *(missing)* | `elevation_m: Optional[Decimal]` | Server has extra field |
| *(missing)* | `slope_degree: Optional[Decimal]` | Server has extra field |
| *(missing)* | `irrigation_type: Optional[str]` | Server has extra field |
| *(missing)* | `drainage_type: Optional[str]` | Server has extra field |
| *(missing)* | `metadata: Optional[dict]` | Server has extra field |

### 1.4 CropCycle Interface

| Frontend (`farms-api.ts`) | Server (`CropCycle` in shared_models) | Gap Type |
|---------------------------|---------------------------------------|----------|
| `id: string` | `id: UUID` | Type mismatch |
| `field_id: string` | `field_id: UUID` | Type mismatch |
| `crop_type: string` | `product_category`, `crop_name` | **Field name mismatch** - server uses product_category + crop_name |
| `planting_date: string` | `planting_date: date` | Type mismatch (string vs date) |
| `expected_harvest_date?: string` | `expected_harvest_date?: date` | Type mismatch |
| `status: string` | `status: str` | OK |
| `yield_estimate?: number` | `expected_yield_kg: Optional[Decimal]` | **Field name mismatch** + type |
| `actual_yield?: number` | `actual_yield_kg: Optional[Decimal]` | **Field name mismatch** + type |
| `created_at: string` | `created_at: datetime` | Type mismatch |
| *(missing)* | `variety: Optional[str]` | Server has extra field |
| *(missing)* | `cultivar: Optional[str]` | Server has extra field |
| *(missing)* | `actual_harvest_date: Optional[date]` | Server has extra field |
| *(missing)* | `yield_quality_grade: Optional[str]` | Server has extra field |
| *(missing)* | `seed_source: Optional[str]` | Server has extra field |
| *(missing)* | `planting_density_per_ha: Optional[int]` | Server has extra field |
| *(missing)* | `seed_cost_usd: Optional[Decimal]` | Server has extra field |
| *(missing)* | `notes: Optional[str]` | Server has extra field |
| *(missing)* | `metadata: Optional[dict]` | Server has extra field |

### 1.5 Order Interface

| Frontend (`orders-api.ts`) | Server (`Order` in shared_models) | Gap Type |
|----------------------------|-----------------------------------|----------|
| `id: string` | `id: UUID` | Type mismatch |
| `farmer_id: string` | `farmer_id: str` | OK |
| `merchant_id: string` | `merchant_id: str` | OK |
| `product_id: string` | `product_id: str` | OK |
| `product_name: string` | *(not present)* | **Frontend has extra field not on server** |
| `quantity: number` | `quantity: PositiveFloat` | OK |
| `unit: string` | *(not present)* | **Frontend has extra field** |
| `unit_price: number` | `unit_price: PositiveFloat` | OK |
| `total_price: number` | `total_price: Optional[PositiveFloat]` | OK |
| `status: OrderStatus` | `status: OrderStatus` | OK |
| `delivery_address?: string` | *(not present in OrderBase)* | **Frontend has extra field** |
| `distance_km?: number` | *(not present)* | **Frontend has extra field** |
| `created_at: string` | `created_at: datetime` | Type mismatch |
| `updated_at?: string` | *(not present in OrderBase)* | **Frontend has extra field** |
| *(missing)* | `delivery_cost: Optional[confloat(ge=0.0)]` | Server has extra field |
| *(missing)* | `platform_fee: Optional[confloat(ge=0.0)]` | Server has extra field |
| *(missing)* | `escrow_id: Optional[str]` | Server has extra field |
| *(missing)* | `subtotal: Optional[PositiveFloat]` | Server has extra field |
| *(missing)* | `delivery_fee: Optional[PositiveFloat]` | Server has extra field |
| *(missing)* | `delivery_margin: Optional[PositiveFloat]` | Server has extra field |
| *(missing)* | `quality_fee: Optional[PositiveFloat]` | Server has extra field |

### 1.6 Order Status Enum Differences

| Frontend (`orders-api.ts`) | Server (`OrderStatus` enum) |
|----------------------------|----------------------------|
| `PENDING_PAYMENT` | `CREATED` |
| `PAYMENT_FAILED` | *(not present)* |
| `FUNDED` | `CONFIRMED` |
| `PROCESSING` | `IN_PROGRESS` |
| `PICKED_UP` | *(not present)* |
| `IN_TRANSIT` | `IN_TRANSIT` |
| `DELIVERED` | `DELIVERED` |
| `COMPLETED` | `COMPLETED` |
| `CANCELLED` | `CANCELLED` |
| `DISPUTED` | `DISPUTED` |

**Critical Issue**: Frontend uses `PENDING_PAYMENT` but server uses `CREATED`. The query in FarmerDashboard.tsx (line 154) `ordersAPI.list({ status: 'PENDING_PAYMENT' })` will return **no results**.

---

## 2. Endpoint Silos

### 2.1 Farm → Fields Relationship

| Frontend Expectation | Server Reality | Gap |
|---------------------|----------------|-----|
| `farmsData?.farms?.reduce((acc, farm) => acc + (farm.fields?.length || 0), 0)` | Server does NOT return fields nested in farms | **Critical** - Dashboard tries to access `farm.fields` which doesn't exist |
| Access fields via `GET /agri/farms/{farm_id}/fields/` | Requires `farm_id` as query param for `GET /agri/fields/` | Endpoint mismatch |

### 2.2 Missing API Endpoints for Dashboard Data

| Dashboard Data Need | Frontend Code | Server Status |
|--------------------|---------------|---------------|
| Pending harvest count | `pendingHarvest = 2` (hardcoded) | **NO ENDPOINT** - Needs harvest API |
| Alerts count | `value={1}` (hardcoded) | **NO ENDPOINT** - Needs alerts/notifications API |
| Total earnings | `value="$450"` (hardcoded) | **NO ENDPOINT** - Needs accounting/revenue API |
| Recent activity feed | Hardcoded in UI | **NO ENDPOINT** - Needs activity log API |
| Field geometry for map | Dashboard renders SVG polygons | **NO ENDPOINT** - Needs field boundaries API |

### 2.3 Required New Endpoints

1. **GET /agri/farms/{farm_id}/fields/** - Nested fields in farm response OR
2. **GET /agri/fields/** with optional farm_id filter (currently requires farm_id)
3. **GET /agri/harvests/pending** - Pending harvest counts
4. **GET /alerts/** - Farm alerts/notifications
5. **GET /accounting/farmer/earnings** - Earnings data
6. **GET /activity/** - Recent activity feed

---

## 3. Error Handling & Status Codes

### 3.1 Current Frontend Error Handling

The frontend services (`farms-api.ts`, `orders-api.ts`) use axios which:
- Throws on non-2xx responses
- Returns error response in `error.response.data`

### 3.2 Server Error Responses

| Scenario | Server Status | Server Response Format |
|----------|---------------|------------------------|
| Validation Error | `422 Unprocessable Entity` | `{ "detail": [...] }` |
| Not Found | `404` | `{ "detail": "Farm not found" }` |
| Forbidden | `403` | `{ "detail": "Access denied" }` |
| Unauthorized | `401` | `{ "detail": "..." }` |
| Server Error | `500` | `{ "detail": "..." }` |

### 3.3 Gaps Identified

1. **Frontend doesn't handle 422 validation errors** - Server returns detailed validation messages that frontend doesn't display
2. **Frontend assumes authenticated access** - Server has `get_optional_user` for list endpoints, but frontend may fail unexpectedly
3. **No retry logic** for transient failures
4. **No error mapping** - Raw server errors shown to users

---

## 4. Parameter Inconsistency

### 4.1 Farm List Endpoint

| Frontend Param | Frontend Code | Server Param | Server Logic |
|----------------|---------------|--------------|--------------|
| `page` | `page?: number` | `page: int = Query(default=1, ge=1)` | ✅ Matches |
| `page_size` | `page_size?: number` | `page_size: int = Query(default=20, ge=1, le=100)` | ✅ Matches |
| `farmer_id` | `farmer_id?: string` | `farmer_id: Optional[str] = Query(None)` | ✅ Matches |

**Status**: ✅ Parameters align

### 4.2 Order List Endpoint

| Frontend Param | Frontend Code | Server Param | Server Logic |
|----------------|---------------|--------------|--------------|
| `page` | `page?: number` | *(not implemented)* | ❌ Not supported |
| `page_size` | `page_size?: number` | *(not implemented)* | ❌ Not supported |
| `status` | `status?: OrderStatus` | *(filtering not shown in routes)* | ❌ Unknown |
| `farmer_id` | `farmer_id?: string` | *(handled via row-level security)* | ⚠️ Different |
| `merchant_id` | `merchant_id?: string` | *(not implemented)* | ❌ Not supported |

**Status**: ❌ Server doesn't support pagination on orders list

### 4.3 Field List Endpoint

| Frontend Param | Frontend Code | Server Param | Server Logic |
|----------------|---------------|--------------|--------------|
| `farm_id` | `farm_id?: string` (query param) | `farm_id: str = Query(..., description="Farm ID")` | ⚠️ **Required** on server, optional on frontend |

**Status**: ⚠️ Server requires farm_id but frontend doesn't mark it as required

---

## Summary: Mismatches Found

### Critical (Breaking)

| # | Category | Issue | Impact |
|---|----------|-------|--------|
| 1 | Data Model | `FarmListResponse.items` vs `farms` | Dashboard crashes - `farmsData.farms` is undefined |
| 2 | Data Model | `farm.fields` access | Dashboard tries to access nested fields that don't exist |
| 3 | Data Model | Order status `PENDING_PAYMENT` vs `CREATED` | Pending orders query returns empty |
| 4 | Endpoint | No nested fields in farm response | Cannot calculate total fields |
| 5 | Endpoint | Hardcoded dashboard values | No real data for harvests, alerts, earnings |

### High Priority

| # | Category | Issue | Impact |
|---|----------|-------|--------|
| 6 | Data Model | Farm: `location` vs `location_lat/lng/address` | Location display broken |
| 7 | Data Model | Field: `area_hectares` vs `area_ha` | Field area displays wrong |
| 8 | Data Model | CropCycle: `crop_type` vs `product_category/crop_name` | Crop info mismatch |
| 9 | Data Model | CropCycle: `yield_estimate` vs `expected_yield_kg` | Yield data mismatch |
| 10 | Data Model | Type: `string` vs `UUID` | TypeScript type errors |

### Medium Priority

| # | Category | Issue | Impact |
|---|----------|-------|--------|
| 11 | Data Model | Order: extra fields (`product_name`, `unit`, etc.) | Extra fields undefined |
| 12 | Error Handling | No 422 validation error handling | Poor user feedback |
| 13 | Endpoint | No pagination on orders list | Performance issues |
| 14 | Endpoint | farm_id required for fields list | API design mismatch |

---

## Action Plan

### Frontend Updates Required

| Priority | Action | File(s) |
|----------|--------|---------|
| **P0** | Update `FarmListResponse` to use `farms` instead of `items` | `farms-api.ts` |
| **P0** | Update dashboard to call separate endpoint for fields | `FarmerDashboard.tsx` |
| **P0** | Fix order status enum to match server (`CREATED` not `PENDING_PAYMENT`) | `orders-api.ts`, `FarmerDashboard.tsx` |
| **P1** | Update Farm interface fields: `location` → `location_lat`, `location_lng`, `location_address` | `farms-api.ts` |
| **P1** | Update Field interface: `area_hectares` → `area_ha` | `farms-api.ts` |
| **P1** | Update CropCycle interface: `crop_type` → `product_category`/`crop_name`, `yield_estimate` → `expected_yield_kg` | `farms-api.ts` |
| **P1** | Add `total_pages` to `FarmListResponse` | `farms-api.ts` |
| **P2** | Add error handling for 422 validation errors | API service layer |
| **P2** | Add retry logic for failed requests | API service layer |
| **P2** | Update Order interface - add missing fields, remove non-existent | `orders-api.ts` |

### Backend Updates Required

| Priority | Action | File(s) |
|----------|--------|---------|
| **P0** | Add optional nested fields to farm response OR create dedicated endpoint | `farms/routes.py`, `farms/service.py` |
| **P1** | Add pagination support to orders list endpoint | `orders/routes.py` |
| **P1** | Add status filter to orders list | `orders/routes.py` |
| **P2** | Create harvest pending endpoint | `harvest/routes.py` |
| **P2** | Create alerts/notifications endpoint | `notifications/routes.py` |
| **P2** | Create farmer earnings endpoint | `accounting/routes.py` |
| **P2** | Create activity feed endpoint | `activity/routes.py` |

### New API Endpoints Needed

| Endpoint | Purpose |
|----------|---------|
| `GET /agri/farms/{farm_id}/fields/` | Get fields for a specific farm |
| `GET /agri/harvests/summary` | Get harvest statistics |
| `GET /alerts/` | Get farm alerts |
| `GET /accounting/farmer/earnings` | Get farmer earnings |
| `GET /activity/feed` | Get recent activity |

---

*Generated: 2026-03-09*
*Analysis covers: FarmerDashboard.tsx, farms-api.ts, orders-api.ts, server/app/api/v1/farms/*