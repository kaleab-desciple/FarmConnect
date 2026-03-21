## Complete Business Logic Flow: Harvest to Product Listing in FarmConnect

### Overview: "Yield Only, Quality Later" Model

This workflow implements a two-phase approach where farmers first record their harvest yield, and then quality assessment is performed by authorized personnel before the harvest can be listed in the marketplace.

---

### Phase 1: Harvest Recording

**API Endpoint**: `POST /api/v1/agri/harvests/harvests`

**Flow**:
1. Farmer submits harvest data via [`harvest_routes.py:16-30`](server/app/api/v1/harvest/harvest_routes.py:16)
2. [`HarvestService.record_harvest()`](server/app/application/harvest/service.py:31) validates:
   - Crop cycle exists
   - Field exists and belongs to farmer
   - Quantity doesn't exceed 150% of expected yield
3. Harvest is created with `quality_grade: NULL`
4. CropCycle status updated to `HARVESTED` or `PARTIALLY_HARVESTED`

**Data Model** ([`entities.py:271-308`](server/app/domain/farm/entities.py:271)):
```python
Harvest:
  - id: UUID
  - farmer_id: str
  - crop_cycle_id: UUID
  - field_id: UUID
  - harvest_date: date
  - quantity_harvested: Decimal
  - quality_grade: QualityGrade (NULL initially)
```

---

### Phase 2: Quality Assessment

**API Endpoints**:
- `POST /harvests/{id}/quality/assess` - Create assessment
- `GET /harvests/{id}/quality/assessment` - Get latest assessment
- `GET /harvests/{id}/quality/history` - Get assessment history

**Authorization**: Only AGRONOMIST, AGENT, MODERATOR roles can assess (FARMER/ADMIN excluded)

**Flow** ([`quality_service.py:28-109`](server/app/application/harvest/quality_service.py:28)):
1. Authorized user submits assessment with:
   - `assessment_method`: VISUAL, MANUAL, or INSTRUMENT
   - `appearance_score`: 1-10 scale
   - `uniformity_score`: 1-10 scale
   - `damage_pct`: 0-100%
2. Service validates method-specific requirements
3. If no grade provided, auto-calculate using weighted algorithm:
   - GRADE_A: appearance ≥8, uniformity ≥8, damage ≤5%
   - GRADE_B: appearance ≥6, uniformity ≥6, damage ≤15%
   - GRADE_C: appearance ≥4, damage ≤30%
   - REJECT: otherwise
4. Create QualityAssessment record
5. Update Harvest.quality_grade with assigned grade

**Data Model** ([`entities.py:505-545`](server/app/domain/harvest/entities.py:505)):
```python
QualityAssessment:
  - id: UUID
  - harvest_id: UUID (FK)
  - assessor_id: str (FK to users)
  - assessor_role: str
  - assessment_method: enum
  - assessment_date: datetime
  - appearance_score: int
  - uniformity_score: int
  - damage_pct: float
  - assigned_grade: str (GRADE_A/B/C/REJECT)
```

---

### Phase 3: Product Conversion (Listing)

**API Endpoint**: `POST /harvests/{id}/convert-to-product`

**Business Rule**: Harvest MUST have valid quality assessment before conversion

**Validation Flow** ([`service.py:115-140`](server/app/application/harvest/service.py:115)):
1. Check harvest exists → 404 if not found
2. Check quality_grade is set → 400 if NULL
3. Check QualityAssessment record exists → 400 if missing
4. Check grade is not REJECT → 400 if REJECT

**Conversion Flow** ([`service.py:161-371`](server/app/application/harvest/service.py:161)):
1. Create HarvestEvent from legacy Harvest
2. Create HarvestBatch (draft)
3. Add contribution linking event to batch
4. Seal batch (compute lineage_hash)
5. Set batch status to QC_PENDING
6. **Auto-create QC report** if internal assessment exists (passed=True)
7. Update batch to QC_PASSED
8. Create Product with:
   - `is_active=True` if QC passed
   - `is_active=False` if still pending QC
9. Create ProductBatch and link to HarvestBatch

---

### State Machine: HarvestBatch

```
DRAFT → SEALED → QC_PENDING → QC_PASSED / QC_FAILED
```

**Transitions**:
- DRAFT → SEALED: When contribution added and sealed
- SEALED → QC_PENDING: Initial QC status
- QC_PENDING → QC_PASSED: When QC report created with passed=True
- QC_PENDING → QC_FAILED: When QC report created with passed=False

---

### Key Business Rules

| Rule | Implementation |
|------|----------------|
| Only authorized roles can assess | `quality_service.py:21` - AUTHORIZED_ROLES |
| Assessment required before listing | `service.py:117-140` - Three validation checks |
| Rejected harvests cannot be listed | `service.py:135-140` - REJECT grade check |
| Auto-activate product on QC pass | `service.py:307` - is_active=bool(is_batch_qc_passed) |
| Lineage tracking | `service.py:312-317` - harvest_batch_id in metadata |

---

### Data Integrity Guarantees

1. **FK Constraints**: harvest_id → harvests.id, assessor_id → users.id
2. **Check Constraints**: appearance_score (1-10), uniformity_score (1-10), damage_pct (0-100)
3. **Role-based Authorization**: Only AGRONOMIST/AGENT/MODERATOR can assess
4. **Farmer Authorization**: Only harvest owner or privileged users can convert
5. **Audit Trail**: All assessments recorded with assessor_id and timestamp

---

### Error Handling

| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| Harvest not found | 404 | "Harvest not found" |
| No quality grade | 400 | "Harvest must have a quality assessment..." |
| No assessment record | 400 | "No quality assessment record found..." |
| Grade is REJECT | 400 | "This harvest has been rejected..." |
| Not authorized | 403 | "Not authorized" |
