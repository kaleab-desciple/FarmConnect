"""Harvest Batch Repository for advanced batch management with lineage tracking.

This repository provides:
- HarvestEvent CRUD operations for field-level harvest tracking
- HarvestBatch CRUD with aggregation and sealing
- Lineage hash computation for immutable provenance
- Contribution management with append-only enforcement after sealing
- Audit event recording
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.infrastructure.db.models.harvest import (
    HarvestEventORM,
    HarvestBatchORM,
    HarvestBatchContributionORM,
    BatchQCReportORM,
    ProductBatchSourceORM,
    AuditEventORM,
)
from app.domain.harvest.entities import (
    HarvestEvent,
    HarvestEventCreate,
    HarvestBatch,
    HarvestBatchCreate,
    HarvestBatchSealRequest,
    HarvestBatchContribution,
    HarvestBatchContributionCreate,
    BatchQCReport,
    BatchQCReportCreate,
    ProductBatchSource,
    AuditEvent,
    HarvestBatchState,
    compute_lineage_hash,
)


class HarvestBatchRepository:
    """Repository for harvest events and batch management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================
    # HarvestEvent Operations
    # ========================================
    
    def create_event(self, event: HarvestEventCreate) -> HarvestEvent:
        """Create a new harvest event."""
        orm = HarvestEventORM(
            id=str(uuid4()),
            farm_id=event.farm_id,
            field_id=event.field_id,
            crop_cycle_id=str(event.crop_cycle_id) if event.crop_cycle_id else None,
            collected_by=event.collected_by,
            harvested_at=event.harvested_at,
            gross_weight_kg=event.gross_weight_kg,
            moisture_pct=event.moisture_pct,
            loss_kg=event.loss_kg,
            photos=event.photos,
            weighbridge_receipt=event.weighbridge_receipt,
            location=event.location,
            notes=event.notes,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        
        # Record audit event
        self._create_audit_event(
            event_type="harvest_event.created",
            entity_type="harvest_event",
            entity_id=orm.id,
            payload={"farm_id": event.farm_id, "field_id": event.field_id, "weight_kg": event.gross_weight_kg},
            user_id=event.collected_by,
        )
        
        return self._orm_to_event(orm)
    
    def get_event_by_id(self, event_id: str) -> Optional[HarvestEvent]:
        """Get a harvest event by ID."""
        orm = self.db.query(HarvestEventORM).filter(HarvestEventORM.id == event_id).first()
        return self._orm_to_event(orm) if orm else None
    
    def get_events_by_farm(self, farm_id: str) -> List[HarvestEvent]:
        """Get all harvest events for a farm."""
        orms = self.db.query(HarvestEventORM).filter(HarvestEventORM.farm_id == farm_id).all()
        return [self._orm_to_event(orm) for orm in orms]
    
    def get_events_by_field(self, field_id: str) -> List[HarvestEvent]:
        """Get all harvest events for a field."""
        orms = self.db.query(HarvestEventORM).filter(HarvestEventORM.field_id == field_id).all()
        return [self._orm_to_event(orm) for orm in orms]
    
    # ========================================
    # HarvestBatch Operations
    # ========================================
    
    def create_draft_batch(self, batch: HarvestBatchCreate) -> HarvestBatch:
        """Create a new draft harvest batch."""
        orm = HarvestBatchORM(
            id=str(uuid4()),
            batch_code=batch.batch_code,
            aggregator_id=batch.aggregator_id,
            status=HarvestBatchState.DRAFT,
            notes=batch.notes,
            metadata_=batch.metadata,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        
        # Record audit event
        self._create_audit_event(
            event_type="batch.created",
            entity_type="harvest_batch",
            entity_id=orm.id,
            payload={"batch_code": batch.batch_code, "aggregator_id": batch.aggregator_id},
            user_id=batch.aggregator_id,
        )
        
        return self._orm_to_batch(orm)
    
    def get_batch_by_id(self, batch_id: str) -> Optional[HarvestBatch]:
        """Get a harvest batch by ID."""
        orm = self.db.query(HarvestBatchORM).filter(HarvestBatchORM.id == batch_id).first()
        return self._orm_to_batch(orm) if orm else None
    
    def get_batch_by_code(self, batch_code: str) -> Optional[HarvestBatch]:
        """Get a harvest batch by batch code."""
        orm = self.db.query(HarvestBatchORM).filter(HarvestBatchORM.batch_code == batch_code).first()
        return self._orm_to_batch(orm) if orm else None
    
    def get_batches_by_aggregator(self, aggregator_id: str) -> List[HarvestBatch]:
        """Get all harvest batches for an aggregator."""
        orms = self.db.query(HarvestBatchORM).filter(HarvestBatchORM.aggregator_id == aggregator_id).all()
        return [self._orm_to_batch(orm) for orm in orms]
    
    def get_batches_by_status(self, status: HarvestBatchState) -> List[HarvestBatch]:
        """Get all harvest batches with a specific status."""
        orms = self.db.query(HarvestBatchORM).filter(HarvestBatchORM.status == status).all()
        return [self._orm_to_batch(orm) for orm in orms]
    
    # ========================================
    # Contribution Operations
    # ========================================
    
    def add_contribution(
        self,
        batch_id: str,
        contribution: HarvestBatchContributionCreate,
    ) -> HarvestBatchContribution:
        """Add a contribution to a harvest batch."""
        # Check if batch is sealed
        batch = self.get_batch_by_id(batch_id)
        if not batch:
            raise ValueError("Batch not found")
        if batch.status == HarvestBatchState.SEALED:
            raise ValueError("Cannot add contributions to a SEALED batch")
        
        # Check if this event is already contributed
        existing = self.db.query(HarvestBatchContributionORM).filter(
            HarvestBatchContributionORM.harvest_batch_id == batch_id,
            HarvestBatchContributionORM.harvest_event_id == str(contribution.harvest_event_id),
        ).first()
        if existing:
            raise ValueError("This harvest event is already contributed to this batch")
        
        # Check if harvest event is already in a sealed batch (prevent double-counting)
        sealed_check = self.db.query(HarvestBatchContributionORM).join(
            HarvestBatchORM,
            HarvestBatchContributionORM.harvest_batch_id == HarvestBatchORM.id
        ).filter(
            HarvestBatchContributionORM.harvest_event_id == str(contribution.harvest_event_id),
            HarvestBatchORM.status == HarvestBatchState.SEALED,
        ).first()
        if sealed_check:
            raise ValueError(
                "This harvest event is already contributed to a SEALED batch and cannot be reused"
            )
        
        # Validate contributed weight doesn't exceed harvest event weight
        event = self.get_event_by_id(str(contribution.harvest_event_id))
        if event and contribution.contributed_weight_kg > event.gross_weight_kg:
            raise ValueError(
                f"Contributed weight ({contribution.contributed_weight_kg}) cannot exceed "
                f"harvest event weight ({event.gross_weight_kg})"
            )
        
        orm = HarvestBatchContributionORM(
            id=str(uuid4()),
            harvest_batch_id=batch_id,
            harvest_event_id=str(contribution.harvest_event_id),
            farmer_id=contribution.farmer_id,
            contributed_weight_kg=contribution.contributed_weight_kg,
            reported_moisture_pct=contribution.reported_moisture_pct,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        
        return self._orm_to_contribution(orm)
    
    def get_contributions_by_batch(self, batch_id: str) -> List[HarvestBatchContribution]:
        """Get all contributions for a batch."""
        orms = self.db.query(HarvestBatchContributionORM).filter(
            HarvestBatchContributionORM.harvest_batch_id == batch_id
        ).all()
        return [self._orm_to_contribution(orm) for orm in orms]
    
    def get_contribution_data_for_hash(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get contribution data formatted for lineage hash computation."""
        contributions = self.db.query(
            HarvestBatchContributionORM.harvest_event_id,
            HarvestBatchContributionORM.farmer_id,
            HarvestBatchContributionORM.contributed_weight_kg,
            HarvestBatchContributionORM.reported_moisture_pct,
            HarvestEventORM.harvested_at,
        ).join(
            HarvestEventORM,
            HarvestBatchContributionORM.harvest_event_id == HarvestEventORM.id
        ).filter(
            HarvestBatchContributionORM.harvest_batch_id == batch_id
        ).all()
        
        return [
            {
                "harvest_event_id": c.harvest_event_id,
                "farmer_id": c.farmer_id,
                "contributed_weight_kg": c.contributed_weight_kg,
                "reported_moisture_pct": c.reported_moisture_pct,
                "harvested_at": c.harvested_at,
            }
            for c in contributions
        ]
    
    # ========================================
    # Seal & Lineage Operations
    # ========================================
    
    def compute_lineage_hash(self, batch_id: str) -> str:
        """Compute lineage hash for a batch."""
        batch = self.get_batch_by_id(batch_id)
        if not batch:
            raise ValueError("Batch not found")
        
        contributions = self.get_contribution_data_for_hash(batch_id)
        
        return compute_lineage_hash(
            batch_id=str(batch.id),
            aggregator_id=batch.aggregator_id,
            created_at=batch.created_at,
            contributions=contributions,
        )
    
    def seal_batch(
        self,
        batch_id: str,
        seal_request: HarvestBatchSealRequest,
    ) -> HarvestBatch:
        """
        Seal a harvest batch.
        
        This operation:
        1. Validates the batch is in DRAFT status (with row lock)
        2. Computes the lineage hash from contributions
        3. Calculates aggregated weight and average moisture
        4. Sets status to SEALED with sealed_at, sealed_by, and seal_evidence
        
        All operations run in a single DB transaction with SELECT FOR UPDATE
        to serialize concurrent seal attempts.
        """
        # Get batch with row lock to prevent concurrent seal attempts
        orm = self.db.query(HarvestBatchORM).filter(
            HarvestBatchORM.id == batch_id
        ).with_for_update().first()
        
        if not orm:
            raise ValueError("Batch not found")
        
        if orm.status != HarvestBatchState.DRAFT:
            raise ValueError(f"Cannot seal batch in {orm.status} status. Only DRAFT batches can be sealed.")
        
        # Get contributions for aggregation - must be done inside transaction
        contributions = self.get_contribution_data_for_hash(batch_id)
        if not contributions:
            raise ValueError("Cannot seal an empty batch. At least one contribution is required.")
        
        # Verify no harvest events are already in sealed batches
        for c in contributions:
            existing_sealed = self.db.query(HarvestBatchContributionORM).join(
                HarvestBatchORM,
                HarvestBatchContributionORM.harvest_batch_id == HarvestBatchORM.id
            ).filter(
                HarvestBatchContributionORM.harvest_event_id == c['harvest_event_id'],
                HarvestBatchORM.status == HarvestBatchState.SEALED,
                HarvestBatchORM.id != batch_id  # exclude current batch
            ).first()
            if existing_sealed:
                raise ValueError(
                    f"Harvest event {c['harvest_event_id']} is already used in a sealed batch"
                )
        
        # Compute lineage hash
        lineage_hash = compute_lineage_hash(
            batch_id=str(orm.id),
            aggregator_id=orm.aggregator_id,
            created_at=orm.created_at,
            contributions=contributions,
        )
        
        # Calculate aggregated weight
        aggregated_weight = sum(c["contributed_weight_kg"] for c in contributions)
        
        # Calculate average moisture (weighted by contribution weight)
        moistures = [c["reported_moisture_pct"] for c in contributions if c["reported_moisture_pct"]]
        if moistures:
            # Weighted average by contribution weight
            weighted_sum = sum(
                c["reported_moisture_pct"] * c["contributed_weight_kg"] 
                for c in contributions if c["reported_moisture_pct"]
            )
            moisture_avg = weighted_sum / aggregated_weight if aggregated_weight > 0 else None
        else:
            moisture_avg = None
        
        # Update batch atomically
        now = datetime.now(timezone.utc)
        orm.status = HarvestBatchState.SEALED
        orm.sealed_at = now
        orm.sealed_by = seal_request.sealed_by
        orm.seal_evidence = seal_request.seal_evidence
        orm.lineage_hash = lineage_hash
        orm.aggregated_weight_kg = aggregated_weight
        orm.moisture_avg = moisture_avg
        orm.updated_at = now
        
        self.db.commit()
        self.db.refresh(orm)
        
        # Record audit event
        self._create_audit_event(
            event_type="batch.sealed",
            entity_type="harvest_batch",
            entity_id=batch_id,
            payload={
                "lineage_hash": lineage_hash,
                "aggregated_weight_kg": aggregated_weight,
                "moisture_avg": moisture_avg,
                "contribution_count": len(contributions),
            },
            user_id=seal_request.sealed_by,
        )
        
        return self._orm_to_batch(orm)
    
    def update_batch_status(
        self,
        batch_id: str,
        new_status: HarvestBatchState,
        user_id: str,
        notes: Optional[str] = None,
    ) -> HarvestBatch:
        """Update batch status (e.g., to QC_PENDING, QC_PASSED, QC_FAILED)."""
        orm = self.db.query(HarvestBatchORM).filter(HarvestBatchORM.id == batch_id).first()
        if not orm:
            raise ValueError("Batch not found")
        
        old_status = orm.status
        orm.status = new_status
        orm.updated_at = datetime.now(timezone.utc)
        
        if notes:
            orm.notes = (orm.notes or "") + f"\\n[{datetime.now(timezone.utc).isoformat()}] Status change: {old_status} -> {new_status}. Notes: {notes}"
        
        self.db.commit()
        self.db.refresh(orm)
        
        # Record audit event
        self._create_audit_event(
            event_type=f"batch.status_changed",
            entity_type="harvest_batch",
            entity_id=batch_id,
            payload={"old_status": old_status.value, "new_status": new_status.value},
            user_id=user_id,
        )
        
        return self._orm_to_batch(orm)
    
    # ========================================
    # QC Report Operations
    # ========================================
    
    def create_qc_report(self, report: BatchQCReportCreate) -> BatchQCReport:
        """Create a QC report for a batch."""
        # Check batch exists
        batch = self.get_batch_by_id(str(report.batch_id))
        if not batch:
            raise ValueError("Batch not found")
        
        orm = BatchQCReportORM(
            id=str(uuid4()),
            batch_id=str(report.batch_id),
            lab_id=report.lab_id,
            tested_at=report.tested_at,
            metrics=report.metrics,
            passed=report.passed,
            report_url=report.report_url,
            signed_hash=report.signed_hash,
            notes=report.notes,
        )
        self.db.add(orm)
        
        # Update batch status based on QC result
        new_status = HarvestBatchState.QC_PASSED if report.passed else HarvestBatchState.QC_FAILED
        batch_orm = self.db.query(HarvestBatchORM).filter(HarvestBatchORM.id == str(report.batch_id)).first()
        batch_orm.status = new_status
        batch_orm.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(orm)
        
        # Record audit event
        self._create_audit_event(
            event_type="qc.completed",
            entity_type="harvest_batch",
            entity_id=str(report.batch_id),
            payload={
                "lab_id": report.lab_id,
                "passed": report.passed,
                "metrics": report.metrics,
            },
            user_id=report.lab_id,
        )
        
        return self._orm_to_qc_report(orm)
    
    def get_qc_reports_by_batch(self, batch_id: str) -> List[BatchQCReport]:
        """Get all QC reports for a batch."""
        orms = self.db.query(BatchQCReportORM).filter(BatchQCReportORM.batch_id == batch_id).all()
        return [self._orm_to_qc_report(orm) for orm in orms]
    
    # ========================================
    # Product Batch Linkage
    # ========================================
    
    def link_product_batch_to_harvest_batch(
        self,
        product_batch_id: str,
        harvest_batch_id: str,
        contribution_weight_kg: float,
    ) -> ProductBatchSource:
        """Link a product batch to a harvest batch."""
        # Verify harvest batch is sealed and passed QC
        batch = self.get_batch_by_id(harvest_batch_id)
        if not batch:
            raise ValueError("Harvest batch not found")
        
        if batch.status != HarvestBatchState.QC_PASSED:
            raise ValueError(
                f"Cannot link to batch in {batch.status} status. "
                "Only QC_PASSED batches can be used for products."
            )
        
        orm = ProductBatchSourceORM(
            id=str(uuid4()),
            product_batch_id=product_batch_id,
            harvest_batch_id=harvest_batch_id,
            contribution_weight_kg=contribution_weight_kg,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        
        # Record audit event
        self._create_audit_event(
            event_type="product_batch.linked",
            entity_type="product_batch",
            entity_id=product_batch_id,
            payload={"harvest_batch_id": harvest_batch_id, "weight_kg": contribution_weight_kg},
        )
        
        return self._orm_to_product_batch_source(orm)
    
    def verify_batch_can_be_used_for_listing(self, harvest_batch_id: str) -> tuple[bool, str]:
        """
        Verify a harvest batch can be used for product listing.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        batch = self.get_batch_by_id(harvest_batch_id)
        if not batch:
            return False, "Harvest batch not found"
        
        if batch.status != HarvestBatchState.QC_PASSED:
            return False, f"Harvest batch must be QC_PASSED. Current status: {batch.status}"
        
        return True, ""
    
    # ========================================
    # Audit Operations
    # ========================================
    
    def _create_audit_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        payload: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        signature: Optional[str] = None,
    ) -> None:
        """Create an audit event."""
        # Get previous event hash for chain
        last_event = self.db.query(AuditEventORM).filter(
            AuditEventORM.entity_type == entity_type,
            AuditEventORM.entity_id == entity_id,
        ).order_by(AuditEventORM.created_at.desc()).first()
        
        # Compute payload hash
        import hashlib
        import json
        payload_hash = None
        if payload:
            payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
            payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        
        event = AuditEventORM(
            id=str(uuid4()),
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            payload_hash=payload_hash,
            previous_event_hash=last_event.payload_hash if last_event else None,
            user_id=user_id,
            signature=signature,
        )
        self.db.add(event)
        self.db.flush()
    
    def get_audit_events(self, entity_type: str, entity_id: str) -> List[AuditEvent]:
        """Get audit trail for an entity."""
        orms = self.db.query(AuditEventORM).filter(
            AuditEventORM.entity_type == entity_type,
            AuditEventORM.entity_id == entity_id,
        ).order_by(AuditEventORM.created_at.asc()).all()
        return [self._orm_to_audit_event(orm) for orm in orms]
    
    # ========================================
    # ORM to Domain Mappers
    # ========================================
    
    def _orm_to_event(self, orm: Optional[HarvestEventORM]) -> Optional[HarvestEvent]:
        if not orm:
            return None
        return HarvestEvent(
            id=UUID(orm.id),
            farm_id=orm.farm_id,
            field_id=orm.field_id,
            crop_cycle_id=UUID(orm.crop_cycle_id) if orm.crop_cycle_id else None,
            collected_by=orm.collected_by,
            harvested_at=orm.harvested_at,
            gross_weight_kg=orm.gross_weight_kg,
            moisture_pct=orm.moisture_pct,
            loss_kg=orm.loss_kg,
            photos=orm.photos,
            weighbridge_receipt=orm.weighbridge_receipt,
            location=orm.location,
            notes=orm.notes,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
    
    def _orm_to_batch(self, orm: Optional[HarvestBatchORM]) -> Optional[HarvestBatch]:
        if not orm:
            return None
        
        # Load contributions
        contributions = self.get_contributions_by_batch(orm.id)
        
        return HarvestBatch(
            id=UUID(orm.id),
            batch_code=orm.batch_code,
            aggregator_id=orm.aggregator_id,
            status=orm.status,
            aggregated_weight_kg=orm.aggregated_weight_kg,
            moisture_avg=orm.moisture_avg,
            sealed_at=orm.sealed_at,
            sealed_by=orm.sealed_by,
            seal_evidence=orm.seal_evidence,
            lineage_hash=orm.lineage_hash,
            lineage_signature=orm.lineage_signature,
            notes=orm.notes,
            metadata=orm.metadata_,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            contributions=contributions,
        )
    
    def _orm_to_contribution(self, orm: Optional[HarvestBatchContributionORM]) -> Optional[HarvestBatchContribution]:
        if not orm:
            return None
        return HarvestBatchContribution(
            id=UUID(orm.id),
            harvest_batch_id=UUID(orm.harvest_batch_id),
            harvest_event_id=UUID(orm.harvest_event_id),
            farmer_id=orm.farmer_id,
            contributed_weight_kg=orm.contributed_weight_kg,
            reported_moisture_pct=orm.reported_moisture_pct,
            created_at=orm.created_at,
        )
    
    def _orm_to_qc_report(self, orm: Optional[BatchQCReportORM]) -> Optional[BatchQCReport]:
        if not orm:
            return None
        return BatchQCReport(
            id=UUID(orm.id),
            batch_id=UUID(orm.batch_id),
            lab_id=orm.lab_id,
            tested_at=orm.tested_at,
            metrics=orm.metrics,
            passed=orm.passed,
            report_url=orm.report_url,
            signed_hash=orm.signed_hash,
            notes=orm.notes,
            created_at=orm.created_at,
        )
    
    def _orm_to_product_batch_source(self, orm: Optional[ProductBatchSourceORM]) -> Optional[ProductBatchSource]:
        if not orm:
            return None
        return ProductBatchSource(
            id=UUID(orm.id),
            product_batch_id=orm.product_batch_id,
            harvest_batch_id=UUID(orm.harvest_batch_id),
            contribution_weight_kg=orm.contribution_weight_kg,
            created_at=orm.created_at,
        )
    
    def _orm_to_audit_event(self, orm: Optional[AuditEventORM]) -> Optional[AuditEvent]:
        if not orm:
            return None
        return AuditEvent(
            id=UUID(orm.id),
            event_type=orm.event_type,
            entity_type=orm.entity_type,
            entity_id=orm.entity_id,
            payload=orm.payload,
            payload_hash=orm.payload_hash,
            previous_event_hash=orm.previous_event_hash,
            user_id=orm.user_id,
            signature=orm.signature,
            created_at=orm.created_at,
        )
