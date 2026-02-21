This document provides a complete implementation plan to add the Aggregator concept, smallholder reconciliation and split settlement features to the FarmConnect platform. 

The project follows a Clean Architecture / DDD structure with strict boundaries:
domain/ → business rules, entities, policies
application/ → use‑cases and orchestration
infrastructure/ → database, repositories, ORM models
api/ → FastAPI routes and request/response schemas



## One-line summary
An Aggregator is a first-class actor/entity that collects harvest from many smallholders, creates sealed harvest batches, accepts/weighs material, reconciles source contributions to physical weighments, and manages split settlements (paying many smallholders from a single sale) while preserving provenance, audits and dispute-handling.

---

## Business intent and why it’s required
- Smallholders typically sell small quantities; marketplaces need an entity that consolidates supply into tradeable lots (scale).
- Aggregators must provide proof of origin for each unit sold (lineage) and be financially accountable to contributors.
- Without reconciliation and split settlements, payments are slow/error-prone and disputes are frequent.
- Implementing this properly supports trust, price discovery, and regulatory/certification traceability.

---

## Key roles & responsibilities
- Aggregator: collects, inspects, creates batches, seals batch(es), requests QC, packages product, lists product, receives sale proceeds, triggers split settlement to contributors.
- Smallholder (Farmer): provides harvest events and contributions; claims payment for their contribution.
- Marketplace/Platform: validates provenance, holds escrow, enforces settlement rules, provides audit, resolves disputes.
- Agronomist/Inspector: spot-checks weighments, validates quality.
- Admin/Manager: handles exceptions/large disputes and can override per policy (with audit).

---

## Core domain concepts (entities) — concrete proposals

1) Aggregator
- `aggregator_id` (uuid)
- `name`, `company_info`, `contact`, `kyc_status`, `metadata` (jsonb)
- `wallet_id` (fk to FinancialAccount or FarmWallet)
- `created_at`, `status` (ACTIVE/SUSPENDED)

2) AggregationGroup (optional)
- Groups many harvest_batches under a campaign/consignment
- `aggregation_id`, `aggregator_id`, `name`, `expected_total_kg`, `status`, `created_at`

3) HarvestBatch (already discussed) — add aggregator_id, acceptance_weighments, aggregated_weight_kg

4) HarvestBatchContribution (already discussed) — per-harvest-event contribution

5) AcceptanceWeighment (weighment records for a batch)
- `id`, `batch_id`, `weighment_time`, `weighbridge_id` (or location/device), `gross_weight_kg`, `tare_weight_kg`, `net_weight_kg`, `weigher_id`, `receipt_url/json`, `created_at`
- Allow multiple weighments (pickup, consolidation, packaging)

6) ReconciliationRecord (the reconciliation snapshot)
- `recon_id`, `batch_id`, `expected_total_kg` (sum of contributions), `measured_total_kg` (sum of acceptance weighments), `difference_kg`, `variance_pct`, `recon_status` (OK, WARNING, DISPUTE), `notes`, `created_at`, `created_by`

7) SettlementRule
- `rule_id`, `batch_id` or `aggregator_id` default rules, `split_method` (BY_WEIGHT, BY_VALUE, FIXED_RATE), `platform_fee_pct`, `aggregator_commission_pct`, `tax_details`, `rounded` config, `created_at`

8) SplitSettlement (per-contributor settlement record)
- `settlement_id`, `batch_id`, `contribution_id` (harvest_batch_contribution.id), `farmer_id`, `contributed_weight_kg`, `share_amount`, `currency`, `status` (PENDING/PAID/FAILED/ADJUSTED), `payout_reference`, `created_at`, `paid_at`

9) AggregatorSettlementSummary
- `summary_id`, `batch_id`, `aggregator_id`, `gross_sale_amount`, `total_platform_fee`, `total_commission`, `net_settlement_amount`, `payout_status`, `created_at`

10) AuditEvent (append-only) — extend to include settlement events (settlement_initiated, payment_made, refund_given)

---

## Typical lifecycle & when tables are affected

1. Harvest contributions recorded
- `harvest_events` INSERT (farmer)
- `harvest_batch_contributions` INSERT (aggregator adds contributions to a draft batch)

