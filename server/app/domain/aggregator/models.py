"""
Aggregator domain models for smallholder reconciliation and split settlement.

These models represent:
- Aggregator: Collection center that collects harvest from smallholders
- AcceptanceWeighment: Weight recording at aggregator entry
- ReconciliationRecord: Comparison of farmer-declared vs aggregator-measured
- SettlementRule: Rules for splitting payments among smallholders
- AggregatorSettlementSummary: Summary of all settlements for a batch
- SplitSettlement: Individual smallholder's payment calculation
- SmallholderPayment: Payment record for each smallholder
"""

from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List
from dataclasses import dataclass, field

from app.domain.common.enums import (
    ReconciliationStatus,
    SettlementStatus,
    SettlementMethod,
    WeighmentType,
    SmallholderPaymentStatus,
    QualityGrade,
)


@dataclass
class Aggregator:
    """Aggregator entity - collection center that collects harvest from smallholders."""
    id: Optional[str] = None
    name: str = ""
    code: str = ""
    description: Optional[str] = None
    location: Optional[dict] = None  # GeoJSON
    operator_id: Optional[str] = None  # User who operates this aggregator
    is_active: bool = True
    min_quality_grade: Optional[QualityGrade] = None
    max_weight_per_delivery: Optional[Decimal] = None  # in kg
    operating_hours: Optional[str] = None  # e.g., "08:00-18:00"
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AcceptanceWeighment:
    """Weight recording when smallholder delivers harvest to aggregator."""
    id: Optional[str] = None
    aggregator_id: str = ""
    smallholder_id: str = ""  # farmer_id
    batch_id: Optional[str] = None  # Reference to harvest batch if available
    weighment_type: WeighmentType = WeighmentType.INITIAL
    gross_weight: Decimal = Decimal(0)  # Weight with packaging
    tare_weight: Decimal = Decimal(0)  # Weight of packaging/container
    net_weight: Decimal = Decimal(0)  # gross_weight - tare_weight
    moisture_content: Optional[Decimal] = None  # Percentage
    quality_grade: Optional[QualityGrade] = None
    quality_score: Optional[Decimal] = None  # 0-100
    remarks: Optional[str] = None
    Weighment_image_urls: Optional[List[str]] = None
    recorded_by: Optional[str] = None
    verified_by: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None


@dataclass
class ReconciliationRecord:
    """Reconciliation between farmer-declared quantity and aggregator-measured quantity."""
    id: Optional[str] = None
    aggregator_id: str = ""
    batch_id: Optional[str] = None
    reconciliation_date: Optional[date] = None
    
    # Farmer declared (from harvest batch)
    declared_total_weight: Decimal = Decimal(0)
    declared_count: int = 0
    
    # Aggregator measured (from acceptance weighments)
    measured_total_weight: Decimal = Decimal(0)
    measured_count: int = 0
    
    # Variance
    weight_variance: Decimal = Decimal(0)
    variance_percentage: Decimal = Decimal(0)
    
    # Status
    status: ReconciliationStatus = ReconciliationStatus.PENDING
    notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SettlementRule:
    """Rules for splitting payments among smallholders."""
    id: Optional[str] = None
    aggregator_id: str = ""
    name: str = ""
    description: Optional[str] = None
    
    # Settlement method
    method: SettlementMethod = SettlementMethod.BY_WEIGHT
    
    # Parameters for each method
    # For BY_WEIGHT: proportional by net weight delivered
    # For BY_VALUE: proportional by crop value (weight * quality-adjusted price)
    # For FIXED_RATE: fixed rate per kg regardless of weight
    # For TIERED: different rates based on quality grade
    
    fixed_rate_per_kg: Optional[Decimal] = None  # For FIXED_RATE method
    
    # Tiered rates (for TIERED method)
    tier_premium: Optional[Decimal] = None  # Premium per kg for PREMIUM grade
    tier_grade_a: Optional[Decimal] = None   # Rate per kg for GRADE_A
    tier_grade_b: Optional[Decimal] = None   # Rate per kg for GRADE_B
    tier_grade_c: Optional[Decimal] = None   # Rate per kg for GRADE_C
    
    # Deductions
    aggregator_fee_percentage: Decimal = Decimal(0)  # Aggregator service fee
    quality_penalty_percentage: Decimal = Decimal(0)  # Penalty for below-standard quality
    
    # Processing
    processing_fee_fixed: Optional[Decimal] = None
    processing_fee_percentage: Optional[Decimal] = None
    
    is_active: bool = True
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AggregatorSettlementSummary:
    """Summary of settlement for a batch at an aggregator."""
    id: Optional[str] = None
    aggregator_id: str = ""
    batch_id: Optional[str] = None
    settlement_rule_id: Optional[str] = None
    
    # Totals
    total_smallholders: int = 0
    total_gross_weight: Decimal = Decimal(0)
    total_net_weight: Decimal = Decimal(0)
    
    # Financials
    gross_amount: Decimal = Decimal(0)  # Before deductions
    aggregator_fee: Decimal = Decimal(0)
    processing_fees: Decimal = Decimal(0)
    quality_penalties: Decimal = Decimal(0)
    net_amount: Decimal = Decimal(0)  # To be distributed
    
    currency: str = "USD"
    
    # Reconciliation
    reconciliation_id: Optional[str] = None
    
    # Status
    status: SettlementStatus = SettlementStatus.PENDING
    prepared_by: Optional[str] = None
    prepared_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SplitSettlement:
    """Individual smallholder's share from the settlement."""
    id: Optional[str] = None
    settlement_summary_id: str = ""
    smallholder_id: str = ""  # farmer_id
    
    # Weight details
    net_weight: Decimal = Decimal(0)
    quality_grade: Optional[QualityGrade] = None
    
    # Calculations
    base_rate: Decimal = Decimal(0)
    quality_adjustment: Decimal = Decimal(0)
    subtotal: Decimal = Decimal(0)
    
    # Deductions
    aggregator_fee: Decimal = Decimal(0)
    processing_fee: Decimal = Decimal(0)
    quality_penalty: Decimal = Decimal(0)
    other_deductions: Decimal = Decimal(0)
    
    # Final
    gross_amount: Decimal = Decimal(0)
    deduction_total: Decimal = Decimal(0)
    net_amount: Decimal = Decimal(0)
    
    currency: str = "USD"
    
    # Status
    payment_status: SmallholderPaymentStatus = SmallholderPaymentStatus.PENDING
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SmallholderPayment:
    """Payment record for smallholder after settlement processing."""
    id: Optional[str] = None
    split_settlement_id: str = ""
    settlement_summary_id: str = ""
    smallholder_id: str = ""
    aggregator_id: str = ""
    
    # Amount
    amount: Decimal = Decimal(0)
    currency: str = "USD"
    
    # Payment details
    payment_method: Optional[str] = None  # BANK_TRANSFER, MOBILE_MONEY, CASH
    payment_reference: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    mobile_money_number: Optional[str] = None
    
    # Status tracking
    status: SmallholderPaymentStatus = SmallholderPaymentStatus.PENDING
    initiated_by: Optional[str] = None
    initiated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    
    # Metadata
    notes: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
