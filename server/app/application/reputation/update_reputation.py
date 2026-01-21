from app.domain.reputation.entities import Reputation
from app.infrastructure.repositories.reputation_repo import ReputationRepository


class UpdateReputationUseCase:
    def __init__(self, reputation_repo: ReputationRepository):
        self.reputation_repo = reputation_repo

    def execute(self, user_id: str, event_type: str, **kwargs) -> Reputation:
        reputation = self.reputation_repo.create_or_get(user_id)

        if event_type == 'successful_order':
            reputation.record_successful_order()
        elif event_type == 'dispute_lost':
            reputation.record_dispute_lost()
        elif event_type == 'penalty_applied':
            penalty_amount = kwargs.get('penalty_amount', 0)
            reputation.record_penalty(penalty_amount)
        elif event_type == 'dispute_won':
            reputation.record_dispute_won()
        elif event_type == 'late_delivery':
            delay_days = kwargs.get('delay_days', 0)
            reputation.update_delivery_delay(delay_days)

        return self.reputation_repo.save(reputation)