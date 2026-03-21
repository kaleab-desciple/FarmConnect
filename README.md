# Complete Business Logic Flow: Harvest to Product Listing

This document provides a comprehensive analysis of how harvested products transition through the product listing process in the FarmConnect system.

---

## 1. Overview Architecture

The harvest-to-product-listing workflow consists of three main phases:

1. **Harvest Recording Phase** - Recording a harvest event from a crop cycle
2. **Batch Aggregation Phase** - Creating harvest batches with lineage tracking
3. **Product Conversion Phase** - Converting validated harvests into marketplace listings

---

## 2. Data Models and Entities

### 2.1 Domain Entities (from [`entities.py`](server/app/domain/farm/entities.py))

#### [`Harvest`](server/app/domain/farm/entities.py:302) Entity
```python
class Harvest(BaseModel):
    id: UUID
    farmer_id: str                          # Foreign key to farmer
    crop_cycle_id: Optional[UUID] = None    # Links to growing cycle
    field_id: UUID                          # Field where harvest occurred
    harvest_date: date                     # Date of harvest
    quantity_harvested: Decimal             # Amount harvested (must be > 0)
    unit: Optional["Unit"] = None           # KG, TON, LITER, etc.
    quality_grade: Optional["QualityGrade"] = None  # GRADE_A, GRADE_B, GRADE_C
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
```

#### [`CropCycle`](server/app/domain/farm/entities.py:153) Entity
Tracks the growing cycle from planting to harvest:
```python
class CropCycle(BaseModel):
    id: UUID
    field_id: UUID
    product_category: str                   # CEREALS, VEGETABLES, FRUITS, etc.
    crop_name: str
    variety: Optional[str] = None
    planting_date: date
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    status: str = "PLANNED"                 # PLANNED → PLANTED → GROWING → HARVESTED
    expected_yield_kg: Optional[Decimal]    # Estimated yield for validation
    actual_yield_kg: Optional[Decimal]      # Updated as harvests are recorded
```

### 2.2 Harvest Batch Entities (from [`entities.py`](server/app/domain/harvest/entities.py))

#### [`HarvestBatchState`](server/app/domain/harvest/entities.py:11) State Machine
```python
class HarvestBatchState(str, Enum):
    DRAFT = "DRAFT"           # Initial state after creation
    SEALED = "SEALED"         # Batch closed, lineage computed
    QC_PENDING = "QC_PENDING" # Awaiting quality assessment
    QC_PASSED = "QC_PASSED"   # Passed quality control
    QC_FAILED = "QC_FAILED"   # Failed quality control
    ARCHIVED = "ARCHIVED"     # Archived for records
```

#### [`HarvestEvent`](server/app/domain/harvest/entities.py:58) Entity
Field-level harvest tracking event:
```python
class HarvestEvent(BaseModel):
    id: UUID
    farm_id: str
    field_id: str
    crop_cycle_id: Optional[UUID] = None
    collected_by: Optional[str] = None
    harvested_at: datetime
    gross_weight_kg: float               # Must be > 0
    moisture_pct: Optional[float] = None  # 0-100
    loss_kg: float = 0
    photos: Optional[List[Dict]] = None
    weighbridge_receipt: Optional[Dict] = None
    location: Optional[Dict] = None       # GeoJSON
    notes: Optional[str] = None
```

#### [`HarvestBatch`](server/app/domain/harvest/entities.py:124) Entity
Aggregated batch with lineage tracking:
```python
class HarvestBatch(BaseModel):
    id: UUID
    batch_code: str                       # Unique identifier (e.g., "BATCH-abc123")
    aggregator_id: Optional[str] = None   # Who aggregated the batch
    status: HarvestBatchState = DRAFT
    aggregated_weight_kg: Optional[float] = None
    moisture_avg: Optional[float] = None
    sealed_at: Optional[datetime] = None
    sealed_by: Optional[str] = None
    seal_evidence: Optional[Dict] = None
    lineage_hash: Optional[str] = None    # Cryptographic proof of lineage
    created_at: datetime
    updated_at: datetime
```

