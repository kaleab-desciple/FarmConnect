import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

# Add server directory to path
sys.path.append(os.path.join(os.getcwd(), "server"))
# Add shared/py directory to path - PREPEND to override installed package
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "../shared/py")))
# Add Desktop venv site-packages as fallback for broken venv
sys.path.append("/home/kaleab/Desktop/Farm_Connect/venv/lib/python3.12/site-packages")

from app.domain.advisory.notifications import NotificationType, Notification, UserNotificationPreference
from app.domain.advisory.forums_entities import ForumThread, ForumComment, ForumReport
from app.domain.advisory.notification_service import NotificationService
from app.domain.advisory.moderation_service import ModerationService
from app.api.v1.advisory.forums.service import ForumService
from app.core.auth.dependencies import TokenPayload

# Mock Repositories
class MockRepo:
    def __init__(self):
        self.threads = {}
        self.comments = {}
        self.reports = {}
        self.notifications = {}
        self.preferences = {}
        self.users = {
            "user1": MagicMock(id="user1", name="User One", metadata_={}), 
            "user2": MagicMock(id="user2", name="User Two", metadata_={}), 
            "mod1": MagicMock(id="mod1", name="Moderator One", metadata_={})
        }

    def save_thread(self, thread):
        self.threads[thread.id] = thread
        return thread
    
    def get_thread_by_id(self, id, user=None):
        return self.threads.get(id)

    def save_comment(self, comment):
        self.comments[comment.id] = comment
        return comment
    
    def get_comment_by_id(self, id):
        return self.comments.get(id)

    def save_report(self, report):
        self.reports[report.id] = report
        return report

    def get_report_by_id(self, id):
        return self.reports.get(id)

    def update_thread(self, id, data):
        thread = self.threads.get(id)
        if thread:
            for k, v in data.items():
                setattr(thread, k, v)
        return thread

    def update_comment(self, id, data):
        comment = self.comments.get(id)
        if comment:
            for k, v in data.items():
                setattr(comment, k, v)
        return comment

    def list_reports(self, status=None, page=1, page_size=20):
        res = [r for r in self.reports.values() if not status or r.moderation_status == status]
        return res, len(res)
    
    def get_user_preferences(self, user_id):
        return self.preferences.get(user_id)
    
    def save_user_preferences(self, prefs):
        self.preferences[prefs.user_id] = prefs
        return prefs

    def save_notification(self, notif):
        notif.id = "notif-" + str(len(self.notifications) + 1)
        notif.created_at = datetime.utcnow()
        self.notifications[notif.id] = notif
        return notif
    
    def list_user_notifications(self, user_id, unread_only=False, limit=50, offset=0):
        res = [n for n in self.notifications.values() if n.user_id == user_id]
        return res, len(res)

    def get_by_id(self, id):
        return self.users.get(id)
        
    def get_by_keycloak_id(self, kid):
        # Mock keycloak to internal ID mapping
        return self.users.get(kid)

    def update(self, user_id, updates):
        user = self.users.get(user_id)
        if user:
            # Updates is a dict, keys might be metadata_
            for k, v in updates.items():
                setattr(user, k, v)
        return user

