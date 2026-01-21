from app.infrastructure.repositories.reputation_repo import ReputationRepository


class LoanService:
    def __init__(self, reputation_repo: ReputationRepository):
        self.reputation_repo = reputation_repo

    def calculate_max_loan_amount(self, user_id: str, avg_order_value: float = 1000.0) -> float:
        """Calculate max loan amount based on reputation score."""
        reputation = self.reputation_repo.get_by_user_id(user_id)
        if not reputation:
            return 0.0  # No reputation, no loan

        score = reputation.reputation_score
        if score >= 80:
            return avg_order_value * 3
        elif score >= 60:
            return avg_order_value * 1.5
        else:
            return 0.0  # Not eligible

    def is_eligible_for_loan(self, user_id: str) -> bool:
        """Check if user is eligible for loan based on score."""
        max_amount = self.calculate_max_loan_amount(user_id)
        return max_amount > 0
