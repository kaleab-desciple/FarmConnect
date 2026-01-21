from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None
