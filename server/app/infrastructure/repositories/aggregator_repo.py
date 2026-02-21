"""Aggregator repositories for smallholder reconciliation and split settlement.

This module contains:
- AggregatorRepository: CRUD operations for aggregators
- AcceptanceWeighmentRepository: CRUD operations for weighments
- ReconciliationRepository: CRUD operations for reconciliation records
- SettlementRuleRepository: CRUD operations for settlement rules
- SettlementSummaryRepository: CRUD operations for settlement summaries
- SplitSettlementRepository: CRUD operations for split settlements
"""

from typing import List, Optional
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.db.models.aggregator import (
    AggregatorORM,
    AcceptanceWeighmentORM,
    ReconciliationRecordORM,
    SettlementRuleORM,
    AggregatorSettlementSummaryORM,
    SplitSettlementORM,
)


class AggregatorRepository:
    """Repository for Aggregator operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, name: str, **kwargs) -> AggregatorORM:
        """Create a new aggregator."""
        aggregator = AggregatorORM(
            id=str(uuid4()),
            name=name,
            **kwargs
        )
        self.session.add(aggregator)
        self.session.flush()
        return aggregator
    
    def get_by_id(self, aggregator_id: str) -> Optional[AggregatorORM]:
        """Get aggregator by ID."""
        return self.session.query(AggregatorORM).filter(AggregatorORM.id == aggregator_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[AggregatorORM]:
        """Get all aggregators."""
        return self.session.query(AggregatorORM).order_by(
            AggregatorORM.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_active(self) -> List[AggregatorORM]:
        """Get all active aggregators."""
        return self.session.query(AggregatorORM).filter(
            AggregatorORM.is_active == True
        ).order_by(AggregatorORM.name).all()
    
    def update(self, aggregator_id: str, **kwargs) -> Optional[AggregatorORM]:
        """Update an aggregator."""
        aggregator = self.get_by_id(aggregator_id)
        if aggregator:
            for key, value in kwargs.items():
                if hasattr(aggregator, key):
                    setattr(aggregator, key, value)
            aggregator.updated_at = datetime.now(timezone.utc)
            self.session.flush()
        return aggregator
    
    def delete(self, aggregator_id: str) -> bool:
        """Soft delete an aggregator (set is_active to False)."""
        aggregator = self.get_by_id(aggregator_id)
        if aggregator:
            aggregator.is_active = False
            aggregator.updated_at = datetime.now(timezone.utc)
            self.session.flush()
            return True
        return False


class AcceptanceWeighmentRepository:
    """Repository for AcceptanceWeighment operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, batch_id: str, gross_weight_kg: float, tare_weight_kg: float, 
                    net_weight_kg: float, **kwargs) -> AcceptanceWeighmentORM:
        """Create a new acceptance weighment."""
        weighment = AcceptanceWeighmentORM(
            id=str(uuid4()),
            batch_id=batch_id,
            gross_weight_kg=gross_weight_kg,
            tare_weight_kg=tare_weight_kg,
            net_weight_kg=net_weight_kg,
            recorded_at=kwargs.get('recorded_at', datetime.now(timezone.utc)),
            **kwargs
        )
        self.session.add(weighment)
        self.session.flush()
        return weighment
    
    def get_by_id(self, weighment_id: str) -> Optional[AcceptanceWeighmentORM]:
        """Get weighment by ID."""
        return self.session.query(AcceptanceWeighmentORM).filter(
            AcceptanceWeighmentORM.id == weighment_id
        ).first()
    
    def get_by_batch(self, batch_id: str) -> List[AcceptanceWeighmentORM]:
        """Get all weighments for a batch."""
        return self.session.query(AcceptanceWeighmentORM).filter(
            AcceptanceWeighmentORM.batch_id == batch_id
        ).order_by(AcceptanceWeighmentORM.created_at).all()
    
    def get_total_weight(self, batch_id: str) -> float:
        """Get total net weight for a batch."""
        weighments = self.get_by_batch(batch_id)
        return sum(w.net_weight_kg for w in weighments)


class ReconciliationRepository:
    """Repository for ReconciliationRecord operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, batch_id: str, expected_total_kg: float, measured_total_kg: float,
                    created_by: Optional[str] = None, **kwargs) -> ReconciliationRecordORM:
        """Create a new reconciliation record."""
        difference_kg = measured_total_kg - expected_total_kg
        variance_pct = (difference_kg / expected_total_kg * 100) if expected_total_kg > 0 else 0
        
        # Determine status based on variance
        if abs(variance_pct) <= 2:
            recon_status = 'OK'
        elif abs(variance_pct) <= 5:
            recon_status = 'WARNING'
        else:
            recon_status = 'DISPUTE'
        
        record = ReconciliationRecordORM(
            id=str(uuid4()),
            batch_id=batch_id,
            expected_total_kg=expected_total_kg,
            measured_total_kg=measured_total_kg,
            difference_kg=difference_kg,
            variance_pct=variance_pct,
            recon_status=recon_status,
            created_by=created_by,
            **kwargs
        )
        self.session.add(record)
        self.session.flush()
        return record
    
    def get_by_id(self, recon_id: str) -> Optional[ReconciliationRecordORM]:
        """Get reconciliation record by ID."""
        return self.session.query(ReconciliationRecordORM).filter(
            ReconciliationRecordORM.id == recon_id
        ).first()
    
    def get_by_batch(self, batch_id: str) -> List[ReconciliationRecordORM]:
        """Get all reconciliation records for a batch."""
        return self.session.query(ReconciliationRecordORM).filter(
            ReconciliationRecordORM.batch_id == batch_id
        ).order_by(ReconciliationRecordORM.created_at.desc()).all()


class SettlementRuleRepository:
    """Repository for SettlementRule operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, aggregator_id: str, name: str, split_method: str, **kwargs) -> SettlementRuleORM:
        """Create a new settlement rule."""
        rule = SettlementRuleORM(
            id=str(uuid4()),
            aggregator_id=aggregator_id,
            name=name,
            split_method=split_method,
            **kwargs
        )
        self.session.add(rule)
        self.session.flush()
        return rule
    
    def get_by_id(self, rule_id: str) -> Optional[SettlementRuleORM]:
        """Get settlement rule by ID."""
        return self.session.query(SettlementRuleORM).filter(
            SettlementRuleORM.id == rule_id
        ).first()
    
    def get_by_aggregator(self, aggregator_id: str) -> List[SettlementRuleORM]:
        """Get all settlement rules for an aggregator."""
        return self.session.query(SettlementRuleORM).filter(
            SettlementRuleORM.aggregator_id == aggregator_id
        ).order_by(SettlementRuleORM.created_at.desc()).all()
    
    def get_default(self, aggregator_id: Optional[str] = None) -> Optional[SettlementRuleORM]:
        """Get the default settlement rule for an aggregator."""
        query = self.session.query(SettlementRuleORM).filter(SettlementRuleORM.is_default == True)
        if aggregator_id:
            query = query.filter(SettlementRuleORM.aggregator_id == aggregator_id)
        return query.first()


