from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.mappers import orm_to_domain, domain_to_orm
from app.infrastructure.db.models.alert import AlertORM
from app.domain.agriculture.entities import Alert as DomainAlert

class AlertRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, alert: DomainAlert) -> DomainAlert:
        orm = self.session.query(AlertORM).filter(AlertORM.id == str(alert.id)).one_or_none() if alert.id else None
        
        if orm:
            # Update existing alert
            updated_orm = domain_to_orm(alert)
            for key, value in updated_orm.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(orm, key, value)
        else:
            # Create new alert
            orm = domain_to_orm(alert)
            self.session.add(orm)
        
        self.session.flush()
        return orm_to_domain(orm)

    def get_by_id(self, alert_id: str) -> Optional[DomainAlert]:
        orm = self.session.query(AlertORM).filter(AlertORM.id == alert_id).one_or_none()
        if not orm:
            return None
        return orm_to_domain(orm)

    def list_by_user(
        self, 
        user_id: str,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> List[DomainAlert]:
        query = self.session.query(AlertORM).filter(
            AlertORM.user_id == user_id,
            AlertORM.dismissed == False
        )
        
        if severity:
            query = query.filter(AlertORM.severity == severity)
        
        if alert_type:
            query = query.filter(AlertORM.alert_type == alert_type)
        
        if unread_only:
            query = query.filter(AlertORM.acknowledged == False)
        
        orms = query.order_by(AlertORM.created_at.desc()).offset(skip).limit(limit).all()
        return [orm_to_domain(orm) for orm in orms]

    def list_critical(self, user_id: str) -> List[DomainAlert]:
        orms = self.session.query(AlertORM).filter(
            AlertORM.user_id == user_id,
            AlertORM.severity.in_(['CRITICAL', 'EMERGENCY']),
            AlertORM.dismissed == False
        ).order_by(AlertORM.created_at.desc()).limit(20).all()
        
        return [orm_to_domain(orm) for orm in orms]

    def get_unread_count(self, user_id: str) -> int:
        return self.session.query(AlertORM).filter(
            AlertORM.user_id == user_id,
            AlertORM.acknowledged == False,
            AlertORM.dismissed == False
        ).count()

    def acknowledge(self, alert_id: str) -> Optional[DomainAlert]:
        orm = self.session.query(AlertORM).filter(AlertORM.id == alert_id).one_or_none()
        if not orm:
            return None
        
        from datetime import datetime, timezone
        orm.acknowledged = True
        orm.acknowledged_at = datetime.now(timezone.utc)
        self.session.flush()
        return orm_to_domain(orm)

    def dismiss(self, alert_id: str) -> Optional[DomainAlert]:
        orm = self.session.query(AlertORM).filter(AlertORM.id == alert_id).one_or_none()
        if not orm:
            return None
        
        from datetime import datetime, timezone
        orm.dismissed = True
        orm.dismissed_at = datetime.now(timezone.utc)
        self.session.flush()
        return orm_to_domain(orm)