2. Aggregator accepts/consolidates and records acceptance weighments
- `acceptance_weighments` INSERT(s) (at collection points/weighbridge)

3. Reconciliation occurs (automatic or manual)
- Platform computes `expected_total_kg` = SUM(contributed_weight_kg)
- Platform computes `measured_total_kg` = SUM(net_weight_kg) from weighments
- Create `reconciliation_record` (INSERT) with difference and status
- If variance exceeds threshold, set status `DISPUTE` and create `dispute_event`

4. Seal batch once acceptable
- `harvest_batches` UPDATE status -> SEALED (lineage hash set)
- Contributions become immutable (DB trigger)

5. Batch sold -> sale proceeds received into Escrow
- `orders` / `escrows` updated (existing tables)

6. Settlement planned & computed
- Platform or aggregator invokes settlement process:
  - Create `aggregator_settlement_summary` (INSERT)
  - For each `harvest_batch_contribution` create `split_settlement` entries (INSERT)
  - Optionally insert `payment_instruction` and call payment provider/escrow to disburse

7. Payouts executed
- Update `split_settlement.status` -> PAID or FAILED, write `payout_reference`
- Update `financial_account` or `farm_wallet` balances

8. Post-settlement reconciliation
- Reconcile provider receipts with `split_settlement` and create `audit_event` records

---

## Reconciliation details: algorithms & rules

- Expected_total = sum(contributed_weight_kg (contribution records)). This reflects contributions declared by farmers.
- Measured_total = sum(net_weight_kg across weighments). This is the physically measured mass at aggregator points.
- Difference = Measured_total - Expected_total
  - If difference within tolerance (e.g., ±2%): mark `OK`.
  - If positive (measured > expected): either pro-rate extra gain to contributors or aggregator keeps per policy.
  - If negative (measured < expected): pro-rate loss to all contributors, or attribute losses by time/location if evidence exists.
- Rounding & minimum payout:
  - Apply rounding rules to currency amounts to avoid fractional cents. Define rounding strategy (round half up/truncate).
  - If contributor’s computed share < min_payout_threshold, the platform can:
    - Accumulate into a “micro-payout ledger” until threshold reached; OR
    - Pay out immediately with payment fees deducted.
- Fees & deductions:
  - Platform fee, aggregator commission, transport/handling deductions, tax withholding.
- Share calculation variants:
  - BY_WEIGHT: share_amount = (contributed_weight / measured_total) * (net_sale_amount - platform_fees - aggregator_commission)
  - BY_VALUE: if contributions tracked with quality grade and price per kg per grade, allocate by contribution value (weight * grade_price)
  - FIXED_RATE: pay fixed rate per kg to contributors, aggregator keeps residual

---

## State machine suggestions

Batch settlement state:
- DRAFT -> SEALED -> LISTED -> SOLD -> SETTLEMENT_PENDING -> SETTLEMENT_IN_PROGRESS -> SETTLED -> SETTLEMENT_DISPUTE -> RECONCILED -> ARCHIVED

SplitSettlement states:
- PENDING -> PREPARED -> PAYMENT_SENT -> PAID -> FAILED -> ADJUSTED -> RECLAIMED

Reconciliation statuses:
- OK -> WARNING -> DISPUTE -> RESOLVED

---

## Critical invariants (enforce consistently)

- Sum of `split_settlement.share_amount` + `total_platform_fees` + `aggregator_commission` == `gross_sale_amount` (allow rounding deltas within config limit)
- Sum of `split_settlement.contributed_weight_kg` == SUM contributions for batch (unless corrections recorded; corrections create new records)
- No `split_settlement` is created before the batch is SEALED and sale proceeds are recorded (use a transaction locking).
- Once a `harvest_batch` is SEALED, contributions cannot be altered; reconciliation must create separate adjustment records (no retroactive changes).
- Escrow release uses batch/listing IDs for traceability (link every payout to sale id and batch ids).

---

## API & service sketch (endpoints & service methods)

