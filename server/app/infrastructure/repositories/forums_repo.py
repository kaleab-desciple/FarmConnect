"""
Forum Repository - Data Access Layer
Advisory Service - Farm Connect AgriManagement
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
import logging

from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.infrastructure.db.models import ForumThreadORM, ForumCommentORM, ForumVoteORM, ForumBookmarkORM, ForumReportORM
from app.domain.advisory.forums_entities import ForumThread, ForumComment, ForumVote, ForumBookmark, ForumReport
from app.core.auth.dependencies import TokenPayload
#from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ForumRepository:
    """Repository for forum data access with Row-Level Authorization (RLA)"""
    
    VALID_CATEGORIES = [
        "pest_disease", "irrigation", "fertilization", "soil_health",
        "weather", "harvest_storage", "market_prices", "equipment",
        "organic_farming", "livestock", "general"
    ]
    
    VALID_THREAD_STATUSES = ["open", "resolved", "closed", "archived"]
    
    def __init__(self, session: Session):
        self.session = session
    
    def _apply_rla_filters(self, query, current_user: Optional[TokenPayload] = None):
        """
        Apply row-level authorization filters based on user role.
        For forums, read access is generally public, but moderation actions are restricted.
        """
        if not current_user:
            return query
        
        # Admins and moderators have full access
        if (current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MODERATOR") or 
            current_user.is_service_account):
            return query
        
        # Regular users can only see approved content
        return query.filter(ForumThreadORM.moderation_status == "approved")
    
    def save_thread(self, thread: ForumThread) -> ForumThread:
        """Save a forum thread (create or update)"""
        orm = None
        if thread.id:
            orm = self.session.query(ForumThreadORM).filter(
                ForumThreadORM.id == thread.id
            ).one_or_none()
        
        if orm:
            # Update existing
            updated_orm = domain_to_orm(thread)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new
            orm = domain_to_orm(thread)
            self.session.add(orm)
        
        self.session.commit()
        return orm_to_domain(orm)
    
    def get_thread_by_id(
        self, 
        thread_id: str, 
        current_user: Optional[TokenPayload] = None
    ) -> Optional[ForumThread]:
        """Get a thread by ID with RLA"""
        query = self.session.query(ForumThreadORM).filter(
            ForumThreadORM.id == thread_id
        )
        query = self._apply_rla_filters(query, current_user)
        
        orm = query.one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)
    
    def get_thread_by_slug(self, slug: str) -> Optional[ForumThread]:
        """Get a thread by slug"""
        orm = self.session.query(ForumThreadORM).filter(
            ForumThreadORM.slug == slug
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)
    
    def list_threads(
        self,
        current_user: Optional[TokenPayload] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        author_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "bumped_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ForumThread], int]:
        """
        List threads with filtering, pagination, and RLA.
        Returns (threads, total_count)
        """
        # Build base query
        query = self.session.query(ForumThreadORM)
        query = self._apply_rla_filters(query, current_user)
        
        # Apply filters
        if category:
            query = query.filter(ForumThreadORM.category == category)
        
        if status:
            query = query.filter(ForumThreadORM.status == status)
        
        if author_id:
            query = query.filter(ForumThreadORM.author_id == author_id)
        
        if tags:
            # PostgreSQL array containment
            query = query.filter(ForumThreadORM.tags.contains(tags))
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(ForumThreadORM, sort_by, ForumThreadORM.bumped_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute
        orms = query.all()
        threads = [orm_to_domain(orm) for orm in orms]
        
        return threads, total
    
    def update_thread(
        self, 
        thread_id: str, 
        updates: Dict[str, Any],
        current_user: Optional[TokenPayload] = None
    ) -> Optional[ForumThread]:
        """Update a thread with ownership check"""
        query = self.session.query(ForumThreadORM).filter(
            ForumThreadORM.id == thread_id
        )
        
        orm = query.one_or_none()
        if not orm:
            return None
        
        # Ownership check
        if current_user and not (
            current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MODERATOR")
        ):
            if orm.author_id != current_user.user_id:
                return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        
        orm.updated_at = __import__('datetime').datetime.utcnow()
        self.session.commit()
        
        return orm_to_domain(orm)
    
    def increment_view_count(self, thread_id: str) -> None:
        """Increment view count for a thread"""
        self.session.execute(
            __import__('sqlalchemy').update(ForumThreadORM)
            .where(ForumThreadORM.id == thread_id)
            .values(view_count=ForumThreadORM.view_count + 1)
        )
        self.session.commit()
    
    def delete_thread(
        self, 
        thread_id: str, 
        current_user: Optional[TokenPayload] = None
    ) -> bool:
        """Delete a thread with ownership check"""
        query = self.session.query(ForumThreadORM).filter(
            ForumThreadORM.id == thread_id
        )
        
        orm = query.one_or_none()
        if not orm:
            return False
        
        # Ownership check
        if current_user and not (
            current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MODERATOR")
        ):
            if orm.author_id != current_user.user_id:
                return False
        
        self.session.delete(orm)
        self.session.commit()
        return True
    
    # ============ Comment Operations ============
    
    def save_comment(self, comment: ForumComment) -> ForumComment:
        """Save a comment"""
        orm = None
        if comment.id:
            orm = self.session.query(ForumCommentORM).filter(
                ForumCommentORM.id == comment.id
            ).one_or_none()
        
        if orm:
            updated_orm = domain_to_orm(comment)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            orm = domain_to_orm(comment)
            self.session.add(orm)
        
        self.session.commit()
        
        # Update thread comment count
        if not comment.id:  # New comment
            self.session.execute(
                __import__('sqlalchemy').update(ForumThreadORM)
                .where(ForumThreadORM.id == comment.thread_id)
                .values(
                    comment_count=ForumThreadORM.comment_count + 1,
                    bumped_at=__import__('datetime').datetime.utcnow()
                )
            )
        
        return orm_to_domain(orm)
    
    def update_comment(
        self,
        comment_id: str,
        updates: Dict[str, Any],
        current_user: Optional[TokenPayload] = None
    ) -> Optional[ForumComment]:
        """Update a comment with ownership check"""
        query = self.session.query(ForumCommentORM).filter(
            ForumCommentORM.id == comment_id
        )
        
        orm = query.one_or_none()
        if not orm:
            return None
        
        # Ownership check
        if current_user and not (
            current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MODERATOR")
        ):
            if orm.author_id != current_user.user_id:
                return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        
        orm.updated_at = __import__('datetime').datetime.utcnow()
        self.session.commit()
        
        return orm_to_domain(orm)
    
    def get_comment_by_id(self, comment_id: str) -> Optional[ForumComment]:
        """Get a comment by ID"""
        orm = self.session.query(ForumCommentORM).filter(
            ForumCommentORM.id == comment_id
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)
    
    def list_thread_comments(
        self,
        thread_id: str,
        page: int = 1,
        page_size: int = 50,
        current_user: Optional[TokenPayload] = None
    ) -> tuple[List[ForumComment], int]:
        """List comments for a thread"""
        # First check thread exists and is accessible
        thread = self.get_thread_by_id(thread_id, current_user)
        if not thread:
            return [], 0
        
        # Build query
        query = self.session.query(ForumCommentORM).filter(
            ForumCommentORM.thread_id == thread_id,
            ForumCommentORM.moderation_status == "approved"
        )
        
        # Get total
        total = query.count()
        
        # Apply sorting (oldest first for comments)
        query = query.order_by(ForumCommentORM.created_at)
        
        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        orms = query.all()
        comments = [orm_to_domain(orm) for orm in orms]
        
        return comments, total
    
    def delete_comment(
        self,
        comment_id: str,
        current_user: Optional[TokenPayload] = None
    ) -> bool:
        """Delete a comment"""
        query = self.session.query(ForumCommentORM).filter(
            ForumCommentORM.id == comment_id
        )
        
        orm = query.one_or_none()
        if not orm:
            return False
        
        # Ownership check
        if current_user and not (
            current_user.has_realm_role("ADMIN") or 
            current_user.has_realm_role("MODERATOR")
        ):
            if orm.author_id != current_user.user_id:
                return False
        
        thread_id = orm.thread_id
        
        self.session.delete(orm)
        
        # Update thread comment count
        self.session.execute(
            __import__('sqlalchemy').update(ForumThreadORM)
            .where(ForumThreadORM.id == thread_id)
            .values(comment_count=ForumThreadORM.comment_count - 1)
        )
        
        self.session.commit()
        return True
    
    def mark_accepted_answer(
        self,
        comment_id: str,
        thread_id: str,
        current_user: Optional[TokenPayload] = None
    ) -> bool:
        """Mark a comment as the accepted answer"""
        # Get thread to verify ownership
        thread = self.get_thread_by_id(thread_id, current_user)
        if not thread:
            return False
        
        if current_user and thread.author_id != current_user.user_id:
            return False
        
        # Unmark any existing accepted answer
        self.session.query(ForumCommentORM).filter(
            ForumCommentORM.thread_id == thread_id,
            ForumCommentORM.is_accepted_answer == True
        ).update({"is_accepted_answer": False})
        
        # Mark new accepted answer
        self.session.query(ForumCommentORM).filter(
            ForumCommentORM.id == comment_id
        ).update({"is_accepted_answer": True})
        
        self.session.commit()
        return True
    
    # ============ Vote Operations ============
    
    def save_vote(self, vote: ForumVote) -> ForumVote:
        """Save a vote (upsert)"""
        # Check for existing vote
        existing = None
        if vote.thread_id:
            existing = self.session.query(ForumVoteORM).filter(
                ForumVoteORM.thread_id == vote.thread_id,
                ForumVoteORM.voter_id == vote.voter_id
            ).one_or_none()
        elif vote.comment_id:
            existing = self.session.query(ForumVoteORM).filter(
                ForumVoteORM.comment_id == vote.comment_id,
                ForumVoteORM.voter_id == vote.voter_id
            ).one_or_none()
        
        if existing:
            # Update existing vote
            if vote.vote_type != existing.vote_type:
                # Vote type changed, update counts accordingly
                thread_id = existing.thread_id
                comment_id = existing.comment_id
                self._update_vote_counts(thread_id, comment_id, existing.vote_type, vote.vote_type)
                existing.vote_type = vote.vote_type
        else:
            # Create new vote
            orm = domain_to_orm(vote)
            self.session.add(orm)
            
            # Update counts
            self._update_vote_counts(vote.thread_id, vote.comment_id, None, vote.vote_type)
        
        self.session.commit()
        return orm_to_domain(existing or orm)
    
    def _update_vote_counts(
        self,
        thread_id: Optional[str],
        comment_id: Optional[str],
        old_vote_type: Optional[str],
        new_vote_type: Optional[str]
    ):
        """Update vote counts on thread or comment"""
        # Rollback old vote type
        if old_vote_type and old_vote_type == "up":
            if thread_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumThreadORM)
                    .where(ForumThreadORM.id == thread_id)
                    .values(upvote_count=ForumThreadORM.upvote_count - 1)
                )
            elif comment_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumCommentORM)
                    .where(ForumCommentORM.id == comment_id)
                    .values(upvote_count=ForumCommentORM.upvote_count - 1)
                )
        elif old_vote_type and old_vote_type == "down":
            if thread_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumThreadORM)
                    .where(ForumThreadORM.id == thread_id)
                    .values(downvote_count=ForumThreadORM.downvote_count - 1)
                )
            elif comment_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumCommentORM)
                    .where(ForumCommentORM.id == comment_id)
                    .values(downvote_count=ForumCommentORM.downvote_count - 1)
                )
        
        # Apply new vote type
        if new_vote_type == "up":
            if thread_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumThreadORM)
                    .where(ForumThreadORM.id == thread_id)
                    .values(upvote_count=ForumThreadORM.upvote_count + 1)
                )
            elif comment_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumCommentORM)
                    .where(ForumCommentORM.id == comment_id)
                    .values(upvote_count=ForumCommentORM.upvote_count + 1)
                )
        elif new_vote_type == "down":
            if thread_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumThreadORM)
                    .where(ForumThreadORM.id == thread_id)
                    .values(downvote_count=ForumThreadORM.downvote_count + 1)
                )
            elif comment_id:
                self.session.execute(
                    __import__('sqlalchemy').update(ForumCommentORM)
                    .where(ForumCommentORM.id == comment_id)
                    .values(downvote_count=ForumCommentORM.downvote_count + 1)
                )
    
    def get_user_vote(
        self,
        thread_id: Optional[str],
        comment_id: Optional[str],
        voter_id: str
    ) -> Optional[ForumVote]:
        """Get user's vote on a thread or comment"""
        query = self.session.query(ForumVoteORM)
        
        if thread_id:
            query = query.filter(
                ForumVoteORM.thread_id == thread_id,
                ForumVoteORM.voter_id == voter_id
            )
        elif comment_id:
            query = query.filter(
                ForumVoteORM.comment_id == comment_id,
                ForumVoteORM.voter_id == voter_id
            )
        
        orm = query.one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)
    
    def delete_vote(
        self,
        thread_id: Optional[str],
        comment_id: Optional[str],
        voter_id: str
    ) -> bool:
        """Delete a vote"""
        query = self.session.query(ForumVoteORM)
        
        if thread_id:
            query = query.filter(
                ForumVoteORM.thread_id == thread_id,
                ForumVoteORM.voter_id == voter_id
            )
        elif comment_id:
            query = query.filter(
                ForumVoteORM.comment_id == comment_id,
                ForumVoteORM.voter_id == voter_id
            )
        
        orm = query.one_or_none()
        if not orm:
            return False
        
        # Update counts before deletion
        self._update_vote_counts(thread_id, comment_id, orm.vote_type, None)
        
        self.session.delete(orm)
        self.session.commit()
        return True
    
    # ============ Bookmark Operations ============
    
    def save_bookmark(self, bookmark: ForumBookmark) -> ForumBookmark:
        """Save a bookmark"""
        orm = None
        if bookmark.id:
            orm = self.session.query(ForumBookmarkORM).filter(
                ForumBookmarkORM.id == bookmark.id
            ).one_or_none()
        
        if orm:
            updated_orm = domain_to_orm(bookmark)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            orm = domain_to_orm(bookmark)
            self.session.add(orm)
            
            # Update thread bookmark count
            self.session.execute(
                __import__('sqlalchemy').update(ForumThreadORM)
                .where(ForumThreadORM.id == bookmark.thread_id)
                .values(bookmark_count=ForumThreadORM.bookmark_count + 1)
            )
        
        self.session.commit()
        return orm_to_domain(orm)
    
    def get_user_bookmark(
        self,
        thread_id: str,
        user_id: str
    ) -> Optional[ForumBookmark]:
        """Check if user has bookmarked a thread"""
        orm = self.session.query(ForumBookmarkORM).filter(
            ForumBookmarkORM.thread_id == thread_id,
            ForumBookmarkORM.user_id == user_id
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)
    
    def delete_bookmark(
        self,
        thread_id: str,
        user_id: str
    ) -> bool:
        """Remove a bookmark"""
        orm = self.session.query(ForumBookmarkORM).filter(
            ForumBookmarkORM.thread_id == thread_id,
            ForumBookmarkORM.user_id == user_id
        ).one_or_none()
        
        if not orm:
            return False
        
        self.session.delete(orm)
        
        # Update thread bookmark count
        self.session.execute(
            __import__('sqlalchemy').update(ForumThreadORM)
            .where(ForumThreadORM.id == thread_id)
            .values(bookmark_count=ForumThreadORM.bookmark_count - 1)
        )
        
        self.session.commit()
        return True
    
    # ============ Category and Tag Operations ============
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories with thread counts"""
        results = self.session.query(
            ForumThreadORM.category,
            func.count(ForumThreadORM.id).label('thread_count')
        ).filter(
            ForumThreadORM.moderation_status == "approved"
        ).group_by(
            ForumThreadORM.category
        ).all()
        
        return [
            {"name": r.category, "thread_count": r.thread_count}
            for r in results
        ]
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, str]]:
        """Get popular tags"""
        # This is a simplified version - in production you'd use PostgreSQL's unnest
        results = self.session.query(
            ForumThreadORM.tags
        ).filter(
            ForumThreadORM.moderation_status == "approved",
            ForumThreadORM.tags.isnot(None)
        ).all()
        
        tag_counts = {}
        for row in results:
            if row.tags:
                for tag in row.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"name": tag, "count": count} for tag, count in sorted_tags]

    # ============ Moderation Report Operations ============

    def save_report(self, report: ForumReport) -> ForumReport:
        """Save a moderation report"""
        orm = None
        if report.id:
            orm = self.session.query(ForumReportORM).filter(
                ForumReportORM.id == report.id
            ).one_or_none()
        
        if orm:
            updated_orm = domain_to_orm(report)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            orm = domain_to_orm(report)
            self.session.add(orm)
        
        self.session.commit()
        return orm_to_domain(orm)

    def get_report_by_id(self, report_id: str) -> Optional[ForumReport]:
        """Get a report by ID"""
        orm = self.session.query(ForumReportORM).filter(
            ForumReportORM.id == report_id
        ).one_or_none()
        
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_reports(
        self,
        status: Optional[str] = None,
        report_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ForumReport], int]:
        """List moderation reports"""
        query = self.session.query(ForumReportORM)
        
        if status:
            query = query.filter(ForumReportORM.moderation_status == status)
            
        if report_type:
            query = query.filter(ForumReportORM.report_type == report_type)
            
        total = query.count()
        
        # Sort by creation date desc
        query = query.order_by(desc(ForumReportORM.created_at))
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        orms = query.all()
        return [orm_to_domain(orm) for orm in orms], total
