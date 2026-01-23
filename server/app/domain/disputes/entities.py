from dataclasses import dataclass
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime, timezone
from app.domain.common.enums import DisputeState, DisputeResolution

@dataclass
class Dispute:
    id: Optional[str] = None
    order_id: Optional[str] = None
    raised_by: Optional[str] = None
    state: Optional[DisputeState] = None
    reason: Optional[str] = None
    resolution: Optional[DisputeResolution] = None
    evidence_urls: Optional[List[Any]] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    def resolve(self, resolution: DisputeResolution) -> None:
        """Mark the dispute as resolved with the given resolution."""
        self.state = DisputeState.RESOLVED
        self.resolution = resolution
        self.resolved_at = datetime.now(timezone.utc)