APIs (examples)
- POST /api/aggregators — create aggregator and KYC metadata
- GET /api/aggregators/{id} — get aggregator profile
- POST /api/aggregators/{id}/batches — create batch (DRAFT)
- POST /api/batches/{batch_id}/contributions — add contribution
- POST /api/batches/{batch_id}/weighments — record weighbridge weighment
- POST /api/batches/{batch_id}/reconcile — run reconciliation (or scheduled job)
- POST /api/batches/{batch_id}/seal — seal batch (aggregator only)
- POST /api/batches/{batch_id}/settle — compute settlement (admin/aggregator)
- GET /api/settlements/{settlement_id} — check settlement status
- Webhook: POST /api/payments/webhook — receive payment provider results to set split settlement statuses

Service responsibilities (server-side)
- `ReconciliationService.reconcile(batch_id)` — compute diffs, flag disputes, create `reconciliation_record`
- `SettlementService.prepare_settlement(batch_id, settlement_rule)` — compute split amounts, create `aggregator_settlement_summary`, create `split_settlement` entries
- `PaymentGatewayAdapter.execute_payouts(settlement_summary_id)` — send batched payouts (or per-contributor) to payment provider using farm payout details
- `SettlementService.finalize_settlement(summary_id, provider_receipts)` — mark `split_settlement` as PAID/FAILED, update wallets and write audit events

---

## Auditing & dispute workflow

- Always write an `audit_event` when reconciliations or settlements start/finish and when status changes.
- For disputes:
  - Create `dispute` record referencing the reconciliation or settlement
  - Allow evidence upload (weighbridge receipts, photos, witness attestation)
  - Auto-flag old disputes for manual review by Admin
- Support partial manual adjustments:
  - Admin adjustments should create `adjustment` audit records; adjustments should not edit original sealed contributions — instead append new `split_settlement` adjustments and mark original as superseded.

---

## Edge cases & pragmatic rules for smallholders

- Late or missing contributions: if a farmer claims contribution but has no verification, aggregator can accept with note; to avoid fraud require at least photo+weighbridge receipt to count.
- Missing bank/payment details for some smallholders: hold their share in a `farm_wallet` until they provide payout details.
- Micro-payouts: optionally aggregate micro payments until threshold to reduce transaction costs.
- Currency & exchange: support multi-currency sales and convert per configured exchange rates at settlement time; store exchange rate used.
- Liability for spoilage in aggregation chain: define contractual rules (e.g., aggregator responsible after acceptance weighment).
- Rounding remainders: platform can credit rounding remainder to aggregator or platform by policy — store rounding policy and record in audit.

---

## Data schema snippets (concise)

Add these tables (example columns only):

- aggregators
  - id, name, kyc_status, wallet_id, metadata, created_at

- acceptance_weighments
  - id, batch_id, weighbridge_id, gross_weight_kg, tare_kg, net_weight_kg, receipt_url, weigher_id, created_at

- reconciliation_records
  - id, batch_id, expected_total_kg, measured_total_kg, difference_kg, variance_pct, recon_status, notes, created_by, created_at

- settlement_rules
  - id, aggregator_id, split_method, platform_fee_pct, aggregator_commission_pct, min_payout_threshold, rounding_policy_json

- split_settlements
  - id, batch_id, contribution_id, farmer_id, share_amount, currency, status, payout_details_id, payout_reference, created_at, paid_at

- aggregator_settlement_summaries
  - id, batch_id, aggregator_id, gross_sale_amount, total_fees, net_to_distribute, created_at, status

---

## Implementation checklist (prioritized)

High priority (foundation)
1. Add `aggregators` table + model and role mapping (AGGREGATOR role privileges).
2. Link `harvest_batches.aggregator_id` (migration if not present).
3. Add `acceptance_weighments` and `reconciliation_records` tables + repositories.
4. Build `ReconciliationService` to compute expected vs measured, set `recon_status`, and create `dispute` when threshold exceeded.
5. Add `settlement_rules` table and `split_settlements` + `aggregator_settlement_summaries`.
6. Implement `SettlementService.prepare_settlement()` and unit tests for BY_WEIGHT, BY_VALUE and rounding.

Medium priority (payments & UX)
7. Integrate with escrow/payment provider adapter (mock first, then real).
8. Add UI flows / admin endpoints for dispute resolution and manual adjustments.
9. Add micro-payout accumulation and payout scheduling.

Low/longer term
10. Add flexible contract templates to specify aggregator liability and dispute SLA.
11. Add reporting (per-aggregator KPIs, payout times, reconciliation variance).
12. Add extended fraud detection (duplicate harvest events, suspicious weighment patterns).

