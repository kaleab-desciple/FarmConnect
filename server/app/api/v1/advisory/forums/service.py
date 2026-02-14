"""
Forum Service - Business Logic Layer
Advisory Service - Farm Connect AgriManagement
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
import re
import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.auth.dependencies import TokenPayload
from app.domain.advisory.forums_entities import ForumThread, ForumComment, ForumVote, ForumBookmark
from app.infrastructure.repositories.forums_repo import ForumRepository
from app.infrastructure.repositories.notification_repo import NotificationRepository
from app.domain.advisory.notification_service import NotificationService
from app.domain.advisory.moderation_service import ModerationService
from app.domain.advisory.notifications import NotificationType, NotificationPriority
from shared_models import ForumThread as ThreadDTO, ForumThreadCreate, ForumThreadUpdate
from shared_models import ForumComment as CommentDTO, ForumCommentCreate, ForumCommentUpdate
from shared_models import CategoryResponse, TagResponse

logger = logging.getLogger(__name__)


class ForumService:
    """Service layer for forum operations following clean architecture patterns"""
    
    VALID_CATEGORIES = [
        "pest_disease", "irrigation", "fertilization", "soil_health",
        "weather", "harvest_storage", "market_prices", "equipment",
        "organic_farming", "livestock", "general"
    ]
    
    VALID_THREAD_STATUSES = ["open", "resolved", "closed", "archived"]
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = ForumRepository(session)
        from app.infrastructure.repositories.user_repo import UserRepository
        self.user_repo = UserRepository(session)
        self.notification_service = NotificationService(NotificationRepository(session), self.user_repo)
        self.moderation_service = ModerationService(self.repo, self.notification_service, self.user_repo)

    def _get_internal_user_id(self, token_payload: TokenPayload) -> str:
        """Resolve internal user ID from Keycloak ID in token"""
        user = None
        keycloak_id = token_payload.user_id
        
        if keycloak_id:
            user = self.user_repo.get_by_keycloak_id(keycloak_id)
            
        # Fallback: Try email if user not found by ID (e.g. missing sub claim)
        if not user and token_payload.email:
             user = self.user_repo.get_by_email(token_payload.email)
        
        if not user:
            # Fallback for service accounts or special cases if needed
            # For now, strict requirement for user existence
            logger.warning(f"User not found for Keycloak ID: {keycloak_id} or Email: {token_payload.email}")
            raise HTTPException(
                status_code=401,
                detail="User account not found. Please ensure you are registered."
            )
        
        return user.id
    
    def _validate_category(self, category: str) -> bool:
        """Validate category is valid"""
        return category in self.VALID_CATEGORIES
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        slug = title.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug[:100]
        return f"{slug}-{uuid4().hex[:8]}"
    
    def _check_spam(self, content: str) -> None:
        """Check content for spam patterns"""
        is_spam = self.moderation_service.detect_spam(content)
        if is_spam:
            raise HTTPException(
                status_code=400,
                detail="Content contains prohibited spam patterns."
            )
    
    # ============ Thread Operations ============
    
    def create_thread(
        self,
        thread_data: ForumThreadCreate,
        current_user: TokenPayload
    ) -> ForumThread:
        """
        Create a new forum thread.
        
        Args:
            thread_data: Thread creation data
            current_user: Authenticated user
            
        Returns:
            Created thread
            
        Raises:
            HTTPException: Validation errors or spam detection
        """
        # Validate category
        if not self._validate_category(thread_data.category):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}"
            )
        
        # Check for spam
        self._check_spam(thread_data.title + " " + thread_data.content_body)
        
        # Generate slug
        slug = self._generate_slug(thread_data.title)
        
        # Create domain entity
        now = datetime.utcnow()
        # Resolve internal user ID
        internal_user_id = self._get_internal_user_id(current_user)
        
        thread = ForumThread(
            id=str(uuid4()),
            title=thread_data.title,
            slug=slug,
            content_body=thread_data.content_body,
            content_format=thread_data.content_format or "markdown",
            author_id=internal_user_id,
            author_username=getattr(current_user, 'username', current_user.user_id),
            author_reputation=0,
            author_badge=None,
            category=thread_data.category,
            subcategory=thread_data.subcategory,
            tags=thread_data.tags or [],
            context_field_id=thread_data.context_field_id,
            context_crop_cycle_id=thread_data.context_crop_cycle_id,
            context_crop_type=thread_data.context_crop_type,
            context_growth_stage=thread_data.context_growth_stage,
            status="open",
            moderation_status="approved",
            view_count=0,
            upvote_count=0,
            downvote_count=0,
            bookmark_count=0,
            comment_count=0,
            created_at=now,
            updated_at=now,
            bumped_at=now,
            last_activity_at=now
        )
        
        # Save via repository
        saved_thread = self.repo.save_thread(thread)
        
        logger.info(f"Created forum thread: {saved_thread.id} by user: {internal_user_id}")
        
        return saved_thread
    
    def get_thread(
        self,
        thread_id: str,
        current_user: Optional[TokenPayload] = None,
        increment_view: bool = True
    ) -> Dict[str, Any]:
        """
        Get a thread by ID.
        
        Args:
            thread_id: Thread ID
            current_user: Optional authenticated user
            increment_view: Whether to increment view count
            
        Returns:
            Thread data with additional metadata
            
        Raises:
            HTTPException: Thread not found
        """
        thread = self.repo.get_thread_by_id(thread_id, current_user)
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Increment view count
        if increment_view:
            self.repo.increment_view_count(thread_id)
        
        # Check if user has bookmarked
        bookmarked = False
        if current_user:
            bookmark = self.repo.get_user_bookmark(thread_id, current_user.user_id)
            bookmarked = bookmark is not None
        
        # Get user's vote
        user_vote = None
        if current_user:
            vote = self.repo.get_user_vote(thread_id=thread_id, voter_id=current_user.user_id)
            user_vote = vote.vote_type if vote else None
        
        # Build response
        return {
            **thread.to_dict(),
            "bookmarked": bookmarked,
            "user_vote": user_vote
        }
    
    def list_threads(
        self,
        current_user: Optional[TokenPayload] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        author_id: Optional[str] = None,
        tags: Optional[str] = None,
        sort_by: str = "bumped_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List threads with filtering and pagination.
        
        Args:
            current_user: Optional authenticated user
            category: Filter by category
            status: Filter by status
            author_id: Filter by author
            tags: Filter by tags (comma-separated string)
            sort_by: Sort field
            sort_order: Sort direction
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated thread list
        """
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
        
        # Validate category
        if category and not self._validate_category(category):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}"
            )
        
        # Get threads from repository
        threads, total = self.repo.list_threads(
            current_user=current_user,
            category=category,
            status=status,
            author_id=author_id,
            tags=tag_list,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        # Build response
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return {
            "threads": [self._thread_to_response(t) for t in threads],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def update_thread(
        self,
        thread_id: str,
        thread_data: ForumThreadUpdate,
        current_user: TokenPayload
    ) -> ForumThread:
        """
        Update a thread.
        
        Args:
            thread_id: Thread ID
            thread_data: Update data
            current_user: Authenticated user
            
        Returns:
            Updated thread
            
        Raises:
            HTTPException: Thread not found or unauthorized
        """
        # Build updates dict
        updates = {}
        
        if thread_data.title is not None:
            self._check_spam(thread_data.title)
            updates["title"] = thread_data.title
            updates["slug"] = self._generate_slug(thread_data.title)
        
        if thread_data.content_body is not None:
            self._check_spam(thread_data.content_body)
            updates["content_body"] = thread_data.content_body
        
        if thread_data.tags is not None:
            if len(thread_data.tags) > 10:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum 10 tags allowed"
                )
            updates["tags"] = thread_data.tags
        
        if thread_data.status is not None:
            if thread_data.status not in self.VALID_THREAD_STATUSES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join(self.VALID_THREAD_STATUSES)}"
                )
            updates["status"] = thread_data.status
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        # Update via repository
        # Update via repository (repo handles ownership check based on passed user object)
        # Note: repo.update_thread expects current_user to check roles/id
        # We need to ensure repo checks against internal ID if user is not admin
        # For now, let's keep passing current_user to repo, but we might need to patch repo too
        # checking repo code... repo compares orm.author_id != current_user.user_id
        # This is problematic because current_user.user_id is UUID, orm.author_id is FAR-XXX
        
        # We need to construct a "principals" object or similar, or just pass the ID for checking
        # But repo method signature expects TokenPayload.
        
        # Let's override the user_id in the token payload copy effectively
        
        internal_user_id = self._get_internal_user_id(current_user)
        user_context = TokenPayload({
            **current_user.raw_payload,
            "sub": internal_user_id # Override sub with internal ID for repo checks
        })
        
        updated_thread = self.repo.update_thread(thread_id, updates, user_context)
        
        if not updated_thread:
            raise HTTPException(status_code=404, detail="Thread not found or unauthorized")
        
        logger.info(f"Updated forum thread: {thread_id} by user: {current_user.user_id}")
        
        return updated_thread
    
    def delete_thread(
        self,
        thread_id: str,
        current_user: TokenPayload
    ) -> bool:
        """
        Delete a thread.
        
        Args:
            thread_id: Thread ID
            current_user: Authenticated user
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: Thread not found or unauthorized
        """
        internal_user_id = self._get_internal_user_id(current_user)
        user_context = TokenPayload({
            **current_user.raw_payload,
            "sub": internal_user_id
        })
        success = self.repo.delete_thread(thread_id, user_context)
        
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found or unauthorized")
        
        logger.info(f"Deleted forum thread: {thread_id} by user: {current_user.user_id}")
        
        return True
    
    # ============ Comment Operations ============
    
    async def create_comment(
        self,
        thread_id: str,
        comment_data: ForumCommentCreate,
        current_user: TokenPayload
    ) -> ForumComment:
        """
        Create a comment on a thread.
        
        Args:
            thread_id: Thread ID
            comment_data: Comment creation data
            current_user: Authenticated user
            
        Returns:
            Created comment
        """
        # Verify thread exists
        thread = self.repo.get_thread_by_id(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Check for spam
        self._check_spam(comment_data.content)
        
        # Validate parent comment if provided
        if comment_data.parent_id:
            parent = self.repo.get_comment_by_id(comment_data.parent_id)
            if not parent or parent.thread_id != thread_id:
                raise HTTPException(
                    status_code=400,
                    detail="Parent comment not found in this thread"
                )
        
        # Create domain entity
        now = datetime.utcnow()
        
        # Resolve internal user ID
        internal_user_id = self._get_internal_user_id(current_user)
        
        comment = ForumComment(
            id=str(uuid4()),
            thread_id=thread_id,
            parent_id=comment_data.parent_id,
            author_id=internal_user_id,
            author_username=getattr(current_user, 'username', current_user.user_id),
            author_reputation=0,
            author_badge=None,
            content=comment_data.content,
            content_format="markdown",
            attachments=comment_data.attachments or [],
            moderation_status="approved",
            upvote_count=0,
            downvote_count=0,
            is_accepted_answer=False,
            is_edited=False,
            edit_history=[],
            created_at=now,
            updated_at=now
        )
        
        # Save via repository
        saved_comment = self.repo.save_comment(comment)
        
        logger.info(f"Created comment: {saved_comment.id} on thread: {thread_id}")
        
        saved_comment = self.repo.save_comment(comment)
        
        logger.info(f"Created comment: {saved_comment.id} on thread: {thread_id}")
        
        # Notify thread author of reply
        if thread.author_id != internal_user_id:
            await self.notification_service.create_notification(
                user_id=thread.author_id,
                type=NotificationType.THREAD_REPLY,
                title="New Reply to your Thread",
                message=f"{getattr(current_user, 'username', 'Someone')} replied to your thread: {thread.title}",
                context={"thread_id": thread_id, "comment_id": saved_comment.id},
                from_user_id=internal_user_id,
                action_url=f"/forums/threads/{thread.slug}#{saved_comment.id}"
            )
            
        # Notify parent comment author if nested reply
        if comment_data.parent_id:
            parent = self.repo.get_comment_by_id(comment_data.parent_id)
            if parent and parent.author_id != internal_user_id and parent.author_id != thread.author_id:
                 await self.notification_service.create_notification(
                    user_id=parent.author_id,
                    type=NotificationType.THREAD_REPLY,
                    title="New Reply to your Comment",
                    message=f"{getattr(current_user, 'username', 'Someone')} replied to your comment",
                    context={"thread_id": thread_id, "comment_id": saved_comment.id},
                    from_user_id=internal_user_id,
                    action_url=f"/forums/threads/{thread.slug}#{saved_comment.id}"
                )
        
        return saved_comment
    
    def update_comment(
        self,
        comment_id: str,
        comment_data: ForumCommentUpdate,
        current_user: TokenPayload
    ) -> ForumComment:
        """
        Update a comment.
        
        Args:
            comment_id: Comment ID
            comment_data: Update data
            current_user: Authenticated user
            
        Returns:
            Updated comment
        """
        # Get existing comment
        comment = self.repo.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Ownership check
        if comment.author_id != current_user.user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own comments"
            )
        
        # Check for spam
        self._check_spam(comment_data.content)
        
        # Build updates
        updates = {
            "content": comment_data.content,
            "is_edited": True,
            "edit_history": comment.edit_history + [{
                "content": comment.content,
                "edited_at": comment.updated_at.isoformat() if isinstance(comment.updated_at, datetime) else comment.updated_at
            }],
            "updated_at": datetime.utcnow()
        }
        
        internal_user_id = self._get_internal_user_id(current_user)
        user_context = TokenPayload({
            **current_user.raw_payload,
            "sub": internal_user_id
        })
        
        # Update via repository
        updated_comment = self.repo.update_comment(comment_id, updates, user_context)
        
        logger.info(f"Updated comment: {comment_id}")
        
        return updated_comment
    
    def delete_comment(
        self,
        comment_id: str,
        current_user: TokenPayload
    ) -> bool:
        """
        Delete a comment.
        
        Args:
            comment_id: Comment ID
            current_user: Authenticated user
            
        Returns:
            True if deleted
        """
        internal_user_id = self._get_internal_user_id(current_user)
        user_context = TokenPayload({
            **current_user.raw_payload,
            "sub": internal_user_id
        })
        success = self.repo.delete_comment(comment_id, user_context)
        
        if not success:
            raise HTTPException(status_code=404, detail="Comment not found or unauthorized")
        
        logger.info(f"Deleted comment: {comment_id}")
        
        return True
    
    def list_comments(
        self,
        thread_id: str,
        current_user: Optional[TokenPayload] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        List comments for a thread.
        
        Args:
            thread_id: Thread ID
            current_user: Optional authenticated user
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated comment list
        """
        comments, total = self.repo.list_thread_comments(
            thread_id=thread_id,
            current_user=current_user,
            page=page,
            page_size=page_size
        )
        
        return {
            "comments": [self._comment_to_response(c) for c in comments],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def mark_accepted_answer(
        self,
        thread_id: str,
        comment_id: str,
        current_user: TokenPayload
    ) -> bool:
        """
        Mark a comment as the accepted answer.
        
        Args:
            thread_id: Thread ID
            comment_id: Comment ID
            current_user: Authenticated user
            
        Returns:
            True if successful
        """
        internal_user_id = self._get_internal_user_id(current_user)
        user_context = TokenPayload({
            **current_user.raw_payload,
            "sub": internal_user_id
        })
        success = self.repo.mark_accepted_answer(comment_id, thread_id, user_context)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Thread not found or you are not the author"
            )
        
        logger.info(f"Marked comment: {comment_id} as accepted answer for thread: {thread_id}")
        
        # Notify comment author
        comment = self.repo.get_comment_by_id(comment_id)
        thread = self.repo.get_thread_by_id(thread_id)
        
        if comment and thread and comment.author_id != internal_user_id:
             await self.notification_service.create_notification(
                user_id=comment.author_id,
                type=NotificationType.ANSWER_ACCEPTED,
                title="Answer Accepted",
                message=f"Your answer to '{thread.title}' was accepted!",
                context={"thread_id": thread_id, "comment_id": comment_id},
                from_user_id=internal_user_id,
                action_url=f"/forums/threads/{thread.slug}#{comment_id}",
                priority=NotificationPriority.HIGH
            )
            
        return True
    
    # ============ Vote Operations ============
    
    async def vote(
        self,
        thread_id: Optional[str],
        comment_id: Optional[str],
        vote_type: str,
        current_user: TokenPayload
    ) -> Dict[str, Any]:
        """
        Vote on a thread or comment.
        
        Args:
            thread_id: Thread ID (optional)
            comment_id: Comment ID (optional)
            vote_type: "up" or "down"
            current_user: Authenticated user
            
        Returns:
            Vote result with updated counts
        """
        if vote_type not in ["up", "down"]:
            raise HTTPException(status_code=400, detail="Invalid vote type")
        
        internal_user_id = self._get_internal_user_id(current_user)
        
        # Create vote entity
        vote = ForumVote(
            id=str(uuid4()),
            thread_id=thread_id,
            comment_id=comment_id,
            voter_id=internal_user_id,
            vote_type=vote_type,
            created_at=datetime.utcnow()
        )
        
        # Save via repository
        saved_vote = self.repo.save_vote(vote)
        
        # Get updated counts
        if thread_id:
            thread = self.repo.get_thread_by_id(thread_id)
            upvote_count = thread.upvote_count if thread else 0
            downvote_count = thread.downvote_count if thread else 0
        else:
            comment = self.repo.get_comment_by_id(comment_id)
            upvote_count = comment.upvote_count if comment else 0
            downvote_count = comment.downvote_count if comment else 0
        
        logger.info(f"User: {current_user.user_id} voted {vote_type} on {thread_id or comment_id}")
        
        # Notify author on upvote (if not self-vote)
        if vote_type == "up":
            target_author_id = None
            context = {}
            msg = ""
            
            if thread_id:
                thread = self.repo.get_thread_by_id(thread_id)
                if thread:
                    target_author_id = thread.author_id
                    context = {"thread_id": thread_id}
                    msg = f"Your thread '{thread.title}' received an upvote"
            elif comment_id:
                 comment = self.repo.get_comment_by_id(comment_id)
                 if comment:
                    target_author_id = comment.author_id
                    context = {"comment_id": comment_id}
                    # Getting thread for context if possible
                    context["thread_id"] = comment.thread_id
                    msg = "Your comment received an upvote"
            
            if target_author_id and target_author_id != internal_user_id:
                await self.notification_service.create_notification(
                    user_id=target_author_id,
                    type=NotificationType.COMMENT_UPVOTE, # Reusing upvote type for both
                    title="New Upvote",
                    message=msg,
                    context=context,
                    from_user_id=internal_user_id
                )
        
        return {
            "thread_id": thread_id,
            "comment_id": comment_id,
            "vote_type": vote_type,
            "upvote_count": upvote_count,
            "downvote_count": downvote_count,
            "user_vote": vote_type
        }
    
    def delete_vote(
        self,
        thread_id: Optional[str],
        comment_id: Optional[str],
        current_user: TokenPayload
    ) -> bool:
        """
        Remove a vote.
        
        Args:
            thread_id: Thread ID (optional)
            comment_id: Comment ID (optional)
            current_user: Authenticated user
            
        Returns:
            True if deleted
        """
        internal_user_id = self._get_internal_user_id(current_user)
        success = self.repo.delete_vote(thread_id, comment_id, internal_user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Vote not found")
        
        logger.info(f"Removed vote from user: {current_user.user_id}")
        
        return True
    
    # ============ Bookmark Operations ============
    
    def toggle_bookmark(
        self,
        thread_id: str,
        current_user: TokenPayload
    ) -> Dict[str, Any]:
        """
        Toggle bookmark on a thread.
        
        Args:
            thread_id: Thread ID
            current_user: Authenticated user
            
        Returns:
            Bookmark status
        """
        internal_user_id = self._get_internal_user_id(current_user)
        
        # Check if already bookmarked
        existing = self.repo.get_user_bookmark(thread_id, internal_user_id)
        
        if existing:
            # Remove bookmark
            success = self.repo.delete_bookmark(thread_id, internal_user_id)
            if success:
                return {"bookmarked": False}
        
        # Create bookmark
        bookmark = ForumBookmark(
            id=str(uuid4()),
            thread_id=thread_id,
            user_id=internal_user_id,
            created_at=datetime.utcnow()
        )
        
        self.repo.save_bookmark(bookmark)
        
        return {"bookmarked": True}
    
    # ============ Category and Tag Operations ============
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories with thread counts"""
        return self.repo.get_categories()
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, str]]:
        """Get popular tags"""
        return self.repo.get_popular_tags(limit)
    
    # ============ Helper Methods ============
    
    def _thread_to_response(self, thread: ForumThread) -> Dict[str, Any]:
        """Convert thread domain entity to API response"""
        data = thread.to_dict()
        # Truncate content for list view
        if len(data.get("content_body", "")) > 200:
            data["content_body"] = data["content_body"][:200] + "..."
        return data
    
    def _comment_to_response(self, comment: ForumComment) -> Dict[str, Any]:
        """Convert comment domain entity to API response"""
        return comment.to_dict()