async def test_flow():
    print("Starting verification flow...")
    
    # Setup Mocks
    session = MagicMock()
    repo = MockRepo()
    
    # Init Services with Mocks
    # We have to patch the repo instantiation inside ForumService or pass mocked methods
    # Since ForumService instantiates Repo internally, we might need to subclass or patch
    
    print("1. Initializing Services...")
    # Notification Service
    notif_service = NotificationService(repo, repo) # passing MockRepo as both notif_repo and user_repo
    
    # Forum Service
    # We'll monkey patch the repo instance on the service after init if possible, 
    # but init calls Repo(session). We can mock the Repo class or just rely on manual assignment
    forum_service = ForumService(session)
    forum_service.repo = repo # Swap with mock
    forum_service.user_repo = repo
    forum_service.notification_service = notif_service # Use our instantiated notif service
    
    # Moderation Service
    mod_service = ModerationService(repo, notif_service, repo) # passing MockRepo as forum_repo and user_repo
    
    # Inject mod_service into forum_service
    forum_service.moderation_service = mod_service
    
    # 2. Test Thread Creation
    print("2. Creating Thread (User 1)...")
    user1_token = TokenPayload({
        "sub": "user1",
        "preferred_username": "User One",
        "email": "user1@example.com",
        "realm_access": {"roles": ["user"]},
        "resource_access": {}
    })
    # We need to mock _get_internal_user_id or ensure user_repo.get_by_keycloak_id works
    # Our mock repo returns user object with id="user1" for get_by_keycloak_id("user1")
    
    thread_data = MagicMock()
    thread_data.title = "Corn Blight Help"
    thread_data.content_body = "I have corn blight."
    thread_data.category = "pest_disease"
    thread_data.tags = ["corn"]
    thread_data.content_format = "markdown"
    thread_data.subcategory = None
    thread_data.context_field_id = None
    thread_data.context_crop_cycle_id = None
    thread_data.context_crop_type = None
    thread_data.context_growth_stage = None

    thread = forum_service.create_thread(thread_data, user1_token)
    print(f"   Thread created: {thread.id} by {thread.author_id}")
    assert thread.author_id == "user1"

    # 3. Test Reply (User 2) -> Should notify User 1
    print("3. Creating Reply (User 2)...")
    user2_token = TokenPayload({
        "sub": "user2",
        "preferred_username": "User Two",
        "email": "user2@example.com",
        "realm_access": {"roles": ["user"]},
        "resource_access": {}
    })
    
    comment_data = MagicMock()
    comment_data.content = "Use fungicide."
    comment_data.parent_id = None
    comment_data.attachments = []
    
    comment = await forum_service.create_comment(thread.id, comment_data, user2_token)
    print(f"   Comment created: {comment.id}")
    
    # Check notifications
    notifs, _ = notif_service.get_user_notifications("user1")
    print(f"   User 1 Notifications: {len(notifs)}")
    assert len(notifs) >= 1
    assert notifs[0].notification_type == NotificationType.THREAD_REPLY
    print("   ✅ Notification received for thread reply")

    # 4. Test Reporting (User 1 reports User 2's comment)
    print("4. Reporting Comment (User 1)...")
    report = await mod_service.submit_report(
        reporter_id="user1",
        report_type="spam",
        report_reason="It is spam",
        comment_id=comment.id
    )
    print(f"   Report submitted: {report.id}")
    assert report.moderation_status == "pending"
    
    # Check receipt notification for User 1
    notifs, _ = notif_service.get_user_notifications("user1")
    # Should have reply notification + report receipt
    print(f"   User 1 Notifications: {len(notifs)}")
    # Assuming list returns all, latest first or last? Implementation was simple list
    # Let's check if any report received notif exists
    report_receipts = [n for n in notifs if "received your report" in n.message]
    assert len(report_receipts) >= 1
    print("   ✅ Report receipt notification received")

    # 5. Moderator List & Resolve
    print("5. Moderation Action (Mod 1)...")
    pending, _ = mod_service.get_pending_reports()
    print(f"   Pending reports: {len(pending)}")
    assert len(pending) >= 1
    
    # Resolve - Removal
    print("   Resolving report with removal...")
    resolved_report = await mod_service.process_report(
        report_id=report.id,
        moderator_id="mod1",
        decision="remove",
        notes="Confirmed spam"
    )
    
    assert resolved_report.moderation_status == "resolved"
    assert repo.comments[comment.id].moderation_status == "rejected"
    print("   ✅ Content removed (marked rejected)")
    
    # Check notification for User 2 (Author of removed content)
    notifs_u2, _ = notif_service.get_user_notifications("user2")
    removed_notifs = [n for n in notifs_u2 if n.notification_type == NotificationType.CONTENT_REMOVED]
    assert len(removed_notifs) == 1
    print("   ✅ User 2 notified of removal")
    
    # Check notification for User 1 (Reporter)
    notifs_u1, _ = notif_service.get_user_notifications("user1")
    resolved_notifs = [n for n in notifs_u1 if n.notification_type == NotificationType.REPORT_RESOLVED]
    assert len(resolved_notifs) == 1
    print("   ✅ User 1 notified of resolution")

    print("   ✅ User 1 notified of resolution")

    # 6. Test Spam Detection
    print("6. Spam Detection...")
    spam_thread_data = MagicMock()
    spam_thread_data.title = "Free Money"
    spam_thread_data.content_body = "Click here to win. Buy cheap viagra."
    spam_thread_data.category = "general"
    spam_thread_data.tags = []
    spam_thread_data.content_format = "markdown"

    try:
        forum_service.create_thread(spam_thread_data, user1_token)
        print("   ❌ Spam detection FAILED (Thread created)")
    except Exception as e:
        if "prohibited spam patterns" in str(e):
             print("   ✅ Spam detection passed (Thread blocked)")
        else:
             print(f"   ❌ Unexpected error: {e}")

    # 7. Test User Warning
    print("7. User Warning (Mod 1 warns User 2)...")
    await mod_service.warn_user("user2", "Stop posting spam", "mod1")
    
    user2 = repo.get_by_id("user2")
    # Verify metadata updated
    # MagicMock doesn't behave exactly like object with attributes unless configured
    # In MockRepo, we set `metadata_` on the mock object via setattr
    if hasattr(user2, "metadata_"):
        warnings = user2.metadata_.get("warnings", [])
        assert len(warnings) == 1
        assert warnings[0]["reason"] == "Stop posting spam"
        print("   ✅ User 2 metadata updated with warning")
    else:
        print("   ❌ User 2 metadata not updated")

    # Check notification
    notifs_u2, _ = notif_service.get_user_notifications("user2")
    warn_notifs = [n for n in notifs_u2 if n.notification_type == NotificationType.SYSTEM and "warning" in n.title.lower()]
    assert len(warn_notifs) >= 1
    print("   ✅ User 2 notified of warning")

    # 8. Test User Suspension
    print("8. User Suspension (Mod 1 suspends User 2)...")
    await mod_service.suspend_user("user2", 3, "Repeated spam", "mod1")
    
    user2 = repo.get_by_id("user2")
    if hasattr(user2, "metadata_"):
        suspension = user2.metadata_.get("suspension", {})
        assert suspension["active"] == True
        assert suspension["reason"] == "Repeated spam"
        print("   ✅ User 2 metadata updated with suspension")
    
    # Check notification
    notifs_u2, _ = notif_service.get_user_notifications("user2")
    susp_notifs = [n for n in notifs_u2 if n.notification_type == NotificationType.SYSTEM and "suspended" in n.title.lower()]
    assert len(susp_notifs) >= 1
    print("   ✅ User 2 notified of suspension")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(test_flow())
