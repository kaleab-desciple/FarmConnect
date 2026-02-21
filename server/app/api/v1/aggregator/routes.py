"""Aggregator API routes for smallholder reconciliation and split settlement.

This module provides endpoints for managing:
- Aggregators: Collection centers that aggregate harvest from smallholders
- Weighments: Weight recording when smallholders deliver to aggregators
- Reconciliation: Comparing farmer-declared vs aggregator-measured quantities
- Settlements: Calculating and processing split payments to smallholders

Business Flow:
1. Smallholder delivers harvest to aggregator
2. Aggregator records weighment (gross - tare = net weight)
3. Batch is sealed and sold in marketplace
4. Reconciliation compares declared vs measured quantities
5. Settlement calculates fees and splits payment among farmers
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.application.services.aggregator_service import (
    AggregatorService,
    ReconciliationService,
    SettlementService,
)

router = APIRouter()


# ========================================
# Pydantic Models (Request/Response DTOs)
# ========================================

class AggregatorCreate(BaseModel):
    """Request model for creating an aggregator."""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the collection center")
    company_info: Optional[dict] = Field(None, description="Company registration details")
    contact: Optional[dict] = Field(None, description="Contact information (phone, email)")
    wallet_id: Optional[str] = Field(None, description="Payment wallet ID for settlements")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class AggregatorUpdate(BaseModel):
    """Request model for updating an aggregator."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    company_info: Optional[dict] = None
    contact: Optional[dict] = None
    wallet_id: Optional[str] = None
    kyc_status: Optional[str] = Field(None, description="KYC status: PENDING, VERIFIED, REJECTED")
    is_active: Optional[bool] = Field(None, description="Whether aggregator is active")


class WeighmentCreate(BaseModel):
    """Request model for recording a weighment.
    
    Business Logic:
    - net_weight = gross_weight - tare_weight
    - Multiple weighments can be recorded for a single batch
    - Weight is recorded in kilograms
    """
    batch_id: str = Field(..., description="Harvest batch ID being weighed")
    gross_weight_kg: float = Field(..., gt=0, description="Total weight including packaging (kg)")
    tare_weight_kg: float = Field(..., ge=0, description="Weight of empty packaging/container (kg)")
    weigher_id: Optional[str] = Field(None, description="User ID of person recording the weight")
    weighbridge_id: Optional[str] = Field(None, description="Weighbridge/equipment ID")
    receipt_url: Optional[str] = Field(None, description="URL to weighbridge receipt image/PDF")
    location: Optional[dict] = Field(None, description="GPS location where weighing occurred")


class SettlementRuleCreate(BaseModel):
    """Request model for creating a settlement rule.
    
    Business Logic:
    - Split methods determine how payment is divided among farmers:
      * BY_WEIGHT: Proportional to weight delivered
      * BY_VALUE: Proportional to value (weight × price)
      * FIXED_RATE: Fixed amount per kg
    - Platform fee: Percentage kept by FarmConnect
    - Aggregator commission: Percentage kept by collection center
    """
    aggregator_id: str = Field(..., description="Aggregator this rule belongs to")
    name: str = Field(..., min_length=1, max_length=100, description="Rule name")
    split_method: str = Field(..., pattern="^(BY_WEIGHT|BY_VALUE|FIXED_RATE)$", 
                               description="How to split payment among farmers")
    platform_fee_pct: float = Field(default=5.0, ge=0, le=100, 
                                    description="Platform fee percentage (0-100)")
    aggregator_commission_pct: float = Field(default=10.0, ge=0, le=100,
                                              description="Aggregator commission percentage (0-100)")
    min_payout_threshold: float = Field(default=10.0, ge=0,
                                        description="Minimum amount before payout is triggered")
    is_default: bool = Field(default=False, description="Use this as default rule if true")


class SettlementPrepare(BaseModel):
    """Request model for preparing a settlement.
    
    Business Logic:
    - Gross sale amount is the total amount received from buyer
    - Fees are deducted to calculate net amount for distribution
    - Each farmer receives share proportional to their contribution
    """
    batch_id: str = Field(..., description="Harvest batch that was sold")
    aggregator_id: str = Field(..., description="Aggregator handling the batch")
    gross_sale_amount: float = Field(..., gt=0, description="Total sale amount received")
    rule_id: Optional[str] = Field(None, description="Settlement rule ID (uses default if not provided)")


class SplitSettlementUpdate(BaseModel):
    """Request model for updating settlement payment status.
    
    Business Logic:
    - Status progression: PENDING → PREPARED → PAYMENT_SENT → PAID
    - On failure: status = FAILED with reason
    - After adjustment: status = ADJUSTED
    """
    status: str = Field(..., pattern="^(PENDING|PREPARED|PAYMENT_SENT|PAID|FAILED|ADJUSTED)$",
                        description="New payment status")
    payout_reference: Optional[str] = Field(None, description="Payment transaction reference")
    failure_reason: Optional[str] = Field(None, description="Reason if status is FAILED")