class SettlementSummaryRepository:
    """Repository for AggregatorSettlementSummary operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, batch_id: str, aggregator_id: str, gross_sale_amount: float,
                   total_platform_fee: float, total_commission: float, net_to_distribute: float,
                   **kwargs) -> AggregatorSettlementSummaryORM:
        """Create a new settlement summary."""
        summary = AggregatorSettlementSummaryORM(
            id=str(uuid4()),
            batch_id=batch_id,
            aggregator_id=aggregator_id,
            gross_sale_amount=gross_sale_amount,
            total_platform_fee=total_platform_fee,
            total_commission=total_commission,
            net_to_distribute=net_to_distribute,
            **kwargs
        )
        self.session.add(summary)
        self.session.flush()
        return summary
    
    def get_by_id(self, summary_id: str) -> Optional[AggregatorSettlementSummaryORM]:
        """Get settlement summary by ID."""
        return self.session.query(AggregatorSettlementSummaryORM).filter(
            AggregatorSettlementSummaryORM.id == summary_id
        ).first()
    
    def get_by_batch(self, batch_id: str) -> Optional[AggregatorSettlementSummaryORM]:
        """Get settlement summary for a batch."""
        return self.session.query(AggregatorSettlementSummaryORM).filter(
            AggregatorSettlementSummaryORM.batch_id == batch_id
        ).first()
    
    def get_by_aggregator(self, aggregator_id: str, skip: int = 0, limit: int = 50) -> List[AggregatorSettlementSummaryORM]:
        """Get all settlement summaries for an aggregator."""
        return self.session.query(AggregatorSettlementSummaryORM).filter(
            AggregatorSettlementSummaryORM.aggregator_id == aggregator_id
        ).order_by(AggregatorSettlementSummaryORM.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_status(self, summary_id: str, status: str) -> Optional[AggregatorSettlementSummaryORM]:
        """Update settlement summary status."""
        summary = self.get_by_id(summary_id)
        if summary:
            summary.status = status
            self.session.flush()
        return summary


class SplitSettlementRepository:
    """Repository for SplitSettlement operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, settlement_summary_id: str, contribution_id: str, 
                    farmer_id: str, contributed_weight_kg: float, share_amount: float,
                    **kwargs) -> SplitSettlementORM:
        """Create a new split settlement."""
        settlement = SplitSettlementORM(
            id=str(uuid4()),
            settlement_summary_id=settlement_summary_id,
            contribution_id=contribution_id,
            farmer_id=farmer_id,
            contributed_weight_kg=contributed_weight_kg,
            share_amount=share_amount,
            **kwargs
        )
        self.session.add(settlement)
        self.session.flush()
        return settlement
    
    def get_by_id(self, settlement_id: str) -> Optional[SplitSettlementORM]:
        """Get split settlement by ID."""
        return self.session.query(SplitSettlementORM).filter(
            SplitSettlementORM.id == settlement_id
        ).first()
    
    def get_by_summary(self, summary_id: str) -> List[SplitSettlementORM]:
        """Get all split settlements for a summary."""
        return self.session.query(SplitSettlementORM).filter(
            SplitSettlementORM.settlement_summary_id == summary_id
        ).order_by(SplitSettlementORM.share_amount.desc()).all()
    
    def get_by_farmer(self, farmer_id: str, skip: int = 0, limit: int = 50) -> List[SplitSettlementORM]:
        """Get all split settlements for a farmer."""
        return self.session.query(SplitSettlementORM).filter(
            SplitSettlementORM.farmer_id == farmer_id
        ).order_by(SplitSettlementORM.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_status(self, settlement_id: str, status: str, 
                           payout_reference: Optional[str] = None,
                           failure_reason: Optional[str] = None) -> Optional[SplitSettlementORM]:
        """Update split settlement status."""
        settlement = self.get_by_id(settlement_id)
        if settlement:
            settlement.status = status
            if payout_reference:
                settlement.payout_reference = payout_reference
            if failure_reason:
                settlement.failure_reason = failure_reason
            if status == 'PAID':
                settlement.paid_at = datetime.now(timezone.utc)
            self.session.flush()
        return settlement