#### [`BatchQCReport`](server/app/domain/harvest/entities.py:170) Entity
Quality control lab results:
```python
class BatchQCReport(BaseModel):
    id: UUID
    batch_id: UUID
    lab_id: Optional[str] = None
    tested_at: datetime
    metrics: Optional[Dict] = None        # {moisture_pct: 12.4, aflatoxin_ppb: 3.4}
    passed: bool
    report_url: Optional[str] = None
    signed_hash: Optional[str] = None
    notes: Optional[str] = None
```

---

## 3. Service Layer Transformations

### 3.1 [`HarvestService`](server/app/application/harvest/service.py:25) - Primary Service

The [`HarvestService`](server/app/application/harvest/service.py:25) orchestrates the entire workflow:

#### Method: [`record_harvest()`](server/app/application/harvest/service.py:31)
**Purpose**: Records a new harvest event and validates against crop cycle estimates

**Business Rules**:
1. Validates crop cycle exists
2. Validates field exists
3. Authenticates and authorizes the user
4. Validates quantity doesn't exceed 150% of expected yield (warning threshold)
5. Updates crop cycle status based on harvest completion

**Status Transitions**:
- If `new_total >= expected_yield` → CropCycleStatus.HARVESTED
- Otherwise → CropCycleStatus.PARTIALLY_HARVESTED

#### Method: [`convert_to_product()`](server/app/application/harvest/service.py:110)
**Purpose**: Converts a validated harvest into a marketplace product listing

**Key Validation - Quality Grade Requirement**:
```python
# Lines 117-121 in service.py
if not harvest.quality_grade:
    raise HTTPException(
        status_code=400,
        detail="Harvest must have a QCGrade assessment before converting..."
    )
```

This enforces the "Yield Only, Quality Later" workflow - quality assessment must complete first.

---

## 4. API Endpoints and Request/Response Schemas

### 4.1 Harvest Recording Endpoint

**Endpoint**: `POST /api/v1/harvests/`

**Permission Required**: `harvests:create`

**Request Schema** ([`HarvestCreate`](server/app/domain/farm/entities.py:287)):
```python
class HarvestCreate(HarvestBase):
    farmer_id: str
    crop_cycle_id: Optional[UUID] = None
    field_id: UUID
    harvest_date: date
    quantity_harvested: Decimal  # Must be > 0
    unit: Optional["Unit"] = None
    quality_grade: Optional["QualityGrade"] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None
```

**Response**:
```json
{
    "id": "uuid-string",
    "status": "recorded",
    "harvest_date": "2024-01-15",
    "quantity": "1500.00"
}
```

### 4.2 Harvest Listing for Crop Cycle

**Endpoint**: `GET /api/v1/harvests/crop-cycle/{cycle_id}`

**Permission Required**: `harvests:read`

**Response**:
```json
[
    {
        "id": "uuid-string",
        "harvest_date": "2024-01-15",
        "quantity": "1500.00",
        "unit": "KG",
        "quality_grade": "GRADE_A"
    }
]
```

### 4.3 Convert to Product Endpoint

**Endpoint**: `POST /api/v1/harvests/{harvest_id}/convert-to-product`

**Permission Required**: `products:create`

