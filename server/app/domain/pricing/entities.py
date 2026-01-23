from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.domain.common.enums import RuleType, FeeType


@dataclass(frozen=True)
class PricingRule:
    id: str
    rule_type: RuleType
    product_category: Optional[str]
    quality_grade: Optional[str]
    region: Optional[str]
    min_distance_km: Optional[float]
    max_distance_km: Optional[float]
    fee_type: FeeType
    fee_value: float
    priority: int
    active: bool
    valid_from: datetime
    valid_to: Optional[datetime]

    def matches(self, product_category: str, quality_grade: str, region: str, distance_km: float) -> bool:
        """Check if this rule applies to the given parameters."""
        if not self.active:
            return False
        now = datetime.now(timezone.utc)
        if self.valid_from > now or (self.valid_to and self.valid_to < now):
            return False
        if self.product_category and self.product_category != product_category:
            return False
        if self.quality_grade and self.quality_grade != quality_grade:
            return False
        if self.region and self.region != region:
            return False
        if self.min_distance_km is not None and distance_km < self.min_distance_km:
            return False
        if self.max_distance_km is not None and distance_km > self.max_distance_km:
            return False
        return True