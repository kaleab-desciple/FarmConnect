from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class UserCreated:
    user_id: UUID
    timestamp: datetime = datetime.utcnow()

@dataclass
class UserUpdated:
    user_id: UUID
    timestamp: datetime = datetime.utcnow()