**Request Schema** (flexible dict with optional fields):
```python
{
    "name": Optional[str],                    # Product name (auto-generated if missing)
    "description": Optional[str],
    "category": Optional[str],                # VEGETABLES, FRUITS, GRAINS, etc.
    "base_price": Optional[float],
    "currency": Optional[str],                # Default: "USD"
    "quantity": Optional[float],              # Defaults to harvest quantity
    "expiry_date": Optional[date],
    "location": Optional[dict],
    "images": Optional[List[str]],
    
    # Batch-related (optional)
    "harvest_batch_id": Optional[UUID],      # Use existing batch
    "batch_code": Optional[str],
    "batch_notes": Optional[str],
    "batch_metadata": Optional[dict],
    "seal_evidence": Optional[dict],
    
    # QC Report (optional - for inline QC)
    "qc_report": {
        "lab_id": Optional[str],
        "tested_at": Optional[datetime],
        "metrics": Optional[dict],
        "passed": bool,
        "report_url": Optional[str],
        "signed_hash": Optional[str],
        "notes": Optional[str]
    }
}
```

**Response Schema** ([`ProductConversionResponse`](server/app/api/v1/harvest/schemas.py:35)):
```python
class ProductConversionResponse(BaseModel):
    id: str                                    # Product ID
    name: Optional[str]
    total_quantity: Optional[str]
    status: Optional[str] = "converted"
    is_active: Optional[bool]                  # True only if QC_PASSED
    product_batches: List[ProductBatchLink]   # Linked product batches
    
    # Primary harvest batch summary
    harvest_batch_id: Optional[str]
    harvest_batch_status: Optional[str]       # DRAFT, SEALED, QC_PENDING, etc.
    harvest_batch_lineage_hash: Optional[str] # Cryptographic proof
    harvest_batch_aggregated_weight_kg: Optional[float]
    
    # Latest QC summary
    qc_status: Optional[str]                  # PASSED, FAILED
    qc_lab_id: Optional[str]
    qc_tested_at: Optional[str]
```

### 4.4 Harvest Statistics Endpoint

**Endpoint**: `GET /api/v1/harvests/statistics`

**Permission Required**: `harvests:read`

**Query Parameters**:
- `farmer_id`: Optional filter by farmer UUID

**Response**:
```json
{
    "total_harvests": 15,
    "pending_harvests": 3,        # READY status
    "completed_harvests": 10,    # HARVESTED status
    "total_quantity_kg": 1500.5,
    "by_status": {
        "PLANNED": 2,
        "IN_PROGRESS": 1,
        "READY": 3,
        "HARVESTED": 8,
        "CANCELLED": 1
    }
}
```

---

## 5. Validation Logic

### 5.1 Harvest Recording Validation

| Validation | Rule | Action |
|------------|------|--------|
| Crop Cycle Exists | Must find crop cycle by ID | HTTP 404 if missing |
| Field Exists | Must find field by ID | HTTP 404 if missing |
| Authorization | User's farmer_id must match or user has ADMIN/AGENT/AGRONOMIST role | HTTP 403 if unauthorized |
| Yield Threshold | `new_total <= expected * 1.5` | Warning logged but allowed |
| Quantity > 0 | Must be positive decimal | Pydantic validation |

### 5.2 Product Conversion Validation

| Validation | Rule | Action |
|------------|------|--------|
| Harvest Exists | Must find harvest by ID | HTTP 404 if missing |
| Quality Grade Required | `harvest.quality_grade` must be set | HTTP 400 if missing |
| Authorization | User must own harvest or have privileged role | HTTP 403 if unauthorized |
| Farmer Profile | User must have linked farmer profile | HTTP 400 if missing |
| Batch QC Status | For active listing: batch must be QC_PASSED | Product created as inactive if QC pending |

---

## 6. Status Transitions and State Machines

### 6.1 Crop Cycle Status Flow

```
PLANNED → PLANTED → GROWING → HARVESTED
                          ↓
                   PARTIALLY_HARVESTED
```

Transitions occur in [`record_harvest()`](server/app/application/harvest/service.py:95):
```python
if new_total >= expected and expected > 0:
    crop_cycle.status = CropCycleStatus.HARVESTED
else:
    crop_cycle.status = CropCycleStatus.PARTIALLY_HARVESTED
```

### 6.2 Harvest Batch Status Flow

