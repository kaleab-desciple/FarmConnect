from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class Reputation:
    user_id: str
    completed_orders: int = 0
    successful_orders: int = 0
    disputes_lost: int = 0
    avg_delivery_delay: Optional[int] = None  # days
    reputation_score: int = 50  # 0-100

    def update_score(self) -> None:
        """Recalculate reputation score based on current metrics."""
        score = 50  # base

        # Successful orders: +2 each
        score += self.successful_orders * 2

        # Disputes lost: -10 each
        score -= self.disputes_lost * 10

        # Late delivery: -1 per day average
        if self.avg_delivery_delay:
            score -= self.avg_delivery_delay

        # Clamp between 0-100
        self.reputation_score = max(0, min(100, score))

    def record_successful_order(self) -> None:
        self.completed_orders += 1
        self.successful_orders += 1
        self.update_score()

    def record_dispute_lost(self) -> None:
        self.disputes_lost += 1
        self.update_score()



    def record_dispute_won(self) -> None:
        # Dispute won: +3
        self.reputation_score = min(100, self.reputation_score + 3)

    def update_delivery_delay(self, delay_days: int) -> None:
        # Simple average update (in real system, would track all orders)
        if self.avg_delivery_delay is None:
            self.avg_delivery_delay = delay_days
        else:
            self.avg_delivery_delay = (self.avg_delivery_delay + delay_days) // 2
        self.update_score()