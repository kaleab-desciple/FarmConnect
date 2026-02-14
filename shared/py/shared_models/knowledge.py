"""
Knowledge Shared Models - DTOs
Advisory Service - Farm Connect AgriManagement
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============ Enums ============

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


# ============ Article DTOs ============

class KnowledgeArticleBase(BaseModel):
    """Base knowledge article model"""
    title: str = Field(..., min_length=10, max_length=200, description="Article title")
    summary: str = Field(..., min_length=50, max_length=500, description="Article summary")
    content: str = Field(..., min_length=100, description="Article content")
    content_format: str = Field(default="markdown", description="Content format")
    article_type: ArticleType = Field(..., description="Article type")
    category: ArticleCategory = Field(..., description="Article category")
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_length=20)
    keywords: List[str] = Field(default_factory=list, max_length=30)
    related_crop_types: List[str] = Field(default_factory=list)
    related_regions: List[str] = Field(default_factory=list)
    linked_treatments: List[str] = Field(default_factory=list)
    author_id: Optional[str] = Field(None, description="Author User ID (optional, defaults to current user)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Comprehensive Guide to Pest Management in Coffee",
                "summary": "This guide provides detailed protocols for identifying and managing common coffee pests using sustainable integrated pest management techniques.",
                "content": "Coffee pests such as the Coffee Berry Borer (Hypothenemus hampei) can significantly impact yield and quality. Integrated Pest Management (IPM) strategies include cultural practices like proper pruning, sanitation, and the use of biological controls.",
                "content_format": "markdown",
                "article_type": "pest_guide",
                "category": "pest_management",
                "subcategory": "Coffee Pests",
                "tags": ["coffee", "pest-control", "sustainable-farming"],
                "keywords": ["berry borer", "ipm", "agronomy"],
                "related_crop_types": ["Coffee"],
                "related_regions": ["East Africa"],
                "linked_treatments": [],
                "author_id": "ADM-00001"
            }
        }
    )


class KnowledgeArticleCreate(KnowledgeArticleBase):
    """Article creation model"""
    pass


class KnowledgeArticleUpdate(BaseModel):
    """Article update model"""
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    summary: Optional[str] = Field(None, min_length=50, max_length=500)
    content: Optional[str] = Field(None, min_length=100)
    tags: Optional[List[str]] = Field(None, max_length=20)
    keywords: Optional[List[str]] = Field(None, max_length=30)
    status: Optional[str] = None
    change_summary: Optional[str] = None


class KnowledgeArticle(KnowledgeArticleBase):
    """Article response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    slug: str
    author_id: str
    author_username: str
    author_badge: Optional[str] = None
    contributors: List[str] = []
    reviewer_id: Optional[str] = None
    review_status: str
    approved_at: Optional[datetime] = None
    version: int
    previous_versions: List[dict] = []
    change_summary: Optional[str] = None
    related_articles: List[str] = []
    view_count: int
    helpful_count: int
    not_helpful_count: int
    status: str
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ============ Search DTOs ============

class ArticleSearchQuery(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=2, max_length=200)
    categories: Optional[List[str]] = None
    article_types: Optional[List[str]] = None
    crop_types: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchResultItem(BaseModel):
    """Search result item"""
    id: str
    title: str
    slug: str
    summary: str
    article_type: str
    category: str
    tags: List[str]
    relevance_score: float
    matched_terms: List[str]
    view_count: int
    helpful_count: int


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    total_results: int
    page: int
    page_size: int
    results: List[SearchResultItem]
    suggestions: List[str]


# ============ Category DTO ============

class KnowledgeCategory(BaseModel):
    """Category response model"""
    id: str
    name: str
    slug: str
    description: str
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    article_count: int


# ============ Version DTO ============

class ArticleVersion(BaseModel):
    """Article version response model"""
    version_id: str
    version_number: int
    title: str
    summary: str
    change_summary: Optional[str] = None
    editor_id: str
    editor_username: str
    created_at: datetime


class ArticleHistoryResponse(BaseModel):
    """Article history response"""
    article_id: str
    versions: List[ArticleVersion]
    total_versions: int


# ============ Rating DTO ============

class ArticleRatingResponse(BaseModel):
    """Article rating response"""
    article_id: str
    is_helpful: bool
    helpful_count: int
    not_helpful_count: int


# ============ Pagination DTOs ============

class ArticleListResponse(BaseModel):
    """Article list response with pagination"""
    articles: List[KnowledgeArticle]
    total: int
    page: int
    page_size: int
    total_pages: int


class RelatedArticlesResponse(BaseModel):
    """Related articles response"""
    articles: List[KnowledgeArticle]


class TrendingArticlesResponse(BaseModel):
    """Trending articles response"""
    articles: List[KnowledgeArticle]

