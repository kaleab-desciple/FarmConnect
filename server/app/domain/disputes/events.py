from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class DisputeRaised:
    dispute_id: UUID
    timestamp: datetime = datetime.utcnow()
