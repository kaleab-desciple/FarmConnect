"""Harvest API routes."""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth.dependencies import require_auth, require_permission
from app.domain.farm.entities import Harvest, HarvestCreate, HarvestUpdate
from app.application.harvest.service import HarvestService
from app.api.v1.harvest.schemas import ProductConversionResponse

router = APIRouter(prefix="/harvests")

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def record_harvest(
    data: HarvestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("harvests:create"))
):
    """Record a new harvest event."""
    service = HarvestService(db)
    harvest = service.record_harvest(data, current_user)
    return {
        "id": str(harvest.id),
        "status": "recorded",
        "harvest_date": harvest.harvest_date.isoformat(),
        "quantity": str(harvest.quantity_harvested)
    }

@router.get("/crop-cycle/{cycle_id}", response_model=List[Dict[str, Any]])
async def list_harvests_for_cycle(
    cycle_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("harvests:read"))
):
    """List all harvests for a specific crop cycle."""
    service = HarvestService(db)
    harvests = service.harvest_repo.get_by_crop_cycle_id(cycle_id)
    return [
        {
            "id": str(h.id),
            "harvest_date": h.harvest_date.isoformat(),
            "quantity": str(h.quantity_harvested),
            "unit": h.unit,
            "quality_grade": h.quality_grade
        } for h in harvests
    ]

@router.post("/{harvest_id}/convert-to-product", response_model=ProductConversionResponse)
async def convert_to_product(
    harvest_id: UUID,
    product_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("products:create"))
):
    """
    Convert a harvest into a sellable product.
    
    This endpoint handles the full workflow when product_data does NOT include harvest_batch_id:
    
    1. Create HarvestEvent: A HarvestEvent is created from the legacy Harvest record
    
    2. Create Draft HarvestBatch: A draft batch is created to hold the harvest data
    
    3. Add Contribution: HarvestBatchContribution links the event to the batch
    
    4. Seal Batch: HarvestBatchRepository.seal_batch() computes:
       - lineage_hash: Cryptographic hash of the harvest lineage
       - aggregated_weight_kg: Total weight aggregated from contributions
       - moisture_avg: Average moisture content
    
    5. Set QC_PENDING Status: The batch status is immediately set to QC_PENDING
    
    6. Inline QC Report (optional): If product_data contains qc_report, a QC report
       is created via hb_repo.create_qc_report(), which sets QC_PASSED or QC_FAILED
    
    7. Product Creation:
       - If QC_PASSED: ProductService.create_product creates an ACTIVE product (is_active=True),
         and ProductBatch is linked via hb_repo.link_product_batch_to_harvest_batch()
       - If QC still pending: Product is created as INACTIVE (is_active=False) and
         harvest_batch_id is stored in product.metadata to preserve lineage
    
    The response is enriched with batch & QC linkage information for client UX.
    """
    service = HarvestService(db)
    product = service.convert_to_product(harvest_id, product_data, current_user)
    # Enrich response with batch & QC linkage for client UX
    from app.infrastructure.db.models.inventory import ProductBatchORM
    from app.infrastructure.db.models.harvest import ProductBatchSourceORM, HarvestBatchORM, BatchQCReportORM

    product_id = str(product.id)

    # Find product batches (if any) created for this product
    product_batches = db.query(ProductBatchORM).filter(ProductBatchORM.product_id == product_id).all()

    pb_list = []
    linked_batches = []
    for pb in product_batches:
        # Find harvest batches linked to this product batch
        sources = db.query(ProductBatchSourceORM).filter(ProductBatchSourceORM.product_batch_id == pb.id).all()
        links = []
        for s in sources:
            hb = db.query(HarvestBatchORM).filter(HarvestBatchORM.id == s.harvest_batch_id).first()
            if not hb:
                continue
            # QC reports for the harvest batch
            qc_rs = db.query(BatchQCReportORM).filter(BatchQCReportORM.batch_id == hb.id).all()
            qc_list = [
                {
                    "id": str(q.id),
                    "lab_id": q.lab_id,
                    "tested_at": q.tested_at.isoformat() if q.tested_at else None,
                    "metrics": q.metrics,
                    "passed": bool(q.passed),
                    "report_url": q.report_url,
                    "verified": bool(getattr(q, 'verified', False)),
                }
                for q in qc_rs
            ]

            links.append({
                "harvest_batch_id": hb.id,
                "batch_code": hb.batch_code,
                "status": hb.status.value if hasattr(hb.status, 'value') else hb.status,
                "lineage_hash": hb.lineage_hash,
                "aggregated_weight_kg": hb.aggregated_weight_kg,
                "moisture_avg": hb.moisture_avg,
                "qc_reports": qc_list,
                "contribution_weight_kg": s.contribution_weight_kg,
            })
            linked_batches.append(hb)

        pb_list.append({
            "id": pb.id,
            "batch_code": pb.batch_code,
            "total_quantity": str(pb.total_quantity),
            "quality_grade": pb.quality_grade.value if hasattr(pb, 'quality_grade') and pb.quality_grade else pb.quality_grade,
            "links": links,
        })

    # If there are linked harvest batches, pick primary (first) for top-level fields
    primary_harvest_batch = linked_batches[0] if linked_batches else None

    response = {
        "id": product_id,
        "name": product.name,
        "total_quantity": str(product.total_quantity) if hasattr(product, 'total_quantity') else None,
        "status": "converted",
        "is_active": bool(getattr(product, 'is_active', None)),
        "product_batches": pb_list,
    }

    if primary_harvest_batch:
        response.update({
            "harvest_batch_id": primary_harvest_batch.id,
            "harvest_batch_status": primary_harvest_batch.status.value if hasattr(primary_harvest_batch.status, 'value') else primary_harvest_batch.status,
            "harvest_batch_lineage_hash": primary_harvest_batch.lineage_hash,
            "harvest_batch_aggregated_weight_kg": primary_harvest_batch.aggregated_weight_kg,
        })

        # derive QC status from latest QC report if present
        latest_qc = db.query(BatchQCReportORM).filter(BatchQCReportORM.batch_id == primary_harvest_batch.id).order_by(BatchQCReportORM.tested_at.desc()).first()
        if latest_qc:
            response.update({
                "qc_status": "PASSED" if latest_qc.passed else "FAILED",
                "qc_lab_id": latest_qc.lab_id,
                "qc_tested_at": latest_qc.tested_at.isoformat() if latest_qc.tested_at else None,
            })

    return response
