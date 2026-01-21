from app.domain.payments.ports import PaymentProvider
from abc import ABC

class BankProvider(PaymentProvider, ABC):
    pass