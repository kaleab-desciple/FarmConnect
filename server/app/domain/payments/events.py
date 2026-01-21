from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class PaymentProcessed:
    payment_id: UUID
    timestamp: datetime = datetime.utcnow()
