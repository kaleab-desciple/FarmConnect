"""
Knowledge Repository - Data Access Layer
Advisory Service - Farm Connect AgriManagement
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, text
from datetime import datetime, timezone
import json
import logging
import re

from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.infrastructure.db.models.knowledge import (
    KnowledgeArticleORM, KnowledgeArticleVersionORM, 
    KnowledgeArticleRatingORM, KnowledgeCategoryORM, ArticleSearchQueryORM
)
from app.domain.advisory.knowledge import KnowledgeArticle, KnowledgeCategory, ArticleSearchQuery
from app.core.auth.dependencies import TokenPayload

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Repository for knowledge base data access with Row-Level Authorization"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _apply_rla_filters(self, query, current_user: Optional[TokenPayload] = None, resolved_user_id: Optional[str] = None):
        """Apply row-level authorization filters"""
        if not current_user:
            # Public access - only published articles
            return query.filter(KnowledgeArticleORM.status == "published")
        
        # Check user roles
        is_admin = current_user.has_realm_role("ADMIN")
        is_moderator = current_user.has_realm_role("MODERATOR")
        
        if is_admin or is_moderator or current_user.is_service_account:
            return query  # Full access
        
        # Use resolved internal ID if provided, otherwise fallback to keycloak_id (for legacy/back-compat)
        uid = resolved_user_id or current_user.user_id
        
        # Authors can see their own drafts
        return query.filter(
            or_(
                KnowledgeArticleORM.status == "published",
                KnowledgeArticleORM.author_id == uid
            )
        )
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug"""
        slug = title.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug[:100]
        import uuid
        return f"{slug}-{uuid.uuid4().hex[:8]}"
    
    # ============ Article Operations ============
    
    def save_article(self, article: KnowledgeArticle) -> KnowledgeArticle:
        """Save an article (create or update)"""
        orm = None
        if article.id:
            orm = self.session.query(KnowledgeArticleORM).filter(
                KnowledgeArticleORM.id == article.id
            ).one_or_none()
        
        if orm:
            # Update existing
            updated_orm = domain_to_orm(article)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new
            orm = domain_to_orm(article)
            self.session.add(orm)
        
        self.session.commit()
        return orm_to_domain(orm)
    
    def get_article_by_id(
        self, 
        article_id: str, 
        current_user: Optional[TokenPayload] = None,
        resolved_user_id: Optional[str] = None
    ) -> Optional[KnowledgeArticle]:
        """Get an article by ID with RLA"""
        query = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.id == article_id
        )
        query = self._apply_rla_filters(query, current_user, resolved_user_id)
        
        orm = query.one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)
    
    def get_article_by_slug(self, slug: str) -> Optional[KnowledgeArticle]:
        """Get an article by slug"""
        orm = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.slug == slug,
            KnowledgeArticleORM.status == "published"
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)
    
    def list_articles(
        self,
        current_user: Optional[TokenPayload] = None,
        resolved_user_id: Optional[str] = None,
        category: Optional[str] = None,
        article_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        crop_type: Optional[str] = None,
        region: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[KnowledgeArticle], int]:
        """List articles with filtering, pagination, and RLA"""
        query = self.session.query(KnowledgeArticleORM)
        query = self._apply_rla_filters(query, current_user, resolved_user_id)
        
        # Apply filters
        if category:
            query = query.filter(KnowledgeArticleORM.category == category)
        
        if article_type:
            query = query.filter(KnowledgeArticleORM.article_type == article_type)
        
        if tags:
            query = query.filter(KnowledgeArticleORM.tags.contains(tags))
        
        if crop_type:
            query = query.filter(KnowledgeArticleORM.related_crop_types.contains([crop_type]))
        
        if region:
            query = query.filter(KnowledgeArticleORM.related_regions.contains([region]))
        
        if status and (current_user and (
            current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MODERATOR")
        )):
            query = query.filter(KnowledgeArticleORM.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(KnowledgeArticleORM, sort_by, KnowledgeArticleORM.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        orms = query.all()
        articles = [orm_to_domain(orm) for orm in orms]
        
        return articles, total
    
    def update_article(
        self, 
        article_id: str, 
        updates: Dict[str, Any],
        current_user: Optional[TokenPayload] = None
    ) -> Optional[KnowledgeArticle]:
        """Update an article with ownership check"""
        query = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.id == article_id
        )
        
        orm = query.one_or_none()
        if not orm:
            return None
        
        # Ownership/permission check
        resolved_user_id = updates.get('_resolved_user_id')
        if not self._can_edit(orm, current_user, resolved_user_id):
            return None
        
        if '_resolved_user_id' in updates:
            del updates['_resolved_user_id']
        
        # Save current version to history before update
        if "content" in updates or "title" in updates:
            self._save_version(orm)
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        
        orm.updated_at = datetime.now(timezone.utc)
        
        # Update slug if title changed
        if "title" in updates:
            orm.slug = self._generate_slug(updates["title"])
        
        # Increment version if content changed
        if "content" in updates or "title" in updates:
            orm.version += 1
        
        self.session.commit()
        return orm_to_domain(orm)
    
    def _can_edit(self, orm: KnowledgeArticleORM, current_user: Optional[TokenPayload], resolved_user_id: Optional[str] = None) -> bool:
        """Check if user can edit the article"""
        if not current_user:
            return False
        
        # Admins and moderators can edit any article
        if (current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MODERATOR") or 
            current_user.is_service_account):
            return True
        
        # Use resolved internal ID if provided
        uid = resolved_user_id or current_user.user_id
        
        # Authors can edit their own articles
        return orm.author_id == uid
    
    def _save_version(self, orm: KnowledgeArticleORM) -> None:
        """Save current article state as a version"""
        version = KnowledgeArticleVersionORM(
            id=str(uuid.uuid4()),
            article_id=orm.id,
            version_number=orm.version,
            title=orm.title,
            summary=orm.summary,
            content=orm.content,
            content_format=orm.content_format,
            change_summary=orm.change_summary,
            editor_id=orm.author_id,
            editor_username=orm.author_username,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(version)
    
    def delete_article(
        self, 
        article_id: str, 
        current_user: Optional[TokenPayload] = None,
        resolved_user_id: Optional[str] = None
    ) -> bool:
        """Delete an article with ownership check"""
        query = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.id == article_id
        )
        
        orm = query.one_or_none()
        if not orm:
            return False
        
        # Only author, admin, or moderator can delete
        if not self._can_edit(orm, current_user, resolved_user_id):
            return False
        
        self.session.delete(orm)
        self.session.commit()
        return True
    
    def increment_view_count(self, article_id: str) -> None:
        """Increment view count for an article"""
        self.session.execute(
            text("""
                UPDATE knowledge_articles 
                SET view_count = view_count + 1 
                WHERE id = :id
            """),
            {"id": article_id}
        )
        self.session.commit()
    
    # ============ Publish Operations ============
    
    def publish_article(
        self,
        article_id: str,
        current_user: Optional[TokenPayload] = None,
        resolved_user_id: Optional[str] = None
    ) -> Optional[KnowledgeArticle]:
        """Publish an article"""
        query = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.id == article_id
        )
        
        orm = query.one_or_none()
        if not orm:
            return None
        
        # Only author, admin, or moderator can publish
        if not self._can_edit(orm, current_user, resolved_user_id):
            return None
        
        orm.status = "published"
        orm.published_at = datetime.now(timezone.utc)
        orm.updated_at = datetime.now(timezone.utc)
        
        self.session.commit()
        return orm_to_domain(orm)
    
    # ============ Rating Operations ============
    
    def rate_article(
        self,
        article_id: str,
        user_id: str,
        is_helpful: bool
    ) -> Optional[Dict[str, Any]]:
        """Rate an article"""
        # Check if already rated
        existing = self.session.query(KnowledgeArticleRatingORM).filter(
            KnowledgeArticleRatingORM.article_id == article_id,
            KnowledgeArticleRatingORM.user_id == user_id
        ).one_or_none()
        
        old_is_helpful = None
        if existing:
            # Update existing rating
            old_is_helpful = existing.is_helpful
            existing.is_helpful = is_helpful
        else:
            # Create new rating
            rating = KnowledgeArticleRatingORM(
                id=str(uuid.uuid4()),
                article_id=article_id,
                user_id=user_id,
                is_helpful=is_helpful
            )
            self.session.add(rating)
        
        # Update counts on article
        article = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.id == article_id
        ).one_or_none()
        
        if not article:
            return None
        
        # Adjust counts based on rating change
        if old_is_helpful is None:
            # New rating
            if is_helpful:
                article.helpful_count += 1
            else:
                article.not_helpful_count += 1
        elif old_is_helpful != is_helpful:
            # Changed rating
            if is_helpful:
                article.helpful_count += 1
                article.not_helpful_count -= 1
            else:
                article.not_helpful_count += 1
                article.helpful_count -= 1
        
        self.session.commit()
        
        return {
            "article_id": article_id,
            "is_helpful": is_helpful,
            "helpful_count": article.helpful_count,
            "not_helpful_count": article.not_helpful_count
        }
    
    # ============ Search Operations ============
    
    def search_articles(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        article_types: Optional[List[str]] = None,
        crop_types: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20,
        current_user: Optional[TokenPayload] = None,
        resolved_user_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search articles by keyword"""
        base_query = self.session.query(KnowledgeArticleORM)
        base_query = self._apply_rla_filters(base_query, current_user, resolved_user_id)
        
        # Build search conditions
        search_term = f"%{query}%"
        conditions = [
            KnowledgeArticleORM.title.ilike(search_term),
            KnowledgeArticleORM.summary.ilike(search_term),
            KnowledgeArticleORM.content.ilike(search_term),
            KnowledgeArticleORM.keywords.contains([query.lower()])
        ]
        
        base_query = base_query.filter(or_(*conditions))
        
        # Apply additional filters
        if categories:
            base_query = base_query.filter(KnowledgeArticleORM.category.in_(categories))
        
        if article_types:
            base_query = base_query.filter(KnowledgeArticleORM.article_type.in_(article_types))
        
        if crop_types:
            base_query = base_query.filter(
                or_(*[KnowledgeArticleORM.related_crop_types.contains([ct]) for ct in crop_types])
            )
        
        # Get total count
        total = base_query.count()
        
        # Apply sorting by relevance (simple: view_count desc)
        base_query = base_query.order_by(desc(KnowledgeArticleORM.view_count))
        
        # Apply pagination
        offset = (page - 1) * page_size
        base_query = base_query.offset(offset).limit(page_size)
        
        orms = base_query.all()
        
        # Build results with relevance scoring
        results = []
        for orm in orms:
            relevance = self._calculate_relevance(orm, query)
            matched_terms = self._get_matched_terms(orm, query)
            
            results.append({
                **orm_to_domain(orm).to_dict(),
                "relevance_score": relevance,
                "matched_terms": matched_terms
            })
        
        return results, total
    
    def _calculate_relevance(self, orm: KnowledgeArticleORM, query: str) -> float:
        """Calculate relevance score for search result"""
        query_lower = query.lower()
        score = 0.0
        
        # Title match (highest weight)
        if query_lower in orm.title.lower():
            score += 10.0
        
        # Keywords match
        if orm.keywords:
            for kw in orm.keywords:
                if query_lower in kw.lower():
                    score += 5.0
        
        # Summary match
        if orm.summary and query_lower in orm.summary.lower():
            score += 3.0
        
        # Content match (lowest weight)
        if orm.content and query_lower in orm.content.lower():
            score += 1.0
        
        # Boost by engagement
        score += min(orm.view_count / 100, 5)  # Max 5 points
        score += min(orm.helpful_count / 50, 3)  # Max 3 points
        
        return round(score, 2)
    
    def _get_matched_terms(self, orm: KnowledgeArticleORM, query: str) -> List[str]:
        """Get list of matched terms"""
        query_lower = query.lower()
        matched = []
        
        if query_lower in orm.title.lower():
            matched.append("title")
        if orm.keywords and any(query_lower in kw.lower() for kw in orm.keywords):
            matched.append("keywords")
        if query_lower in orm.summary.lower():
            matched.append("summary")
        if orm.content and query_lower in orm.content.lower():
            matched.append("content")
        
        return matched
    
    def log_search_query(
        self,
        query_text: str,
        results_count: int,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        clicked_article_id: Optional[str] = None
    ) -> None:
        """Log search query for analytics"""
        search_log = ArticleSearchQueryORM(
            id=str(uuid.uuid4()),
            query_text=query_text,
            results_count=results_count,
            user_id=user_id,
            ip_address=ip_address,
            clicked_article_id=clicked_article_id
        )
        self.session.add(search_log)
        self.session.commit()
    
    def get_search_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on prefix"""
        prefix_lower = prefix.lower()
        
        # Get recent queries matching prefix
        results = self.session.query(
            ArticleSearchQueryORM.query_text,
            func.count(ArticleSearchQueryORM.id).label('count')
        ).filter(
            ArticleSearchQueryORM.query_text.ilike(f"{prefix_lower}%")
        ).group_by(
            ArticleSearchQueryORM.query_text
        ).order_by(
            desc('count')
        ).limit(limit).all()
        
        return [r.query_text for r in results]
    
    # ============ Category Operations ============
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        orms = self.session.query(KnowledgeCategoryORM).filter(
            KnowledgeCategoryORM.is_active == True
        ).order_by(KnowledgeCategoryORM.sort_order).all()
        
        return [
            {
                "id": orm.slug,
                "name": orm.name,
                "slug": orm.slug,
                "description": orm.description,
                "parent_id": orm.parent_id,
                "icon": orm.icon,
                "article_count": orm.article_count
            }
            for orm in orms
        ]
    
    def get_category_by_slug(self, slug: str) -> Optional[KnowledgeCategory]:
        """Get category by slug"""
        orm = self.session.query(KnowledgeCategoryORM).filter(
            KnowledgeCategoryORM.slug == slug
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)
    
    # ============ Version History ============
    
    def get_article_versions(
        self,
        article_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get article version history"""
        query = self.session.query(KnowledgeArticleVersionORM).filter(
            KnowledgeArticleVersionORM.article_id == article_id
        ).order_by(desc(KnowledgeArticleVersionORM.version_number))
        
        total = query.count()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        orms = query.all()
        
        versions = [
            {
                "version_id": orm.id,
                "version_number": orm.version_number,
                "title": orm.title,
                "summary": orm.summary,
                "change_summary": orm.change_summary,
                "editor_id": orm.editor_id,
                "editor_username": orm.editor_username,
                "created_at": orm.created_at.isoformat() if orm.created_at else None
            }
            for orm in orms
        ]
        
        return versions, total
    
    # ============ Related Articles ============
    
    def get_related_articles(
        self,
        article_id: str,
        limit: int = 5
    ) -> List[KnowledgeArticle]:
        """Get related articles based on tags, category, crop type"""
        article = self.get_article_by_id(article_id)
        if not article:
            return []
        
        query = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.id != article_id,
            KnowledgeArticleORM.status == "published"
        )
        
        # Build related conditions
        conditions = []
        
        # Same category
        conditions.append(KnowledgeArticleORM.category == article.category)
        
        # Same tags
        if article.tags:
            conditions.append(KnowledgeArticleORM.tags.overlap(article.tags))
        
        # Same crop types
        if article.related_crop_types:
            conditions.append(
                KnowledgeArticleORM.related_crop_types.overlap(article.related_crop_types)
            )
        
        query = query.filter(or_(*conditions))
        
        # Order by relevance
        query = query.order_by(desc(KnowledgeArticleORM.view_count)).limit(limit)
        
        orms = query.all()
        return [orm_to_domain(orm) for orm in orms]
    
    # ============ Trending/Recent ============
    
    def get_trending_articles(self, limit: int = 10) -> List[KnowledgeArticle]:
        """Get trending articles based on recent views and ratings"""
        # Get articles published in last 30 days with most views
        thirty_days_ago = datetime.now(timezone.utc) - __import__('datetime').timedelta(days=30)
        
        orms = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.status == "published",
            KnowledgeArticleORM.published_at >= thirty_days_ago
        ).order_by(
            desc(KnowledgeArticleORM.view_count),
            desc(KnowledgeArticleORM.helpful_count)
        ).limit(limit).all()
        
        return [orm_to_domain(orm) for orm in orms]
    
    def get_recent_articles(self, limit: int = 10) -> List[KnowledgeArticle]:
        """Get most recently published articles"""
        orms = self.session.query(KnowledgeArticleORM).filter(
            KnowledgeArticleORM.status == "published",
            KnowledgeArticleORM.published_at.isnot(None)
        ).order_by(
            desc(KnowledgeArticleORM.published_at)
        ).limit(limit).all()
        
        return [orm_to_domain(orm) for orm in orms]


# Import uuid for version IDs
import uuid
