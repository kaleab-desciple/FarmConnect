from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from shared_models.enums import UserRole

@dataclass(frozen=True)
class User:
    id: Optional[str] = None
    role: Optional[UserRole] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata_: Optional[Dict[str, Any]] = None