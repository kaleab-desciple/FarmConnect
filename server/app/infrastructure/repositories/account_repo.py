from typing import Optional
from sqlalchemy.orm import Session
from app.domain.accounting.entities import Account, OwnerType, AccountType
from app.infrastructure.db.models.account import AccountORM


class AccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, account: Account) -> None:
        orm = AccountORM(
            id=str(account.id),
            owner_type=account.owner_type,
            owner_id=account.owner_id,
            account_type=account.account_type,
            name=account.name,
            currency=account.currency,
            created_at=account.created_at
        )
        self.session.add(orm)
        self.session.commit()

    def get_by_id(self, account_id: str) -> Optional[Account]:
        orm = self.session.query(AccountORM).filter(AccountORM.id == account_id).first()
        if not orm:
            return None
        return Account(
            id=orm.id,
            owner_type=orm.owner_type,
            owner_id=orm.owner_id,
            account_type=orm.account_type,
            name=orm.name,
            currency=orm.currency,
            created_at=orm.created_at
        )

    def get_by_owner_and_type(self, owner_type: any, owner_id: str, account_type: any) -> Optional[Account]:
        # Normalize types for query: AccountORM expects Enum objects
        
        if isinstance(owner_type, str):
            try:
                owner_type = OwnerType(owner_type)
            except ValueError:
                pass # let it fail or pass string if that's what caller intended
                
        if isinstance(account_type, str):
            try:
                account_type = AccountType(account_type)
            except ValueError:
                pass

        orm = self.session.query(AccountORM).filter(
            AccountORM.owner_type == owner_type,
            AccountORM.owner_id == str(owner_id),
            AccountORM.account_type == account_type
        ).first()
        
        if not orm:
            return None
            
        return Account(
            id=orm.id,
            owner_type=orm.owner_type,
            owner_id=orm.owner_id,
            account_type=orm.account_type,
            name=orm.name,
            currency=orm.currency,
            created_at=orm.created_at
        )