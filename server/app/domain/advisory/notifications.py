"""
Domain Entities for Notification System
Advisory Service - Farm Connect AgriManagement
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
import uuid


class NotificationType(str, Enum):
    """Notification types for forums and advisory"""
    THREAD_REPLY = "thread_reply"
    THREAD_RESOLVED = "thread_resolved"
    ANSWER_ACCEPTED = "answer_accepted"
    COMMENT_UPVOTE = "comment_upvote"
    THREAD_UPVOTE = "thread_upvote"
    NEW_FOLLOWER = "new_follower"
    MENTION = "mention"
    MODERATION_ACTION = "moderation_action"
    REPORT_RESPONSE = "report_response"
    ARTICLE_PUBLISHED = "article_published"
    ARTICLE_UPDATE = "article_update"
    EXPERT_RESPONSE = "expert_response"
    SYSTEM = "system"
    REPORT_RECEIVED = "report_received"
    REPORT_RESOLVED = "report_resolved"
    CONTENT_REMOVED = "content_removed"
    NEW_ARTICLE = "new_article"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Notification entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    notification_type: NotificationType = NotificationType.THREAD_REPLY
    
    # Content
    title: str = ""
    message: str = ""
    action_url: Optional[str] = None
    
    # Context
    thread_id: Optional[str] = None
    comment_id: Optional[str] = None
    article_id: Optional[str] = None
    from_user_id: Optional[str] = None
    from_user_name: Optional[str] = None
    
    # Delivery
    channels: list = field(default_factory=lambda: ["in_app"])
    channel_status: dict = field(default_factory=dict)
    
    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "notification_type": self.notification_type.value if self.notification_type else None,
            "title": self.title,
            "message": self.message,
            "action_url": self.action_url,
            "thread_id": self.thread_id,
            "comment_id": self.comment_id,
            "article_id": self.article_id,
            "from_user_id": self.from_user_id,
            "from_user_name": self.from_user_name,
            "channels": self.channels,
            "channel_status": self.channel_status,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "priority": self.priority.value if self.priority else None,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Notification':
        """Create from dictionary"""
        notification = cls()
        for key, value in data.items():
            if hasattr(notification, key):
                if key in ["created_at", "read_at", "expires_at"]:
                    setattr(notification, key, datetime.fromisoformat(value) if value else None)
                elif key == "notification_type":
                    setattr(notification, key, NotificationType(value) if value else None)
                elif key == "priority":
                    setattr(notification, key, NotificationPriority(value) if value else None)
                else:
                    setattr(notification, key, value)
        return notification


@dataclass
class UserNotificationPreference:
    """User notification preferences"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    
    # Channel preferences
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    
    # Type preferences
    reply_notifications: bool = True
    upvote_notifications: bool = True
    mention_notifications: bool = True
    moderation_notifications: bool = True
    article_notifications: bool = False
    
    # Frequency limits
    email_digest: str = "immediate"  # immediate, daily, weekly, none
    max_daily_notifications: int = 50
    
    # Quiet hours
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[int] = None  # Hour of day (0-23)
    quiet_hours_end: Optional[int] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_enabled": self.email_enabled,
            "sms_enabled": self.sms_enabled,
            "push_enabled": self.push_enabled,
            "in_app_enabled": self.in_app_enabled,
            "reply_notifications": self.reply_notifications,
            "upvote_notifications": self.upvote_notifications,
            "mention_notifications": self.mention_notifications,
            "moderation_notifications": self.moderation_notifications,
            "article_notifications": self.article_notifications,
            "email_digest": self.email_digest,
            "max_daily_notifications": self.max_daily_notifications,
            "quiet_hours_enabled": self.quiet_hours_enabled,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