```
DRAFT → SEALED → QC_PENDING → QC_PASSED (or QC_FAILED)
    ↓                              ↓
  ARCHIVED                    ARCHIVED
```

**State Transitions in [`convert_to_product()`](server/app/application/harvest/service.py:214)**:

1. **DRAFT → SEALED**: When [`seal_batch()`](server/app/infrastructure/repositories/harvest_batch_repo.py:259) is called
   - Computes lineage_hash
   - Calculates aggregated_weight_kg
   - Calculates moisture_avg

2. **SEALED → QC_PENDING**: Immediately after sealing (line 218)
   ```python
   hb_repo.update_batch_status(str(sealed.id), HarvestBatchState.QC_PENDING, ...)
   ```

3. **QC_PENDING → QC_PASSED/QC_FAILED**: When [`create_qc_report()`](server/app/infrastructure/repositories/harvest_batch_repo.py:397) is called
   - Sets status based on `passed` field

### 6.3 Product Active State

```
INACTIVE (QC Pending/Failed) → ACTIVE (QC Passed)
```

In [`convert_to_product()`](server/app/application/harvest/service.py:307):
```python
is_active=bool(is_batch_qc_passed)  # True only if QC_PASSED
```

---

## 7. Relationships Between Farm Entities and Harvested Products

### 7.1 Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Farm    │────<│   Field    │────<│  CropCycle │
└─────────────┘     └─────────────┘     └─────────────┘
                                             │
                                             │ 1:N
                                             ▼
                                      ┌─────────────┐
                                      │   Harvest  │
                                      └─────────────┘
                                             │
                                             │ converts to
                                             ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Product  │<────│ProductBatch │<────│HarvestBatch │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           │ N:M              │ N:M
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │ProductSource│     │Contribution │
                    └─────────────┘     └─────────────┘
```

### 7.2 Key Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| Farm → Fields | 1:N | A farm has multiple fields |
| Field → CropCycles | 1:N | A field can have multiple growing cycles |
| CropCycle → Harvests | 1:N | A crop cycle can have multiple harvests |
| Harvest → HarvestEvent | 1:1 | Converted when creating batch |
| HarvestEvent → HarvestBatchContribution | 1:N | Events contribute to batches |
| HarvestBatch → HarvestBatchContribution | 1:N | Batch aggregates contributions |
| HarvestBatch → BatchQCReport | 1:N | Multiple QC reports possible |
| Product → ProductBatch | 1:N | Product can have multiple batches |
| ProductBatch → HarvestBatch | N:M | Linked via ProductBatchSource |

---

## 8. Data Integrity Throughout the Listing Workflow

### 8.1 Lineage Hash Computation

The system uses cryptographic hashing to ensure batch integrity:

**Function**: [`compute_lineage_hash()`](server/app/domain/harvest/entities.py:244)

```python
def compute_lineage_hash(
    batch_id: str,
    aggregator_id: Optional[str],
    created_at: datetime,
    contributions: List[Dict[str, Any]]
) -> str:
    # 1. Sort contributions deterministically
    sorted_contributions = sorted(
        contributions,
        key=lambda x: (
            str(x.get('harvest_event_id', '')),
            str(x.get('farmer_id', '')),
            str(x.get('contributed_weight_kg', 0)),
            str(x.get('harvested_at', ''))
        )
    )
    
    # 2. Build canonical JSON
    canonical_data = {
        "batch_id": str(batch_id),
        "aggregator_id": str(aggregator_id) if aggregator_id else None,
        "created_at": created_at.isoformat() if created_at else None,
        "contributions": [...]
    }
    
    # 3. Compute SHA256
    lineage_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    return lineage_hash