---

## Example settlement transaction (pseudocode)
This ensures atomicity and correct balances:
```
BEGIN TRANSACTION
  SELECT batch FOR UPDATE
  validate batch.status == 'SOLD' and not already settled
  gross_sale_amount = get_sale_amount_for_batch(batch_id)
  total_platform_fee = gross_sale_amount * platform_fee_pct
  aggregator_commission = gross_sale_amount * aggregator_commission_pct
  net_pool = gross_sale_amount - total_platform_fee - aggregator_commission

  measured_total = SELECT SUM(net_weight_kg) FROM acceptance_weighments WHERE batch_id = X
  for each contribution c:
    proportion = c.contributed_weight_kg / measured_total
    share = round(net_pool * proportion, currency_precision)
    create split_settlement(c.id, share, status='PENDING')
    sum_allocated += share

  rounding_remainder = net_pool - sum_allocated
  handle rounding_remainder per policy (credit aggregator or platform)
  create aggregator_settlement_summary(gross_sale_amount, total_platform_fee, aggregator_commission, net_pool, status='PAYMENT_SCHEDULED')
COMMIT

# Then call payment provider off-transaction to execute payouts,
# and update split_settlement rows to PAID/FAILED and summary status accordingly.
```

---

## Tests / acceptance you should add
- Reconciliation happy path: contributions sum equals measured weight -> recon_status OK.
- Reconciliation discrepancy -> recon_status DISPUTE and block sealing or require admin.
- Settlement BY_WEIGHT: check allocations sum + fees == gross_sale_amount (with rounding policy).
- Payment failure handling: if provider fails for some farmers, mark their settlement FAILED and leave the rest PAID.
- Immutability: sealing a batch prevents changes to contribution records and changes in reconciliation must produce an audit record.

---

## Operational & policy suggestions
- Define tolerances per commodity (percent variance allowed). Keep these configurable as `reconciliation_thresholds` per commodity/region.
- Require weighbridge receipts and at least one geo-tagged photo per acceptance weighment.
- For high-value or regulated commodities, require a second independent weighment or supervisor sign-off.
- Store all evidence hashes and receipt pdf URLs; use them in dispute resolution.

---
================================
================================
## Goals

- Treat Aggregator as a first-class actor that collects harvest from smallholders and forms saleable lots.
- Provide robust reconciliation between declared contributions and physical weighments.
- Implement deterministic, auditable split settlement flows to pay contributors from a single sale/payout.
- Preserve traceability and immutability (sealed harvest batches remain immutable; adjustments create new records).
- Provide APIs, services, and tests to validate correctness and support production rollout.

## High-level flow

1. Farmers create `harvest_event` records (existing or added) describing field-level harvests.
2. Aggregator creates a `harvest_batch` (DRAFT) and adds `harvest_batch_contributions` (links to harvest events).
3. Aggregator records `acceptance_weighments` (weighbridge receipts) for consolidation points.
4. System performs `reconciliation` (expected = sum(contributions) vs measured = sum(weighments)).
5. If within tolerance: batch can be SEALED; else create `dispute` or `RECONCILE_REQUIRED` path.
6. After sale, `SettlementService` computes `split_settlements` (BY_WEIGHT / BY_VALUE / FIXED_RATE) and creates `aggregator_settlement_summary`.
7. Payments executed via payment provider; settlement rows updated to PAID/FAILED. All actions generate append-only audit events.

## Acceptance criteria

- Aggregators can be created and associated with sealed harvest batches.
- Reconciliation computes and persists expected/measured totals and statuses (OK / WARNING / DISPUTE).
- Settlement computes per-contributor shares with rounding policy; invariants hold (sum checks within tolerance).
- Sealed batches cannot have contributions modified (DB trigger + repo guard).
- Unit tests and integration tests covering reconciliation and settlement happy/failure flows.

## Data model (DB tables and key columns)

Add these tables via Alembic migrations (naming and styles follow existing migrations):

1. `aggregators`
- id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
- name: text
- company_info: jsonb
- contact: jsonb
- kyc_status: enum('PENDING','VERIFIED','REJECTED')
- wallet_id: string (fk to financial accounts if present)
- metadata: jsonb
- created_at: timestamptz

