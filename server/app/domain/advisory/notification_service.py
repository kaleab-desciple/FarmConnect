"""
Notification Service - Business Logic
Advisory Service - Farm Connect AgriManagement
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.domain.advisory.notifications import (
    Notification, UserNotificationPreference, NotificationType, 
    NotificationChannel, NotificationPriority
)
from app.infrastructure.repositories.notification_repo import NotificationRepository
from app.infrastructure.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications and user preferences"""
    
    def __init__(
        self, 
        notification_repo: NotificationRepository,
        user_repo: UserRepository
    ):
        self.notification_repo = notification_repo
        self.user_repo = user_repo

    async def create_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        context: Dict[str, str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        from_user_id: Optional[str] = None,
        channels: Optional[List[str]] = None
    ) -> Optional[Notification]:
        """
        Create and send a notification to a user.
        Checks user preferences before sending.
        """
        # 1. Check user preferences
        prefs = self.notification_repo.get_user_preferences(user_id)
        if not prefs:
            # Create default preferences if none exist
            prefs = UserNotificationPreference(user_id=user_id)
            self.notification_repo.save_user_preferences(prefs)
            
        # 2. Check if this type of notification is enabled
        if not self._is_notification_enabled(prefs, type):
            logger.info(f"Notification {type} suppressed by user {user_id} preferences")
            return None
            
        # 3. Determine channels
        if not channels:
            channels = self._get_enabled_channels(prefs)
        
        if not channels:
            logger.info(f"No channels enabled for user {user_id}")
            return None

        # 4. Create Notification entity
        context = context or {}
        notification = Notification(
            user_id=user_id,
            notification_type=type,
            title=title,
            message=message,
            action_url=action_url,
            priority=priority,
            from_user_id=from_user_id,
            channels=channels,
            thread_id=context.get("thread_id"),
            comment_id=context.get("comment_id"),
            article_id=context.get("article_id")
        )
        
        # 5. Populate from_user_name if known
        if from_user_id:
            from_user = self.user_repo.get_by_id(from_user_id)
            if from_user:
                notification.from_user_name = from_user.name
        
        # 6. Save in-app notification
        saved_notification = self.notification_repo.save_notification(notification)
        
        # 7. Dispatch to other channels (Email, SMS, Push) - Stubs for now
        # In a real system, this would push to a queue (e.g., Celery, Kafka)
        # self.email_service.send(...)
        
        return saved_notification

    def _is_notification_enabled(self, prefs: UserNotificationPreference, type: NotificationType) -> bool:
        """Check if a specific notification type is enabled in preferences"""
        if type in [NotificationType.THREAD_REPLY, NotificationType.THREAD_RESOLVED, NotificationType.ANSWER_ACCEPTED]:
            return prefs.reply_notifications
        elif type == NotificationType.COMMENT_UPVOTE:
            return prefs.upvote_notifications
        elif type == NotificationType.MENTION:
            return prefs.mention_notifications
        elif type in [NotificationType.REPORT_RECEIVED, NotificationType.REPORT_RESOLVED, NotificationType.CONTENT_REMOVED]:
            return prefs.moderation_notifications
        elif type in [NotificationType.NEW_ARTICLE, NotificationType.ARTICLE_UPDATE]:
            return prefs.article_notifications
        
        # Default to True for system/other types
        return True

    def _get_enabled_channels(self, prefs: UserNotificationPreference) -> List[str]:
        """Get list of enabled channels string names"""
        channels = []
        if prefs.in_app_enabled:
            channels.append("in_app")
        if prefs.email_enabled:
            channels.append("email")
        if prefs.sms_enabled:
            channels.append("sms")
        if prefs.push_enabled:
            channels.append("push")
        return channels

    def get_user_notifications(
        self, 
        user_id: str, 
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Notification], int]:
        """Get notifications for a user"""
        return self.notification_repo.list_user_notifications(
            user_id, unread_only, limit, offset
        )

    def mark_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read, ensuring ownership"""
        notif = self.notification_repo.get_notification_by_id(notification_id)
        if not notif or notif.user_id != user_id:
            return False
            
        return self.notification_repo.mark_as_read(notification_id)

    def mark_all_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read"""
        return self.notification_repo.mark_all_as_read(user_id)

    def update_preferences(
        self, 
        user_id: str, 
        preferences_data: Dict[str, Any]
    ) -> UserNotificationPreference:
        """Update user notification preferences"""
        current_prefs = self.notification_repo.get_user_preferences(user_id)
        if not current_prefs:
            current_prefs = UserNotificationPreference(user_id=user_id)
            
        # Update fields
        for key, value in preferences_data.items():
            if hasattr(current_prefs, key):
                setattr(current_prefs, key, value)
                
        return self.notification_repo.save_user_preferences(current_prefs)

    def get_preferences(self, user_id: str) -> UserNotificationPreference:
        """Get or create user preferences"""
        prefs = self.notification_repo.get_user_preferences(user_id)
        if not prefs:
            prefs = UserNotificationPreference(user_id=user_id)
            self.notification_repo.save_user_preferences(prefs)
        return prefs