```

**Integrity Guarantees**:
- Deterministic ordering prevents hash manipulation
- Includes all contribution weights and farmer IDs
- Timestamped with batch creation time

### 8.2 Audit Events

All major operations create audit events in [`HarvestBatchRepository`](server/app/infrastructure/repositories/harvest_batch_repo.py:72):

| Event Type | When Created |
|------------|--------------|
| `harvest_event.created` | Event created |
| `batch.created` | Draft batch created |
| `batch.sealed` | Batch sealed with lineage |
| `batch.status_changed` | QC status change |
| `qc.completed` | QC report submitted |
| `product_batch.linked` | Product linked to harvest batch |

### 8.3 Concurrency Protection

The [`seal_batch()`](server/app/infrastructure/repositories/harvest_batch_repo.py:259) method uses row-level locking:

```python
# Get batch with row lock to prevent concurrent seal attempts
orm = self.db.query(HarvestBatchORM).filter(
    HarvestBatchORM.id == batch_id
).with_for_update().first()
```

### 8.4 Double-Spend Prevention

The system prevents harvest events from being used in multiple sealed batches:

```python
# In add_contribution() - lines 172-183
sealed_check = self.db.query(HarvestBatchContributionORM).join(
    HarvestBatchORM,
    ...
).filter(
    HarvestBatchContributionORM.harvest_event_id == str(contribution.harvest_event_id),
    HarvestBatchORM.status == HarvestBatchState.SEALED,
).first()
if sealed_check:
    raise ValueError("This harvest event is already contributed to a SEALED batch...")
```

---

## 9. Complete Workflow Step-by-Step

### Phase 1: Harvest Recording

1. **Farmer records harvest** via `POST /harvests/`
2. **Service validates**:
   - Crop cycle exists and is valid
   - Field exists
   - User is authorized
   - Quantity is within acceptable bounds
3. **Harvest created** in database
4. **CropCycle updated**:
   - `actual_yield_kg` incremented
   - `actual_harvest_date` set
   - Status changed to HARVESTED or PARTIALLY_HARVESTED

### Phase 2: Quality Assessment

5. **Quality grade assigned** to harvest (external process or manual entry)
   - This is a **mandatory prerequisite** for conversion

### Phase 3: Product Conversion

6. **Farmer calls** `POST /harvests/{id}/convert-to-product`
7. **Service validates**:
   - Harvest exists
   - Quality grade is set (enforced!)
   - User authorization
   - Farmer profile exists
8. **Batch creation flow**:
   - Creates HarvestEvent from legacy Harvest
   - Creates draft HarvestBatch
   - Adds contribution linking event to batch
   - Seals batch (computes lineage_hash, aggregated_weight, moisture_avg)
   - Sets status to QC_PENDING
9. **Optional inline QC**:
   - If `qc_report` provided, creates BatchQCReport
   - Status changes to QC_PASSED or QC_FAILED
10. **Product creation**:
    - If QC_PASSED: Product created as ACTIVE
    - Otherwise: Product created as INACTIVE
11. **ProductBatch creation** and linkage to HarvestBatch

---

## 10. Edge Cases and Error Handling

| Scenario | Handling |
|----------|----------|
| Harvest without quality grade | Conversion blocked with HTTP 400 |
| QC failed batch | Product created as inactive, can be re-QC'd |
| Existing harvest_batch_id provided | Skip batch creation, use existing |
| Unauthorized user | HTTP 403 Forbidden |
| Missing farmer profile | HTTP 400 with helpful message |
| Duplicate harvest event in sealed batch | ValueError prevented at contribution time |
| Concurrent seal attempts | Row locking prevents race condition |
| Empty batch sealing | Requires at least one contribution |

---

## 11. Business Rules Summary

1. **Yield Validation**: Harvests can exceed expected yield by up to 150% (warning threshold)
2. **Quality First**: No product conversion without quality grade assessment
3. **QC Gate**: Products only become active (listable) when batch passes QC
4. **Lineage Integrity**: Sealed batches cannot be modified - immutable provenance
5. **Single-Use Events**: Harvest events can only contribute to one sealed batch
6. **Authorization**: Farmers can only convert their own harvests (unless privileged role)
