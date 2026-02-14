"""
Forum ORM Models
Advisory Service - Farm Connect AgriManagement
"""
from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, Text, Boolean, ARRAY, Enum as SAEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.domain.common.enums import OrderStatus  # Using existing enum as placeholder


class ForumThreadORM(Base):
    """Forum thread ORM model"""
    __tablename__ = "forum_threads"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    content_body: Mapped[str] = mapped_column(Text, nullable=False)
    content_format: Mapped[str] = mapped_column(String(20), default="markdown")
    
    # Author information
    author_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    author_username: Mapped[str] = mapped_column(String(100), nullable=False)
    author_reputation: Mapped[int] = mapped_column(Integer, default=0)
    author_badge: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Categorization
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(50)), default=list)
    
    # Context linkage
    context_field_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    context_crop_cycle_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    context_crop_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    context_growth_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    moderation_status: Mapped[str] = mapped_column(String(20), default="approved", index=True)
    
    # Engagement stats
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    upvote_count: Mapped[int] = mapped_column(Integer, default=0)
    downvote_count: Mapped[int] = mapped_column(Integer, default=0)
    bookmark_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    bumped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    comments: Mapped[List["ForumCommentORM"]] = relationship("ForumCommentORM", back_populates="thread", cascade="all, delete-orphan")
    votes: Mapped[List["ForumVoteORM"]] = relationship("ForumVoteORM", back_populates="thread", cascade="all, delete-orphan")
    bookmarks: Mapped[List["ForumBookmarkORM"]] = relationship("ForumBookmarkORM", back_populates="thread", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_forum_threads_category_status', 'category', 'status'),
        Index('idx_forum_threads_bumped', 'bumped_at'),
    )


class ForumCommentORM(Base):
    """Forum comment ORM model"""
    __tablename__ = "forum_comments"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    thread_id: Mapped[str] = mapped_column(String, ForeignKey("forum_threads.id"), nullable=False, index=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("forum_comments.id"), nullable=True, index=True)
    
    # Author information
    author_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    author_username: Mapped[str] = mapped_column(String(100), nullable=False)
    author_reputation: Mapped[int] = mapped_column(Integer, default=0)
    author_badge: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_format: Mapped[str] = mapped_column(String(20), default="markdown")
    
    # Attachments (JSON)
    attachments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # Moderation
    moderation_status: Mapped[str] = mapped_column(String(20), default="approved")
    moderation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Engagement
    upvote_count: Mapped[int] = mapped_column(Integer, default=0)
    downvote_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_accepted_answer: Mapped[bool] = mapped_column(Boolean, default=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    edit_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    thread: Mapped["ForumThreadORM"] = relationship("ForumThreadORM", back_populates="comments")
    parent: Mapped[Optional["ForumCommentORM"]] = relationship("ForumCommentORM", remote_side=[id], backref="replies")
    votes: Mapped[List["ForumVoteORM"]] = relationship("ForumVoteORM", back_populates="comment", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_forum_comments_thread_created', 'thread_id', 'created_at'),
    )


class ForumVoteORM(Base):
    """Forum vote ORM model"""
    __tablename__ = "forum_votes"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    thread_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("forum_threads.id"), nullable=True, index=True)
    comment_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("forum_comments.id"), nullable=True, index=True)
    
    # Voter information
    voter_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    vote_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "up" or "down"
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    thread: Mapped[Optional["ForumThreadORM"]] = relationship("ForumThreadORM", back_populates="votes")
    comment: Mapped[Optional["ForumCommentORM"]] = relationship("ForumCommentORM", back_populates="votes")
    
    __table_args__ = (
        Index('idx_forum_votes_unique', 'thread_id', 'comment_id', 'voter_id', unique=True),
    )


class ForumBookmarkORM(Base):
    """Forum bookmark ORM model"""
    __tablename__ = "forum_bookmarks"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    thread_id: Mapped[str] = mapped_column(String, ForeignKey("forum_threads.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    folder_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    thread: Mapped["ForumThreadORM"] = relationship("ForumThreadORM", back_populates="bookmarks")
    
    __table_args__ = (
        Index('idx_forum_bookmarks_unique', 'thread_id', 'user_id', unique=True),
    )


class ForumReportORM(Base):
    """Forum report ORM model for moderation"""
    __tablename__ = "forum_reports"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    thread_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    comment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Report details
    reporter_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(30), nullable=False)  # spam, inappropriate, misinformation, other
    report_reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Moderation
    assigned_moderator_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    moderation_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    moderation_decision: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # upheld, dismissed
    moderation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_forum_reports_status', 'moderation_status', 'report_type'),
    )
