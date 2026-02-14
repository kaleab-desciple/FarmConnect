"""
Notification Repository - Data Access Layer
Advisory Service - Farm Connect AgriManagement
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from datetime import datetime

from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.infrastructure.db.models.notifications import NotificationORM, NotificationPreferenceORM
from app.domain.advisory.notifications import Notification, UserNotificationPreference


class NotificationRepository:
    """Repository for notification data access"""
    
    def __init__(self, session: Session):
        self.session = session

    def save_notification(self, notification: Notification) -> Notification:
        """Save a notification (create or update)"""
        orm = None
        if notification.id:
            orm = self.session.query(NotificationORM).filter(
                NotificationORM.id == notification.id
            ).one_or_none()
        
        if orm:
            # Update existing
            updated_orm = domain_to_orm(notification)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new
            orm = domain_to_orm(notification)
            self.session.add(orm)
        
        self.session.commit()
        return orm_to_domain(orm)

    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID"""
        orm = self.session.query(NotificationORM).filter(
            NotificationORM.id == notification_id
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Notification], int]:
        """List notifications for a user"""
        query = self.session.query(NotificationORM).filter(
            NotificationORM.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(NotificationORM.is_read == False)
            
        # Total count before pagination
        total = query.count()
        
        # Sort by creation date desc
        query = query.order_by(desc(NotificationORM.created_at))
        
        # Pagination
        query = query.offset(offset).limit(limit)
        
        orms = query.all()
        return [orm_to_domain(orm) for orm in orms], total

    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        result = self.session.query(NotificationORM).filter(
            NotificationORM.id == notification_id
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        self.session.commit()
        return result > 0

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read"""
        result = self.session.query(NotificationORM).filter(
            NotificationORM.user_id == user_id,
            NotificationORM.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        self.session.commit()
        return result

    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        result = self.session.query(NotificationORM).filter(
            NotificationORM.id == notification_id
        ).delete()
        self.session.commit()
        return result > 0

    # ============ Preferences ============

    def get_user_preferences(self, user_id: str) -> Optional[UserNotificationPreference]:
        """Get notification preferences for a user"""
        orm = self.session.query(NotificationPreferenceORM).filter(
            NotificationPreferenceORM.user_id == user_id
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)

    def save_user_preferences(self, preferences: UserNotificationPreference) -> UserNotificationPreference:
        """Save user notification preferences"""
        orm = self.session.query(NotificationPreferenceORM).filter(
            NotificationPreferenceORM.user_id == preferences.user_id
        ).one_or_none()
        
        if orm:
            # Update
            updated_orm = domain_to_orm(preferences)
            # Preserve ID if it was auto-generated differently in domain vs DB
            preferences_id = orm.id 
            
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create
            orm = domain_to_orm(preferences)
            self.session.add(orm)
            
        self.session.commit()
        return orm_to_domain(orm)