2. `acceptance_weighments`
- id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
- batch_id: uuid REFERENCES harvest_batches(id)
- weighbridge_id: text
- gross_weight_kg: float
- tare_weight_kg: float
- net_weight_kg: float
- receipt_url: text (signed URL or object key)
- weigher_id: string (user id)
- recorded_at: timestamptz
- created_at: timestamptz

3. `reconciliation_records`
- id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
- batch_id: uuid REFERENCES harvest_batches(id)
- expected_total_kg: float
- measured_total_kg: float
- difference_kg: float
- variance_pct: float
- recon_status: enum('OK','WARNING','DISPUTE')
- notes: text
- created_by: string
- created_at: timestamptz

4. `settlement_rules`
- id: uuid
- aggregator_id: uuid NULLABLE
- split_method: enum('BY_WEIGHT','BY_VALUE','FIXED_RATE')
- platform_fee_pct: float
- aggregator_commission_pct: float
- min_payout_threshold: float
- rounding_policy jsonb (e.g. {"precision":2,"mode":"ROUND_HALF_UP","remainder_to":"AGGREGATOR"})
- created_at

5. `aggregator_settlement_summaries`
- id: uuid
- batch_id: uuid REFERENCES harvest_batches(id)
- aggregator_id: uuid REFERENCES aggregators(id)
- gross_sale_amount: float
- total_platform_fee: float
- total_commission: float
- net_to_distribute: float
- rounding_adjustment: float
- currency: text
- status: enum('PENDING','IN_PROGRESS','PAID','FAILED')
- created_at

6. `split_settlements`
- id: uuid
- settlement_summary_id: uuid REFERENCES aggregator_settlement_summaries(id)
- contribution_id: uuid REFERENCES harvest_batch_contributions(id)
- farmer_id: uuid
- contributed_weight_kg: float
- share_amount: float
- currency: text
- status: enum('PENDING','PREPARED','PAYMENT_SENT','PAID','FAILED','ADJUSTED')
- payout_reference: text
- created_at, paid_at

7. `reconciliation_disputes` (optional)
- id: uuid
- recon_id: uuid REFERENCES reconciliation_records(id)
- raised_by: user id
- description, evidence jsonb
- status: enum('OPEN','RESOLVED','REJECTED')
- created_at

Add indexes on `batch_id`, `aggregator_id`, and `contribution_id` where applicable.

## Domain models and ORM

Create domain dataclasses under `server/app/domain/aggregator/models.py` following `inventory.py` style:
- Aggregator
- AcceptanceWeighment
- ReconciliationRecord
- SettlementRule
- AggregatorSettlementSummary
- SplitSettlement

Create ORM models under `server/app/infrastructure/db/models/aggregator.py` using `Base` and `mapped_column` patterns similar to `inventory.py`:
- AggregatorORM
- AcceptanceWeighmentORM
- ReconciliationRecordORM
- SettlementRuleORM
- AggregatorSettlementSummaryORM
- SplitSettlementORM

Use SAEnum with create_type=False for new enums and create the Postgres enum types in the migration.

## Repositories

Add repository classes in `server/app/infrastructure/repositories/aggregator_repo.py`:
- AggregatorRepository: CRUD aggregator profiles.
- AcceptanceWeighmentRepository: append weighments, query by batch.
- ReconciliationRepository: persist reconciliation snapshots.
- SettlementRepository: create summaries and split_settlements, update statuses.

Repository responsibilities:
- Use DB sessions injected per request.
- Provide atomic methods for creating settlement summaries and split entries inside transactions.

## Services

Create application services under `server/app/application/services`:

- `ReconciliationService`
  - reconcile(batch_id) -> computes expected_total, measured_total, difference, variance, writes ReconciliationRecord and returns recon_status.
  - validation rules: uses commodity-specific tolerance config (DB or config file).

- `SettlementService`
  - prepare_settlement(batch_id, gross_sale_amount, currency, settlement_rule_id=None)
    - Locks batch row SELECT FOR UPDATE
    - Validates batch.status == 'SOLD' and no prior settlement
    - Computes platform_fee and aggregator_commission
    - Computes measured_total from AcceptanceWeighment (or contributions sum if weighments missing)
    - For each contribution, compute share based on split_method
    - Apply rounding policy, compute rounding_adjustment and record who receives remainder
    - Create AggregatorSettlementSummary and SplitSettlement rows (all inside DB transaction)
  - execute_payouts(summary_id)
    - Off-transaction: call PaymentGatewayAdapter to execute payouts, update split_settlements statuses and payout_reference

