from app.domain.payments.ports import PaymentProvider
from app.domain.payments.exceptions import PaymentFailed
from uuid import UUID
from decimal import Decimal

class MockWalletProvider(PaymentProvider):
    def debit(
        self,
        reference_id: UUID,
        amount: Decimal,
        source_account: str
    ) -> None:
        if amount > 10_000:
            raise PaymentFailed("Wallet limit exceeded")

        print(
            f"[WALLET] Debited {amount} from wallet {source_account} "
            f"(ref={reference_id})"
        )
