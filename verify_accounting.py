import sys
import os
from uuid import uuid4
from decimal import Decimal

# Add server to path
sys.path.append('/home/kaleab/Desktop/Farm_Connect/server')

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from app.application.accounting.ledger_to_journal_mapper import LedgerToJournalMapper
from app.application.accounting.get_account_statement import GetAccountStatement, GetAccountStatementRequest
from app.domain.ledger.entities import LedgerEvent, LedgerEventType, AggregateType, Direction, ReferenceType
from app.domain.accounting.entities import OwnerType, AccountType

def verify():
    session = SessionLocal()
    account_repo = AccountRepository(session)
    journal_repo = JournalRepository(session)
    mapper = LedgerToJournalMapper(account_repo)
    
    # Simulate User and Escrow
    user_id = f"TESTUSER-{uuid4().hex[:8]}"
    escrow_id_1 = f"ESCROW-{uuid4().hex[:8]}"
    escrow_id_2 = f"ESCROW-{uuid4().hex[:8]}"
    
    print(f"Testing with User: {user_id}")
    
    # Event 1: Fund Escrow 1
    event1 = LedgerEvent(
        id=str(uuid4()),
        aggregate_type=AggregateType.USER,
        aggregate_id=user_id,
        event_type=LedgerEventType.ESCROW_FUNDED,
        amount=Decimal("1000.00"),
        direction=Direction.DEBIT, # Dummy
        reference_type=ReferenceType.ESCROW,
        reference_id=escrow_id_1,
        event_metadata={}
    )
    print("Mapping Event 1 (Funding Escrow 1)...")
    mapper.map_event_to_journal_lines(event1)
    
    # Check if accounts created
    merchant_cash = account_repo.get_by_owner_and_type(OwnerType.USER.value, user_id, AccountType.ASSET.value)
    if not merchant_cash:
        print("FAIL: Merchant Cash account not created")
        return
    print(f"Merchant Cash Account Created: {merchant_cash.id}")
    
    # Event 2: Fund Escrow 2 (Same User)
    event2 = LedgerEvent(
        id=str(uuid4()),
        aggregate_type=AggregateType.USER,
        aggregate_id=user_id,
        event_type=LedgerEventType.ESCROW_FUNDED,
        amount=Decimal("500.00"),
        direction=Direction.DEBIT, # Dummy
        reference_type=ReferenceType.ESCROW,
        reference_id=escrow_id_2,
        event_metadata={}
    )
    print("Mapping Event 2 (Funding Escrow 2)...")
    mapper.map_event_to_journal_lines(event2)
    
    # Check if duplicate account created
    merchant_cash_2 = account_repo.get_by_owner_and_type(OwnerType.USER.value, user_id, AccountType.ASSET.value)
    if merchant_cash.id != merchant_cash_2.id:
        print(f"FAIL: Duplicate Merchant Cash account created! {merchant_cash.id} vs {merchant_cash_2.id}")
        exit(1)
    else:
        print("SUCCESS: Merchant Cash account reused")
        
    # Strict Verification: Check DB Count
    from app.infrastructure.db.models.account import AccountORM
    
    count = session.query(AccountORM).filter(
        AccountORM.owner_id == user_id,
        AccountORM.account_type == AccountType.ASSET
    ).count()
    
    if count != 1:
        print(f"FAIL: Database has {count} asset accounts for user {user_id}, expected 1")
        exit(1)
    else:
        print(f"SUCCESS: Database confirmed exactly 1 account for user")
        
    # Verify Reporting
    print("\nVerifying Reporting...")
    # We need to actually SAVE the journal entries to test reporting, but the mapper only returns lines.
    # The mapper logic in `map_event_to_journal_lines` does NOT save the journal entry, it just returns lines.
    # We need to manually create and save a journal entry using these lines to test the repository.
    
    # Note: The mapper calls `create_account_uc` which DOES save accounts.
    # So accounts exist in DB.
    
    # Let's save a dummy journal entry for the merchant cash account
    from app.domain.accounting.entities import JournalEntry, JournalLine
    from app.domain.accounting.entities import ReferenceType as AccRefType
    from datetime import datetime
    
    lines = [
        JournalLine(account_id=merchant_cash.id, debit_amount=Decimal("1000.00"), credit_amount=Decimal("0")),
        # Balancing line (dummy)
        JournalLine(account_id=merchant_cash.id, debit_amount=Decimal("0"), credit_amount=Decimal("1000.00")) 
    ]
    
    entry = JournalEntry(
        id=uuid4(),
        reference_type=AccRefType.ORDER,
        reference_id="TEST-ORDER",
        description="Test Entry",
        lines=lines,
        created_at=datetime.now()
    )
    
    journal_repo.save(entry)
    session.commit()
    
    # Get Statement
    uc = GetAccountStatement(journal_repo)
    statement = uc.execute(GetAccountStatementRequest(str(merchant_cash.id)))
    
    print(f"Statement for {merchant_cash.name}:")
    for line in statement:
        print(f"  {line.created_at} | {line.description} | Dr {line.debit} | Cr {line.credit} | Bal {line.balance_after}")
        
    if len(statement) > 0:
        print("SUCCESS: Statement generated")
    else:
        print("FAIL: Statement empty")

if __name__ == "__main__":
    verify()
