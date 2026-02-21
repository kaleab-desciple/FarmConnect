"""QC Service for quality control evaluation and signature verification.

This service provides:
- QC grade evaluation based on configurable rules
- Signature verification for lab reports
- QC workflow orchestration
"""
import hashlib
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.infrastructure.repositories.qc_repo import QCRepository
from app.infrastructure.repositories.harvest_batch_repo import HarvestBatchRepository
from app.domain.harvest.entities import (
    BatchQCReportV2Create,
    SampleCreate,
    LabProviderCreate,
    HarvestBatchState,
    HarvestBatch,
)
from app.domain.common.enums import QCGrade

logger = logging.getLogger(__name__)


class QCService:
    """Service for QC evaluation and lab report processing."""
    
    def __init__(self, db: Session):
        self.db = db
        self.qc_repo = QCRepository(db)
        self.batch_repo = HarvestBatchRepository(db)
    
    # ========================================
    # Lab Webhook Processing
    # ========================================
    
    def process_lab_webhook(
        self,
        lab_id: str,
        sample_id: Optional[str],
        batch_id: str,
        tested_at: datetime,
        metrics: Dict[str, float],
        report_url: Optional[str],
        signed_hash: Optional[str],
    ) -> Tuple[Dict[str, Any], bool, Optional[str]]:
        """
        Process a lab webhook and create a QC report.
        
        Args:
            lab_id: The lab provider ID
            sample_id: The sample ID (if exists)
            batch_id: The harvest batch ID
            tested_at: When the test was performed
            metrics: The test metrics (e.g., {"moisture_pct": 12.4, "aflatoxin_ppb": 3.4})
            report_url: URL to the full report
            signed_hash: Lab-supplied signature or hash
        
        Returns:
            Tuple of (report_dict, success, error_message)
        """
        # 1. Validate lab exists
        lab = self.qc_repo.get_lab_provider_by_id(lab_id)
        if not lab:
            return {"error": "Lab not found"}, False, "LAB_NOT_FOUND"
        
        # 2. Validate batch exists and is in SEALED or QC_PENDING state
        batch = self.batch_repo.get_batch_by_id(batch_id)
        if not batch:
            return {"error": "Batch not found"}, False, "BATCH_NOT_FOUND"
        
        if batch.status not in [HarvestBatchState.SEALED, HarvestBatchState.QC_PENDING]:
            return {
                "error": f"Batch is in {batch.status} state, cannot accept QC reports"
            }, False, f"INVALID_BATCH_STATE_{batch.status}"
        
        # 3. Check for idempotent report
        existing_report = self.qc_repo.check_idempotent_report(
            sample_id=sample_id,
            lab_id=lab_id,
            tested_at=tested_at,
        )
        if existing_report:
            return {
                "id": str(existing_report.id),
                "message": "Report already exists (idempotent)"
            }, True, None
        
        # 4. Get commodity from batch metadata or default
        commodity = batch.metadata.get("commodity", "maize") if batch.metadata else "maize"
        
        # 5. Evaluate grade
        grade, passed = self.evaluate_grade(commodity, metrics)
        
        # 6. Verify signature if public key exists
        verified = False
        if lab.public_key and signed_hash:
            verified = self.verify_signature(
                payload={
                    "batch_id": batch_id,
                    "sample_id": sample_id,
                    "tested_at": tested_at.isoformat(),
                    "metrics": metrics,
                },
                signed_hash=signed_hash,
                public_key=lab.public_key,
            )
        elif signed_hash:
            # No public key but has hash - mark as unverified for manual review
            verified = False
            logger.warning(f"Lab {lab_id} has no public key, signature verification skipped")
        
        # 7. Create QC report
        report_create = BatchQCReportV2Create(
            batch_id=UUID(batch_id),
            sample_id=UUID(sample_id) if sample_id else None,
            lab_id=lab_id,
            tested_at=tested_at,
            metrics=metrics,
            grade=grade,
            passed=passed,
            report_url=report_url,
            signed_hash=signed_hash,
            verified=verified,
            notes=None,
        )
        
        report = self.qc_repo.create_qc_report(report_create)
        
        return {
            "id": str(report.id),
            "batch_id": str(report.batch_id),
            "grade": report.grade,
            "passed": report.passed,
            "verified": report.verified,
            "tested_at": report.tested_at.isoformat(),
        }, True, None
    
    # ========================================
    # Grade Evaluation
    # ========================================
    
    def evaluate_grade(
        self, 
        commodity: str, 
        metrics: Dict[str, float]
    ) -> Tuple[str, bool]:
        """
        Evaluate grade based on configurable rules.
        
        Rules are evaluated in order: GRADE_A -> GRADE_B -> GRADE_C -> REJECT
        The first grade whose rules all pass is assigned.
        
        Args:
            commodity: The commodity type (e.g., "maize", "wheat")
            metrics: The test metrics
        
        Returns:
            Tuple of (grade, passed)
        """
        rules = self.qc_repo.get_grade_rules_by_commodity(commodity)
        
        if not rules:
            # Fallback to default rules if none configured
            logger.warning(f"No rules found for commodity {commodity}, using defaults")
            return self._evaluate_default_grade(metrics)
        
        for rule in rules:
            if self._check_rules(rule.rules, metrics):
                # Determine if passed based on grade
                passed = rule.grade != QCGrade.REJECT.value
                return rule.grade, passed
        
        # If no rules pass, reject
        return QCGrade.REJECT.value, False
    
    def _check_rules(self, rule_defs: List[Dict[str, Any]], metrics: Dict[str, float]) -> bool:
        """Check if all rule definitions pass for the given metrics."""
        for rule in rule_defs:
            metric = rule.get("metric")
            operator = rule.get("op")
            threshold = rule.get("value")
            
            if metric not in metrics:
                return False
            
            actual = metrics[metric]
            
            if operator == "<=":
                if not actual <= threshold:
                    return False
            elif operator == "<":
                if not actual < threshold:
                    return False
            elif operator == ">=":
                if not actual >= threshold:
                    return False
            elif operator == ">":
                if not actual > threshold:
                    return False
            elif operator == "==":
                if not actual == threshold:
                    return False
            elif operator == "!=":
                if not actual != threshold:
                    return False
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        
        return True
    
    def _evaluate_default_grade(self, metrics: Dict[str, float]) -> Tuple[str, bool]:
        """Fallback default grade evaluation."""
        # Default maize rules
        moisture = metrics.get("moisture_pct", 100)
        aflatoxin = metrics.get("aflatoxin_ppb", float('inf'))
        
        if moisture <= 13.0 and aflatoxin <= 5:
            return QCGrade.GRADE_A.value, True
        elif moisture <= 14.0 and aflatoxin <= 10:
            return QCGrade.GRADE_B.value, True
        elif moisture <= 15.0 and aflatoxin <= 20:
            return QCGrade.GRADE_C.value, True
        else:
            return QCGrade.REJECT.value, False
    
    # ========================================
    # Signature Verification
    # ========================================
    
    def verify_signature(
        self,
        payload: Dict[str, Any],
        signed_hash: str,
        public_key: str,
    ) -> bool:
        """
        Verify the signature of a lab report.
        
        Args:
            payload: The original payload
            signed_hash: The signature/hash provided by lab
            public_key: The PEM public key of the lab
        
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Compute canonical hash of payload
            canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            computed_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
            
            # For now, simple hash comparison (in production, use proper RSA/ECDSA)
            # The signed_hash format could be: "sha256:abcdef..." or just the hash
            if signed_hash.startswith("sha256:"):
                provided_hash = signed_hash[7:]  # Remove "sha256:" prefix
            else:
                provided_hash = signed_hash
            
            return computed_hash == provided_hash
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    # ========================================
    # Sample Management
    # ========================================
    
    def create_sample(
        self,
        sample_code: str,
        harvest_batch_id: str,
        collected_by: Optional[str],
        sample_points: Optional[Dict[str, Any]],
        photos: Optional[List[Dict[str, Any]]],
        chain_of_custody: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a new sample for QC testing."""
        # Validate batch exists
        batch = self.batch_repo.get_batch_by_id(harvest_batch_id)
        if not batch:
            raise ValueError("Batch not found")
        
        if batch.status != HarvestBatchState.SEALED:
            raise ValueError(f"Cannot create sample for batch in {batch.status} state")
        
        sample = self.qc_repo.create_sample(SampleCreate(
            sample_code=sample_code,
            harvest_batch_id=UUID(harvest_batch_id),
            collected_by=collected_by,
            collected_at=datetime.now(timezone.utc),
            sample_points=sample_points,
            photos=photos,
            chain_of_custody=chain_of_custody,
            submitted_to_lab=False,
        ))
        
        return {
            "id": str(sample.id),
            "sample_code": sample.sample_code,
            "harvest_batch_id": str(sample.harvest_batch_id),
            "submitted_to_lab": sample.submitted_to_lab,
            "created_at": sample.created_at.isoformat(),
        }
    
    # ========================================
    # Lab Provider Management
    # ========================================
    
    def create_lab_provider(
        self,
        name: str,
        public_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new lab provider."""
        lab = self.qc_repo.create_lab_provider(LabProviderCreate(
            name=name,
            public_key=public_key,
            metadata=metadata,
        ))
        
        return {
            "id": str(lab.id),
            "name": lab.name,
            "public_key": lab.public_key is not None,
            "created_at": lab.created_at.isoformat(),
        }
    
    # ========================================
    # Listing Validation
    # ========================================
    
    def validate_batch_for_listing(
        self,
        batch_id: str,
        require_lab_test: bool = True,
        require_verified: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a batch can be used for product listing.
        
        Args:
            batch_id: The harvest batch ID
            require_lab_test: Whether lab test is required for this commodity
            require_verified: Whether signature verification is required
        
        Returns:
            Tuple of (is_valid, error_code)
        """
        batch = self.batch_repo.get_batch_by_id(batch_id)
        if not batch:
            return False, "BATCH_NOT_FOUND"
        
        # Check batch is sealed
        if batch.status != HarvestBatchState.SEALED:
            # Allow QC_PASSED as well (backward compatibility)
            if batch.status not in [HarvestBatchState.SEALED, HarvestBatchState.QC_PASSED]:
                return False, "MISSING_SEAL"
        
        # If lab test required, check for valid QC report
        if require_lab_test:
            has_valid_report = self.qc_repo.has_valid_qc_report(
                batch_id, 
                require_verified=require_verified
            )
            if not has_valid_report:
                if require_verified:
                    return False, "QC_UNVERIFIED"
                return False, "MISSING_QC_REPORT"
        
        return True, None
    
    def validate_multiple_batches_for_listing(
        self,
        batch_ids: List[str],
        require_lab_test: bool = True,
        require_verified: bool = False,
    ) -> Tuple[bool, List[str]]:
        """
        Validate multiple batches for product listing.
        
        Returns:
            Tuple of (all_valid, error_codes)
        """
        errors = []
        
        for batch_id in batch_ids:
            valid, error = self.validate_batch_for_listing(
                batch_id,
                require_lab_test=require_lab_test,
                require_verified=require_verified,
            )
            if not valid:
                errors.append(f"{batch_id}:{error}")
        
        return len(errors) == 0, errors
