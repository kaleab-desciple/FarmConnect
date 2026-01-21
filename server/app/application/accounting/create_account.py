from uuid import uuid4
from datetime import datetime, timezone
from typing import Protocol
from app.domain.accounting.entities import Account, OwnerType, AccountType


class AccountRepository(Protocol):
    def save(self, account: Account) -> None:
        ...

    def get_by_id(self, account_id: str) -> Account | None:
        ...


class CreateAccountRequest:
    def __init__(self, owner_type: OwnerType, owner_id: str, account_type: AccountType, name: str, currency: str):
        self.owner_type = owner_type
        self.owner_id = owner_id
        self.account_type = account_type
        self.name = name
        self.currency = currency


class CreateAccount:
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def execute(self, request: CreateAccountRequest) -> Account:
        account = Account(
            id=uuid4(),
            owner_type=request.owner_type,
            owner_id=request.owner_id,
            account_type=request.account_type,
            name=request.name,
            currency=request.currency,
            created_at=datetime.now(timezone.utc)
        )
        self.account_repo.save(account)
        return account