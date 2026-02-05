"""
Test script to verify that accounts are properly reused instead of creating duplicates.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.repositories.account_repo import AccountRepository
from app.application.accounting.ledger_to_journal_mapper import LedgerToJournalMapper
from app.domain.accounting.entities import OwnerType, AccountType
from app.core.config.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_account_reuse():
    """Test that _get_or_create_account reuses existing accounts."""
    session = SessionLocal()
    
    try:
        account_repo = AccountRepository(session)
        mapper = LedgerToJournalMapper(account_repo)
        
        print("=" * 80)
        print("Testing Account Reuse Functionality")
        print("=" * 80)
        
        # Test 1: Create first account for a user
        print("\n1. Creating first account for user MER-00001...")
        account_id_1 = mapper._get_or_create_account(
            OwnerType.USER, "MER-00001", AccountType.ASSET, "Merchant Cash"
        )
        print(f"   Created/Retrieved Account ID: {account_id_1}")
        
        # Count accounts for this user
        count_1 = session.execute(
            "SELECT COUNT(*) FROM accounts WHERE owner_type = 'USER' AND owner_id = 'MER-00001' AND account_type = 'ASSET'"
        ).scalar()
        print(f"   Total ASSET accounts for MER-00001: {count_1}")
        
        # Test 2: Try to create same account again - should reuse
        print("\n2. Attempting to create same account again...")
        account_id_2 = mapper._get_or_create_account(
            OwnerType.USER, "MER-00001", AccountType.ASSET, "Merchant Cash"
        )
        print(f"   Created/Retrieved Account ID: {account_id_2}")
        
        # Count accounts again
        count_2 = session.execute(
            "SELECT COUNT(*) FROM accounts WHERE owner_type = 'USER' AND owner_id = 'MER-00001' AND account_type = 'ASSET'"
        ).scalar()
        print(f"   Total ASSET accounts for MER-00001: {count_2}")
        
        # Verify they're the same
        if account_id_1 == account_id_2:
            print("   ✓ SUCCESS: Same account was reused!")
        else:
            print("   ✗ FAILURE: Different accounts were created!")
            
        if count_1 == count_2 == 1:
            print("   ✓ SUCCESS: Only one account exists!")
        else:
            print(f"   ✗ FAILURE: Expected 1 account, found {count_2}!")
        
        # Test 3: Create different account type for same user
        print("\n3. Creating different account type (LIABILITY) for same user...")
        account_id_3 = mapper._get_or_create_account(
            OwnerType.USER, "MER-00001", AccountType.LIABILITY, "Merchant Payable"
        )
        print(f"   Created/Retrieved Account ID: {account_id_3}")
        
        # Count all accounts for this user
        total_count = session.execute(
            "SELECT COUNT(*) FROM accounts WHERE owner_type = 'USER' AND owner_id = 'MER-00001'"
        ).scalar()
        print(f"   Total accounts for MER-00001: {total_count}")
        
        if total_count == 2:
            print("   ✓ SUCCESS: Two different account types exist!")
        else:
            print(f"   ✗ FAILURE: Expected 2 accounts, found {total_count}!")
        
        # Test 4: Test with escrow accounts
        print("\n4. Testing escrow account reuse...")
        escrow_id = "test-escrow-123"
        
        escrow_account_1 = mapper._get_or_create_account(
            OwnerType.ESCROW, escrow_id, AccountType.LIABILITY, "Escrow Holding"
        )
        print(f"   First call - Account ID: {escrow_account_1}")
        
        escrow_account_2 = mapper._get_or_create_account(
            OwnerType.ESCROW, escrow_id, AccountType.LIABILITY, "Escrow Holding"
        )
        print(f"   Second call - Account ID: {escrow_account_2}")
        
        escrow_count = session.execute(
            f"SELECT COUNT(*) FROM accounts WHERE owner_type = 'ESCROW' AND owner_id = '{escrow_id}'"
        ).scalar()
        print(f"   Total escrow accounts: {escrow_count}")
        
        if escrow_account_1 == escrow_account_2 and escrow_count == 1:
            print("   ✓ SUCCESS: Escrow account was reused!")
        else:
            print("   ✗ FAILURE: Escrow account was not properly reused!")
        
        # Test 5: Test platform account reuse
        print("\n5. Testing platform account reuse...")
        
        platform_account_1 = mapper._get_or_create_account(
            OwnerType.SYSTEM, "platform", AccountType.REVENUE, "Platform Revenue"
        )
        print(f"   First call - Account ID: {platform_account_1}")
        
        platform_account_2 = mapper._get_or_create_account(
            OwnerType.SYSTEM, "platform", AccountType.REVENUE, "Platform Revenue"
        )
        print(f"   Second call - Account ID: {platform_account_2}")
        
        platform_count = session.execute(
            "SELECT COUNT(*) FROM accounts WHERE owner_type = 'SYSTEM' AND owner_id = 'platform'"
        ).scalar()
        print(f"   Total platform accounts: {platform_count}")
        
        if platform_account_1 == platform_account_2 and platform_count == 1:
            print("   ✓ SUCCESS: Platform account was reused!")
        else:
            print("   ✗ FAILURE: Platform account was not properly reused!")
        
        # Summary
        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)
        
        # Get total account count
        total_accounts = session.execute("SELECT COUNT(*) FROM accounts").scalar()
        print(f"Total accounts in database: {total_accounts}")
        
        # Show account breakdown
        print("\nAccount breakdown by owner:")
        results = session.execute("""
            SELECT owner_type, owner_id, account_type, COUNT(*) as count
            FROM accounts
            GROUP BY owner_type, owner_id, account_type
            ORDER BY owner_type, owner_id, account_type
        """).fetchall()
        
        for row in results:
            print(f"  {row[0]:10} | {row[1]:20} | {row[2]:10} | Count: {row[3]}")
        
        # Check for duplicates
        duplicates = session.execute("""
            SELECT owner_type, owner_id, account_type, COUNT(*) as count
            FROM accounts
            GROUP BY owner_type, owner_id, account_type
            HAVING COUNT(*) > 1
        """).fetchall()
        
        if duplicates:
            print("\n⚠ WARNING: Found duplicate accounts:")
            for row in duplicates:
                print(f"  {row[0]} | {row[1]} | {row[2]} | Count: {row[3]}")
        else:
            print("\n✓ No duplicate accounts found!")
        
        session.rollback()  # Don't commit test data
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_account_reuse()
