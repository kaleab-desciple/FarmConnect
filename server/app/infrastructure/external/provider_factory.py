from app.domain.payments.ports import PaymentProvider
from app.infrastructure.external.banks.mock_bank import MockBankProvider
from app.infrastructure.external.wallets.mock_wallet import MockWalletProvider

def get_payment_provider(provider_type: str) -> PaymentProvider:
    if provider_type == "BANK":
        return MockBankProvider()
    if provider_type == "WALLET":
        return MockWalletProvider()

    raise ValueError(f"Unknown provider {provider_type}")

class ProviderFactory:
    @staticmethod
    def get(provider_type: str) -> PaymentProvider:
        return get_payment_provider(provider_type)
