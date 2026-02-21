# Aggregator Reconciliation & Settlement API Documentation

This module provides endpoints for Aggregator management, Smallholder Reconciliation, and Split Settlement in the FarmConnect system.

## Overview

The Aggregator Settlement workflow enables collection centers to:
- Manage aggregator entities (collection centers)
- Record weighments when smallholders deliver harvest
- Reconcile farmer-declared vs aggregator-measured quantities
- Calculate and process split settlements for smallholders based on configurable rules

## Endpoints

### Aggregator Management

**POST** `/api/v1/aggregator/aggregators`

Create a new aggregator (collection center).

```json
{
    "name": "Kalki Collection Center",
    "company_info": {
        "registration_number": "RC-123456",
        "founded_year": 2020
    },
    "contact": {
        "phone": "+251911234567",
        "email": "info@kalki.com"
    },
    "wallet_id": "wallet-uuid"
}
```

**GET** `/api/v1/aggregator/aggregators`

List all aggregators.

**GET** `/api/v1/aggregator/aggregators/{aggregator_id}`

Get a specific aggregator.

**PATCH** `/api/v1/aggregator/aggregators/{aggregator_id}`

Update an aggregator.

---

### Weighment Recording

**POST** `/api/v1/aggregator/weighments`

Record a weighment when a smallholder delivers harvest to the aggregator.

```json
{
    "batch_id": "harvest-batch-uuid",
    "gross_weight_kg": 500.0,
    "tare_weight_kg": 25.0,
    "weigher_id": "user-uuid",
    "weighbridge_id": "WB-001",
    "receipt_url": "https://cdn.example.com/receipts/r-001.pdf",
    "location": {
        "lat": 9.032,
        "lon": 38.746
    }
}
```

**GET** `/api/v1/aggregator/batches/{batch_id}/weighments`

Get all weighments for a specific batch.

---

### Reconciliation

**POST** `/api/v1/aggregator/batches/{batch_id}/reconcile`

Reconcile a batch: compare farmer-declared quantity vs aggregator-measured quantity.

The system calculates:
- Expected total weight (from harvest batch contributions)
- Measured total weight (from acceptance weighments)
- Difference and variance percentage

Variance status determination:
- **OK**: Variance ≤ 2%
- **WARNING**: 2% < Variance ≤ 5%
- **DISPUTE**: Variance > 5%

**GET** `/api/v1/aggregator/batches/{batch_id}/reconciliation`

Get all reconciliation records for a batch.

---

### Settlement Rules

**POST** `/api/v1/aggregator/settlement-rules`

Create a settlement rule for splitting payments among smallholders.

```json
{
    "aggregator_id": "aggregator-uuid",
    "name": "Standard Weight-Based Split",
    "split_method": "BY_WEIGHT",
    "platform_fee_pct": 5.0,
    "aggregator_commission_pct": 10.0,
    "min_payout_threshold": 10.0,
    "is_default": true
}
```

Split Methods:
- `BY_WEIGHT`: Proportional by net weight delivered
- `BY_VALUE`: Proportional by crop value (weight × quality-adjusted price)
- `FIXED_RATE`: Fixed rate per kg regardless of weight

**GET** `/api/v1/aggregator/aggregators/{aggregator_id}/settlement-rules`

Get all settlement rules for an aggregator.

---

### Settlement Processing

**POST** `/api/v1/aggregator/settlements/prepare`

Prepare settlement for a batch after sale.

```json
{
    "batch_id": "harvest-batch-uuid",
    "aggregator_id": "aggregator-uuid",
    "gross_sale_amount": 50000.00,
    "rule_id": "settlement-rule-uuid"
}
```

The system calculates:
- Platform fee (percentage of gross)
- Aggregator commission (percentage of gross)
- Net amount to distribute
- Individual smallholder shares based on their contribution weight

**GET** `/api/v1/aggregator/settlements/{summary_id}`

Get settlement summary with all split settlements.

**PATCH** `/api/v1/aggregator/settlements/{split_id}/status`

Update split settlement payment status.

```json
{
    "status": "PAID",
    "payout_reference": "TXN-123456"
}
```

Status values: `PENDING`, `PREPARED`, `PAYMENT_SENT`, `PAID`, `FAILED`, `ADJUSTED`

---

### Farmer Settlements

**GET** `/api/v1/aggregator/farmers/{farmer_id}/settlements`

Get all settlement records for a specific farmer.

---

## Workflow

```
Smallholder Delivers Harvest
           │
           ▼
    Record Weighment
           │
           ▼
    Batch Sealed & Sold
           │
           ▼
    Run Reconciliation
    (Compare declared vs measured)
           │
           ▼
    Prepare Settlement
    (Calculate fees & splits)
           │
           ▼
    Process Payments
    (Per smallholder share)
```

## Variance Tolerance

The reconciliation system handles variance between farmer-declared and aggregator-measured quantities:

| Variance | Status | Action |
|----------|--------|--------|
| ≤ 2% | OK | Proceed normally |
| 2-5% | WARNING | Review and approve |
| > 5% | DISPUTE | Manual intervention required |

## Settlement Calculations

For a batch sold at $50,000 with BY_WEIGHT method:

1. **Calculate Fees**:
   - Platform fee: $50,000 × 5% = $2,500
   - Aggregator commission: $50,000 × 10% = $5,000

2. **Net to Distribute**:
   - $50,000 - $2,500 - $5,000 = $42,500

3. **Split Among Smallholders** (by weight):
   - Smallholder A: 500kg (25%) → $10,625
   - Smallholder B: 1,000kg (50%) → $21,250
   - Smallholder C: 500kg (25%) → $10,625

## Running Tests

```bash
# Run all aggregator-related tests
pytest -q server/app/tests -k aggregator

# Run settlement-specific tests
pytest -q server/app/tests -k settlement
```

## Database Migrations

After implementing the changes, run migrations:

```bash
alembic upgrade head
```

The migration creates the following tables:
- `aggregators` - Collection center entities
- `acceptance_weighments` - Weight recordings
- `reconciliation_records` - Variance records
- `settlement_rules` - Split payment rules
- `aggregator_settlement_summaries` - Batch settlement summaries
- `split_settlements` - Individual smallholder payments

Also adds columns to `harvest_batches`:
- `aggregator_id` - Reference to aggregator
- `settlement_state` - Batch settlement state

## Error Codes

| Code | Description |
|------|-------------|
| `AGGREGATOR_NOT_FOUND` | Aggregator not found |
| `BATCH_NOT_FOUND` | Harvest batch doesn't exist |
| `INVALID_BATCH_STATE` | Batch not in valid state |
| `NO_SETTLEMENT_RULE` | No settlement rule configured |
| `INSUFFICIENT_WEIGHMENTS` | No weighments recorded for batch |
| `SETTLEMENT_ALREADY_EXISTS` | Settlement already prepared |
