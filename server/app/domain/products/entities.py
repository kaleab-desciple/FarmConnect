from decimal import Decimal
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.domain.common.enums import Category, Unit, QualityGrade


@dataclass(frozen=True)
class Product:
    category: Category
    unit: Unit
    base_price: Decimal
    id: Optional[str] = None
    farmer_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = "USD"
    quantity_available: Optional[Decimal] = None
    quality_grade: Optional[QualityGrade] = None
    harvest_id: Optional[str] = None  # Traceability
    crop_cycle_id: Optional[str] = None  # Traceability
    harvest_date: Optional[date] = None
    expiry_date: Optional[date] = None
    location: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None