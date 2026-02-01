from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class AlertBase(BaseModel):
    alert_type: str
    severity: str
    title: str
    message: str
    action_required: Optional[str] = None
    action_url: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None

class AlertCreate(AlertBase):
    user_id: str
    field_id: Optional[UUID] = None
    crop_cycle_id: Optional[UUID] = None

class AlertUpdate(BaseModel):
    acknowledged: Optional[bool] = None
    dismissed: Optional[bool] = None

class Alert(AlertBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: str
    field_id: Optional[UUID] = None
    crop_cycle_id: Optional[UUID] = None
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    dismissed: bool
    dismissed_at: Optional[datetime] = None
    created_at: datetime
