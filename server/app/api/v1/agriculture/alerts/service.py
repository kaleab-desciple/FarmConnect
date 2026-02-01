from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.infrastructure.repositories.alert_repo import AlertRepository
from app.infrastructure.db.mappers import domain_to_dto
from app.domain.agriculture.entities import Alert as DomainAlert
from app.domain.agriculture.enums import AlertType, AlertSeverity
from app.core.config.agriculture_config import agriculture_config
from shared_models import Alert as AlertDTO, AlertCreate, AlertUpdate

class AlertService:
    def __init__(self, session: Session):
        self.session = session
        self.alert_repo = AlertRepository(session)

    def create_alert(self, alert_data: AlertCreate) -> Optional[AlertDTO]:
        """Create a new alert"""
        # Check if weather alerts are enabled
        if alert_data.alert_type in ['WEATHER_WARNING', 'FROST_ALERT', 'DROUGHT_ALERT']:
            if not agriculture_config.enable_weather_alerts:
                return None  # Weather alerts disabled
        
        domain_alert = DomainAlert(
            id=uuid4(),
            user_id=alert_data.user_id,
            field_id=alert_data.field_id,
            crop_cycle_id=alert_data.crop_cycle_id,
            alert_type=AlertType(alert_data.alert_type),
            severity=AlertSeverity(alert_data.severity),
            title=alert_data.title,
            message=alert_data.message,
            action_required=alert_data.action_required,
            action_url=alert_data.action_url,
            related_entity_type=alert_data.related_entity_type,
            related_entity_id=alert_data.related_entity_id,
            expires_at=alert_data.expires_at,
            acknowledged=False,
            dismissed=False,
            metadata={},
            created_at=datetime.now(timezone.utc)
        )
        
        saved_alert = self.alert_repo.save(domain_alert)
        self.session.commit()
        return domain_to_dto(saved_alert)

    def get_alert(self, alert_id: str) -> Optional[AlertDTO]:
        """Get alert by ID"""
        domain_alert = self.alert_repo.get_by_id(alert_id)
        if not domain_alert:
            return None
        return domain_to_dto(domain_alert)

    def list_alerts(
        self,
        user_id: str,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> List[AlertDTO]:
        """List alerts for a user"""
        domain_alerts = self.alert_repo.list_by_user(
            user_id=user_id,
            severity=severity,
            alert_type=alert_type,
            unread_only=unread_only,
            skip=skip,
            limit=limit
        )
        return [domain_to_dto(alert) for alert in domain_alerts]

    def list_critical_alerts(self, user_id: str) -> List[AlertDTO]:
        """List critical and emergency alerts"""
        domain_alerts = self.alert_repo.list_critical(user_id)
        return [domain_to_dto(alert) for alert in domain_alerts]

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread alerts"""
        return self.alert_repo.get_unread_count(user_id)

    def acknowledge_alert(self, alert_id: str) -> Optional[AlertDTO]:
        """Acknowledge an alert"""
        domain_alert = self.alert_repo.acknowledge(alert_id)
        if domain_alert:
            self.session.commit()
            return domain_to_dto(domain_alert)
        return None

    def dismiss_alert(self, alert_id: str) -> Optional[AlertDTO]:
        """Dismiss an alert"""
        domain_alert = self.alert_repo.dismiss(alert_id)
        if domain_alert:
            self.session.commit()
            return domain_to_dto(domain_alert)
        return None
    
    def cleanup_old_alerts(self, user_id: str) -> int:
        """Clean up alerts older than retention period"""
        from datetime import datetime, timezone, timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=agriculture_config.alert_retention_days)
        
        # This would need a repository method to delete old alerts
        # For now, just return 0 as a placeholder
        return 0
    
    def is_weather_alerts_enabled(self) -> bool:
        """Check if weather alerts are enabled"""
        return agriculture_config.enable_weather_alerts
    
    def should_send_critical_email(self) -> bool:
        """Check if critical alerts should trigger emails"""
        return agriculture_config.critical_alert_email
