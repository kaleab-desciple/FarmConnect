"""Background worker that activates products when their source harvest batch passes QC.

This worker polls for harvest batches in QC_PASSED state and activates any
products whose metadata references the batch but are still inactive. Activation
includes creating a ProductBatch, linking it to the harvest batch, appending an
InventoryMovement (stock-in), and marking the product active.

The worker is intentionally conservative and idempotent: it only activates
products that are currently inactive and whose metadata.harvest_batch_id matches
the passed batch. It commits changes per-product to avoid long transactions.
"""
"""from __future__ import annotations

import asyncio
import logging
from decimal import Decimal
from typing import Optional

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


def _process_once() -> None:
    # Synchronous processing pass: find QC_PASSED batches and activate products.
    from app.infrastructure.db.models.harvest import HarvestBatchORM
    from app.infrastructure.db.models.product import ProductORM
    from app.infrastructure.repositories.product_repo import ProductRepository
    from app.infrastructure.repositories.harvest_batch_repo import HarvestBatchRepository
    from app.infrastructure.repositories.inventory_repo import ProductBatchRepository, InventoryMovementRepository
    from app.domain.products.inventory import ProductBatch as DomainProductBatch, InventoryMovement
    from app.domain.common.enums import InventoryMovementType

    db = SessionLocal()
    try:
        # Load all sealed/passed batches
        batches = db.query(HarvestBatchORM).filter(HarvestBatchORM.status == 'QC_PASSED').all()

        prod_repo = ProductRepository(db)
        hb_repo = HarvestBatchRepository(db)
        pb_repo = ProductBatchRepository(db)
        inv_repo = InventoryMovementRepository(db)

        for batch in batches:
            try:
                # Find products that reference this batch in metadata and are inactive
                products = db.query(ProductORM).filter(ProductORM.deleted_at.is_(None)).all()
                for p in products:
                    metadata = getattr(p, 'metadata_', None) or {}
                    if not metadata:
                        continue
                    if metadata.get('harvest_batch_id') != batch.id:
                        continue
                    if p.is_active:
                        # already active
                        continue

                    logger.info("Activating product %s for harvest batch %s", p.id, batch.id)

                    # Load domain product, flip active flag and save
                    domain_product = prod_repo.get_by_id(p.id)
                    if not domain_product:
                        logger.warning("Domain product not found for ORM id %s", p.id)
                        continue

                    domain_product.is_active = True
                    saved = prod_repo.save(domain_product)

                    # Create a ProductBatch for inventory
                    total_q = Decimal(str(p.total_quantity or 0))
                    pb = DomainProductBatch(
                        product_id=p.id,
                        batch_code=f"PB-{str(p.id)[:8]}",
                        total_quantity=total_q,
                        harvest_date=batch.sealed_at.date() if batch.sealed_at else None,
                        expiry_date=None,
                        quality_grade=p.quality_grade,
                    )
                    saved_pb = pb_repo.save(pb)

                    # Link product batch to harvest batch (may raise if business rules block it)
                    try:
                        hb_repo.link_product_batch_to_harvest_batch(str(saved_pb.id), batch.id, contribution_weight_kg=float(saved_pb.total_quantity))
                    except Exception as e:
                        logger.exception("Failed linking product batch %s to harvest batch %s: %s", saved_pb.id, batch.id, e)

                    # Append an inventory movement (stock in)
                    movement = InventoryMovement(
                        product_id=p.id,
                        movement_type=InventoryMovementType.STOCK_IN,
                        quantity=total_q,
                        reference_type="PRODUCT_BATCH_CREATION",
                        reference_id=str(saved_pb.id),
                        id=None,
                        batch_id=str(saved_pb.id),
                        notes="Activated from QC passed harvest batch",
                        created_by="system",
                    )
                    try:
                        inv_repo.append(movement)
                    except Exception:
                        logger.exception("Failed to append inventory movement for product %s", p.id)

                    # Commit per-product to keep transactions small
                    db.commit()

            except Exception:
                logger.exception("Error processing batch %s", batch.id)

    finally:
        db.close()


async def _loop(poll_interval: float = 5.0) -> None:
    # Async loop that periodically runs the synchronous processing pass.
    while True:
        try:
            await asyncio.to_thread(_process_once)
        except Exception:
            logger.exception("Unhandled error in QC activation worker")
        await asyncio.sleep(poll_interval)


async def start_worker(app) -> None:
    # Start the background QC activation worker and attach task to app.state.
    if getattr(app.state, 'qc_worker_task', None):
        # already running
        return

    task = asyncio.create_task(_loop())
    app.state.qc_worker_task = task
    logger.info("QC activation worker started")


async def stop_worker(app) -> None:
    # Stop the background QC activation worker if running.
    task: Optional[asyncio.Task] = getattr(app.state, 'qc_worker_task', None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        logger.info("QC activation worker stopped")
"""