"""QC Repository for quality control and lab management.

This repository provides:
- LabProvider CRUD operations
- Sample (sampling request) CRUD operations
- BatchQCReport CRUD operations
- Certification CRUD operations
- QCGradeRule management
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.infrastructure.db.models.harvest import (
    LabProviderORM,
    SampleORM,
    BatchQCReportV2ORM,
    CertificationORM,
    QCGradeRuleORM,
    HarvestBatchORM,
)
from app.domain.harvest.entities import (
    LabProvider,
    LabProviderCreate,
    Sample,
    SampleCreate,
    BatchQCReportV2,
    BatchQCReportV2Create,
    Certification,
    CertificationCreate,
    QCGradeRule,
    QCGradeRuleCreate,
    HarvestBatchState,
)
from app.domain.common.enums import QCGrade


class QCRepository:
    """Repository for QC and lab management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================
    # LabProvider Operations
    # ========================================
    
    def create_lab_provider(self, lab: LabProviderCreate) -> LabProvider:
        """Create a new lab provider."""
        orm = LabProviderORM(
            id=str(uuid4()),
            name=lab.name,
            public_key=lab.public_key,
            metadata_=lab.metadata,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._orm_to_lab_provider(orm)
    
    def get_lab_provider_by_id(self, lab_id: str) -> Optional[LabProvider]:
        """Get a lab provider by ID."""
        orm = self.db.query(LabProviderORM).filter(LabProviderORM.id == lab_id).first()
        return self._orm_to_lab_provider(orm) if orm else None
    
    def get_lab_provider_by_name(self, name: str) -> Optional[LabProvider]:
        """Get a lab provider by name."""
        orm = self.db.query(LabProviderORM).filter(LabProviderORM.name == name).first()
        return self._orm_to_lab_provider(orm) if orm else None
    
    def get_all_lab_providers(self) -> List[LabProvider]:
        """Get all lab providers."""
        orms = self.db.query(LabProviderORM).all()
        return [self._orm_to_lab_provider(orm) for orm in orms]
    
    def update_lab_provider(self, lab_id: str, **kwargs) -> Optional[LabProvider]:
        """Update a lab provider."""
        orm = self.db.query(LabProviderORM).filter(LabProviderORM.id == lab_id).first()
        if not orm:
            return None
        
        for key, value in kwargs.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        
        self.db.commit()
        self.db.refresh(orm)
        return self._orm_to_lab_provider(orm)
    
    # ========================================
    # Sample Operations
    # ========================================
    
    def create_sample(self, sample: SampleCreate) -> Sample:
        """Create a new sample."""
        orm = SampleORM(
            id=str(uuid4()),
            sample_code=sample.sample_code,
            harvest_batch_id=str(sample.harvest_batch_id),
            collected_by=sample.collected_by,
            collected_at=sample.collected_at,
            sample_points=sample.sample_points,
            photos=sample.photos,
            chain_of_custody=sample.chain_of_custody,
            submitted_to_lab=sample.submitted_to_lab,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._orm_to_sample(orm)
    
    def get_sample_by_id(self, sample_id: str) -> Optional[Sample]:
        """Get a sample by ID."""
        orm = self.db.query(SampleORM).filter(SampleORM.id == sample_id).first()
        return self._orm_to_sample(orm) if orm else None
    
    def get_sample_by_code(self, sample_code: str) -> Optional[Sample]:
        """Get a sample by sample code."""
        orm = self.db.query(SampleORM).filter(SampleORM.sample_code == sample_code).first()
        return self._orm_to_sample(orm) if orm else None
    
    def get_samples_by_batch(self, batch_id: str) -> List[Sample]:
        """Get all samples for a batch."""
        orms = self.db.query(SampleORM).filter(SampleORM.harvest_batch_id == batch_id).all()
        return [self._orm_to_sample(orm) for orm in orms]
    
    def mark_sample_submitted(self, sample_id: str) -> Optional[Sample]:
        """Mark a sample as submitted to lab."""
        orm = self.db.query(SampleORM).filter(SampleORM.id == sample_id).first()
        if not orm:
            return None
        
        orm.submitted_to_lab = True
        self.db.commit()
        self.db.refresh(orm)
        return self._orm_to_sample(orm)
    
    # ========================================
    # BatchQCReport Operations
    # ========================================
    
    def create_qc_report(self, report: BatchQCReportV2Create) -> BatchQCReportV2:
        """Create a new QC report."""
        orm = BatchQCReportV2ORM(
            id=str(uuid4()),
            batch_id=str(report.batch_id),
            sample_id=str(report.sample_id) if report.sample_id else None,
            lab_id=report.lab_id,
            tested_at=report.tested_at,
            metrics=report.metrics,
            grade=report.grade,
            passed=report.passed,
            report_url=report.report_url,
            signed_hash=report.signed_hash,
            verified=report.verified,
            notes=report.notes,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        
        # Update harvest batch status
        self._update_batch_status(str(report.batch_id), report.passed)
        
        return self._orm_to_qc_report(orm)
    
    def get_qc_report_by_id(self, report_id: str) -> Optional[BatchQCReportV2]:
        """Get a QC report by ID."""
        orm = self.db.query(BatchQCReportV2ORM).filter(BatchQCReportV2ORM.id == report_id).first()
        return self._orm_to_qc_report(orm) if orm else None
    
    def get_qc_reports_by_batch(self, batch_id: str) -> List[BatchQCReportV2]:
        """Get all QC reports for a batch."""
        orms = self.db.query(BatchQCReportV2ORM).filter(
            BatchQCReportV2ORM.batch_id == batch_id
        ).order_by(BatchQCReportV2ORM.tested_at.desc()).all()
        return [self._orm_to_qc_report(orm) for orm in orms]
    
    def get_latest_qc_report(self, batch_id: str) -> Optional[BatchQCReportV2]:
        """Get the latest QC report for a batch."""
        orm = self.db.query(BatchQCReportV2ORM).filter(
            BatchQCReportV2ORM.batch_id == batch_id
        ).order_by(BatchQCReportV2ORM.tested_at.desc()).first()
        return self._orm_to_qc_report(orm) if orm else None
    
    def check_idempotent_report(
        self, 
        sample_id: Optional[str], 
        lab_id: Optional[str], 
        tested_at: datetime
    ) -> Optional[BatchQCReportV2]:
        """Check if a QC report already exists for idempotency."""
        query = self.db.query(BatchQCReportV2ORM)
        
        if sample_id:
            query = query.filter(BatchQCReportV2ORM.sample_id == sample_id)
        if lab_id:
            query = query.filter(BatchQCReportV2ORM.lab_id == lab_id)
        
        # Within 1 minute tolerance for tested_at
        from datetime import timedelta
        time_window = timedelta(minutes=1)
        query = query.filter(
            func.abs(func.extract('epoch', BatchQCReportV2ORM.tested_at) - 
                    func.extract('epoch', tested_at)) < 60
        )
        
        orm = query.first()
        return self._orm_to_qc_report(orm) if orm else None
    
    def has_valid_qc_report(self, batch_id: str, require_verified: bool = False) -> bool:
        """Check if a batch has a valid QC report."""
        query = self.db.query(BatchQCReportV2ORM).filter(
            BatchQCReportV2ORM.batch_id == batch_id,
            BatchQCReportV2ORM.passed == True
        )
        
        if require_verified:
            query = query.filter(BatchQCReportV2ORM.verified == True)
        
        return query.first() is not None
    
    # ========================================
    # Certification Operations
    # ========================================
    
    def create_certification(self, cert: CertificationCreate) -> Certification:
        """Create a new certification."""
        orm = CertificationORM(
            id=str(uuid4()),
            harvest_batch_id=str(cert.harvest_batch_id),
            issuer=cert.issuer,
            cert_type=cert.cert_type,
            cert_number=cert.cert_number,
            valid_from=cert.valid_from,
            valid_to=cert.valid_to,
            cert_url=cert.cert_url,
            signed_hash=cert.signed_hash,
            metadata_=cert.metadata,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._orm_to_certification(orm)
    
    def get_certification_by_id(self, cert_id: str) -> Optional[Certification]:
        """Get a certification by ID."""
        orm = self.db.query(CertificationORM).filter(CertificationORM.id == cert_id).first()
        return self._orm_to_certification(orm) if orm else None
    
    def get_certifications_by_batch(self, batch_id: str) -> List[Certification]:
        """Get all certifications for a batch."""
        orms = self.db.query(CertificationORM).filter(
            CertificationORM.harvest_batch_id == batch_id
        ).all()
        return [self._orm_to_certification(orm) for orm in orms]
    
    def get_valid_certifications(self, batch_id: str) -> List[Certification]:
        """Get all valid (non-expired) certifications for a batch."""
        now = datetime.now(timezone.utc)
        orms = self.db.query(CertificationORM).filter(
            CertificationORM.harvest_batch_id == batch_id,
            CertificationORM.valid_from <= now,
            CertificationORM.valid_to >= now,
        ).all()
        return [self._orm_to_certification(orm) for orm in orms]
    
    # ========================================
    # QC Grade Rule Operations
    # ========================================
    
    def create_grade_rule(self, rule: QCGradeRuleCreate) -> QCGradeRule:
        """Create a new QC grade rule."""
        orm = QCGradeRuleORM(
            id=str(uuid4()),
            commodity=rule.commodity,
            grade=rule.grade,
            rules=rule.rules,
            is_active=rule.is_active,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._orm_to_grade_rule(orm)
    
    def get_grade_rules_by_commodity(self, commodity: str) -> List[QCGradeRule]:
        """Get all grade rules for a commodity, ordered by grade (A > B > C > REJECT)."""
        # Order by grade priority: GRADE_A first, then GRADE_B, etc.
        grade_order = {
            'GRADE_A': 1,
            'GRADE_B': 2,
            'GRADE_C': 3,
            'REJECT': 4,
        }
        
        orms = self.db.query(QCGradeRuleORM).filter(
            QCGradeRuleORM.commodity == commodity,
            QCGradeRuleORM.is_active == True
        ).all()
        
        # Sort by grade priority
        sorted_orms = sorted(orms, key=lambda x: grade_order.get(x.grade, 999))
        return [self._orm_to_grade_rule(orm) for orm in sorted_orms]
    
    def get_all_grade_rules(self) -> List[QCGradeRule]:
        """Get all grade rules."""
        orms = self.db.query(QCGradeRuleORM).all()
        return [self._orm_to_grade_rule(orm) for orm in orms]
    
    # ========================================
    # Private Helper Methods
    # ========================================
    
    def _update_batch_status(self, batch_id: str, passed: bool) -> None:
        """Update harvest batch status based on QC result."""
        batch = self.db.query(HarvestBatchORM).filter(HarvestBatchORM.id == batch_id).first()
        if batch:
            batch.status = HarvestBatchState.QC_PASSED if passed else HarvestBatchState.QC_FAILED
            batch.updated_at = datetime.now(timezone.utc)
            self.db.commit()
    
    def _orm_to_lab_provider(self, orm: LabProviderORM) -> LabProvider:
        return LabProvider(
            id=UUID(orm.id),
            name=orm.name,
            public_key=orm.public_key,
            metadata=orm.metadata_,
            created_at=orm.created_at,
        )
    
    def _orm_to_sample(self, orm: SampleORM) -> Sample:
        return Sample(
            id=UUID(orm.id),
            sample_code=orm.sample_code,
            harvest_batch_id=UUID(orm.harvest_batch_id),
            collected_by=orm.collected_by,
            collected_at=orm.collected_at,
            sample_points=orm.sample_points,
            photos=orm.photos,
            chain_of_custody=orm.chain_of_custody,
            submitted_to_lab=orm.submitted_to_lab,
            created_at=orm.created_at,
        )
    
    def _orm_to_qc_report(self, orm: BatchQCReportV2ORM) -> BatchQCReportV2:
        return BatchQCReportV2(
            id=UUID(orm.id),
            batch_id=UUID(orm.batch_id),
            sample_id=UUID(orm.sample_id) if orm.sample_id else None,
            lab_id=orm.lab_id,
            tested_at=orm.tested_at,
            metrics=orm.metrics,
            grade=orm.grade,
            passed=orm.passed,
            report_url=orm.report_url,
            signed_hash=orm.signed_hash,
            verified=orm.verified,
            notes=orm.notes,
            created_at=orm.created_at,
        )
    
    def _orm_to_certification(self, orm: CertificationORM) -> Certification:
        return Certification(
            id=UUID(orm.id),
            harvest_batch_id=UUID(orm.harvest_batch_id),
            issuer=orm.issuer,
            cert_type=orm.cert_type,
            cert_number=orm.cert_number,
            valid_from=orm.valid_from,
            valid_to=orm.valid_to,
            cert_url=orm.cert_url,
            signed_hash=orm.signed_hash,
            metadata=orm.metadata_,
            created_at=orm.created_at,
        )
    
    def _orm_to_grade_rule(self, orm: QCGradeRuleORM) -> QCGradeRule:
        return QCGradeRule(
            id=UUID(orm.id),
            commodity=orm.commodity,
            grade=orm.grade,
            rules=orm.rules,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
