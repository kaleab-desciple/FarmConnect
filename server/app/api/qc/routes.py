"""QC API Routes for lab webhooks and QC management.

This module provides:
- POST /api/qc/lab_webhook - Receive lab reports from external lab systems
- POST /api/qc/samples - Create sampling requests
- GET /api/qc/reports/{batch_id} - Get QC reports for a batch
- POST /api/qc/labs - Register a new lab provider
- GET /api/qc/labs - List all lab providers
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.application.services.qc_service import QCService


router = APIRouter()


# ========================================
# Pydantic Request/Response Models
# ========================================

class LabWebhookPayload(BaseModel):
    """Payload for lab webhook endpoint."""
    lab_id: str = Field(..., description="Lab provider ID")
    sample_id: Optional[str] = Field(None, description="Sample ID if exists")
    batch_id: str = Field(..., description="Harvest batch ID")
    tested_at: datetime = Field(..., description="When the test was performed")
    metrics: Dict[str, float] = Field(..., description="Test metrics, e.g., {\"moisture_pct\": 12.4}")
    report_url: Optional[str] = Field(None, description="URL to full report PDF")
    signed_hash: Optional[str] = Field(None, description="Lab signature or hash")


class LabWebhookResponse(BaseModel):
    """Response from lab webhook endpoint."""
    id: str
    batch_id: str
    grade: str
    passed: bool
    verified: bool
    tested_at: str


class SampleCreateRequest(BaseModel):
    """Request to create a sample."""
    sample_code: str
    harvest_batch_id: str
    collected_by: Optional[str] = None
    sample_points: Optional[Dict[str, Any]] = None
    photos: Optional[List[Dict[str, Any]]] = None
    chain_of_custody: Optional[Dict[str, Any]] = None


class SampleResponse(BaseModel):
    """Response for sample creation."""
    id: str
    sample_code: str
    harvest_batch_id: str
    submitted_to_lab: bool
    created_at: str


class LabProviderCreateRequest(BaseModel):
    """Request to create a lab provider."""
    name: str
    public_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LabProviderResponse(BaseModel):
    """Response for lab provider."""
    id: str
    name: str
    public_key: bool  # Just indicates if key exists
    created_at: str


class QCReportResponse(BaseModel):
    """Response for QC report."""
    id: str
    batch_id: str
    sample_id: Optional[str]
    lab_id: Optional[str]
    tested_at: str
    metrics: Optional[Dict[str, float]]
    grade: Optional[str]
    passed: bool
    verified: bool
    report_url: Optional[str]
    created_at: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    code: str


# ========================================
# API Endpoints
# ========================================

@router.post("/lab_webhook", response_model=LabWebhookResponse)
def lab_webhook(
    payload: LabWebhookPayload,
    x_lab_id: Optional[str] = Header(None, description="Lab ID header for additional verification"),
    db: Session = Depends(get_db)
):
    """
    Receive lab test results from external lab systems.
    
    This endpoint accepts QC reports from accredited labs. It:
    1. Validates the lab exists
    2. Validates the batch is in a valid state (SEALED or QC_PENDING)
    3. Checks for idempotent reports (same sample/lab/test time)
    4. Evaluates the grade based on configurable rules
    5. Verifies the lab signature if public key is available
    6. Creates the QC report and updates batch status
    
    ## Payload Example
    ```json
    {
        "lab_id": "lab-00001",
        "sample_id": "sample-00001",
        "batch_id": "hb-00001",
        "tested_at": "2026-02-20T08:12:00Z",
        "metrics": {
            "moisture_pct": 12.3,
            "aflatoxin_ppb": 3.2
        },
        "report_url": "https://cdn.example/reports/hb-00001-report.pdf",
        "signed_hash": "sha256:abcdef..."
    }
    ```
    
    ## Response
    Returns the created QC report with grade evaluation.
    
    ## Error Codes
    - LAB_NOT_FOUND: Lab provider not registered
    - BATCH_NOT_FOUND: Harvest batch doesn't exist
    - INVALID_BATCH_STATE_{status}: Batch not in valid state for QC
    """
    service = QCService(db)
    
    result, success, error_code = service.process_lab_webhook(
        lab_id=payload.lab_id,
        sample_id=payload.sample_id,
        batch_id=payload.batch_id,
        tested_at=payload.tested_at,
        metrics=payload.metrics,
        report_url=payload.report_url,
        signed_hash=payload.signed_hash,
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail={"error": result.get("error", "Unknown error"), "code": error_code}
        )
    
    return LabWebhookResponse(**result)


@router.post("/samples", response_model=SampleResponse)
def create_sample(
    request: SampleCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new sample for QC testing.
    
    This endpoint creates a sampling request that can be submitted to a lab.
    The batch must be in SEALED state before samples can be collected.
    """
    service = QCService(db)
    
    try:
        result = service.create_sample(
            sample_code=request.sample_code,
            harvest_batch_id=request.harvest_batch_id,
            collected_by=request.collected_by,
            sample_points=request.sample_points,
            photos=request.photos,
            chain_of_custody=request.chain_of_custody,
        )
        return SampleResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports/{batch_id}", response_model=List[QCReportResponse])
def get_qc_reports(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all QC reports for a harvest batch.
    
    Returns all QC reports ordered by test date (most recent first).
    """
    from app.infrastructure.repositories.qc_repo import QCRepository
    
    repo = QCRepository(db)
    reports = repo.get_qc_reports_by_batch(batch_id)
    
    return [
        QCReportResponse(
            id=str(r.id),
            batch_id=str(r.batch_id),
            sample_id=str(r.sample_id) if r.sample_id else None,
            lab_id=r.lab_id,
            tested_at=r.tested_at.isoformat(),
            metrics=r.metrics,
            grade=r.grade,
            passed=r.passed,
            verified=r.verified,
            report_url=r.report_url,
            created_at=r.created_at.isoformat(),
        )
        for r in reports
    ]


@router.post("/labs", response_model=LabProviderResponse)
def create_lab_provider(
    request: LabProviderCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new lab provider.
    
    Labs can be registered with their public key for signature verification.
    """
    service = QCService(db)
    
    result = service.create_lab_provider(
        name=request.name,
        public_key=request.public_key,
        metadata=request.metadata,
    )
    return LabProviderResponse(**result)


@router.get("/labs", response_model=List[LabProviderResponse])
def list_lab_providers(
    db: Session = Depends(get_db)
):
    """
    List all registered lab providers.
    """
    from app.infrastructure.repositories.qc_repo import QCRepository
    
    repo = QCRepository(db)
    labs = repo.get_all_lab_providers()
    
    return [
        LabProviderResponse(
            id=str(l.id),
            name=l.name,
            public_key=l.public_key is not None,
            created_at=l.created_at.isoformat(),
        )
        for l in labs
    ]


@router.get("/labs/{lab_id}", response_model=LabProviderResponse)
def get_lab_provider(
    lab_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific lab provider by ID."""
    from app.infrastructure.repositories.qc_repo import QCRepository
    
    repo = QCRepository(db)
    lab = repo.get_lab_provider_by_id(lab_id)
    
    if not lab:
        raise HTTPException(status_code=404, detail="Lab provider not found")
    
    return LabProviderResponse(
        id=str(lab.id),
        name=lab.name,
        public_key=lab.public_key is not None,
        created_at=lab.created_at.isoformat(),
    )
