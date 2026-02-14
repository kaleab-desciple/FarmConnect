"""
Knowledge Base ORM Models
Advisory Service - Farm Connect AgriManagement
"""
from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, Text, Boolean, ARRAY, Enum as SAEnum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class KnowledgeArticleORM(Base):
    """Knowledge article ORM model"""
    __tablename__ = "knowledge_articles"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_format: Mapped[str] = mapped_column(String(20), default="markdown")
    
    # Categorization
    article_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(50)), default=list)
    
    # Authorship
    author_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    author_username: Mapped[str] = mapped_column(String(100), nullable=False)
    author_badge: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contributors: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    
    # Review
    reviewer_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1)
    previous_versions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Related entities
    related_crop_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(50)), default=list)
    related_regions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(50)), default=list)
    related_articles: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    linked_treatments: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    
    # Search optimization
    keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(50)), default=list)
    search_vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Engagement
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Publication
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    versions: Mapped[List["KnowledgeArticleVersionORM"]] = relationship(
        "KnowledgeArticleVersionORM", 
        back_populates="article",
        cascade="all, delete-orphan"
    )
    ratings: Mapped[List["KnowledgeArticleRatingORM"]] = relationship(
        "KnowledgeArticleRatingORM",
        back_populates="article",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_knowledge_articles_category_status', 'category', 'status'),
        Index('idx_knowledge_articles_type_status', 'article_type', 'status'),
        Index('idx_knowledge_articles_published', 'published_at'),
    )


class KnowledgeArticleVersionORM(Base):
    """Knowledge article version history ORM model"""
    __tablename__ = "knowledge_article_versions"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    article_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_articles.id"), nullable=False, index=True)
    
    # Version content snapshot
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_format: Mapped[str] = mapped_column(String(20), default="markdown")
    
    # Metadata
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    editor_id: Mapped[str] = mapped_column(String, nullable=False)
    editor_username: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    article: Mapped["KnowledgeArticleORM"] = relationship("KnowledgeArticleORM", back_populates="versions")
    
    __table_args__ = (
        Index('idx_knowledge_versions_article', 'article_id', 'version_number'),
    )


class KnowledgeArticleRatingORM(Base):
    """Knowledge article rating ORM model"""
    __tablename__ = "knowledge_article_ratings"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    article_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_articles.id"), nullable=False, index=True)
    
    # Rating info
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    is_helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    article: Mapped["KnowledgeArticleORM"] = relationship("KnowledgeArticleORM", back_populates="ratings")
    
    __table_args__ = (
        Index('idx_knowledge_ratings_unique', 'article_id', 'user_id', unique=True),
    )


class KnowledgeCategoryORM(Base):
    """Knowledge category ORM model"""
    __tablename__ = "knowledge_categories"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_categories.id"), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Self-referential relationship for hierarchy
    parent: Mapped[Optional["KnowledgeCategoryORM"]] = relationship(
        "KnowledgeCategoryORM", 
        remote_side=[id], 
        backref="children"
    )


class ArticleSearchQueryORM(Base):
    """Article search query tracking ORM model"""
    __tablename__ = "article_search_queries"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    query_text: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_article_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    __table_args__ = (
        Index('idx_search_queries_daily', 'query_text', 'created_at'),
    )
