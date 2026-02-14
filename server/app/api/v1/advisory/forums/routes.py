"""
Forums API Routes - Complete Implementation
Advisory Service - Farm Connect AgriManagement

Following the same architecture, patterns, and structure as the order implementation.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth.dependencies import get_current_user, get_optional_user, require_auth
from app.core.auth import require_permission

from .service import ForumService
from shared_models import (
    ForumThread as ThreadDTO,
    ForumThreadCreate,
    ForumThreadUpdate,
    ForumComment as CommentDTO,
    ForumCommentCreate,
    ForumCommentUpdate,
    VoteRequest,
    VoteResponse,
    CategoryResponse,
    TagResponse,
)

router = APIRouter()


# ============ Thread Routes ============

@router.post(
    "/threads",
    response_model=ThreadDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("forums:create"))],
)
async def create_thread(
    thread_data: ForumThreadCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a new forum thread.
    
    - **title**: Descriptive title (10-200 chars)
    - **content_body**: Main content (20-10000 chars)
    - **category**: pest_disease, irrigation, fertilization, soil_health, weather, etc.
    - **tags**: Up to 10 tags for categorization
    - **context**: Optional linkage to field/crop
    """
    try:
        service = ForumService(db)
        thread = service.create_thread(thread_data, current_user)
        return thread
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads", response_model=Dict[str, Any])
async def list_threads(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    author_id: Optional[str] = Query(None, description="Filter by author"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    sort_by: str = Query(default="bumped_at", pattern="^(bumped_at|created_at|view_count|upvote_count)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    List forum threads with filtering and pagination.
    
    - **category**: pest_disease, irrigation, fertilization, soil_health, weather, etc.
    - **status**: open, resolved, closed, archived
    - **sort_by**: bumped_at, created_at, view_count, upvote_count
    - **sort_order**: asc, desc
    """
    try:
        service = ForumService(db)
        return service.list_threads(
            current_user=current_user,
            category=category,
            status=status,
            author_id=author_id,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}", response_model=Dict[str, Any])
async def get_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get a specific thread by ID.
    
    Returns thread details including author info, tags, and stats.
    Increments view count.
    """
    try:
        service = ForumService(db)
        return service.get_thread(thread_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/threads/{thread_id}", response_model=ThreadDTO)
async def update_thread(
    thread_id: str,
    thread_data: ForumThreadUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Update a thread.
    
    Only the author can update their own thread.
    Status can only be changed to resolved, closed, or archived.
    """
    try:
        service = ForumService(db)
        return service.update_thread(thread_id, thread_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Delete a thread.
    
    Only the author or moderator can delete a thread.
    """
    try:
        service = ForumService(db)
        service.delete_thread(thread_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Comment Routes ============

@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("forums:comment:create"))],
)
async def create_comment(
    thread_id: str,
    comment_data: ForumCommentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Create a comment on a thread.
    
    - **content**: Comment content (5-5000 chars)
    - **parent_id**: Optional parent comment ID for nested replies
    """
    try:
        service = ForumService(db)
        return await service.create_comment(thread_id, comment_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}/comments", response_model=Dict[str, Any])
async def list_comments(
    thread_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    List comments for a thread.
    """
    try:
        service = ForumService(db)
        return service.list_comments(thread_id, current_user, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/comments/{comment_id}", response_model=CommentDTO)
async def update_comment(
    comment_id: str,
    comment_data: ForumCommentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Update a comment.
    
    Only the author can update their own comment.
    """
    try:
        service = ForumService(db)
        return service.update_comment(comment_id, comment_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Delete a comment.
    
    Only the author or moderator can delete a comment.
    """
    try:
        service = ForumService(db)
        service.delete_comment(comment_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/comments/{comment_id}/accept",
    response_model=Dict[str, bool],
    dependencies=[Depends(require_permission("forums:comment:accept"))],
)
async def mark_accepted_answer(
    thread_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Mark a comment as the accepted answer.
    
    Only the thread author can accept an answer.
    """
    try:
        service = ForumService(db)
        success = await service.mark_accepted_answer(thread_id, comment_id, current_user)
        return {"success": success}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Vote Routes ============

@router.post(
    "/threads/{thread_id}/vote",
    response_model=VoteResponse,
    dependencies=[Depends(require_permission("forums:vote"))],
)
async def vote_thread(
    thread_id: str,
    vote_data: VoteRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Vote on a thread (up or down).
    """
    try:
        service = ForumService(db)
        return await service.vote(
            thread_id=thread_id,
            comment_id=None,
            vote_type=vote_data.vote_type,
            current_user=current_user
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/threads/{thread_id}/vote", response_model=VoteResponse)
async def remove_thread_vote(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Remove vote from a thread.
    """
    try:
        service = ForumService(db)
        service.delete_vote(thread_id=thread_id, comment_id=None, current_user=current_user)
        # Return updated counts
        thread = service.repo.get_thread_by_id(thread_id)
        return {
            "thread_id": thread_id,
            "comment_id": None,
            "vote_type": "",
            "upvote_count": thread.upvote_count if thread else 0,
            "downvote_count": thread.downvote_count if thread else 0,
            "user_vote": None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/comments/{comment_id}/vote",
    response_model=VoteResponse,
    dependencies=[Depends(require_permission("forums:vote"))],
)
async def vote_comment(
    comment_id: str,
    vote_data: VoteRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Vote on a comment (up or down).
    """
    try:
        service = ForumService(db)
        return await service.vote(
            thread_id=None,
            comment_id=comment_id,
            vote_type=vote_data.vote_type,
            current_user=current_user
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/comments/{comment_id}/vote", response_model=VoteResponse)
async def remove_comment_vote(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Remove vote from a comment.
    """
    try:
        service = ForumService(db)
        service.delete_vote(thread_id=None, comment_id=comment_id, current_user=current_user)
        # Return updated counts
        comment = service.repo.get_comment_by_id(comment_id)
        return {
            "thread_id": None,
            "comment_id": comment_id,
            "vote_type": "",
            "upvote_count": comment.upvote_count if comment else 0,
            "downvote_count": comment.downvote_count if comment else 0,
            "user_vote": None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Bookmark Routes ============

@router.post(
    "/threads/{thread_id}/bookmark",
    response_model=Dict[str, bool],
    dependencies=[Depends(require_permission("forums:bookmark"))],
)
async def toggle_bookmark(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """
    Toggle bookmark on a thread.
    """
    try:
        service = ForumService(db)
        return service.toggle_bookmark(thread_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ Category and Tag Routes ============

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    db: Session = Depends(get_db)
):
    """
    Get all categories with thread counts.
    """
    try:
        service = ForumService(db)
        return service.get_categories()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags", response_model=List[TagResponse])
async def get_popular_tags(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get popular tags.
    """
    try:
        service = ForumService(db)
        return service.get_popular_tags(limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
