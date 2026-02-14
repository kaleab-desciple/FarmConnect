"""
Domain Entities for Forums System - Threads
Advisory Service - Farm Connect AgriManagement
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field
import uuid


class ThreadStatus(str, Enum):
    """Thread status values"""
    OPEN = "open"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ThreadCategory(str, Enum):
    """Thread categories for agricultural discussions"""
    GENERAL = "general"
    PEST_DISEASE = "pest_disease"
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    SOIL_HEALTH = "soil_health"
    WEATHER = "weather"
    HARVEST = "harvest"
    EQUIPMENT = "equipment"
    MARKET_PRICES = "market_prices"
    ORGANIC_FARMING = "organic_farming"
    LIVESTOCK = "livestock"


@dataclass
class ForumThread:
    """Forum thread entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
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
    category: ThreadCategory = ThreadCategory.GENERAL
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Context linkage
    context_field_id: Optional[str] = None
    context_crop_cycle_id: Optional[str] = None
    context_crop_type: Optional[str] = None
    context_growth_stage: Optional[str] = None
    
    # Status
    status: ThreadStatus = ThreadStatus.OPEN
    
    # Engagement stats
    view_count: int = 0
    upvote_count: int = 0
    downvote_count: int = 0
    bookmark_count: int = 0
    comment_count: int = 0
    
    # Resolution
    accepted_answer_id: Optional[str] = None
    resolution_summary: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    bumped_at: datetime = field(default_factory=datetime.utcnow)
    
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
            "category": self.category.value if self.category else None,
            "subcategory": self.subcategory,
            "tags": self.tags,
            "context_field_id": self.context_field_id,
            "context_crop_cycle_id": self.context_crop_cycle_id,
            "context_crop_type": self.context_crop_type,
            "context_growth_stage": self.context_growth_stage,
            "status": self.status.value if self.status else None,
            "view_count": self.view_count,
            "upvote_count": self.upvote_count,
            "downvote_count": self.downvote_count,
            "bookmark_count": self.bookmark_count,
            "comment_count": self.comment_count,
            "accepted_answer_id": self.accepted_answer_id,
            "resolution_summary": self.resolution_summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "bumped_at": self.bumped_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ForumThread':
        """Create from dictionary"""
        thread = cls()
        for key, value in data.items():
            if hasattr(thread, key):
                if key in ["created_at", "updated_at", "bumped_at"]:
                    setattr(thread, key, datetime.fromisoformat(value) if value else None)
                elif key in ["category", "status"]:
                    enum_class = ThreadStatus if key == "status" else ThreadCategory
                    setattr(thread, key, enum_class(value) if value else None)
                else:
                    setattr(thread, key, value)
        return thread
