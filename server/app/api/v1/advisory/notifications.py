"""
Notifications API Routes
Advisory Service - Farm Connect AgriManagement
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from pydantic import BaseModel

from app.core.auth.dependencies import require_auth, TokenPayload
from app.domain.advisory.notification_service import NotificationService
from app.api.v1.advisory.dependencies import get_notification_service

router = APIRouter()


class NotificationResponse(BaseModel):
    """Notification response model"""
    id: str
    type: str
    title: str
    message: str
    action_url: Optional[str]
    is_read: bool
    created_at: str
    from_user_name: Optional[str]


class PreferencesUpdate(BaseModel):
    """Preferences update model"""
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    reply_notifications: Optional[bool] = None
    upvote_notifications: Optional[bool] = None
    mention_notifications: Optional[bool] = None
    moderation_notifications: Optional[bool] = None
    article_notifications: Optional[bool] = None


@router.get("", response_model=Dict[str, Any])
async def list_notifications(
    unread_only: bool = Query(False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: NotificationService = Depends(get_notification_service),
    current_user: TokenPayload = Depends(require_auth)
):
    """
    List user notifications.
    """
    offset = (page - 1) * page_size
    notifications, total = service.get_user_notifications(
        user_id=current_user.user_id,
        unread_only=unread_only,
        limit=page_size,
        offset=offset
    )
    
    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.notification_type,
                "title": n.title,
                "message": n.message,
                "action_url": n.action_url,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
                "from_user_name": n.from_user_name
            } for n in notifications
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service),
    current_user: TokenPayload = Depends(require_auth)
):
    """
    Mark a notification as read.
    """
    success = service.mark_read(notification_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}


@router.post("/read-all")
async def mark_all_read(
    service: NotificationService = Depends(get_notification_service),
    current_user: TokenPayload = Depends(require_auth)
):
    """
    Mark all notifications as read.
    """
    count = service.mark_all_read(current_user.user_id)
    return {"count": count}


@router.get("/preferences")
async def get_preferences(
    service: NotificationService = Depends(get_notification_service),
    current_user: TokenPayload = Depends(require_auth)
):
    """
    Get user notification preferences.
    """
    prefs = service.get_preferences(current_user.user_id)
    return prefs.__dict__ # Simple return for dataclass/entity


@router.put("/preferences")
async def update_preferences(
    prefs_data: PreferencesUpdate,
    service: NotificationService = Depends(get_notification_service),
    current_user: TokenPayload = Depends(require_auth)
):
    """
    Update user notification preferences.
    """
    data = prefs_data.dict(exclude_unset=True)
    prefs = service.update_preferences(current_user.user_id, data)
    return prefs.__dict__
