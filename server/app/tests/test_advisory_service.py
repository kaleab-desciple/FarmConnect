"""
Unit Tests for Advisory Service
Farm Connect AgriManagement System
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import sys
sys.path.insert(0, '/home/kaleab/Downloads/Farm_Connect/server')

from app.domain.advisory.forums import ForumThread, ThreadStatus, ThreadCategory
from app.domain.advisory.forums_entities import ForumComment, ForumVote
from app.domain.advisory.knowledge import KnowledgeArticle, ArticleStatus, ArticleType
from app.domain.advisory.notifications import Notification, NotificationType
from app.core.middleware.rate_limit import detect_spam, SPAM_PATTERNS


# ============ Forum Thread Tests ============

class TestForumThread:
    """Test cases for ForumThread entity"""
    
    def test_create_thread_defaults(self):
        """Test thread creation with default values"""
        thread = ForumThread(
            title="Test Thread",
            author_id="user-123"
        )
        
        assert thread.title == "Test Thread"
        assert thread.author_id == "user-123"
        assert thread.status == ThreadStatus.OPEN
        assert thread.category == ThreadCategory.GENERAL
        assert thread.view_count == 0
        assert thread.upvote_count == 0
        assert thread.id is not None
    
    def test_thread_to_dict(self):
        """Test thread serialization to dictionary"""
        thread = ForumThread(
            id="thread-123",
            title="Test Thread",
            slug="test-thread",
            author_id="user-123",
            category=ThreadCategory.PEST_DISEASE
        )
        
        result = thread.to_dict()
        
        assert result["id"] == "thread-123"
        assert result["title"] == "Test Thread"
        assert result["slug"] == "test-thread"
        assert result["category"] == "pest_disease"
    
    def test_thread_from_dict(self):
        """Test thread deserialization from dictionary"""
        data = {
            "id": "thread-123",
            "title": "Test Thread",
            "slug": "test-thread",
            "author_id": "user-123",
            "category": "pest_disease",
            "status": "resolved",
            "view_count": 100,
            "created_at": "2024-01-15T10:00:00Z"
        }
        
        thread = ForumThread.from_dict(data)
        
        assert thread.id == "thread-123"
        assert thread.status == ThreadStatus.RESOLVED
        assert thread.view_count == 100


# ============ Forum Comment Tests ============

class TestForumComment:
    """Test cases for ForumComment entity"""
    
    def test_create_comment(self):
        """Test comment creation"""
        comment = ForumComment(
            thread_id="thread-123",
            author_id="user-456",
            content="This is a helpful comment"
        )
        
        assert comment.thread_id == "thread-123"
        assert comment.author_id == "user-456"
        assert comment.upvote_count == 0
        assert comment.is_accepted_answer == False
        assert comment.parent_id is None
    
    def test_comment_with_parent(self):
        """Test nested comment creation"""
        comment = ForumComment(
            thread_id="thread-123",
            parent_id="comment-parent",
            author_id="user-789",
            content="This is a reply"
        )
        
        assert comment.parent_id == "comment-parent"
    
    def test_comment_to_dict(self):
        """Test comment serialization"""
        comment = ForumComment(
            id="comment-123",
            thread_id="thread-456",
            author_id="user-123",
            content="Test content",
            upvote_count=5
        )
        
        result = comment.to_dict()
        
        assert result["id"] == "comment-123"
        assert result["thread_id"] == "thread-456"
        assert result["upvote_count"] == 5


# ============ Knowledge Article Tests ============

class TestKnowledgeArticle:
    """Test cases for KnowledgeArticle entity"""
    
    def test_create_article(self):
        """Test article creation"""
        article = KnowledgeArticle(
            title="Early Blight Guide",
            author_id="expert-123"
        )
        
        assert article.title == "Early Blight Guide"
        assert article.status == ArticleStatus.DRAFT
        assert article.version == 1
        assert article.view_count == 0
    
    def test_article_to_dict(self):
        """Test article serialization"""
        article = KnowledgeArticle(
            id="article-123",
            title="Tomato Guide",
            slug="tomato-guide",
            article_type=ArticleType.DISEASE_GUIDE,
            status=ArticleStatus.PUBLISHED
        )
        
        result = article.to_dict()
        
        assert result["id"] == "article-123"
        assert result["article_type"] == "disease_guide"
        assert result["status"] == "published"
    
    def test_article_from_dict(self):
        """Test article deserialization"""
        data = {
            "id": "article-123",
            "title": "Test Article",
            "slug": "test-article",
            "article_type": "disease_guide",
            "status": "published",
            "version": 2,
            "created_at": "2024-01-15T10:00:00Z"
        }
        
        article = KnowledgeArticle.from_dict(data)
        
        assert article.id == "article-123"
        assert article.article_type == ArticleType.DISEASE_GUIDE
        assert article.status == ArticleStatus.PUBLISHED
        assert article.version == 2


# ============ Notification Tests ============

class TestNotification:
    """Test cases for Notification entity"""
    
    def test_create_notification(self):
        """Test notification creation"""
        notification = Notification(
            user_id="user-123",
            notification_type=NotificationType.THREAD_REPLY,
            title="New Reply",
            message="Someone replied to your thread"
        )
        
        assert notification.user_id == "user-123"
        assert notification.notification_type == NotificationType.THREAD_REPLY
        assert notification.is_read == False
    
    def test_notification_to_dict(self):
        """Test notification serialization"""
        notification = Notification(
            id="notif-123",
            user_id="user-456",
            notification_type=NotificationType.COMMENT_UPVOTE,
            title="Upvote Received",
            message="Your comment was upvoted"
        )
        
        result = notification.to_dict()
        
        assert result["id"] == "notif-123"
        assert result["notification_type"] == "comment_upvote"


# ============ Spam Detection Tests ============

class TestSpamDetection:
    """Test cases for spam detection"""
    
    def test_clean_content(self):
        """Test clean content passes"""
        content = "This is a normal farming question about crop rotation."
        result = detect_spam(content)
        
        assert result == []
    
    def test_excessive_links(self):
        """Test detection of excessive links"""
        content = "Check https://link1.com and https://link2.com and https://link3.com for more info"
        result = detect_spam(content)
        
        assert len(result) >= 1
        assert any(r["type"] == "excessive_links" for r in result)
    
    def test_all_caps(self):
        """Test detection of all caps content"""
        content = "THIS IS ALL CAPS CONTENT DETECTED"
        result = detect_spam(content)
        
        assert len(result) >= 1
        assert any(r["type"] == "all_caps" for r in result)
    
    def test_promotional_content(self):
        """Test detection of promotional language"""
        content = "Buy now for free offer limited time only click here"
        result = detect_spam(content)
        
        assert len(result) >= 1
        assert any(r["type"] == "promotional" for r in result)
    
    def test_repeated_characters(self):
        """Test detection of repeated characters"""
        content = "Helloooooooooo this has repeated characters"
        result = detect_spam(content)
        
        assert len(result) >= 1
        assert any(r["type"] == "repeated_chars" for r in result)
    
    def test_suspicious_domain(self):
        """Test detection of suspicious domains"""
        content = "Check this https://bit.ly/abc123 for more info"
        result = detect_spam(content)
        
        assert len(result) >= 1


# ============ Thread Status Tests ============

class TestThreadStatus:
    """Test cases for thread status transitions"""
    
    def test_status_values(self):
        """Test status enum values"""
        assert ThreadStatus.OPEN.value == "open"
        assert ThreadStatus.RESOLVED.value == "resolved"
        assert ThreadStatus.CLOSED.value == "closed"
        assert ThreadStatus.ARCHIVED.value == "archived"
    
    def test_status_from_string(self):
        """Test creating status from string"""
        status = ThreadStatus("resolved")
        assert status == ThreadStatus.RESOLVED


# ============ Article Status Tests ============

class TestArticleStatus:
    """Test cases for article status"""
    
    def test_status_values(self):
        """Test article status values"""
        assert ArticleStatus.DRAFT.value == "draft"
        assert ArticleStatus.PUBLISHED.value == "published"
        assert ArticleStatus.ARCHIVED.value == "archived"


# ============ Integration Tests ============

class TestIntegration:
    """Integration tests for advisory service"""
    
    def test_thread_creation_flow(self):
        """Test complete thread creation flow"""
        # Create thread
        thread = ForumThread(
            title="Integration Test Thread",
            author_id="test-user",
            category=ThreadCategory.PEST_DISEASE
        )
        
        # Verify thread has ID
        assert thread.id is not None
        
        # Verify thread can be serialized
        data = thread.to_dict()
        assert data["title"] == "Integration Test Thread"
    
    def test_comment_on_thread(self):
        """Test adding comment to thread"""
        thread = ForumThread(
            title="Test Thread",
            author_id="author"
        )
        
        comment = ForumComment(
            thread_id=thread.id,
            author_id="commenter",
            content="Great advice!"
        )
        
        assert comment.thread_id == thread.id
        assert comment.is_accepted_answer == False
    
    def test_notification_creation(self):
        """Test notification creation on event"""
        notification = Notification(
            user_id="user-123",
            notification_type=NotificationType.THREAD_REPLY,
            thread_id="thread-456"
        )
        
        # Notification should be unread
        assert notification.is_read == False
        assert notification.channels == ["in_app"]


# ============ Fixtures ============

@pytest.fixture
def sample_thread_data():
    """Sample thread data for tests"""
    return {
        "title": "Early blight in tomatoes",
        "content_body": "I need help with early blight treatment...",
        "category": "pest_disease",
        "tags": ["tomato", "disease"],
        "author_id": "user-123"
    }


@pytest.fixture
def sample_article_data():
    """Sample article data for tests"""
    return {
        "title": "Early Blight Treatment Guide",
        "summary": "Complete guide to treating early blight",
        "content": "Full article content here...",
        "article_type": "disease_guide",
        "category": "disease_management",
        "keywords": ["tomato", "blight", "treatment"]
    }


# ============ Run Tests ============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
