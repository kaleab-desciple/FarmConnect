from abc import ABC, abstractmethod
from decimal import Decimal

class PaymentProvider(ABC):
    @abstractmethod
    def debit(
        self,
        reference_id: str,
        amount: Decimal,
        source_account: str
    ) -> None:
        """
        Raises PaymentFailed on failure
        """

    @abstractmethod
    def fund_escrow(self, escrow_id: str, amount: Decimal) -> str:
        """
        Fund an escrow account, returns transaction reference
        Raises PaymentFailed on failure
        """

    @abstractmethod
    def release_funds(self, escrow_id: str) -> str:
        """
        Release funds from escrow to farmer, returns transaction reference
        Raises PaymentFailed on failure
        """

    @abstractmethod
    def refund_funds(self, escrow_id: str) -> str:
        """
        Refund funds from escrow to merchant, returns transaction reference
        Raises PaymentFailed on failure
        """

    @abstractmethod
    def partial_release(self, escrow_id: str, penalty: Decimal) -> str:
        """
        Partial release funds from escrow to farmer with penalty, returns transaction reference
        Raises PaymentFailed on failure
        """
