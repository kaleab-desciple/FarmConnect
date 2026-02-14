"""
Forum Shared Models - DTOs
Advisory Service - Farm Connect AgriManagement
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============ Thread DTOs ============

class ForumThreadBase(BaseModel):
    """Base thread model"""
    title: str = Field(..., min_length=10, max_length=200, description="Thread title")
    content_body: str = Field(..., min_length=20, max_length=10000, description="Thread content")
    content_format: str = Field(default="markdown", description="Content format")
    category: str = Field(..., description="Thread category")
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_items=10)
    context_field_id: Optional[str] = None
    context_crop_cycle_id: Optional[str] = None
    context_crop_type: Optional[str] = None
    context_growth_stage: Optional[str] = None


class ForumThreadCreate(ForumThreadBase):
    """Thread creation model"""
    pass


class ForumThreadUpdate(BaseModel):
    """Thread update model"""
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    content_body: Optional[str] = Field(None, min_length=20, max_length=10000)
    tags: Optional[List[str]] = Field(None, max_items=10)
    status: Optional[str] = None


class ForumThread(ForumThreadBase):
    """Thread response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    slug: str
    author_id: str
    author_username: str
    author_reputation: int
    author_badge: Optional[str] = None
    status: str
    view_count: int
    upvote_count: int
    downvote_count: int
    bookmark_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime
    bumped_at: datetime


# ============ Comment DTOs ============

class ForumCommentBase(BaseModel):
    """Base comment model"""
    content: str = Field(..., min_length=5, max_length=5000)
    parent_id: Optional[str] = None
    attachments: List[Dict[str, str]] = Field(default_factory=list)


class ForumCommentCreate(ForumCommentBase):
    """Comment creation model"""
    pass


class ForumCommentUpdate(BaseModel):
    """Comment update model"""
    content: str = Field(..., min_length=5, max_length=5000)


class ForumComment(BaseModel):
    """Comment response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    thread_id: str
    parent_id: Optional[str]
    author_id: str
    author_username: str
    content: str
    content_format: str
    upvote_count: int
    downvote_count: int
    is_accepted_answer: bool
    is_edited: bool
    created_at: datetime
    updated_at: datetime


# ============ Vote DTOs ============

class VoteRequest(BaseModel):
    """Vote request model"""
    vote_type: str = Field(..., pattern="^(up|down)$")


class VoteResponse(BaseModel):
    """Vote response model"""
    thread_id: Optional[str] = None
    comment_id: Optional[str] = None
    vote_type: str
    upvote_count: int
    downvote_count: int
    user_vote: Optional[str] = None


# ============ Bookmark DTO ============

class BookmarkResponse(BaseModel):
    """Bookmark response model"""
    bookmarked: bool


# ============ Category and Tag DTOs ============

class CategoryResponse(BaseModel):
    """Category response model"""
    name: str
    thread_count: int


class TagResponse(BaseModel):
    """Tag response model"""
    name: str
    count: int


# ============ Pagination DTOs ============

class ThreadListResponse(BaseModel):
    """Thread list response with pagination"""
    threads: List[ForumThread]
    total: int
    page: int
    page_size: int
    total_pages: int


class CommentListResponse(BaseModel):
    """Comment list response with pagination"""
    comments: List[ForumComment]
    total: int
    page: int
    page_size: int
