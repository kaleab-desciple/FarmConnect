"""Aggregator services for smallholder reconciliation and split settlement.

This module contains:
- AggregatorService: CRUD operations for aggregators
- ReconciliationService: Reconcile farmer-declared vs aggregator-measured quantities
- SettlementService: Calculate and process split settlements for smallholders
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.infrastructure.repositories.aggregator_repo import (
    AggregatorRepository,
    AcceptanceWeighmentRepository,
    ReconciliationRepository,
    SettlementRuleRepository,
    SettlementSummaryRepository,
    SplitSettlementRepository,
)
from app.infrastructure.repositories.harvest_batch_repo import HarvestBatchRepository
from app.infrastructure.db.models.harvest import HarvestBatchContributionORM


class AggregatorService:
    """Service for managing aggregators."""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = AggregatorRepository(session)
    
    def create_aggregator(self, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new aggregator."""
        aggregator = self.repo.create(name=name, **kwargs)
        self.session.commit()
        return {
            "id": aggregator.id,
            "name": aggregator.name,
            "company_info": aggregator.company_info,
            "contact": aggregator.contact,
            "kyc_status": aggregator.kyc_status,
            "wallet_id": aggregator.wallet_id,
            "is_active": aggregator.is_active,
            "created_at": aggregator.created_at.isoformat() if aggregator.created_at else None,
        }
    
    def get_aggregator(self, aggregator_id: str) -> Optional[Dict[str, Any]]:
        """Get aggregator by ID."""
        aggregator = self.repo.get_by_id(aggregator_id)
        if not aggregator:
            return None
        return {
            "id": aggregator.id,
            "name": aggregator.name,
            "company_info": aggregator.company_info,
            "contact": aggregator.contact,
            "kyc_status": aggregator.kyc_status,
            "wallet_id": aggregator.wallet_id,
            "is_active": aggregator.is_active,
            "created_at": aggregator.created_at.isoformat() if aggregator.created_at else None,
            "updated_at": aggregator.updated_at.isoformat() if aggregator.updated_at else None,
        }
    
    def list_aggregators(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List all aggregators."""
        aggregators = self.repo.get_all(skip=skip, limit=limit)
        return [
            {
                "id": a.id,
                "name": a.name,
                "kyc_status": a.kyc_status,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in aggregators
        ]
    
    def update_aggregator(self, aggregator_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update an aggregator."""
        aggregator = self.repo.update(aggregator_id, **kwargs)
        if not aggregator:
            return None
        self.session.commit()
        return self.get_aggregator(aggregator_id)
    
    def record_weighment(self, batch_id: str, gross_weight_kg: float, tare_weight_kg: float,
                              weigher_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Record a weighment for a batch."""
        weighment_repo = AcceptanceWeighmentRepository(self.session)
        net_weight_kg = gross_weight_kg - tare_weight_kg
        
        weighment = weighment_repo.create(
            batch_id=batch_id,
            gross_weight_kg=gross_weight_kg,
            tare_weight_kg=tare_weight_kg,
            net_weight_kg=net_weight_kg,
            weigher_id=weigher_id,
            **kwargs
        )
        self.session.commit()
        
        return {
            "id": weighment.id,
            "batch_id": weighment.batch_id,
            "gross_weight_kg": weighment.gross_weight_kg,
            "tare_weight_kg": weighment.tare_weight_kg,
            "net_weight_kg": weighment.net_weight_kg,
            "weigher_id": weighment.weigher_id,
            "recorded_at": weighment.recorded_at.isoformat() if weighment.recorded_at else None,
            "created_at": weighment.created_at.isoformat() if weighment.created_at else None,
        }
    
    def get_weighments(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get all weighments for a batch."""
        weighment_repo = AcceptanceWeighmentRepository(self.session)
        weighments = weighment_repo.get_by_batch(batch_id)
        return [
            {
                "id": w.id,
                "batch_id": w.batch_id,
                "gross_weight_kg": w.gross_weight_kg,
                "tare_weight_kg": w.tare_weight_kg,
                "net_weight_kg": w.net_weight_kg,
                "weigher_id": w.weigher_id,
                "recorded_at": w.recorded_at.isoformat() if w.recorded_at else None,
            }
            for w in weighments
        ]


class ReconciliationService:
    """Service for reconciling farmer-declared vs aggregator-measured quantities."""
    
    def __init__(self, session: Session):
        self.session = session
        self.recon_repo = ReconciliationRepository(session)
        self.weighment_repo = AcceptanceWeighmentRepository(session)
        self.batch_repo = HarvestBatchRepository(session)
    
    def reconcile_batch(self, batch_id: str, created_by: Optional[str] = None) -> Dict[str, Any]:
        """Reconcile a batch: compare farmer-declared vs aggregator-measured."""
        
        # Get the batch with its contributions
        result = self.batch_repo.get_batch_with_contributions(batch_id)
        if not result:
            raise ValueError(f"Batch {batch_id} not found")
        
        batch = result["batch"]
        contributions = result["contributions"]
        
        # Get expected total weight (from contributions)
        expected_total_kg = sum(c.contributed_weight_kg for c in contributions)
        
        # Get measured total weight (from weighments)
        measured_total_kg = self.weighment_repo.get_total_weight(batch_id)
        
        # Create reconciliation record
        record = self.recon_repo.create(
            batch_id=batch_id,
            expected_total_kg=expected_total_kg,
            measured_total_kg=measured_total_kg,
            created_by=created_by
        )
        self.session.commit()
        
        return {
            "id": record.id,
            "batch_id": record.batch_id,
            "expected_total_kg": record.expected_total_kg,
            "measured_total_kg": record.measured_total_kg,
            "difference_kg": record.difference_kg,
            "variance_pct": record.variance_pct,
            "recon_status": record.recon_status,
            "notes": record.notes,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
    
    def get_reconciliation(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get reconciliation records for a batch."""
        records = self.recon_repo.get_by_batch(batch_id)
        return [
            {
                "id": r.id,
                "batch_id": r.batch_id,
                "expected_total_kg": r.expected_total_kg,
                "measured_total_kg": r.measured_total_kg,
                "difference_kg": r.difference_kg,
                "variance_pct": r.variance_pct,
                "recon_status": r.recon_status,
                "notes": r.notes,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]


class SettlementService:
    """Service for calculating and processing split settlements."""
    
    def __init__(self, session: Session):
        self.session = session
        self.rule_repo = SettlementRuleRepository(session)
        self.summary_repo = SettlementSummaryRepository(session)
        self.split_repo = SplitSettlementRepository(session)
        self.batch_repo = HarvestBatchRepository(session)
    
    def create_settlement_rule(self, aggregator_id: str, name: str, split_method: str,
                                     **kwargs) -> Dict[str, Any]:
        """Create a new settlement rule."""
        rule = self.rule_repo.create(
            aggregator_id=aggregator_id,
            name=name,
            split_method=split_method,
            **kwargs
        )
        self.session.commit()
        
        return {
            "id": rule.id,
            "aggregator_id": rule.aggregator_id,
            "name": rule.name,
            "split_method": rule.split_method,
            "platform_fee_pct": rule.platform_fee_pct,
            "aggregator_commission_pct": rule.aggregator_commission_pct,
            "min_payout_threshold": rule.min_payout_threshold,
            "is_default": rule.is_default,
            "created_at": rule.created_at.isoformat() if rule.created_at else None,
        }
    
    def get_settlement_rules(self, aggregator_id: str) -> List[Dict[str, Any]]:
        """Get settlement rules for an aggregator."""
        rules = self.rule_repo.get_by_aggregator(aggregator_id)
        return [
            {
                "id": r.id,
                "aggregator_id": r.aggregator_id,
                "name": r.name,
                "split_method": r.split_method,
                "platform_fee_pct": r.platform_fee_pct,
                "aggregator_commission_pct": r.aggregator_commission_pct,
                "min_payout_threshold": r.min_payout_threshold,
                "is_default": r.is_default,
            }
            for r in rules
        ]
    
    def prepare_settlement(self, batch_id: str, aggregator_id: str, 
                               gross_sale_amount: float, 
                               rule_id: Optional[str] = None) -> Dict[str, Any]:
        """Prepare settlement for a batch."""
        
        # Get the batch with its contributions
        result = self.batch_repo.get_batch_with_contributions(batch_id)
        if not result:
            raise ValueError(f"Batch {batch_id} not found")
        
        contributions = result["contributions"]
        
        # Get settlement rule
        rule = None
        if rule_id:
            rule = self.rule_repo.get_by_id(rule_id)
        else:
            rule = self.rule_repo.get_default(aggregator_id)
        
        if not rule:
            raise ValueError("No settlement rule found")
        
        # Calculate totals
        total_weight = sum(c.contributed_weight_kg for c in contributions)
        
        # Calculate fees and commissions
        platform_fee = gross_sale_amount * (rule.platform_fee_pct / 100)
        commission = gross_sale_amount * (rule.aggregator_commission_pct / 100)
        net_to_distribute = gross_sale_amount - platform_fee - commission
        
        # Create settlement summary
        summary = self.summary_repo.create(
            batch_id=batch_id,
            aggregator_id=aggregator_id,
            gross_sale_amount=gross_sale_amount,
            total_platform_fee=platform_fee,
            total_commission=commission,
            net_to_distribute=net_to_distribute,
            settlement_rule_id=rule.id,
            status='PENDING'
        )
        
        # Create split settlements for each farmer
        for contribution in contributions:
            weight_share = contribution.contributed_weight_kg / total_weight if total_weight > 0 else 0
            share_amount = net_to_distribute * weight_share
            
            self.split_repo.create(
                settlement_summary_id=summary.id,
                contribution_id=contribution.id,
                farmer_id=contribution.farmer_id,
                contributed_weight_kg=contribution.contributed_weight_kg,
                share_amount=share_amount,
                status='PENDING'
            )
        
        self.session.commit()
        
        return {
            "id": summary.id,
            "batch_id": summary.batch_id,
            "aggregator_id": summary.aggregator_id,
            "gross_sale_amount": summary.gross_sale_amount,
            "total_platform_fee": summary.total_platform_fee,
            "total_commission": summary.total_commission,
            "net_to_distribute": summary.net_to_distribute,
            "status": summary.status,
            "settlement_rule_id": summary.settlement_rule_id,
            "created_at": summary.created_at.isoformat() if summary.created_at else None,
        }
    
    def get_settlement_summary(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """Get settlement summary with split settlements."""
        summary = self.summary_repo.get_by_id(summary_id)
        if not summary:
            return None
        
        splits = self.split_repo.get_by_summary(summary_id)
        
        return {
            "id": summary.id,
            "batch_id": summary.batch_id,
            "aggregator_id": summary.aggregator_id,
            "gross_sale_amount": summary.gross_sale_amount,
            "total_platform_fee": summary.total_platform_fee,
            "total_commission": summary.total_commission,
            "net_to_distribute": summary.net_to_distribute,
            "status": summary.status,
            "split_settlements": [
                {
                    "id": s.id,
                    "farmer_id": s.farmer_id,
                    "contributed_weight_kg": s.contributed_weight_kg,
                    "share_amount": s.share_amount,
                    "status": s.status,
                }
                for s in splits
            ],
            "created_at": summary.created_at.isoformat() if summary.created_at else None,
        }
    
    def update_split_status(self, split_id: str, status: str,
                                  payout_reference: Optional[str] = None,
                                  failure_reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update split settlement status."""
        split = self.split_repo.update_status(split_id, status, payout_reference, failure_reason)
        if not split:
            return None
        
        self.session.commit()
        
        return {
            "id": split.id,
            "status": split.status,
            "payout_reference": split.payout_reference,
            "paid_at": split.paid_at.isoformat() if split.paid_at else None,
        }
    
    def get_farmer_settlements(self, farmer_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all settlements for a farmer."""
        splits = self.split_repo.get_by_farmer(farmer_id, skip=skip, limit=limit)
        return [
            {
                "id": s.id,
                "settlement_summary_id": s.settlement_summary_id,
                "farmer_id": s.farmer_id,
                "contributed_weight_kg": s.contributed_weight_kg,
                "share_amount": s.share_amount,
                "currency": s.currency,
                "status": s.status,
                "payout_reference": s.payout_reference,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "paid_at": s.paid_at.isoformat() if s.paid_at else None,
            }
            for s in splits
        ]
