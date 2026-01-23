from dataclasses import dataclass
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from app.domain.common.enums import LoanState

@dataclass(frozen=True)
class Loan:
    id: Optional[UUID] = None
    farmer_id: Optional[UUID] = None
    principal: Optional[float] = None
    interest_rate: Optional[float] = None
    state: Optional[LoanState] = None
    auto_approved: Optional[bool] = False
    repayment_schedule: Optional[List[Any]] = None
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
