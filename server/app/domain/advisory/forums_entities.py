"""
Domain Entities for Forums System - Complete Implementation
Advisory Service - Farm Connect AgriManagement
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field
import uuid


class ThreadStatus(Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ModerationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ForumThread:
    """Forum thread entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Content
    title: str = ""
    slug: str = ""
    content_body: str = ""
    content_format: str = "markdown"
    
    # Author information
    author_id: str = ""
    author_username: str = ""
    author_reputation: int = 0
    author_badge: Optional[str] = None
    
    # Categorization
    category: str = ""
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Context linkage (optional)
    context_field_id: Optional[str] = None
    context_crop_cycle_id: Optional[str] = None
    context_crop_type: Optional[str] = None
    context_growth_stage: Optional[str] = None
    
    # Status
    status: str = "open"
    moderation_status: str = "approved"
    
    # Engagement stats
    view_count: int = 0
    upvote_count: int = 0
    downvote_count: int = 0
    bookmark_count: int = 0
    comment_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    bumped_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "content_body": self.content_body,
            "content_format": self.content_format,
            "author_id": self.author_id,
            "author_username": self.author_username,
            "author_reputation": self.author_reputation,
            "author_badge": self.author_badge,
            "category": self.category,
            "subcategory": self.subcategory,
            "tags": self.tags or [],
            "context_field_id": self.context_field_id,
            "context_crop_cycle_id": self.context_crop_cycle_id,
            "context_crop_type": self.context_crop_type,
            "context_growth_stage": self.context_growth_stage,
            "status": self.status,
            "moderation_status": self.moderation_status,
            "view_count": self.view_count,
            "upvote_count": self.upvote_count,
            "downvote_count": self.downvote_count,
            "bookmark_count": self.bookmark_count,
            "comment_count": self.comment_count,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "bumped_at": self.bumped_at.isoformat() if isinstance(self.bumped_at, datetime) else self.bumped_at,
            "last_activity_at": self.last_activity_at.isoformat() if isinstance(self.last_activity_at, datetime) else self.last_activity_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ForumThread':
        """Create from dictionary"""
        thread = cls()
        datetime_fields = ["created_at", "updated_at", "bumped_at", "last_activity_at"]
        for key, value in data.items():
            if hasattr(thread, key):
                if key in datetime_fields and value:
                    if isinstance(value, str):
                        setattr(thread, key, datetime.fromisoformat(value))
                    else:
                        setattr(thread, key, value)
                else:
                    setattr(thread, key, value)
        return thread


@dataclass
class ForumComment:
    """Forum comment/reply entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str = ""
    parent_id: Optional[str] = None  # For nested replies
    
    # Author information
    author_id: str = ""
    author_username: str = ""
    author_reputation: int = 0
    author_badge: Optional[str] = None
    
    # Content
    content: str = ""
    content_format: str = "markdown"
    
    # Attachments
    attachments: List[dict] = field(default_factory=list)
    
    # Moderation
    moderation_status: str = "approved"
    moderation_notes: Optional[str] = None
    
    # Engagement
    upvote_count: int = 0
    downvote_count: int = 0
    
    # Status
    is_accepted_answer: bool = False
    is_edited: bool = False
    edit_history: List[dict] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "parent_id": self.parent_id,
            "author_id": self.author_id,
            "author_username": self.author_username,
            "author_reputation": self.author_reputation,
            "author_badge": self.author_badge,
            "content": self.content,
            "content_format": self.content_format,
            "attachments": self.attachments or [],
            "moderation_status": self.moderation_status,
            "moderation_notes": self.moderation_notes,
            "upvote_count": self.upvote_count,
            "downvote_count": self.downvote_count,
            "is_accepted_answer": self.is_accepted_answer,
            "is_edited": self.is_edited,
            "edit_history": self.edit_history or [],
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ForumComment':
        """Create from dictionary"""
        comment = cls()
        datetime_fields = ["created_at", "updated_at"]
        for key, value in data.items():
            if hasattr(comment, key):
                if key in datetime_fields and value:
                    if isinstance(value, str):
                        setattr(comment, key, datetime.fromisoformat(value))
                    else:
                        setattr(comment, key, value)
                else:
                    setattr(comment, key, value)
        return comment


@dataclass
class ForumVote:
    """Vote entity for content ranking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: Optional[str] = None
    comment_id: Optional[str] = None
    
    # Voter information
    voter_id: str = ""
    vote_type: str = "up"  # "up" or "down"
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "comment_id": self.comment_id,
            "voter_id": self.voter_id,
            "vote_type": self.vote_type,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ForumVote':
        """Create from dictionary"""
        vote = cls()
        for key, value in data.items():
            if hasattr(vote, key):
                if key == "created_at" and value:
                    if isinstance(value, str):
                        setattr(vote, key, datetime.fromisoformat(value))
                    else:
                        setattr(vote, key, value)
                else:
                    setattr(vote, key, value)
        return vote


@dataclass
class ForumBookmark:
    """Bookmark entity for saving threads"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str = ""
    user_id: str = ""
    folder_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "user_id": self.user_id,
            "folder_name": self.folder_name,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


@dataclass
class ForumReport:
    """Report entity for moderation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: Optional[str] = None
    comment_id: Optional[str] = None
    
    # Report details
    reporter_id: str = ""
    report_type: str = ""  # spam, inappropriate, misinformation, other
    report_reason: str = ""
    evidence: Optional[str] = None
    
    # Moderation
    assigned_moderator_id: Optional[str] = None
    moderation_status: str = "pending"
    moderation_decision: Optional[str] = None
    moderation_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "comment_id": self.comment_id,
            "reporter_id": self.reporter_id,
            "report_type": self.report_type,
            "report_reason": self.report_reason,
            "evidence": self.evidence,
            "assigned_moderator_id": self.assigned_moderator_id,
            "moderation_status": self.moderation_status,
            "moderation_decision": self.moderation_decision,
            "moderation_notes": self.moderation_notes,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "resolved_at": self.resolved_at.isoformat() if isinstance(self.resolved_at, datetime) else self.resolved_at
        }
