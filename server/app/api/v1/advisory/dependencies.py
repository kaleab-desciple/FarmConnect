from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.repositories.forums_repo import ForumRepository
from app.infrastructure.repositories.notification_repo import NotificationRepository
from app.infrastructure.repositories.user_repo import UserRepository

from app.domain.advisory.notification_service import NotificationService
from app.domain.advisory.moderation_service import ModerationService

def get_forum_repository(db: Session = Depends(get_db)) -> ForumRepository:
    return ForumRepository(db)

def get_notification_repository(db: Session = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_notification_service(
    notification_repo: NotificationRepository = Depends(get_notification_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> NotificationService:
    return NotificationService(notification_repo, user_repo)

def get_moderation_service(
    forum_repo: ForumRepository = Depends(get_forum_repository),
    notification_service: NotificationService = Depends(get_notification_service),
    user_repo: UserRepository = Depends(get_user_repository)
) -> ModerationService:
    return ModerationService(forum_repo, notification_service, user_repo)
