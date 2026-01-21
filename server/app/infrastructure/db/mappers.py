from typing import Type, Any, Dict
from enum import Enum

# Shared models (Pydantic DTOs)
from shared_models import User, Product, Order, Escrow, Loan, Dispute, Reputation
from shared_models.enums import DisputeResolution
from app.domain.ledger.entities import LedgerEvent

# ORM models
from app.infrastructure.db.models.user import UserORM
from app.infrastructure.db.models.product import ProductORM
from app.infrastructure.db.models.order import OrderORM
from app.infrastructure.db.models.payment import EscrowORM
from app.infrastructure.db.models.loan import LoanORM
from app.infrastructure.db.models.dispute import DisputeORM
from app.infrastructure.db.models.reputation import ReputationORM
from app.infrastructure.db.models.ledger import LedgerEventORM

# Domain entity imports are done lazily inside conversion functions to avoid
# import-time errors during Alembic env import (domain modules may be
# application-specific and not required for migrations).


# === TYPE MAPPING: DTO class -> ORM class ===
TYPE_MAP: dict[Type[Any], Type[Any]] = {
    User: UserORM,
    Product: ProductORM,
    Order: OrderORM,
    Escrow: EscrowORM,
    Loan: LoanORM,
    Dispute: DisputeORM,
    Reputation: ReputationORM,
    LedgerEvent: LedgerEventORM,
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
    return orm_cls(**data)


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
    from app.domain.loans.entities import Loan as DomainLoan
    from app.domain.disputes.entities import Dispute as DomainDispute
    from app.domain.reputation.entities import Reputation as DomainReputation

    orm_type_map = {
        UserORM: DomainUser,
        ProductORM: DomainProduct,
        OrderORM: DomainOrder,
        EscrowORM: DomainEscrow,
        LoanORM: DomainLoan,
        DisputeORM: DomainDispute,
        ReputationORM: DomainReputation,
        LedgerEventORM: LedgerEvent,
    }

    domain_cls = orm_type_map.get(type(orm))
    if domain_cls is None:
        raise ValueError(f"No Domain mapping defined for ORM type {type(orm)}")

    data: Dict[str, Any] = {
        k: v for k, v in orm.__dict__.items() if not k.startswith("_")
    }
#     return domain_cls(**_json_safe(data))    
    return domain_cls(**data)


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
    from app.domain.loans.entities import Loan as DomainLoan
    from app.domain.disputes.entities import Dispute as DomainDispute
    from app.domain.reputation.entities import Reputation as DomainReputation

    domain_type_map = {
        DomainUser: User,
        DomainProduct: Product,
        DomainOrder: Order,
        DomainEscrow: Escrow,
        DomainLoan: Loan,
        DomainDispute: Dispute,
        DomainReputation: Reputation,
    }
    dto_cls = domain_type_map.get(type(domain_obj))
    if dto_cls is None:
        raise ValueError(f"No DTO mapping defined for domain type {type(domain_obj)}")
    return dto_cls(**_json_safe(domain_obj.__dict__))