- `PaymentGatewayAdapter` (interface)
  - execute_batch_payouts(list_of_payout_instructions) -> provider receipts
  - Implementation: mock adapter for tests; real adapters for production (M-Pesa, bank APIs)

## API Endpoints

Add routes under `server/app/api/aggregator/routes.py` and wire into FastAPI app:

- POST /api/aggregators — create aggregator
- GET /api/aggregators/{id}
- POST /api/batches/{batch_id}/weighments — create acceptance weighment
- POST /api/batches/{batch_id}/reconcile — manual reconciliation trigger (calls ReconciliationService)
- POST /api/batches/{batch_id}/seal — seal batch (existing flow should be extended to validate reconciled status)
- POST /api/batches/{batch_id}/settlement/prepare — prepare settlement (returns summary id)
- POST /api/settlements/{summary_id}/payouts — execute payouts via PaymentGatewayAdapter
- GET /api/settlements/{summary_id} — status and splits

Authentication & Authorization:
- Only AGGREGATOR or ADMIN may create weighments and call reconcile/prepare settlement for batches they control.

## Transactional considerations and pseudocode

Reconcile (atomic read/write):

```
def reconcile(batch_id, user_id):
    with db.session.begin():
        batch = db.session.query(HarvestBatchORM).filter_by(id=batch_id).with_for_update().one()
        contributions = db.session.query(HarvestBatchContributionORM).filter_by(harvest_batch_id=batch_id).all()
        expected = sum(c.contributed_weight_kg for c in contributions)
        weighments = db.session.query(AcceptanceWeighmentORM).filter_by(batch_id=batch_id).all()
        measured = sum(w.net_weight_kg for w in weighments)
        diff = measured - expected
        variance = 0 if expected == 0 else diff / expected * 100
        status = compute_status(variance, commodity_tolerance)
        recon = ReconciliationRecordORM(batch_id=batch_id, expected_total_kg=expected, measured_total_kg=measured, difference_kg=diff, variance_pct=variance, recon_status=status, created_by=user_id)
        db.session.add(recon)
    return recon
```

Prepare settlement (atomic creation):

```
def prepare_settlement(batch_id, gross_sale_amount, currency, rule_id):
    with db.session.begin():
        batch = db.session.query(HarvestBatchORM).filter_by(id=batch_id).with_for_update().one()
        assert batch.status == 'SOLD' and not already_settled(batch_id)
        measured_total = get_measured_total(batch_id)
        rule = load_rule(rule_id or default)
        platform_fee = gross_sale_amount * rule.platform_fee_pct / 100.0
        aggregator_comm = gross_sale_amount * rule.aggregator_commission_pct / 100.0
        net_pool = gross_sale_amount - platform_fee - aggregator_comm
        summary = AggregatorSettlementSummaryORM(batch_id=batch_id, aggregator_id=batch.aggregator_id, gross_sale_amount=gross_sale_amount, total_platform_fee=platform_fee, total_commission=aggregator_comm, net_to_distribute=net_pool, currency=currency, status='PENDING')
        db.session.add(summary); db.session.flush()
        split_rows = []
        for c in contributions:
            if rule.split_method == 'BY_WEIGHT':
                proportion = c.contributed_weight_kg / measured_total
                share = round(net_pool * proportion, currency_precision)
            # other methods...
            split = SplitSettlementORM(settlement_summary_id=summary.id, contribution_id=c.id, farmer_id=c.farmer_id, contributed_weight_kg=c.contributed_weight_kg, share_amount=share, currency=currency, status='PENDING')
            db.session.add(split)
            split_rows.append(split)
        # handle rounding remainder per policy
    return summary.id
```

Payments executed outside transaction; update rows with provider receipts and create audit events.

## Immutability & invariants

- Once `harvest_batches.status == 'SEALED'`, contributions cannot be modified; enforce via DB trigger and repository checks.
- Invariant: sum(split_settlements.share_amount) + total_platform_fee + total_commission == gross_sale_amount ± rounding_tolerance
- Invariant: sum(contributed_weight_kg) == expected_total recorded in reconciliation snapshot (unless corrected with explicit adjustments)

