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
    # Escalation chain fields (Gap 3)
    handler_role: Optional[str] = None
    escalated_to: Optional[str] = None
    escalation_note: Optional[str] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    def resolve(self, resolution: DisputeResolution) -> None:
        """Mark the dispute as resolved with the given resolution."""
        self.state = DisputeState.RESOLVED
        self.resolution = resolution
        self.resolved_at = datetime.now(timezone.utc)

    def escalate(self, target_role: str, note: Optional[str] = None) -> None:
        """
        Escalate the dispute to the next handler in the chain.
        MODERATOR → AGENT or MANAGER. MANAGER → ADMIN (recorded as escalated_to).
        """
        target_role = target_role.upper()
        if target_role == "AGENT":
            self.state = DisputeState.ESCALATED_TO_AGENT
        elif target_role == "MANAGER":
            self.state = DisputeState.ESCALATED_TO_MANAGER
        else:
            # For ADMIN escalation just record in escalated_to
            self.state = DisputeState.UNDER_REVIEW
        self.handler_role = target_role
        self.escalated_to = target_role
        self.escalation_note = note
