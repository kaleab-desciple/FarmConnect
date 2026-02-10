#!/usr/bin/env python3
"""Debug script to check accounting state for a user."""
import sys
import os

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import get_db
from app.infrastructure.db.models.account import AccountORM
from app.infrastructure.db.models.journal_entry import JournalEntryORM, JournalLineORM

def main():
    user_id = sys.argv[1] if len(sys.argv) > 1 else "FAR-00002"
    
    db = next(get_db())
    
    print(f"\n=== Checking accounting state for user: {user_id} ===\n")
    
    # Check accounts
    print("--- Accounts ---")
    accounts = db.query(AccountORM).filter(AccountORM.owner_id == user_id).all()
    if accounts:
        for acc in accounts:
            print(f"  Account: {acc.id}")
            print(f"    owner_type: {acc.owner_type}")
            print(f"    owner_id: {acc.owner_id}")
            print(f"    account_type: {acc.account_type}")
            print(f"    name: {acc.name}")
            print()
    else:
        print(f"  No accounts found for user {user_id}")
    
    # Check journal lines for this user
    print("\n--- Journal Lines ---")
    lines = db.query(JournalLineORM).join(
        AccountORM, AccountORM.id == JournalLineORM.account_id
    ).filter(
        AccountORM.owner_id == user_id
    ).all()
    
    if lines:
        for line in lines:
            entry = db.query(JournalEntryORM).filter(
                JournalEntryORM.id == line.journal_entry_id
            ).first()
            print(f"  Journal Entry: {entry.id if entry else 'N/A'}")
            print(f"    reference: {entry.reference_type}/{entry.reference_id if entry else 'N/A'}")
            print(f"    description: {entry.description if entry else 'N/A'}")
            print(f"    debit: {line.debit_amount}, credit: {line.credit_amount}")
            print()
    else:
        print(f"  No journal lines found for user {user_id}")
    
    # Check all accounts in system
    print("\n--- All Accounts in System ---")
    all_accounts = db.query(AccountORM).all()
    for acc in all_accounts[:20]:  # Limit to 20
        print(f"  {acc.id}: {acc.owner_type}/{acc.owner_id} - {acc.account_type} - {acc.name}")
    if len(all_accounts) > 20:
        print(f"  ... and {len(all_accounts) - 20} more accounts")
    
    db.close()

if __name__ == "__main__":
    main()
