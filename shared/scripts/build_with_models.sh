#!/usr/bin/env bash
# FarmConnect Model Generation Build Script
# This script builds the Docker image and extracts generated models to the host

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== FarmConnect Model Generation Build ==="
echo "Project root: ${PROJECT_ROOT}"
echo ""

# Build the Docker image
echo "[1/3] Building Docker image..."
docker-compose build api

# Create a temporary container to extract generated files
echo "[2/3] Extracting generated models from container..."
TEMP_CONTAINER="farmconnect_model_extract_$"

# Run container with the built image, extract files, then remove it
docker run --rm --name "${TEMP_CONTAINER}" farmconnect_api sleep 1

# Copy generated Python models to host
docker cp "${TEMP_CONTAINER}:/app/shared/py/shared_models/"*.py "${PROJECT_ROOT}/shared/py/shared_models/"

# Copy generated TypeScript models to host
docker cp "${TEMP_CONTAINER}:/app/shared/ts/"*.ts "${PROJECT_ROOT}/shared/ts/"

echo "[3/3] Generating __init__.py for shared_models..."
# Generate __init__.py for shared_models (this imports all generated classes)
cat > "${PROJECT_ROOT}/shared/py/shared_models/__init__.py" << 'EOF'
# Auto-generated from schemas - DO NOT EDIT
# This file is regenerated during Docker build from JSON schemas

from .enums import *
from .user import User
from .product import ProductCreate, ProductUpdate, Product
from .order import Order, OrderCreate, OrderUpdate
from .escrow import Escrow
from .dispute import Dispute
from .reputation import Reputation
from .account import Account
from .journal_entry import JournalEntry
from .journal_line import JournalLine
from .ledger_event import LedgerEvent
from .pricing_rule import PricingRule
from .farm import Farm, FarmCreate, FarmUpdate, FarmListResponse
from .farm import Field, FieldCreate, FieldUpdate
from .farm import CropCycle, CropCycleCreate, CropCycleUpdate
from .monitoring import SoilReading, SoilReadingCreate, SoilReadingUpdate
from .monitoring import NDVISnapshot, NDVISnapshotCreate, NDVISnapshotUpdate
from .monitoring import PestDiseaseReport, PestDiseaseReportCreate, PestDiseaseReportUpdate
from .monitoring import TreatmentRecommendation, TreatmentRecommendationCreate, TreatmentRecommendationUpdate
from .delivery import Delivery, DeliveryCreate, DeliveryUpdate
from .weather import WeatherForecast, WeatherForecastCreate
from .weather import WeatherSnapshot, WeatherSnapshotCreate
from .weather import AdvisorySession, AdvisorySessionCreate, AdvisorySessionUpdate
from .weather import AdvisoryMessage, AdvisoryMessageCreate
from .weather import Alert, AlertCreate, AlertUpdate
from .weather import FieldRiskScore, FieldRiskScoreCreate
from .weather import KnowledgeArticle, KnowledgeArticleCreate, KnowledgeArticleUpdate
from .harvest import Harvest, HarvestCreate, HarvestUpdate
from .harvest import HarvestEvent, HarvestEventCreate, HarvestEventUpdate
from .harvest import HarvestBatch, HarvestBatchCreate
from .harvest import HarvestBatchContribution, HarvestBatchContributionCreate
from .harvest import BatchQCReport, BatchQCReportCreate
from .harvest import BatchQCReportV2, BatchQCReportV2Create
from .harvest import Sample, SampleCreate
from .harvest import LabProvider, LabProviderCreate
from .harvest import Certification, CertificationCreate
from .harvest import QCGradeRule, QCGradeRuleCreate
from .harvest import AuditEvent, AuditEventCreate
from .ai import GeoLocation
from .ai import SymptomDetail
from .ai import AnalysisDetection
from .ai import ImageAnalysisResult, ImageAnalysisResultCreate
from .ai import TreatmentOption, TreatmentOptionCreate
from .ai import DiagnosisSession, DiagnosisSessionCreate, DiagnosisSessionUpdate
from .reports import BalanceSheet, ProfitLoss, CashFlow, FinancialSummary


