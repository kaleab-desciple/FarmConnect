from __future__ import annotations
from typing import List, Optional, Any
from pydantic import BaseModel


class QCReportSummary(BaseModel):
    id: str
    lab_id: Optional[str] = None
    tested_at: Optional[str] = None
    metrics: Optional[dict] = None
    passed: bool
    report_url: Optional[str] = None
    verified: Optional[bool] = None


class HarvestBatchLink(BaseModel):
    harvest_batch_id: str
    batch_code: Optional[str] = None
    status: Optional[str] = None
    lineage_hash: Optional[str] = None
    aggregated_weight_kg: Optional[float] = None
    moisture_avg: Optional[float] = None
    qc_reports: List[QCReportSummary] = []
    contribution_weight_kg: Optional[float] = None


class ProductBatchLink(BaseModel):
    id: str
    batch_code: Optional[str] = None
    total_quantity: Optional[str] = None
    quality_grade: Optional[str] = None
    links: List[HarvestBatchLink] = []


class ProductConversionResponse(BaseModel):
    id: str
    name: Optional[str]
    total_quantity: Optional[str]
    status: Optional[str]
    is_active: Optional[bool]
    product_batches: List[ProductBatchLink] = []

    # Primary harvest batch summary
    harvest_batch_id: Optional[str] = None
    harvest_batch_status: Optional[str] = None
    harvest_batch_lineage_hash: Optional[str] = None
    harvest_batch_aggregated_weight_kg: Optional[float] = None

    # Latest QC summary
    qc_status: Optional[str] = None
    qc_lab_id: Optional[str] = None
    qc_tested_at: Optional[str] = None
