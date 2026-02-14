"""
Domain Entities for Knowledge Base System
Advisory Service - Farm Connect AgriManagement
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field
import uuid


class ArticleStatus(str, Enum):
    """Article publication status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"


class ArticleType(str, Enum):
    """Article types"""
    PEST_GUIDE = "pest_guide"
    DISEASE_GUIDE = "disease_guide"
    TREATMENT_PROTOCOL = "treatment_protocol"
    BEST_PRACTICE = "best_practice"
    FAQ = "faq"
    TUTORIAL = "tutorial"
    REGIONAL_GUIDE = "regional_guide"
    CROP_GUIDE = "crop_guide"


class ArticleCategory(str, Enum):
    """Article categories"""
    PEST_MANAGEMENT = "pest_management"
    DISEASE_MANAGEMENT = "disease_management"
    SOIL_HEALTH = "soil_health"
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    WEATHER = "weather"
    HARVEST = "harvest"
    STORAGE = "storage"
    ORGANIC = "organic"
    EQUIPMENT = "equipment"
    GENERAL = "general"


@dataclass
class KnowledgeArticle:
    """Knowledge article entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    slug: str = ""
    summary: str = ""
    content: str = ""
    content_format: str = "markdown"
    
    # Categorization
    article_type: ArticleType = ArticleType.BEST_PRACTICE
    category: ArticleCategory = ArticleCategory.GENERAL
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Authorship
    author_id: str = ""
    author_username: str = ""
    author_badge: Optional[str] = None
    contributors: List[str] = field(default_factory=list)
    
    # Review
    reviewer_id: Optional[str] = None
    review_status: str = "draft"
    approved_at: Optional[datetime] = None
    
    # Version control
    version: int = 1
    previous_versions: List[dict] = field(default_factory=list)
    change_summary: Optional[str] = None
    
    # Related entities
    related_crop_types: List[str] = field(default_factory=list)
    related_regions: List[str] = field(default_factory=list)
    related_articles: List[str] = field(default_factory=list)
    linked_treatments: List[str] = field(default_factory=list)
    
    # Search optimization
    keywords: List[str] = field(default_factory=list)
    search_vector: Optional[str] = None
    
    # Engagement
    view_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    
    # Publication
    status: ArticleStatus = ArticleStatus.DRAFT
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "summary": self.summary,
            "content": self.content,
            "content_format": self.content_format,
            "article_type": self.article_type.value if self.article_type else None,
            "category": self.category.value if self.category else None,
            "subcategory": self.subcategory,
            "tags": self.tags,
            "author_id": self.author_id,
            "author_username": self.author_username,
            "author_badge": self.author_badge,
            "contributors": self.contributors,
            "reviewer_id": self.reviewer_id,
            "review_status": self.review_status,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "version": self.version,
            "previous_versions": self.previous_versions,
            "change_summary": self.change_summary,
            "related_crop_types": self.related_crop_types,
            "related_regions": self.related_regions,
            "related_articles": self.related_articles,
            "linked_treatments": self.linked_treatments,
            "keywords": self.keywords,
            "view_count": self.view_count,
            "helpful_count": self.helpful_count,
            "not_helpful_count": self.not_helpful_count,
            "status": self.status.value if self.status else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'KnowledgeArticle':
        """Create from dictionary"""
        article = cls()
        for key, value in data.items():
            if hasattr(article, key):
                if key in ["created_at", "updated_at", "published_at", "approved_at", "expires_at"]:
                    if isinstance(value, str):
                        setattr(article, key, datetime.fromisoformat(value) if value else None)
                    else:
                        setattr(article, key, value)
                elif key in ["article_type", "category", "status"]:
                    enum_class = ArticleStatus if key == "status" else (ArticleType if key == "article_type" else ArticleCategory)
                    setattr(article, key, enum_class(value) if value else None)
                else:
                    setattr(article, key, value)
        return article


@dataclass
class KnowledgeCategory:
    """Knowledge category entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    slug: str = ""
    description: str = ""
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    article_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "parent_id": self.parent_id,
            "icon": self.icon,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "article_count": self.article_count,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ArticleSearchQuery:
    """Search query entity for analytics"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_text: str = ""
    results_count: int = 0
    clicked_article_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "query_text": self.query_text,
            "results_count": self.results_count,
            "clicked_article_id": self.clicked_article_id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat()
        }
