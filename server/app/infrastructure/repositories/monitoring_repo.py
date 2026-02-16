"""Monitoring repository implementation."""
from typing import List, Optional
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.domain.monitoring.entities import (
    SoilReading, SoilReadingCreate, SoilReadingUpdate,
    NDVISnapshot, NDVISnapshotCreate,
    PestDiseaseReport, PestDiseaseReportCreate, PestDiseaseReportUpdate,
    TreatmentRecommendation, TreatmentRecommendationCreate, TreatmentRecommendationUpdate,
)
from app.infrastructure.db.models import SoilReadingORM, NDVISnapshotORM, PestDiseaseReportORM, TreatmentRecommendationORM


class SoilReadingRepository:
    """Repository for SoilReading operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, reading_data: SoilReadingCreate) -> SoilReading:
        """Create a new soil reading."""
        orm = SoilReadingORM(
            field_id=reading_data.field_id,
            location_geojson=reading_data.location_geojson,
            sample_depth_cm=reading_data.sample_depth_cm,
            sample_depth_range=reading_data.sample_depth_range,
            moisture_pct=reading_data.moisture_pct,
            temperature_c=reading_data.temperature_c,
            ph=reading_data.ph,
            nitrogen_ppm=reading_data.nitrogen_ppm,
            phosphorus_ppm=reading_data.phosphorus_ppm,
            potassium_ppm=reading_data.potassium_ppm,
            organic_matter_pct=reading_data.organic_matter_pct,
            cation_exchange_capacity=reading_data.cation_exchange_capacity,
            electrical_conductivity_ms_cm=reading_data.electrical_conductivity_ms_cm,
            texture_analysis=reading_data.texture_analysis,
            source=reading_data.source,
            lab_name=reading_data.lab_name,
            lab_report_url=reading_data.lab_report_url,
            recorded_by=reading_data.recorded_by,
            recorded_at=reading_data.recorded_at,
            weather_conditions=reading_data.weather_conditions,
            days_since_rain=reading_data.days_since_rain,
            metadata_=reading_data.metadata,
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get_by_id(self, reading_id: str) -> Optional[SoilReading]:
        """Get soil reading by ID."""
        orm = self.session.query(SoilReadingORM).filter(SoilReadingORM.id == reading_id).first()
        return self._to_domain(orm) if orm else None

    def get_by_field_id(self, field_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[SoilReading]:
        """Get soil readings for a field."""
        query = self.session.query(SoilReadingORM).filter(SoilReadingORM.field_id == field_id)
        if start_date:
            query = query.filter(SoilReadingORM.recorded_at >= start_date)
        if end_date:
            query = query.filter(SoilReadingORM.recorded_at <= end_date)
        query = query.order_by(desc(SoilReadingORM.recorded_at))
        orms = query.all()
        return [self._to_domain(orm) for orm in orms]

    def get_latest(self, field_id: str) -> Optional[SoilReading]:
        """Get latest soil reading for a field."""
        orm = self.session.query(SoilReadingORM).filter(
            SoilReadingORM.field_id == field_id
        ).order_by(desc(SoilReadingORM.recorded_at)).first()
        return self._to_domain(orm) if orm else None

    def update(self, reading_id: str, reading_data: SoilReadingUpdate) -> Optional[SoilReading]:
        """Update a soil reading."""
        orm = self.session.query(SoilReadingORM).filter(SoilReadingORM.id == reading_id).first()
        if not orm:
            return None
        update_data = reading_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(orm, "metadata_", value)
            else:
                setattr(orm, key, value)
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: SoilReadingORM) -> SoilReading:
        """Convert ORM to domain entity."""
        return SoilReading(
            id=orm.id,
            field_id=orm.field_id,
            location_geojson=orm.location_geojson,
            sample_depth_cm=orm.sample_depth_cm,
            sample_depth_range=orm.sample_depth_range,
            moisture_pct=orm.moisture_pct,
            temperature_c=orm.temperature_c,
            ph=orm.ph,
            nitrogen_ppm=orm.nitrogen_ppm,
            phosphorus_ppm=orm.phosphorus_ppm,
            potassium_ppm=orm.potassium_ppm,
            organic_matter_pct=orm.organic_matter_pct,
            cation_exchange_capacity=orm.cation_exchange_capacity,
            electrical_conductivity_ms_cm=orm.electrical_conductivity_ms_cm,
            texture_analysis=orm.texture_analysis,
            source=orm.source,
            lab_name=orm.lab_name,
            lab_report_url=orm.lab_report_url,
            recorded_by=orm.recorded_by,
            recorded_at=orm.recorded_at,
            weather_conditions=orm.weather_conditions,
            days_since_rain=orm.days_since_rain,
            metadata=orm.metadata_,
            created_at=orm.created_at,
        )


class NDVIRepository:
    """Repository for NDVISnapshot operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, snapshot_data: NDVISnapshotCreate) -> NDVISnapshot:
        """Create a new NDVI snapshot."""
        orm = NDVISnapshotORM(
            field_id=snapshot_data.field_id,
            crop_cycle_id=snapshot_data.crop_cycle_id,
            source=snapshot_data.source,
            source_metadata=snapshot_data.source_metadata,
            captured_at=snapshot_data.captured_at,
            processed_at=snapshot_data.processed_at,
            ndvi_mean=snapshot_data.ndvi_mean,
            ndvi_min=snapshot_data.ndvi_min,
            ndvi_max=snapshot_data.ndvi_max,
            ndvi_stddev=snapshot_data.ndvi_stddev,
            stress_level=snapshot_data.stress_level,
            cloud_cover_pct=snapshot_data.cloud_cover_pct,
            data_quality_score=snapshot_data.data_quality_score,
            tile_urls=snapshot_data.tile_urls,
            metadata_=snapshot_data.metadata,
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get_by_id(self, snapshot_id: str) -> Optional[NDVISnapshot]:
        """Get NDVI snapshot by ID."""
        orm = self.session.query(NDVISnapshotORM).filter(NDVISnapshotORM.id == snapshot_id).first()
        return self._to_domain(orm) if orm else None

    def get_by_field_id(self, field_id: str, limit: int = 30) -> List[NDVISnapshot]:
        """Get NDVI snapshots for a field."""
        orms = self.session.query(NDVISnapshotORM).filter(
            NDVISnapshotORM.field_id == field_id
        ).order_by(desc(NDVISnapshotORM.captured_at)).limit(limit).all()
        return [self._to_domain(orm) for orm in orms]

    def get_latest(self, field_id: str) -> Optional[NDVISnapshot]:
        """Get latest NDVI snapshot for a field."""
        orm = self.session.query(NDVISnapshotORM).filter(
            NDVISnapshotORM.field_id == field_id
        ).order_by(desc(NDVISnapshotORM.captured_at)).first()
        return self._to_domain(orm) if orm else None

    def _to_domain(self, orm: NDVISnapshotORM) -> NDVISnapshot:
        """Convert ORM to domain entity."""
        return NDVISnapshot(
            id=orm.id,
            field_id=orm.field_id,
            crop_cycle_id=orm.crop_cycle_id,
            source=orm.source,
            source_metadata=orm.source_metadata,
            captured_at=orm.captured_at,
            processed_at=orm.processed_at,
            ndvi_mean=orm.ndvi_mean,
            ndvi_min=orm.ndvi_min,
            ndvi_max=orm.ndvi_max,
            ndvi_stddev=orm.ndvi_stddev,
            stress_level=orm.stress_level,
            cloud_cover_pct=orm.cloud_cover_pct,
            data_quality_score=orm.data_quality_score,
            tile_urls=orm.tile_urls,
            metadata=orm.metadata_,
            created_at=orm.created_at,
        )


class PestDiseaseReportRepository:
    """Repository for PestDiseaseReport operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, report_data: PestDiseaseReportCreate) -> PestDiseaseReport:
        """Create a new pest/disease report."""
        orm = PestDiseaseReportORM(
            field_id=report_data.field_id,
            crop_cycle_id=report_data.crop_cycle_id,
            reported_by=report_data.reported_by,
            location_geojson=report_data.location_geojson,
            image_urls=report_data.image_urls,
            drone_flight_id=report_data.drone_flight_id,
            suspected_issue=report_data.suspected_issue,
            issue_type=report_data.issue_type,
            scientific_name=report_data.scientific_name,
            common_names=report_data.common_names,
            ai_diagnosis_id=report_data.ai_diagnosis_id,
            confidence_pct=report_data.confidence_pct,
            severity=report_data.severity,
            affected_area_ha=report_data.affected_area_ha,
            affected_plant_count=report_data.affected_plant_count,
            symptoms=report_data.symptoms,
            spread_pattern=report_data.spread_pattern,
            verified_by=report_data.verified_by,
            verified_at=report_data.verified_at,
            verification_notes=report_data.verification_notes,
            first_observed_date=report_data.first_observed_date,
            detected_at=report_data.detected_at,
            metadata_=report_data.metadata,
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get_by_id(self, report_id: str) -> Optional[PestDiseaseReport]:
        """Get pest/disease report by ID."""
        orm = self.session.query(PestDiseaseReportORM).filter(PestDiseaseReportORM.id == report_id).first()
        return self._to_domain(orm) if orm else None

    def get_by_field_id(self, field_id: str) -> List[PestDiseaseReport]:
        """Get pest/disease reports for a field."""
        orms = self.session.query(PestDiseaseReportORM).filter(
            PestDiseaseReportORM.field_id == field_id
        ).order_by(desc(PestDiseaseReportORM.detected_at)).all()
        return [self._to_domain(orm) for orm in orms]

    def update(self, report_id: str, report_data: PestDiseaseReportUpdate) -> Optional[PestDiseaseReport]:
        """Update a pest/disease report."""
        orm = self.session.query(PestDiseaseReportORM).filter(PestDiseaseReportORM.id == report_id).first()
        if not orm:
            return None
        update_data = report_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(orm, "metadata_", value)
            else:
                setattr(orm, key, value)
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: PestDiseaseReportORM) -> PestDiseaseReport:
        """Convert ORM to domain entity."""
        return PestDiseaseReport(
            id=orm.id,
            field_id=orm.field_id,
            crop_cycle_id=orm.crop_cycle_id,
            reported_by=orm.reported_by,
            location_geojson=orm.location_geojson,
            image_urls=orm.image_urls,
            drone_flight_id=orm.drone_flight_id,
            suspected_issue=orm.suspected_issue,
            issue_type=orm.issue_type,
            scientific_name=orm.scientific_name,
            common_names=orm.common_names,
            ai_diagnosis_id=orm.ai_diagnosis_id,
            confidence_pct=orm.confidence_pct,
            severity=orm.severity,
            affected_area_ha=orm.affected_area_ha,
            affected_plant_count=orm.affected_plant_count,
            symptoms=orm.symptoms,
            spread_pattern=orm.spread_pattern,
            verified_by=orm.verified_by,
            verified_at=orm.verified_at,
            verification_notes=orm.verification_notes,
            first_observed_date=orm.first_observed_date,
            detected_at=orm.detected_at,
            metadata=orm.metadata_,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )


class TreatmentRecommendationRepository:
    """Repository for TreatmentRecommendation operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, recommendation_data: TreatmentRecommendationCreate) -> TreatmentRecommendation:
        """Create a new treatment recommendation."""
        orm = TreatmentRecommendationORM(
            report_id=recommendation_data.report_id,
            recommended_by=recommendation_data.recommended_by,
            recommendation_source=recommendation_data.recommendation_source,
            description=recommendation_data.description,
            treatment_type=recommendation_data.treatment_type,
            chemical_name=recommendation_data.chemical_name,
            active_ingredient=recommendation_data.active_ingredient,
            formulation=recommendation_data.formulation,
            dosage_per_ha=recommendation_data.dosage_per_ha,
            application_method=recommendation_data.application_method,
            application_timing=recommendation_data.application_timing,
            organic=recommendation_data.organic,
            restricted_use=recommendation_data.restricted_use,
            required_ppe=recommendation_data.required_ppe,
            reentry_interval_hours=recommendation_data.reentry_interval_hours,
            pre_harvest_interval_days=recommendation_data.pre_harvest_interval_days,
            withdrawal_period_days=recommendation_data.withdrawal_period_days,
            estimated_cost_per_ha_usd=recommendation_data.estimated_cost_per_ha_usd,
            effectiveness_rating=recommendation_data.effectiveness_rating,
            expected_results_days=recommendation_data.expected_results_days,
            accepted_by_farmer=recommendation_data.accepted_by_farmer,
            accepted_at=recommendation_data.accepted_at,
            applied=recommendation_data.applied,
            applied_at=recommendation_data.applied_at,
            application_notes=recommendation_data.application_notes,
            metadata_=recommendation_data.metadata,
        )
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get_by_id(self, recommendation_id: str) -> Optional[TreatmentRecommendation]:
        """Get treatment recommendation by ID."""
        orm = self.session.query(TreatmentRecommendationORM).filter(TreatmentRecommendationORM.id == recommendation_id).first()
        return self._to_domain(orm) if orm else None

    def get_by_report_id(self, report_id: str) -> List[TreatmentRecommendation]:
        """Get treatment recommendations for a report."""
        orms = self.session.query(TreatmentRecommendationORM).filter(
            TreatmentRecommendationORM.report_id == report_id
        ).order_by(TreatmentRecommendationORM.created_at).all()
        return [self._to_domain(orm) for orm in orms]

    def update(self, recommendation_id: str, recommendation_data: TreatmentRecommendationUpdate) -> Optional[TreatmentRecommendation]:
        """Update a treatment recommendation."""
        orm = self.session.query(TreatmentRecommendationORM).filter(TreatmentRecommendationORM.id == recommendation_id).first()
        if not orm:
            return None
        update_data = recommendation_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(orm, "metadata_", value)
            else:
                setattr(orm, key, value)
        self.session.commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: TreatmentRecommendationORM) -> TreatmentRecommendation:
        """Convert ORM to domain entity."""
        return TreatmentRecommendation(
            id=orm.id,
            report_id=orm.report_id,
            recommended_by=orm.recommended_by,
            recommendation_source=orm.recommendation_source,
            description=orm.description,
            treatment_type=orm.treatment_type,
            chemical_name=orm.chemical_name,
            active_ingredient=orm.active_ingredient,
            formulation=orm.formulation,
            dosage_per_ha=orm.dosage_per_ha,
            application_method=orm.application_method,
            application_timing=orm.application_timing,
            organic=orm.organic,
            restricted_use=orm.restricted_use,
            required_ppe=orm.required_ppe,
            reentry_interval_hours=orm.reentry_interval_hours,
            pre_harvest_interval_days=orm.pre_harvest_interval_days,
            withdrawal_period_days=orm.withdrawal_period_days,
            estimated_cost_per_ha_usd=orm.estimated_cost_per_ha_usd,
            effectiveness_rating=orm.effectiveness_rating,
            expected_results_days=orm.expected_results_days,
            accepted_by_farmer=orm.accepted_by_farmer,
            accepted_at=orm.accepted_at,
            applied=orm.applied,
            applied_at=orm.applied_at,
            application_notes=orm.application_notes,
            metadata=orm.metadata_,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
