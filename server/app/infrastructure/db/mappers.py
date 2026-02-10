from typing import Type, Any, Dict
from enum import Enum

# Shared models (Pydantic DTOs)
#Farm, Field, CropCycle, Alert
from shared_models import User, Product, Order, Escrow, Dispute, Reputation
from shared_models.enums import DisputeResolution
from app.domain.ledger.entities import LedgerEvent

# ORM models
from app.infrastructure.db.models.user import UserORM
from app.infrastructure.db.models.product import ProductORM
from app.infrastructure.db.models.order import OrderORM
from app.infrastructure.db.models.escrow import EscrowORM
from app.infrastructure.db.models.dispute import DisputeORM
from app.infrastructure.db.models.reputation import ReputationORM
from app.infrastructure.db.models.ledger import LedgerEventORM
from app.infrastructure.db.models.pricing import PricingRuleORM
#from app.infrastructure.db.models.farm import FarmORM, FieldORM
#from app.infrastructure.db.models.crop import CropCycleORM
#from app.infrastructure.db.models.alert import AlertORM

# Domain entity imports are done lazily inside conversion functions to avoid
# import-time errors during Alembic env import (domain modules may be
# application-specific and not required for migrations).


# === TYPE MAPPING: DTO class -> ORM class ===
TYPE_MAP: dict[Type[Any], Type[Any]] = {
    User: UserORM,
    Product: ProductORM,
    Order: OrderORM,
    Escrow: EscrowORM,
    Dispute: DisputeORM,
    Reputation: ReputationORM,
    LedgerEvent: LedgerEventORM,
#    Farm: FarmORM,
#    Field: FieldORM,
#    CropCycle: CropCycleORM,
#    Alert: AlertORM,
}


from uuid import UUID
from pydantic import AnyUrl

