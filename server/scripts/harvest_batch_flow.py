"""Quick smoke test script for harvest batch flow.

Usage (from repo root):
  docker-compose exec api python /app/scripts/harvest_batch_flow.py

This script uses the application's SessionLocal and HarvestBatchRepository to:
 - create a HarvestEvent
 - create a draft HarvestBatch
 - add a contribution linking the event to the batch
 - compute lineage hash
 - seal the batch
 - create a QC report (passed)
 - create a ProductBatch for the first product found (if any)
 - link the ProductBatch to the HarvestBatch

It prints results to stdout for inspection.

Note: Run with AUTH disabled or ensure the DB has required users referenced by farmer/aggregator IDs.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
import sys

from app.core.database import SessionLocal
from app.infrastructure.repositories.harvest_batch_repo import HarvestBatchRepository
from app.domain.harvest.entities import (
    HarvestEventCreate,
    HarvestBatchCreate,
    HarvestBatchContributionCreate,
    HarvestBatchSealRequest,
    BatchQCReportCreate,
)

from app.infrastructure.db.models.product import ProductORM
from app.infrastructure.db.models.inventory import ProductBatchORM


def main():
    db = SessionLocal()
    repo = HarvestBatchRepository(db)

    try:
        # 1) Create a harvest event
        event_payload = HarvestEventCreate(
            farm_id="FAR-00001",
            field_id=str(uuid4()),
            crop_cycle_id=None,
            collected_by="FAR-00001",
            harvested_at=datetime.now(timezone.utc),
            gross_weight_kg=100.5,
            moisture_pct=12.3,
            loss_kg=0,
            photos=None,
            weighbridge_receipt=None,
            location=None,
            notes="Smoke-test event"
        )

        event = repo.create_event(event_payload)
        print("Created HarvestEvent:", event.id)

        # 2) Create a draft batch
        batch_payload = HarvestBatchCreate(
            batch_code=f"SMOKE-{int(datetime.now().timestamp())}",
            aggregator_id="FAR-00001",
            notes="Smoke test batch",
            metadata={"test": True}
        )
        batch = repo.create_draft_batch(batch_payload)
        print("Created HarvestBatch:", batch.id, "code:", batch.batch_code)

        # 3) Add contribution
        contribution_payload = HarvestBatchContributionCreate(
            harvest_batch_id=UUID(str(batch.id)),
            harvest_event_id=UUID(str(event.id)),
            farmer_id="FAR-00001",
            contributed_weight_kg=100.5,
            reported_moisture_pct=12.3,
        )
        contribution = repo.add_contribution(str(batch.id), contribution_payload)
        print("Added contribution:", contribution.id)

        # 4) Compute lineage hash
        lineage_hash = repo.compute_lineage_hash(str(batch.id))
        print("Computed lineage hash:", lineage_hash)

        # 5) Seal the batch
        seal_req = HarvestBatchSealRequest(sealed_by="FAR-00001", seal_evidence={"note": "sealed by smoke test"})
        sealed = repo.seal_batch(str(batch.id), seal_req)
        print("Sealed batch status:", sealed.status, "sealed_at:", sealed.sealed_at, "lineage:", sealed.lineage_hash)

        # 6) Create a QC report (passed)
        qc_payload = BatchQCReportCreate(
            batch_id=UUID(str(batch.id)),
            lab_id="LAB-001",
            tested_at=datetime.now(timezone.utc),
            metrics={"moisture": 12.3},
            passed=True,
            report_url=None,
            signed_hash=None,
            notes="All good"
        )
        qc = repo.create_qc_report(qc_payload)
        print("Created QC report:", qc.id, "passed:", qc.passed)

        # 7) Create a product_batch for linking (use first product if exists)
        product = db.query(ProductORM).first()
        if not product:
            print("No product found in DB to create a ProductBatch. Creating a dummy ProductBatch with no product link.")
            # Create a standalone product batch (product_id must exist; use a synthetic product id)
            prod_batch = ProductBatchORM(
                id=str(uuid4()),
                product_id=str(uuid4()),
                batch_code=f"PB-{int(datetime.now().timestamp())}",
                total_quantity=100.5,
            )
            db.add(prod_batch)
            db.commit()
            db.refresh(prod_batch)
        else:
            prod_batch = ProductBatchORM(
                id=str(uuid4()),
                product_id=product.id,
                batch_code=f"PB-{int(datetime.now().timestamp())}",
                total_quantity=100.5,
            )
            db.add(prod_batch)
            db.commit()
            db.refresh(prod_batch)
            print("Created ProductBatch for product:", product.id)

        # 8) Link product batch to harvest batch (requires QC_PASSED)
        try:
            link = repo.link_product_batch_to_harvest_batch(prod_batch.id, str(batch.id), contribution_weight_kg=100.5)
            print("Linked product batch to harvest batch:", link.id)
        except Exception as e:
            print("Failed to link product batch to harvest batch:", e)

        # 9) Print audit trail
        audits = repo.get_audit_events("harvest_batch", str(batch.id))
        print("Audit events for batch:")
        for a in audits:
            print(" -", a.event_type, a.payload)

    except Exception as e:
        print("Error during smoke flow:", e)
    finally:
        db.close()


if __name__ == "__main__":
    main()
