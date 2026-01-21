from app.domain.payments.ports import PaymentProvider
from app.domain.payments.exceptions import PaymentFailed
from decimal import Decimal
import random
import uuid

class MockBankProvider(PaymentProvider):
    def debit(
        self,
        reference_id: str,
        amount: Decimal,
        source_account: str
    ) -> None:
        # Simulate intermittent failure
        if random.random() < 0.2:
            raise PaymentFailed("Bank debit failed")

        print(
            f"[BANK] Debited {amount} from {source_account} "
            f"(ref={reference_id})"
        )

    def fund_escrow(self, escrow_id: str, amount: Decimal) -> str:
        # Mock always succeeds
        reference = f"MOCK-TXN-{uuid.uuid4().hex[:8].upper()}"
        print(
            f"[BANK] Funded escrow {escrow_id} with {amount} "
            f"(ref={reference})"
        )
        return reference

    def release_funds(self, escrow_id: str) -> str:
        # Mock always succeeds
        reference = f"MOCK-REL-{uuid.uuid4().hex[:8].upper()}"
        print(
            f"[BANK] Released funds from escrow {escrow_id} "
            f"(ref={reference})"
        )
        return reference

    def refund_funds(self, escrow_id: str) -> str:
        # Mock always succeeds
        reference = f"MOCK-REF-{uuid.uuid4().hex[:8].upper()}"
        print(
            f"[BANK] Refunded funds from escrow {escrow_id} "
            f"(ref={reference})"
        )
        return reference

    def partial_release(self, escrow_id: str, penalty: Decimal) -> str:
        # Mock always succeeds
        reference = f"MOCK-PART-{uuid.uuid4().hex[:8].upper()}"
        print(
            f"[BANK] Partial released funds from escrow {escrow_id} with penalty {penalty} "
            f"(ref={reference})"
        )
        return reference
