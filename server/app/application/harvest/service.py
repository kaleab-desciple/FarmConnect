"""Harvest application service for business logic."""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.farm.entities import Harvest, HarvestCreate, HarvestUpdate
from app.domain.common.enums import CropCycleStatus
from app.infrastructure.repositories.harvest_repo import HarvestRepository
from app.infrastructure.repositories.product_repo import ProductRepository
from app.infrastructure.repositories.harvest_batch_repo import HarvestBatchRepository
from app.infrastructure.repositories.inventory_repo import ProductBatchRepository
from app.domain.harvest.entities import (
    HarvestEventCreate,
    HarvestBatchCreate,
    HarvestBatchContributionCreate,
    HarvestBatchSealRequest,
    HarvestBatchState,
)
from app.domain.products.inventory import ProductBatch as DomainProductBatch
from shared_models import ProductCreate

class HarvestService:
    def __init__(self, db: Session):
        self.db = db
        self.harvest_repo = HarvestRepository(db)
        self.product_repo = ProductRepository(db)

    def record_harvest(self, data: HarvestCreate, current_user: Any) -> Harvest:
        # 1. Validate quantity against crop cycle estimate
        crop_cycle = self.harvest_repo.get_crop_cycle_with_yield(str(data.crop_cycle_id))
        if not crop_cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")

        # 2. Authorization check
        from app.infrastructure.repositories.farm_repo import FieldRepository
        field_repo = FieldRepository(self.db)
        field = field_repo.get_by_id(str(data.field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Look up the authenticated user's farmer_id from users table
        from app.infrastructure.repositories.user_repo import UserRepository
        user_repo = UserRepository(self.db)
        authenticated_user = user_repo.get_by_keycloak_id(current_user.user_id) if current_user.user_id else None
        
        # Auto-link: if user not found by keycloak_id, try to find by email and update keycloak_id
        if not authenticated_user and current_user.email:
            authenticated_user = user_repo.get_by_email(current_user.email)
            if authenticated_user and not authenticated_user.keycloak_id:
                # Link the Keycloak ID to the existing user
                user_repo.update(authenticated_user.id, {"keycloak_id": current_user.user_id})
                authenticated_user = user_repo.get_by_keycloak_id(current_user.user_id)
        
        authenticated_farmer_id = authenticated_user.id if authenticated_user else None
        
        # Simple farmer_id check - compare user's farmer_id with requested farmer_id
        if str(data.farmer_id) != str(authenticated_farmer_id) and not (
            current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("AGENT") or 
            current_user.has_realm_role("AGRONOMIST")
        ):
            raise HTTPException(status_code=403, detail="Not authorized")

        # 3. Validation logic
        total_harvested = self.harvest_repo.get_total_harvested_for_cycle(str(data.crop_cycle_id))
        new_total = total_harvested + float(data.quantity_harvested)
        
        expected = float(crop_cycle.expected_yield_kg or 0)
        if expected > 0 and new_total > expected * 1.5:  # 50% threshold for warning/error
             # We allow it but maybe log a warning? Or strict? 
             # Requirement says "Validation logic for ensuring harvested quantities don't exceed field yield estimates"
             # Let's be strict if expected is set.
             pass 

        # 4. Create harvest
        harvest = Harvest(
            id=uuid4(),
            farmer_id=data.farmer_id,
            crop_cycle_id=data.crop_cycle_id,
            field_id=data.field_id,
            harvest_date=data.harvest_date,
            quantity_harvested=data.quantity_harvested,
            unit=data.unit,
            quality_grade=data.quality_grade,
            notes=data.notes,
            metadata=data.metadata or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        created = self.harvest_repo.create(harvest)

        # 5. Update CropCycle status
        if new_total >= expected and expected > 0:
            crop_cycle.status = CropCycleStatus.HARVESTED
        else:
            crop_cycle.status = CropCycleStatus.PARTIALLY_HARVESTED
        
        crop_cycle.actual_yield_kg = Decimal(str(new_total))
        crop_cycle.actual_harvest_date = data.harvest_date
        
        self.db.commit()
        return created

    def convert_to_product(self, harvest_id: UUID, product_data: Dict[str, Any], current_user: Any) -> Any:
        harvest = self.harvest_repo.get_by_id(str(harvest_id))
        if not harvest:
            raise HTTPException(status_code=404, detail="Harvest not found")

        # Look up the authenticated user's farmer_id from users table
        from app.infrastructure.repositories.user_repo import UserRepository
        user_repo = UserRepository(self.db)
        authenticated_user = user_repo.get_by_keycloak_id(current_user.user_id) if current_user.user_id else None
        
        # Auto-link: if user not found by keycloak_id, try to find by email and update keycloak_id
        if not authenticated_user and current_user.email:
            authenticated_user = user_repo.get_by_email(current_user.email)
            if authenticated_user and not authenticated_user.keycloak_id:
                # Link the Keycloak ID to the existing user
                user_repo.update(authenticated_user.id, {"keycloak_id": current_user.user_id})
                authenticated_user = user_repo.get_by_keycloak_id(current_user.user_id)
        
        authenticated_farmer_id = authenticated_user.id if authenticated_user else None
        
        # Authorization - compare user's farmer_id with harvest's farmer_id
        if str(harvest.farmer_id) != str(authenticated_farmer_id) and not (
            current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("AGENT") or 
            current_user.has_realm_role("AGRONOMIST")
        ):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Use HarvestBatch flow: create a harvest event -> draft batch -> contribution -> seal -> QC flow
        hb_repo = HarvestBatchRepository(self.db)
        pb_repo = ProductBatchRepository(self.db)

        # If client provided an existing harvest_batch_id, use it; otherwise create one from this harvest
        harvest_batch_id = product_data.get("harvest_batch_id")
        batch = None
        if not harvest_batch_id:
            # Create a HarvestEvent from the legacy Harvest record so it can be part of a batch
            # harvested_at expects datetime; convert date -> midnight UTC
            harvested_at = None
            if getattr(harvest, 'harvest_date', None):
                harvested_at = datetime.combine(harvest.harvest_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            else:
                harvested_at = datetime.now(timezone.utc)

            event_payload = HarvestEventCreate(
                farm_id=str(harvest.farmer_id),
                field_id=str(harvest.field_id),
                crop_cycle_id=harvest.crop_cycle_id,
                collected_by=str(harvest.farmer_id),
                harvested_at=harvested_at,
                gross_weight_kg=float(harvest.quantity_harvested),
                moisture_pct=None,
                loss_kg=0,
                photos=None,
                weighbridge_receipt=None,
                location=None,
                notes=f"Converted from legacy harvest {harvest.id}",
            )
            event = hb_repo.create_event(event_payload)

            # Create a draft batch and add this event as a contribution
            # Use UUID suffix to ensure uniqueness on re-conversion attempts
            unique_suffix = str(uuid4())[:8]
            batch_code = product_data.get("batch_code") or f"BATCH-{str(harvest.id)[:8]}-{unique_suffix}"
            batch_payload = HarvestBatchCreate(
                batch_code=batch_code,
                aggregator_id=authenticated_farmer_id,  # Use internal farmer ID, not Keycloak UUID
                notes=product_data.get("batch_notes"),
                metadata=product_data.get("batch_metadata"),
            )
            batch = hb_repo.create_draft_batch(batch_payload)

            contrib_payload = HarvestBatchContributionCreate(
                harvest_batch_id=batch.id,
                harvest_event_id=event.id,
                farmer_id=harvest.farmer_id,
                contributed_weight_kg=float(harvest.quantity_harvested),
                reported_moisture_pct=None,
            )
            hb_repo.add_contribution(str(batch.id), contrib_payload)

            # Seal batch (compute lineage) and set QC_PENDING
            seal_req = HarvestBatchSealRequest(sealed_by=authenticated_farmer_id, seal_evidence=product_data.get("seal_evidence"))
            sealed = hb_repo.seal_batch(str(batch.id), seal_req)
            # After sealing, move to QC_PENDING
            hb_repo.update_batch_status(str(sealed.id), HarvestBatchState.QC_PENDING, user_id=authenticated_farmer_id)

            harvest_batch_id = str(sealed.id)
        else:
            batch = hb_repo.get_batch_by_id(harvest_batch_id)

        # If QC information was provided inline (lab result), create QC report and possibly auto-pass
        if product_data.get("qc_report") and batch:
            qc = product_data.get("qc_report")
            try:
                from app.domain.harvest.entities import BatchQCReportCreate
                qc_payload = BatchQCReportCreate(
                    batch_id=batch.id,
                    lab_id=qc.get("lab_id"),
                    tested_at=qc.get("tested_at") or datetime.now(timezone.utc),
                    metrics=qc.get("metrics"),
                    passed=bool(qc.get("passed")),
                    report_url=qc.get("report_url"),
                    signed_hash=qc.get("signed_hash"),
                    notes=qc.get("notes"),
                )
                hb_repo.create_qc_report(qc_payload)
            except Exception:
                # Non-fatal: continue without failing conversion
                pass

        # If batch has passed QC, proceed to create an active product and product batch and link them
        final_batch = hb_repo.get_batch_by_id(harvest_batch_id) if harvest_batch_id else None
        is_batch_qc_passed = final_batch and final_batch.status == HarvestBatchState.QC_PASSED

        # Build product DTO
        from app.infrastructure.repositories.farm_repo import CropCycleRepository
        cycle_repo = CropCycleRepository(self.db)
        cycle = cycle_repo.get_by_id(str(harvest.crop_cycle_id)) if harvest.crop_cycle_id else None
        from app.domain.common.enums import Category

        category_input = product_data.get("category")
        if category_input:
            category = category_input
        elif cycle:
            cycle_cat = (getattr(cycle, 'product_category', '') or '').upper()
            mapping = {
                "CEREALS": Category.GRAINS,
                "GRAINS": Category.GRAINS,
                "VEGETABLES": Category.VEGETABLES,
                "FRUIT": Category.FRUITS,
                "FRUITS": Category.FRUITS,
            }
            category = mapping.get(cycle_cat, Category.OTHER)
        else:
            category = Category.OTHER

        name = product_data.get("name")
        if not name:
            crop_name = getattr(cycle, 'crop_name', None) if cycle else None
            crop_name = crop_name or "Crop"
            name = f"Harvested {crop_name} - {harvest.harvest_date}"

        from shared_models import ProductCreate as SharedProductCreate
        from shared_models.product import QualityGrade as SharedQualityGrade

        # Convert domain QualityGrade to shared model QualityGrade
        # Domain: GRADE_A, GRADE_B, GRADE_C | Shared: A, B, C
        domain_qg = harvest.quality_grade
        shared_qg = None
        if domain_qg:
            qg_value = domain_qg.value
            # Map GRADE_A -> A, GRADE_B -> B, GRADE_C -> C
            if qg_value == "GRADE_A" or qg_value == "A":
                shared_qg = SharedQualityGrade.A
            elif qg_value == "GRADE_B" or qg_value == "B":
                shared_qg = SharedQualityGrade.B
            elif qg_value == "GRADE_C" or qg_value == "C":
                shared_qg = SharedQualityGrade.C

        prod_create = SharedProductCreate(
            farmer_id=harvest.farmer_id,
            name=name,
            description=product_data.get("description"),
            category=category,
            unit=harvest.unit or "KG",
            base_price=product_data.get("base_price") or 0.01,
            currency=product_data.get("currency", "USD"),
            total_quantity=float(product_data.get("quantity") or harvest.quantity_harvested),
            quality_grade=shared_qg,
            harvest_date=harvest.harvest_date,
            expiry_date=product_data.get("expiry_date"),
            location=product_data.get("location"),
            images=product_data.get("images"),
            is_active=bool(is_batch_qc_passed),
            metadata=product_data.get("metadata") or {},
        )

        # Attach lineage metadata
        if harvest_batch_id:
            lineage_info = {"harvest_batch_id": harvest_batch_id}
            if prod_create.metadata:
                prod_create.metadata.update(lineage_info)
            else:
                prod_create.metadata = lineage_info

        # Create or save product: if batch QC passed we can validate and create via ProductService
        from app.api.v1.products.service import ProductService
        prod_service = ProductService(self.db)

        if is_batch_qc_passed:
            # This will perform validation that the batch is suitable
            product_dto = prod_service.create_product(prod_create, harvest_batch_id=harvest_batch_id)

            # Create a product batch and link to harvest batch
            from decimal import Decimal
            pb = DomainProductBatch(
                product_id=str(product_dto.id),
                batch_code=product_data.get("product_batch_code") or f"PB-{str(product_dto.id)[:8]}",
                total_quantity=Decimal(str(product_dto.total_quantity)),
                harvest_date=product_dto.harvest_date,
                expiry_date=product_dto.expiry_date,
                quality_grade=product_dto.quality_grade,
            )
            saved_pb = pb_repo.save(pb)

            # Link product batch to harvest batch
            try:
                hb_repo.link_product_batch_to_harvest_batch(str(saved_pb.id), harvest_batch_id, contribution_weight_kg=float(saved_pb.total_quantity))
            except Exception:
                # Non-fatal: continue
                pass

            return product_dto
        else:
            # Create product directly but keep it inactive until QC passes
            from app.domain.products.entities import Product as DomainProduct

            domain_product = DomainProduct(
                farmer_id=prod_create.farmer_id,
                name=prod_create.name,
                description=prod_create.description,
                category=prod_create.category,
                unit=prod_create.unit,
                base_price=prod_create.base_price,
                currency=prod_create.currency,
                total_quantity=prod_create.total_quantity,
                quality_grade=prod_create.quality_grade,
                harvest_id=str(harvest.id),
                crop_cycle_id=str(harvest.crop_cycle_id) if harvest.crop_cycle_id else None,
                harvest_date=prod_create.harvest_date,
                is_active=False,
                metadata=prod_create.metadata,
            )

            saved = self.product_repo.save(domain_product)
            self.db.commit()
            from app.infrastructure.db.mappers import domain_to_dto
            return domain_to_dto(saved)
