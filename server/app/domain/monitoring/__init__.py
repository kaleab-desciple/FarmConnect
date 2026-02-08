"""Monitoring domain module for agricultural management."""
from .entities import (
    SoilReading,
    SoilReadingCreate,
    SoilReadingUpdate,
    NDVISnapshot,
    NDVISnapshotCreate,
    PestDiseaseReport,
    PestDiseaseReportCreate,
    PestDiseaseReportUpdate,
    TreatmentRecommendation,
    TreatmentRecommendationCreate,
    TreatmentRecommendationUpdate,
)
from .irrigation import (
    IrrigationEvent,
    IrrigationEventCreate,
    IrrigationEventUpdate,
    FieldVisitLog,
    FieldVisitLogCreate,
)

__all__ = [
    "SoilReading",
    "SoilReadingCreate",
    "SoilReadingUpdate",
    "NDVISnapshot",
    "NDVISnapshotCreate",
    "PestDiseaseReport",
    "PestDiseaseReportCreate",
    "PestDiseaseReportUpdate",
    "TreatmentRecommendation",
    "TreatmentRecommendationCreate",
    "TreatmentRecommendationUpdate",
    "IrrigationEvent",
    "IrrigationEventCreate",
    "IrrigationEventUpdate",
    "FieldVisitLog",
    "FieldVisitLogCreate",
]
