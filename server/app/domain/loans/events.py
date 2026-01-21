from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class LoanApproved:
    loan_id: UUID
    timestamp: datetime = datetime.utcnow()