__all__ = [
    # User DTOs
    "User",
    # Product DTOs
    "Product",
    "ProductCreate",
    "ProductUpdate",
    # Order DTOs
    "Order",
    "OrderCreate",
    "OrderUpdate",
    # Escrow DTOs
    "Escrow",
    # Dispute DTOs
    "Dispute",
    # Reputation DTOs
    "Reputation",
    # Pricing Rule DTOs
    "PricingRule",
    # Journal DTOs
    "JournalEntry",
    "JournalLine",
    # Ledger DTOs
    "LedgerEvent",
    # Account DTOs
    "Account",
    # Farm DTOs
    "Farm",
    "FarmCreate",
    "FarmUpdate",
    "FarmListResponse",
    "Field",
    "FieldCreate",
    "FieldUpdate",
    "CropCycle",
    "CropCycleCreate",
    "CropCycleUpdate",
    # Monitoring DTOs
    "SoilReading",
    "SoilReadingCreate",
    "SoilReadingUpdate",
    "NDVISnapshot",
    "NDVISnapshotCreate",
    "NDVISnapshotUpdate",
    "PestDiseaseReport",
    "PestDiseaseReportCreate",
    "PestDiseaseReportUpdate",
    "TreatmentRecommendation",
    "TreatmentRecommendationCreate",
    "TreatmentRecommendationUpdate",
    # Delivery DTOs
    "Delivery",
    "DeliveryCreate",
    "DeliveryUpdate",
    # Weather DTOs
    "WeatherForecast",
    "WeatherForecastCreate",
    "WeatherSnapshot",
    "WeatherSnapshotCreate",
    "AdvisorySession",
    "AdvisorySessionCreate",
    "AdvisorySessionUpdate",
    "AdvisoryMessage",
    "AdvisoryMessageCreate",
    "Alert",
    "AlertCreate",
    "AlertUpdate",
    "FieldRiskScore",
    "FieldRiskScoreCreate",
    "KnowledgeArticle",
    "KnowledgeArticleCreate",
    "KnowledgeArticleUpdate",
    # Harvest DTOs
    "Harvest",
    "HarvestCreate",
    "HarvestUpdate",
    "HarvestEvent",
    "HarvestEventCreate",
    "HarvestEventUpdate",
    "HarvestBatch",
    "HarvestBatchCreate",
    "HarvestBatchContribution",
    "HarvestBatchContributionCreate",
    "BatchQCReport",
    "BatchQCReportCreate",
    "BatchQCReportV2",
    "BatchQCReportV2Create",
    "Sample",
    "SampleCreate",
    "LabProvider",
    "LabProviderCreate",
    "Certification",
    "CertificationCreate",
    "QCGradeRule",
    "QCGradeRuleCreate",
    "AuditEvent",
    "AuditEventCreate",
    # AI DTOs
    "GeoLocation",
    "SymptomDetail",
    "AnalysisDetection",
    "ImageAnalysisResult",
    "ImageAnalysisResultCreate",
    "TreatmentOption",
    "TreatmentOptionCreate",
    "DiagnosisSession",
    "DiagnosisSessionCreate",
    "DiagnosisSessionUpdate",
    # Reports DTOs
    "BalanceSheet",
    "ProfitLoss",
    "CashFlow",
    "FinancialSummary",
    # Enums
    "OwnerType",
    "AccountType",
    "AggregateType",
    "LedgerEventType",
    "QualityGrade",
    "Category",
    "Unit",
    "UserRole",
    "OrderStatus",
    "EscrowState",
    "DisputeState",
    "DisputeResolution",
    "RuleType",
    "FeeType",
    "Provider",
    "Direction",
    "ReferenceType",
]
EOF

echo ""
echo "=== Build Complete ==="
echo "Generated files:"
echo "  - Python models: ${PROJECT_ROOT}/shared/py/shared_models/"
echo "  - TypeScript models: ${PROJECT_ROOT}/shared/ts/"
echo ""
echo "To run the API:"
echo "  docker-compose up -d api"
