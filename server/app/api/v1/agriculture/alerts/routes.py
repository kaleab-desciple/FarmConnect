from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user
from .service import AlertService
from .dto import Alert, AlertCreate, AlertUpdate

router = APIRouter()

@router.get("", response_model=List[Alert])
def list_alerts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List alerts for current user"""
    service = AlertService(db)
    user_id = current_user["sub"]
    
    return service.list_alerts(
        user_id=user_id,
        severity=severity,
        alert_type=alert_type,
        unread_only=unread_only,
        skip=skip,
        limit=limit
    )


@router.get("/unread/count")
def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread alerts"""
    service = AlertService(db)
    user_id = current_user["sub"]
    
    count = service.get_unread_count(user_id)
    return {"unread_count": count}


@router.get("/critical", response_model=List[Alert])
def list_critical_alerts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List critical and emergency alerts"""
    service = AlertService(db)
    user_id = current_user["sub"]
    
    return service.list_critical_alerts(user_id)


@router.get("/{alert_id}", response_model=Alert)
def get_alert(
    alert_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert by ID"""
    service = AlertService(db)
    alert = service.get_alert(str(alert_id))
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    user_id = current_user["sub"]
    user_roles = current_user.get("realm_access", {}).get("roles", [])
    
    if alert.user_id != user_id and "ADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this alert"
        )
    
    return alert


@router.post("/{alert_id}/acknowledge", response_model=Alert)
def acknowledge_alert(
    alert_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    service = AlertService(db)
    
    # Check alert exists and belongs to user
    alert = service.get_alert(str(alert_id))
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    user_id = current_user["sub"]
    
    if alert.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to acknowledge this alert"
        )
    
    updated_alert = service.acknowledge_alert(str(alert_id))
    return updated_alert


@router.post("/{alert_id}/dismiss", response_model=Alert)
def dismiss_alert(
    alert_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss an alert"""
    service = AlertService(db)
    
    # Check alert exists and belongs to user
    alert = service.get_alert(str(alert_id))
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    user_id = current_user["sub"]
    
    if alert.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to dismiss this alert"
        )
    
    updated_alert = service.dismiss_alert(str(alert_id))
    return updated_alert
