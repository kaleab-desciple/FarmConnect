from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text

from shared_models import User
from app.infrastructure.db.mappers import dto_to_orm, orm_to_domain
from app.infrastructure.db.models import UserORM
from app.domain.users.entities import User as DomainUser


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> None:
        if not user.id:
            # Generate ID
            # 1. Get next sequence value
            # Note: This requires the sequence 'user_id_seq' to be created in DB migration
            result = self.session.execute(sa_text("SELECT nextval('user_id_seq')"))
            seq_val = result.scalar()
            
            # 2. Determine prefix
            # user.role is likely an Enum e.g. UserRole.FARMER or string 'FARMER'
            # We want 'FAR', 'MER', etc.
            role_str = str(user.role.value if hasattr(user.role, 'value') else user.role).upper()
            prefix = role_str[:3]
            
            # 3. Format ID
            user.id = f"{prefix}-{seq_val:05d}"

        orm = dto_to_orm(user)
        self.session.add(orm)
        self.session.commit()

    def get_by_id(self, user_id: str) -> Optional[DomainUser]:
        orm = (
            self.session.query(UserORM)
            .filter(UserORM.id == str(user_id))
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_keycloak_id(self, keycloak_id: str) -> Optional[DomainUser]:
        orm = (
            self.session.query(UserORM)
            .filter(UserORM.keycloak_id == keycloak_id)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_email(self, email: str) -> Optional[DomainUser]:
        orm = (
            self.session.query(UserORM)
            .filter(UserORM.email == email)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def get_by_phone(self, phone: str) -> Optional[DomainUser]:
        orm = (
            self.session.query(UserORM)
            .filter(UserORM.phone == phone)
            .one_or_none()
        )
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_all(self) -> List[DomainUser]:
        orms = self.session.query(UserORM).all()
        return [orm_to_domain(orm) for orm in orms]

    def update(self, user_id: str, updates: dict) -> Optional[DomainUser]:
        orm = (
            self.session.query(UserORM)
            .filter(UserORM.id == str(user_id))
            .one_or_none()
        )
        if not orm:
            return None
        for key, value in updates.items():
            if hasattr(orm, key):
                setattr(orm, key, value)
        self.session.commit()
        return orm_to_domain(orm)

    def delete(self, user_id: str) -> bool:
        orm = (
            self.session.query(UserORM)
            .filter(UserORM.id == str(user_id))
            .one_or_none()
        )
        if not orm:
            return False
        self.session.delete(orm)
        self.session.commit()
        return True