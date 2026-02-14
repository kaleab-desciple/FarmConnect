"""
Knowledge Base API Routes - Complete Implementation
Advisory Service - Farm Connect AgriManagement

Following the same architecture, patterns, and structure as the forums and order implementations.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user, get_optional_user, require_auth
from app.core.auth import require_permission, require_admin
from .service import KnowledgeService
from shared_models import (
    KnowledgeArticle as ArticleDTO,
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    ArticleSearchQuery,
)

router = APIRouter()


# ============ Article Routes ============

@router.post(
    "/articles",
    response_model=ArticleDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("knowledge:create"))],
)
async def create_article(
    article_data: KnowledgeArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new knowledge article.
    
    Requires authentication. Articles are created as drafts by default.
    """
    try:
        service = KnowledgeService(db)
        article = service.create_article(article_data, current_user)
        return article
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles", response_model=Dict[str, Any])
async def list_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    article_type: Optional[str] = Query(None, description="Filter by article type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    crop_type: Optional[str] = Query(None, description="Filter by crop type"),
    region: Optional[str] = Query(None, description="Filter by region"),
    status: str = Query(default="published", description="Filter by status"),
    sort_by: str = Query(default="created_at", pattern="^(created_at|view_count|helpful_count)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    List knowledge articles with filtering and pagination.
    """
    try:
        service = KnowledgeService(db)
        return service.list_articles(
            current_user=current_user,
            category=category,
            article_type=article_type,
            tags=tags,
            crop_type=crop_type,
            region=region,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles/{article_id}", response_model=Dict[str, Any])
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get a specific article by ID.
    
    Increments view count. Returns full content.
    """
    try:
        service = KnowledgeService(db)
        return service.get_article(article_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles/slug/{slug}", response_model=Dict[str, Any])
async def get_article_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get article by URL-friendly slug.
    """
    try:
        service = KnowledgeService(db)
        return service.get_article_by_slug(slug, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/articles/{article_id}", response_model=ArticleDTO)
async def update_article(
    article_id: str,
    article_data: KnowledgeArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Update an article.
    
    Creates new version. Preserves edit history.
    """
    try:
        service = KnowledgeService(db)
        return service.update_article(article_id, article_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Delete an article.
    
    Only author, admin, or moderator can delete.
    """
    try:
        service = KnowledgeService(db)
        service.delete_article(article_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/articles/{article_id}/publish",
    response_model=ArticleDTO,
    dependencies=[Depends(require_permission("knowledge:publish"))],
)
async def publish_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Publish an article.
    
    Requires admin or moderator role.
    """
    try:
        service = KnowledgeService(db)
        return service.publish_article(article_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/articles/{article_id}/rate", response_model=Dict[str, Any])
async def rate_article(
    article_id: str,
    helpful: bool = Query(..., description="Whether the article was helpful"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Rate an article as helpful or not helpful.
    """
    try:
        service = KnowledgeService(db)
        return service.rate_article(article_id, helpful, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Search Routes ============

@router.post("/search", response_model=Dict[str, Any])
async def search_articles(
    search_data: ArticleSearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Search knowledge base articles.
    
    - **query**: Search terms (2-200 chars)
    - **categories**: Filter by categories
    - **article_types**: Filter by types
    - **crop_types**: Filter by crop types
    - Returns relevance-ranked results with matched terms
    """
    try:
        service = KnowledgeService(db)
        return service.search_articles(
            query=search_data.query,
            current_user=current_user,
            categories=search_data.categories,
            article_types=search_data.article_types,
            crop_types=search_data.crop_types,
            page=search_data.page,
            page_size=search_data.page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/suggest")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(default=10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search suggestions/autocomplete.
    """
    try:
        service = KnowledgeService(db)
        return {"query": q, "suggestions": service.get_search_suggestions(q, limit)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Category Routes ============

@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all knowledge categories.
    """
    try:
        service = KnowledgeService(db)
        return service.get_categories()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Related Articles Routes ============

@router.get("/articles/{article_id}/related", response_model=Dict[str, Any])
async def get_related_articles(
    article_id: str,
    limit: int = Query(default=5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Get related articles for a given article.
    """
    try:
        service = KnowledgeService(db)
        return service.get_related_articles(article_id, limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Version History Routes ============

@router.get("/articles/{article_id}/history", response_model=Dict[str, Any])
async def get_article_history(
    article_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get article version history.
    """
    try:
        service = KnowledgeService(db)
        return service.get_article_versions(article_id, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Trending/Recent Routes ============

@router.get("/trending", response_model=Dict[str, Any])
async def get_trending_articles(
    limit: int = Query(default=10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending/popular articles.
    
    Based on recent views and helpful ratings.
    """
    try:
        service = KnowledgeService(db)
        return service.get_trending_articles(limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=Dict[str, Any])
async def get_recent_articles(
    limit: int = Query(default=10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get recently published articles.
    """
    try:
        service = KnowledgeService(db)
        return service.get_recent_articles(limit, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
