from app.domain.payments.ports import PaymentProvider
from abc import ABC

class WalletProvider(PaymentProvider, ABC):
    pass
