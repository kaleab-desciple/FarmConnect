"""
Knowledge Service - Business Logic Layer
Advisory Service - Farm Connect AgriManagement
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from uuid import uuid4
import re
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.auth.dependencies import TokenPayload
from app.domain.advisory.knowledge import KnowledgeArticle, ArticleStatus, ArticleType, ArticleCategory
from app.infrastructure.repositories.knowledge_repo import KnowledgeRepository
from app.infrastructure.repositories.user_repo import UserRepository
from shared_models import (
    KnowledgeArticle as ArticleDTO,
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    ArticleSearchQuery,
)

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Service layer for knowledge base operations following clean architecture patterns"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = KnowledgeRepository(session)
        self.user_repo = UserRepository(session)
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        slug = title.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug[:100]
        return f"{slug}-{uuid4().hex[:8]}"
    
    # ============ Article Operations ============
    
    def create_article(
        self,
        article_data: KnowledgeArticleCreate,
        current_user: TokenPayload
    ) -> KnowledgeArticle:
        """
        Create a new knowledge article.
        
        Args:
            article_data: Article creation data
            current_user: Authenticated user
            
        Returns:
            Created article
            
        Raises:
            HTTPException: Validation errors
        """
        # Generate slug
        slug = self._generate_slug(article_data.title)
        
        # Create domain entity
        now = datetime.now(timezone.utc)
        article = KnowledgeArticle(
            id=str(uuid4()),
            title=article_data.title,
            slug=slug,
            summary=article_data.summary,
            content=article_data.content,
            content_format=article_data.content_format or "markdown",
            article_type=ArticleType(article_data.article_type),
            category=ArticleCategory(article_data.category),
            subcategory=article_data.subcategory,
            tags=article_data.tags or [],
            author_id=self._resolve_author_id(article_data.author_id, current_user),
            author_username=current_user.username or "unknown",
            author_badge=None,
            contributors=[],
            reviewer_id=None,
            review_status="pending",
            version=1,
            previous_versions=[],
            change_summary=None,
            related_crop_types=article_data.related_crop_types or [],
            related_regions=article_data.related_regions or [],
            related_articles=[],
            linked_treatments=article_data.linked_treatments or [],
            keywords=article_data.keywords or [],
            view_count=0,
            helpful_count=0,
            not_helpful_count=0,
            status=ArticleStatus.DRAFT,
            published_at=None,
            expires_at=None,
            created_at=now,
            updated_at=now
        )
        
        # Save via repository
        saved_article = self.repo.save_article(article)
        
        logger.info(f"Created knowledge article: {saved_article.id} by user: {current_user.user_id}")
        
        return saved_article
    
    def _resolve_author_id(self, provided_author_id: Optional[str], current_user: TokenPayload) -> str:
        """Resolve internal author ID from provided info or current user token"""
        # 1. Use provided ID if it exists in users table
        if provided_author_id:
            user = self.user_repo.get_by_id(provided_author_id)
            if user:
                return user.id
            logger.warning(f"Provided author_id {provided_author_id} not found in database.")

        # 2. Try to resolve from token email (most reliable for our ADM/FAR/MER internal IDs)
        email = getattr(current_user, 'email', None)
        if email:
            user = self.user_repo.get_by_email(email)
            if user:
                return user.id

        # 3. Try to resolve from token user_id (keycloak_id)
        token_uid = current_user.user_id or current_user.subject
        if token_uid:
            user = self.user_repo.get_by_keycloak_id(token_uid)
            if user:
                return user.id
        
        # 4. Final fallback
        return "unknown"
    
    def get_article(
        self,
        article_id: str,
        current_user: Optional[TokenPayload] = None,
        increment_view: bool = True
    ) -> Dict[str, Any]:
        """
        Get an article by ID.
        
        Args:
            article_id: Article ID
            current_user: Optional authenticated user
            increment_view: Whether to increment view count
            
        Returns:
            Article data with metadata
            
        Raises:
            HTTPException: Article not found
        """
        resolved_user_id = self._resolve_author_id(None, current_user) if current_user else None
        article = self.repo.get_article_by_id(article_id, current_user, resolved_user_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Increment view count
        if increment_view:
            self.repo.increment_view_count(article_id)
        
        # Check if user has rated
        user_rating = None
        if current_user:
            # This would require additional repository method
            pass
        
        return article.to_dict()
    
    def get_article_by_slug(
        self,
        slug: str,
        current_user: Optional[TokenPayload] = None
    ) -> Dict[str, Any]:
        """Get an article by slug"""
        article = self.repo.get_article_by_slug(slug)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Increment view count
        self.repo.increment_view_count(article.id)
        
        return article.to_dict()
    
    def list_articles(
        self,
        current_user: Optional[TokenPayload] = None,
        category: Optional[str] = None,
        article_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        crop_type: Optional[str] = None,
        region: Optional[str] = None,
        status: Optional[str] = "published",
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List articles with filtering and pagination.
        
        Args:
            current_user: Optional authenticated user
            category: Filter by category
            article_type: Filter by article type
            tags: Filter by tags
            crop_type: Filter by crop type
            region: Filter by region
            status: Filter by status (default: published)
            sort_by: Sort field
            sort_order: Sort direction
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated article list
        """
        # Convert tags list to comma-separated string for repo
        tags_param = None
        if tags:
            tags_param = tags
        
        # Get articles from repository
        resolved_user_id = self._resolve_author_id(None, current_user) if current_user else None
        articles, total = self.repo.list_articles(
            current_user=current_user,
            resolved_user_id=resolved_user_id,
            category=category,
            article_type=article_type,
            tags=tags_param,
            crop_type=crop_type,
            region=region,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        # Build response
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return {
            "articles": [a.to_dict() for a in articles],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def update_article(
        self,
        article_id: str,
        article_data: KnowledgeArticleUpdate,
        current_user: TokenPayload
    ) -> KnowledgeArticle:
        """
        Update an article.
        
        Args:
            article_id: Article ID
            article_data: Update data
            current_user: Authenticated user
            
        Returns:
            Updated article
            
        Raises:
            HTTPException: Article not found or unauthorized
        """
        # Build updates dict
        updates = {}
        
        if article_data.title is not None:
            updates["title"] = article_data.title
        
        if article_data.summary is not None:
            updates["summary"] = article_data.summary
        
        if article_data.content is not None:
            updates["content"] = article_data.content
        
        if article_data.tags is not None:
            if len(article_data.tags) > 20:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum 20 tags allowed"
                )
            updates["tags"] = article_data.tags
        
        if article_data.keywords is not None:
            if len(article_data.keywords) > 30:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum 30 keywords allowed"
                )
            updates["keywords"] = article_data.keywords
        
        if article_data.status is not None:
            updates["status"] = article_data.status
        
        if article_data.change_summary is not None:
            updates["change_summary"] = article_data.change_summary
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        # Update via repository
        resolved_user_id = self._resolve_author_id(None, current_user)
        updates['_resolved_user_id'] = resolved_user_id
        updated_article = self.repo.update_article(article_id, updates, current_user)
        
        if not updated_article:
            raise HTTPException(status_code=404, detail="Article not found or unauthorized")
        
        logger.info(f"Updated knowledge article: {article_id} by user: {current_user.user_id}")
        
        return updated_article
    
    def delete_article(
        self,
        article_id: str,
        current_user: TokenPayload
    ) -> bool:
        """
        Delete an article.
        
        Args:
            article_id: Article ID
            current_user: Authenticated user
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: Article not found or unauthorized
        """
        resolved_user_id = self._resolve_author_id(None, current_user)
        success = self.repo.delete_article(article_id, current_user, resolved_user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Article not found or unauthorized")
        
        logger.info(f"Deleted knowledge article: {article_id} by user: {resolved_user_id}")
        
        return True
    
    # ============ Publish Operations ============
    
    def publish_article(
        self,
        article_id: str,
        current_user: TokenPayload
    ) -> KnowledgeArticle:
        """
        Publish an article.
        
        Args:
            article_id: Article ID
            current_user: Authenticated user
            
        Returns:
            Published article
            
        Raises:
            HTTPException: Article not found or unauthorized
        """
        resolved_user_id = self._resolve_author_id(None, current_user)
        article = self.repo.publish_article(article_id, current_user, resolved_user_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found or unauthorized")
        
        logger.info(f"Published knowledge article: {article_id} by user: {resolved_user_id}")
        
        return article
    
    # ============ Rating Operations ============
    
    def rate_article(
        self,
        article_id: str,
        is_helpful: bool,
        current_user: TokenPayload
    ) -> Dict[str, Any]:
        """
        Rate an article as helpful or not helpful.
        
        Args:
            article_id: Article ID
            is_helpful: Whether the article was helpful
            current_user: Authenticated user
            
        Returns:
            Updated rating counts
            
        Raises:
            HTTPException: Article not found
        """
        user_id = self._resolve_author_id(None, current_user)
        result = self.repo.rate_article(article_id, user_id, is_helpful)
        
        if not result:
            raise HTTPException(status_code=404, detail="Article not found")
        
        logger.info(f"User: {user_id} rated article: {article_id} as {'helpful' if is_helpful else 'not helpful'}")
        
        return result
    
    # ============ Search Operations ============
    
    def search_articles(
        self,
        query: str,
        current_user: Optional[TokenPayload] = None,
        categories: Optional[List[str]] = None,
        article_types: Optional[List[str]] = None,
        crop_types: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search articles by keyword.
        
        Args:
            query: Search query
            current_user: Optional authenticated user
            categories: Filter by categories
            article_types: Filter by article types
            crop_types: Filter by crop types
            page: Page number
            page_size: Items per page
            
        Returns:
            Search results with relevance scoring
        """
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        # Search articles
        resolved_user_id = self._resolve_author_id(None, current_user) if current_user else None
        results, total = self.repo.search_articles(
            query=query,
            categories=categories,
            article_types=article_types,
            crop_types=crop_types,
            page=page,
            page_size=page_size,
            current_user=current_user,
            resolved_user_id=resolved_user_id
        )
        
        # Log search query for analytics
        self.repo.log_search_query(
            query_text=query,
            results_count=total,
            user_id=resolved_user_id
        )
        
        # Get suggestions
        suggestions = self.repo.get_search_suggestions(query)
        
        return {
            "query": query,
            "total_results": total,
            "page": page,
            "page_size": page_size,
            "results": results,
            "suggestions": suggestions[:5]  # Limit suggestions
        }
    
    def get_search_suggestions(
        self,
        prefix: str,
        limit: int = 10
    ) -> List[str]:
        """Get search suggestions based on prefix"""
        if len(prefix) < 2:
            return []
        
        return self.repo.get_search_suggestions(prefix, limit)
    
    # ============ Category Operations ============
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        return self.repo.get_categories()
    
    # ============ Version History ============
    
    def get_article_versions(
        self,
        article_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get article version history"""
        # Check article exists
        article = self.repo.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        versions, total = self.repo.get_article_versions(article_id, page, page_size)
        
        return {
            "article_id": article_id,
            "versions": versions,
            "total_versions": total
        }
    
    # ============ Related Articles ============
    
    def get_related_articles(
        self,
        article_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get related articles"""
        articles = self.repo.get_related_articles(article_id, limit)
        
        return {
            "articles": [a.to_dict() for a in articles]
        }
    
    # ============ Trending/Recent ============
    
    def get_trending_articles(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get trending articles"""
        articles = self.repo.get_trending_articles(limit)
        
        return {
            "articles": [a.to_dict() for a in articles]
        }
    
    def get_recent_articles(
        self,
        limit: int = 10,
        current_user: Optional[TokenPayload] = None
    ) -> Dict[str, Any]:
        """Get recently published articles"""
        articles = self.repo.get_recent_articles(limit)
        
        return {
            "articles": [a.to_dict() for a in articles]
        }
