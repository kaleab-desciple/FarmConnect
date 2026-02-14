"""
Notification System ORM Models
Advisory Service - Farm Connect AgriManagement
"""
from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, DateTime, Text, Boolean, ARRAY, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class NotificationORM(Base):
    """Notification ORM model"""
    __tablename__ = "user_notifications"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Context
    thread_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("forum_threads.id"), nullable=True)
    comment_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("forum_comments.id"), nullable=True)
    article_id: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Knowledge articles might not be strict FKs depending on module boundaries
    from_user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    from_user_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Delivery
    channels: Mapped[List[str]] = mapped_column(ARRAY(String(20)), default=["in_app"])
    channel_status: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    # user relationship is likely defined on UserORM or handled via simple join
    
    __table_args__ = (
        Index('idx_user_notifications_user', 'user_id', 'is_read'),
        Index('idx_user_notifications_type', 'notification_type'),
        Index('idx_user_notifications_created', 'created_at'),
    )


class NotificationPreferenceORM(Base):
    """User notification preferences ORM model"""
    __tablename__ = "user_notification_preferences"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Channel preferences
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Type preferences
    reply_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    upvote_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    mention_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    moderation_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    article_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Frequency
    email_digest: Mapped[str] = mapped_column(String(20), default="immediate")
    max_daily_notifications: Mapped[int] = mapped_column(Integer, default=50)
    
    # Quiet hours
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    quiet_hours_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quiet_hours_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