## DB trigger suggestion (Postgres PL/pgSQL)

Create trigger on `harvest_batch_contributions` to block INSERT/UPDATE/DELETE when parent batch is SEALED, similar to the pattern used for harvest immutability. Add triggers in the Alembic migration.

## Tests to implement

- Unit tests (pytest)
  - reconciliation_happy_path: contributions match weighments → recon_status == OK
  - reconciliation_discrepancy: measured < expected by > threshold → recon_status == DISPUTE
  - prepare_settlement_by_weight: shares sum and rounding behavior
  - immutability_after_seal: adding/editing contribution fails with error
  - payout_execution_success and partial failure handling

- Integration tests
  - end-to-end: farmer creates harvest → aggregator forms batch → weighments → reconcile → seal → simulate sale → prepare settlement → execute payouts (mock payment adapter)

## Monitoring, metrics & KPIs

- Reconciliation variance distribution (histogram)
- Number and % of batches in DISPUTE
- Average time from sale to payout (target < 7 days)
- Settlement success rate (paid vs attempted)
- Micro-payout accumulation size and payout counts

## Security & anti-fraud controls

- Require weighbridge receipt (signed or verified URL) and geo-tagged photos for acceptance weighments.
- Log audit events for every reconciliation and settlement action. Store hashes/urls for evidence.
- Rate-limit aggregator actions and require KYC for aggregators above value thresholds.
- Random QC spot-checks: if batch variance high or aggregator variance patterns suspicious, schedule lab sampling and manual review.

## Offline and operational considerations

- Accept harvest_event creation offline with client-generated idempotency keys. Reconciliation and sealing must be server-only operations requiring connectivity.
- For micro-payouts, implement accumulation ledger per farmer to reduce payment provider fees; expose endpoints to view pending balance.

## Rollout plan (phased)

1. Schema & models: add migrations, domain classes and ORMs. (1 week)
2. Repositories & ReconciliationService with unit tests. (1 week)
3. SettlementService (prepare only) and tests for BY_WEIGHT. (1 week)
4. API endpoints (weighments, reconcile, prepare_settlement) and test harness. (1 week)
5. Integrate payment adapter mock and end-to-end test; add audit events. (1 week)
6. Add production payment adapter, KYC workflow, and monitoring dashboards. (2–4 weeks)

Total estimated MVP: 4–6 weeks (one engineer), end-to-end production-ready with payment provider integration 8–12 weeks.

## Implementation checklist (files to add/edit)

- Alembic migration: `server/app/alembic/versions/00XX_add_aggregator_and_settlement.py`
- Domain dataclasses: `server/app/domain/aggregator/models.py`
- ORM models: `server/app/infrastructure/db/models/aggregator.py`
- Repositories: `server/app/infrastructure/repositories/aggregator_repo.py`
- Services: `server/app/application/services/reconciliation_service.py`, `server/app/application/services/settlement_service.py`
- API routes: `server/app/api/aggregator/routes.py`
- Tests: `server/app/tests/test_reconciliation.py`, `server/app/tests/test_settlement.py`, `server/app/tests/test_immutability.py`

## Example JSON messages

Reconcile request (client):
```
POST /api/batches/{batch_id}/reconcile
{ "actor_id": "user-123" }
```

Prepare settlement request (client):
```
POST /api/batches/{batch_id}/settlement/prepare
{
  "gross_sale_amount": 10000.00,
  "currency": "USD",
  "settlement_rule_id": "optional-rule-id"
}
```

Prepare settlement response:
```
{ "settlement_summary_id": "uuid", "status": "PENDING", "total_splits": 23 }
```

## Next steps (what I can implement now)

Tell me which of the following you want me to create first and I will implement it with code, migration and tests:

1. Alembic migration + ORM models + domain dataclasses (foundation)
2. `ReconciliationService` + Repositories + unit tests
3. `SettlementService.prepare_settlement()` + SplitSettlement creation + tests for BY_WEIGHT and rounding
4. API endpoints for weighments, reconcile, prepare settlement and end-to-end integration tests (mock payment adapter)

Pick a number and I will start coding and run tests locally.
