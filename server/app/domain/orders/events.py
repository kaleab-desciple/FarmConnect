from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class OrderCreated:
    order_id: UUID
    timestamp: datetime = datetime.utcnow()

@dataclass
class OrderUpdated:
    order_id: UUID
    timestamp: datetime = datetime.utcnow()
