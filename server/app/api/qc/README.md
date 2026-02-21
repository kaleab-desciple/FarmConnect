# QC & Lab API Documentation

This module provides endpoints for Quality Control (QC) and Lab management in the FarmConnect system.

## Overview

The QC/Grading workflow ensures that harvest batches meet quality standards before being listed in the marketplace. This includes:

- Sample collection and tracking
- Lab report ingestion via webhook
- Grade evaluation based on configurable rules
- Signature verification for lab authenticity
- Product listing validation gates

## Endpoints

### Lab Webhook

**POST** `/api/qc/lab_webhook`

Receive lab test results from external lab systems.

#### Authentication

The webhook accepts:
- `X-Lab-ID` header for additional verification
- Lab provider must be registered in the system

#### Request Body

```json
{
    "lab_id": "lab-00001",
    "sample_id": "sample-00001",
    "batch_id": "hb-00001",
    "tested_at": "2026-02-20T08:12:00Z",
    "metrics": {
        "moisture_pct": 12.3,
        "aflatoxin_ppb": 3.2
    },
    "report_url": "https://cdn.example/reports/hb-00001-report.pdf",
    "signed_hash": "sha256:abcdef..."
}
```

#### Response

```json
{
    "id": "report-uuid",
    "batch_id": "hb-00001",
    "grade": "GRADE_A",
    "passed": true,
    "verified": true,
    "tested_at": "2026-02-20T08:12:00+00:00"
}
```

#### Error Codes

| Code | Description |
|------|-------------|
| `LAB_NOT_FOUND` | Lab provider not registered |
| `BATCH_NOT_FOUND` | Harvest batch doesn't exist |
| `INVALID_BATCH_STATE_{status}` | Batch not in valid state for QC |

### Sample Management

**POST** `/api/qc/samples`

Create a new sample for QC testing.

**GET** `/api/qc/reports/{batch_id}`

Get all QC reports for a harvest batch.

### Lab Provider Management

**POST** `/api/qc/labs`

Register a new lab provider.

**GET** `/api/qc/labs`

List all registered lab providers.

**GET** `/api/qc/labs/{lab_id}`

Get a specific lab provider.

## Grade Evaluation Rules

Grade rules are configurable per commodity and stored in the database. The evaluation order is:

1. **GRADE_A** - Highest quality, meets all A thresholds
2. **GRADE_B** - Meets B thresholds but not A
3. **GRADE_C** - Meets C thresholds but not B
4. **REJECT** - Fails minimum thresholds

### Default Rules

| Commodity | Grade | Moisture | Aflatoxin |
|----------|-------|----------|-----------|
| Maize | A | ≤13.0% | ≤5 ppb |
| Maize | B | ≤14.0% | ≤10 ppb |
| Maize | C | ≤15.0% | ≤20 ppb |
| Wheat | A | ≤12.0% | Protein ≥10% |
| Wheat | B | ≤14.0% | Protein ≥8% |
| Coffee | A | ≤12.0% | Defects ≤5 |

## Signature Verification

Labs can be registered with a public key for signature verification:

1. Lab registers their public key (PEM format) with the system
2. When submitting results, lab includes a `signed_hash`
3. System verifies the hash using the lab's public key
4. If verification passes, `verified=true`; otherwise `verified=false`

### Hash Format

The signed hash should be computed as:
```
sha256:{hash}
```

Where hash is the SHA256 of the canonical JSON payload.

## Product Listing Validation

Before a product can be listed, referenced harvest batches must:

1. Be in `SEALED` or `QC_PASSED` status
2. Have a valid QC report (for commodities requiring lab tests)
3. Have `passed=true` in the QC report
4. Have `verified=true` if the commodity requires signature verification

### Error Codes

| Code | Description |
|------|-------------|
| `MISSING_SEAL` | Batch is not sealed |
| `QC_FAILED` | Batch failed QC |
| `MISSING_QC_REPORT` | No valid QC report found |
| `QC_UNVERIFIED` | Lab signature not verified |
| `CERT_EXPIRED` | Certification expired |

### Commodity Requirements

```python
COMMODITY_QC_REQUIREMENTS = {
    "maize": {"require_lab_test": True, "require_verified": False},
    "wheat": {"require_lab_test": True, "require_verified": False},
    "coffee": {"require_lab_test": True, "require_verified": True},
    "rice": {"require_lab_test": True, "require_verified": False},
}
```

## Running Tests

```bash
# Run all QC tests
pytest -q server/app/tests -k qc

# Run specific test file
pytest -q server/app/tests/test_qc_workflow.py
pytest -q server/app/tests/test_listing_qc_guard.py
```

## Database Migrations

After implementing the changes, run migrations:

```bash
alembic upgrade head
```

The migration creates the following tables:
- `lab_providers` - Registered lab providers
- `samples` - Sample collection records
- `batch_qc_reports` - QC test results
- `certifications` - Product certifications
- `qc_grade_rules` - Configurable grade thresholds

## Idempotency

The webhook endpoint is idempotent - posting the same payload twice will not create duplicate QC records. Idempotency is checked based on:
- Sample ID
- Lab ID  
- Tested at time (within 1 minute tolerance)