# ========================================
# Aggregator Management Endpoints
# ========================================

@router.post("/aggregators", status_code=status.HTTP_201_CREATED, 
             summary="Create Aggregator",
             description="""Create a new aggregator (collection center).
             
             An aggregator is a collection point where smallholders deliver their harvest.
             The aggregator is responsible for weighing, quality checking, and reconciling
             deliveries before forwarding to the marketplace.
             """)
def create_aggregator(
    data: AggregatorCreate,
    db: Session = Depends(get_db)
):
    """Create a new aggregator collection center."""
    service = AggregatorService(db)
    return service.create_aggregator(
        name=data.name,
        company_info=data.company_info,
        contact=data.contact,
        wallet_id=data.wallet_id,
        metadata=data.metadata,
    )


@router.get("/aggregators", 
            summary="List Aggregators",
            description="""List all aggregators with pagination.
            
            Returns active collection centers that can receive farmer deliveries.
            """)
def list_aggregators(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """List all aggregators."""
    service = AggregatorService(db)
    return service.list_aggregators(skip=skip, limit=limit)


@router.get("/aggregators/{aggregator_id}", 
            summary="Get Aggregator",
            description="Get details of a specific aggregator by ID.")
def get_aggregator(
    aggregator_id: str,
    db: Session = Depends(get_db)
):
    """Get an aggregator by ID."""
    service = AggregatorService(db)
    aggregator = service.get_aggregator(aggregator_id)
    if not aggregator:
        raise HTTPException(status_code=404, detail="Aggregator not found")
    return aggregator


@router.patch("/aggregators/{aggregator_id}", 
             summary="Update Aggregator",
             description="Update aggregator details. All fields are optional - only provided fields are updated.")
def update_aggregator(
    aggregator_id: str,
    data: AggregatorUpdate,
    db: Session = Depends(get_db)
):
    """Update an aggregator."""
    service = AggregatorService(db)
    update_data = data.model_dump(exclude_unset=True)
    aggregator = service.update_aggregator(aggregator_id, **update_data)
    if not aggregator:
        raise HTTPException(status_code=404, detail="Aggregator not found")
    return aggregator


# ========================================
# Weighment Recording Endpoints
# ========================================

@router.post("/weighments", status_code=status.HTTP_201_CREATED,
             summary="Record Weighment",
             description="""Record the weight of a delivery when a smallholder brings harvest to the aggregator.
             
             Business Logic:
             - net_weight = gross_weight - tare_weight
             - Multiple deliveries can be recorded for the same batch
             - Creates audit trail of all weighings
             """)
def record_weighment(
    data: WeighmentCreate,
    db: Session = Depends(get_db)
):
    """Record a weighment for a batch.
    
    This is the first step in the reconciliation process.
    Smallholder brings harvest → aggregator weighs it → net weight is calculated.
    """
    service = AggregatorService(db)
    return service.record_weighment(
        batch_id=data.batch_id,
        gross_weight_kg=data.gross_weight_kg,
        tare_weight_kg=data.tare_weight_kg,
        weigher_id=data.weigher_id,
        weighbridge_id=data.weighbridge_id,
        receipt_url=data.receipt_url,
        location=data.location,
    )


@router.get("/batches/{batch_id}/weighments",
           summary="Get Batch Weighments",
           description="""Get all weighments recorded for a specific harvest batch.
           
           Returns chronological list of all deliveries to the aggregator.
           """)
def get_weighments(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Get all weighments for a batch."""
    service = AggregatorService(db)
    return service.get_weighments(batch_id)


# ========================================
# Reconciliation Endpoints
# ========================================

@router.post("/batches/{batch_id}/reconcile", status_code=status.HTTP_201_CREATED,
            summary="Reconcile Batch",
            description="""Reconcile a batch by comparing farmer-declared quantity vs aggregator-measured.
            
            Business Logic:
            1. Sum all harvest event contributions = declared_weight
            2. Sum all acceptance weighments = measured_weight
            3. Calculate variance = measured - declared
            4. Determine status based on variance percentage:
               - ≤2%: OK (proceed normally)
               - 2-5%: WARNING (review required)
               - >5%: DISPUTE (manual intervention)
            """)
def reconcile_batch(
    batch_id: str,
    created_by: Optional[str] = Query(None, description="User performing reconciliation"),
    db: Session = Depends(get_db)
):
    """Reconcile a batch: compare farmer-declared vs aggregator-measured.
    
    This compares:
    - Expected: sum of farmer-declared contributions in the harvest batch
    - Measured: sum of weighments recorded at the aggregator
    
    Large variances may indicate:
    - Post-harvest losses
    - Quality issues (水分 loss)
    - Recording errors
    - Fraud
    """
    service = ReconciliationService(db)
    try:
        return service.reconcile_batch(batch_id, created_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/batches/{batch_id}/reconciliation",
           summary="Get Reconciliation Records",
           description="Get all reconciliation records for a batch (history of all reconciliations).")
def get_reconciliation(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Get reconciliation records for a batch."""
    service = ReconciliationService(db)
    return service.get_reconciliation(batch_id)


# ========================================
# Settlement Rule Endpoints
# ========================================

@router.post("/settlement-rules", status_code=status.HTTP_201_CREATED,
            summary="Create Settlement Rule",
            description="""Create a rule for splitting payments among smallholders.
            
            Business Logic:
            - BY_WEIGHT: Each farmer gets (their_weight / total_weight) × net_amount
            - BY_VALUE: Each farmer gets (their_value / total_value) × net_amount
            - FIXED_RATE: Each farmer gets weight × rate_per_kg
            
            Deductions from gross sale:
            - platform_fee = gross × platform_fee_pct
            - aggregator_commission = gross × aggregator_commission_pct
            - net_to_distribute = gross - platform_fee - commission
            """)
def create_settlement_rule(
    data: SettlementRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new settlement rule."""
    service = SettlementService(db)
    return service.create_settlement_rule(
        aggregator_id=data.aggregator_id,
        name=data.name,
        split_method=data.split_method,
        platform_fee_pct=data.platform_fee_pct,
        aggregator_commission_pct=data.aggregator_commission_pct,
        min_payout_threshold=data.min_payout_threshold,
        is_default=data.is_default,
    )


@router.get("/aggregators/{aggregator_id}/settlement-rules",
           summary="Get Settlement Rules",
           description="Get all settlement rules defined for an aggregator.")
def get_settlement_rules(
    aggregator_id: str,
    db: Session = Depends(get_db)
):
    """Get settlement rules for an aggregator."""
    service = SettlementService(db)
    return service.get_settlement_rules(aggregator_id)


# ========================================
# Settlement Processing Endpoints
# ========================================

@router.post("/settlements/prepare", status_code=status.HTTP_201_CREATED,
            summary="Prepare Settlement",
            description="""Prepare settlement calculation for a sold batch.
            
            Business Logic:
            1. Get all farmer contributions to the batch
            2. Calculate gross_amount - fees = net_to_distribute
            3. Split net amount among farmers based on rule:
               - BY_WEIGHT: proportional to delivered weight
               - BY_VALUE: proportional to crop value
               - FIXED_RATE: weight × fixed rate
            4. Create settlement summary + individual split records
            
            Note: This only PREPARES the calculation. Payment processing
            happens separately via update_split_status.
            """)
def prepare_settlement(
    data: SettlementPrepare,
    db: Session = Depends(get_db)
):
    """Prepare settlement for a batch.
    
    Called after batch is sold in the marketplace.
    Calculates each farmer's share based on their contribution.
    """
    service = SettlementService(db)
    try:
        return service.prepare_settlement(
            batch_id=data.batch_id,
            aggregator_id=data.aggregator_id,
            gross_sale_amount=data.gross_sale_amount,
            rule_id=data.rule_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/settlements/{summary_id}",
           summary="Get Settlement Summary",
           description="Get complete settlement details including all farmer splits.")
def get_settlement_summary(
    summary_id: str,
    db: Session = Depends(get_db)
):
    """Get settlement summary with split settlements."""
    service = SettlementService(db)
    summary = service.get_settlement_summary(summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Settlement summary not found")
    return summary


@router.patch("/settlements/{split_id}/status",
             summary="Update Payment Status",
             description="""Update the payment status for a smallholder's split settlement.
             
             Status Flow:
             PENDING → PREPARED → PAYMENT_SENT → PAID
             (or FAILED at any point requiring retry)
             (or ADJUSTED if amount needs correction)
             """)
def update_split_status(
    split_id: str,
    data: SplitSettlementUpdate,
    db: Session = Depends(get_db)
):
    """Update split settlement status.
    
    This is called by the payment integration when:
    - Payment is initiated (→ PAYMENT_SENT)
    - Payment succeeds (→ PAID, with payout_reference)
    - Payment fails (→ FAILED, with failure_reason)
    """
    service = SettlementService(db)
    split = service.update_split_status(
        split_id=split_id,
        status=data.status,
        payout_reference=data.payout_reference,
        failure_reason=data.failure_reason,
    )
    if not split:
        raise HTTPException(status_code=404, detail="Split settlement not found")
    return split


@router.get("/farmers/{farmer_id}/settlements",
           summary="Get Farmer Settlements",
           description="""Get all settlement payments for a specific farmer.
            
            Allows farmers to view their payment history across all batches.
            """)
def get_farmer_settlements(
    farmer_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """Get all settlements for a farmer."""
    service = SettlementService(db)
    return service.get_farmer_settlements(farmer_id, skip=skip, limit=limit)