# === HELPERS ===
def _json_safe(obj: Any) -> Any:
    """Recursively convert non-serializable Pydantic/UUID types to JSON-safe ones."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (AnyUrl, UUID)):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    # Handle Pydantic models (like Location)
    if hasattr(obj, 'model_dump'):
        return _json_safe(obj.model_dump())
    return obj


# === DTO -> ORM ===
def dto_to_orm(dto: Any) -> Any:
    """
    Convert a shared DTO (Pydantic) to its corresponding ORM model.
    """
    orm_cls = TYPE_MAP.get(type(dto))
    if orm_cls is None:
        raise ValueError(f"No ORM mapping defined for DTO type {type(dto)}")
    
    # Support both Pydantic models (with model_dump) and dataclasses (with __dict__ or asdict)
    from dataclasses import is_dataclass, asdict
    if hasattr(dto, "model_dump"):
        raw_data = dto.model_dump()
    elif is_dataclass(dto):
        raw_data = asdict(dto)
    else:
        raw_data = dto.__dict__
        
    data = _json_safe(raw_data)

    # Specific mapping for Order DTO to OrderORM to handle delivery_cost
    if isinstance(dto, Order) and 'delivery_cost' in data:
        if data.get('delivery_fee') is None and data.get('delivery_cost') is not None:
            data['delivery_fee'] = data['delivery_cost']

    # Filter data to only include keys that are valid ORM attributes
    # We use column attributes to avoid including relationships in basic mapping
    from sqlalchemy import inspect
    mapper = inspect(orm_cls)
    orm_column_keys = {a.key for a in mapper.column_attrs}
    filtered_data = {k: v for k, v in data.items() if k in orm_column_keys}

    return orm_cls(**filtered_data)


# === ORM -> Domain Entity ===
def orm_to_domain(orm: Any) -> Any:
    """
    Convert an ORM object to a pure Domain entity.
    Automatically ignores SQLAlchemy internal attributes (_sa_instance_state)
    and uses the appropriate Domain class based on the ORM type.
    """
    # Import domain classes lazily to keep module import lightweight for Alembic.
    from app.domain.users.entities import User as DomainUser
    from app.domain.products.entities import Product as DomainProduct
    from app.domain.orders.entities import Order as DomainOrder
    from app.domain.payments.entities import Escrow as DomainEscrow
    from app.domain.disputes.entities import Dispute as DomainDispute
    from app.domain.reputation.entities import Reputation as DomainReputation
    from app.domain.pricing.entities import PricingRule
#    from app.domain.agriculture.entities import Farm as DomainFarm, Field as DomainField, CropCycle as DomainCropCycle, Alert as DomainAlert

    orm_type_map = {
        UserORM: DomainUser,
        ProductORM: DomainProduct,
        OrderORM: DomainOrder,
        EscrowORM: DomainEscrow,
        DisputeORM: DomainDispute,
        ReputationORM: DomainReputation,
        LedgerEventORM: LedgerEvent,
        PricingRuleORM: PricingRule,
#        FarmORM: DomainFarm,
#        FieldORM: DomainField,
#        CropCycleORM: DomainCropCycle,
#        AlertORM: DomainAlert,
    }

    domain_cls = orm_type_map.get(type(orm))
    if domain_cls is None:
        raise ValueError(f"No Domain mapping defined for ORM type {type(orm)}")

    data: Dict[str, Any] = {
        k: v for k, v in orm.__dict__.items() if not k.startswith("_")
    }
    
    # Handle SQLAlchemy reserved attribute names
    # Some ORMs use 'metadata_' to avoid conflict with Base.metadata
    # Check if domain class expects 'metadata' or 'metadata_'
    if 'metadata_' in data:
        # Check if the domain class has a 'metadata_' field or 'metadata' field
        import inspect
        if hasattr(domain_cls, '__dataclass_fields__'):
            # For dataclasses
            if 'metadata' in domain_cls.__dataclass_fields__ and 'metadata_' not in domain_cls.__dataclass_fields__:
                data['metadata'] = data.pop('metadata_')
        elif hasattr(domain_cls, 'model_fields'):
            # For Pydantic models
            if 'metadata' in domain_cls.model_fields and 'metadata_' not in domain_cls.model_fields:
                data['metadata'] = data.pop('metadata_')
    
#     return domain_cls(**_json_safe(data))
    return domain_cls(**data)


# === Domain Entity -> ORM ===
def domain_to_orm(domain_obj: Any) -> Any:
    """
    Convert a Domain entity to its corresponding ORM model.
    """
    # Import domain classes lazily
    from app.domain.users.entities import User as DomainUser
    from app.domain.products.entities import Product as DomainProduct
    from app.domain.orders.entities import Order as DomainOrder
    from app.domain.payments.entities import Escrow as DomainEscrow
    from app.domain.disputes.entities import Dispute as DomainDispute
    from app.domain.reputation.entities import Reputation as DomainReputation
    from app.domain.pricing.entities import PricingRule
#    from app.domain.agriculture.entities import Farm as DomainFarm, Field as DomainField, CropCycle as DomainCropCycle
#    from app.domain.agriculture.entities import Alert as DomainAlert

    domain_type_map = {
        DomainUser: UserORM,
        DomainProduct: ProductORM,
        DomainOrder: OrderORM,
        DomainEscrow: EscrowORM,
        DomainDispute: DisputeORM,
        DomainReputation: ReputationORM,
        LedgerEvent: LedgerEventORM,
        PricingRule: PricingRuleORM,
#       DomainFarm: FarmORM,
#       DomainField: FieldORM,
#        DomainCropCycle: CropCycleORM,
#        DomainAlert: AlertORM,
    }

    orm_cls = domain_type_map.get(type(domain_obj))
    if orm_cls is None:
        raise ValueError(f"No ORM mapping defined for domain type {type(domain_obj)}")

    data: Dict[str, Any] = {
        k: v for k, v in domain_obj.__dict__.items() if not k.startswith("_")
    }
    
    # Handle SQLAlchemy reserved attribute names
    # Some ORMs use 'metadata_' to avoid conflict with Base.metadata
    # Check if we need to convert 'metadata' to 'metadata_'
    if 'metadata' in data:
        orm_columns = {c.name for c in orm_cls.__table__.columns}
        # If ORM has a 'metadata' column but the Python attribute is 'metadata_'
        if 'metadata' in orm_columns and hasattr(orm_cls, 'metadata_'):
            data['metadata_'] = data.pop('metadata')
    
    # Filter data to only include keys that are valid ORM attributes
    from sqlalchemy import inspect
    mapper = inspect(orm_cls)
    orm_column_keys = {a.key for a in mapper.column_attrs}
    filtered_data = {k: v for k, v in data.items() if k in orm_column_keys}
    
    return orm_cls(**_json_safe(filtered_data))


# === DOMAIN ENTITY -> DTO (Optional, if needed) ===
def domain_to_dto(domain_obj: Any) -> Any:
    """
    Convert a Domain entity back to the corresponding shared DTO.
    """
    # Lazy import of domain classes
    from app.domain.users.entities import User as DomainUser
    from app.domain.products.entities import Product as DomainProduct
    from app.domain.orders.entities import Order as DomainOrder
    from app.domain.payments.entities import Escrow as DomainEscrow
    from app.domain.disputes.entities import Dispute as DomainDispute
    from app.domain.reputation.entities import Reputation as DomainReputation
#    from app.domain.agriculture.entities import Farm as DomainFarm, Field as DomainField
#    from app.domain.agriculture.entities import CropCycle as DomainCropCycle, Alert as DomainAlert

    domain_type_map = {
        DomainUser: User,
        DomainProduct: Product,
        DomainOrder: Order,
        DomainEscrow: Escrow,
        DomainDispute: Dispute,
        DomainReputation: Reputation,
#        DomainFarm: Farm,
#        DomainField: Field,
#        DomainCropCycle: CropCycle,
#        DomainAlert: Alert,
    }
    dto_cls = domain_type_map.get(type(domain_obj))
    if dto_cls is None:
        raise ValueError(f"No DTO mapping defined for domain type {type(domain_obj)}")
    return dto_cls(**_json_safe(domain_obj.__dict__))

    