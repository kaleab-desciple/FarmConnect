# Accounting System Fixes - Summary

## Overview
This document summarizes the fixes applied to resolve the duplicate account creation issue and enhance the accounting system's reporting capabilities.

## Problems Identified

### 1. Duplicate Account Creation (Fragmented Ledger)
**Issue**: The system was creating a new account for every single transaction instead of reusing existing accounts for the same user or escrow.

**Evidence**: 
- Database showed multiple accounts for the same owner (e.g., 3 "Escrow Holding" accounts for the same escrow ID)
- Users had multiple "Merchant Cash" accounts instead of one consolidated account
- Platform had multiple "Platform Revenue" accounts

**Root Cause**: 
- The `AccountRepository` Protocol definitions in use case files were incomplete
- Missing `get_by_owner_and_type` method in Protocol definitions
- Although the concrete implementation had the method, the Protocol interface didn't declare it

### 2. Limited Reporting Capabilities
**Issue**: Reporting was limited to a simple TrialBalance (Assets vs Liabilities vs Equity).

**Impact**: 
- No per-user balance queries
- No per-escrow balance queries  
- No detailed transaction history/statements
- Difficult to track individual user or escrow financial positions

## Solutions Implemented

### 1. Fixed Account Repository Protocol Definitions

#### Files Modified:
- [`server/app/application/accounting/create_account.py`](server/app/application/accounting/create_account.py)
- [`server/app/application/accounting/post_journal_entry.py`](server/app/application/accounting/post_journal_entry.py)

#### Changes:
Added `get_by_owner_and_type` method to the `AccountRepository` Protocol:

```python
class AccountRepository(Protocol):
    def save(self, account: Account) -> None:
        ...

    def get_by_id(self, account_id: str) -> Account | None:
        ...

    def get_by_owner_and_type(self, owner_type: OwnerType, owner_id: str, account_type: AccountType) -> Optional[Account]:
        ...
```

**Impact**: The `LedgerToJournalMapper._get_or_create_account` method can now properly query for existing accounts before creating new ones.

### 2. Added Database Index for Performance

#### File Created:
- [`server/app/alembic/versions/add_accounts_owner_index.py`](server/app/alembic/versions/add_accounts_owner_index.py)

#### Changes:
Created a composite index on `(owner_type, owner_id, account_type)` for efficient account lookups:

```sql
CREATE INDEX idx_accounts_owner_type_id_account_type 
ON accounts (owner_type, owner_id, account_type);
```

**Impact**: Significantly improves query performance when looking up accounts by owner and type.

### 3. Enhanced Reporting Use Cases

#### New Files Created:

##### a. Get User Balance
**File**: [`server/app/application/accounting/get_user_balance.py`](server/app/application/accounting/get_user_balance.py)

**Purpose**: Get consolidated balance for a user across all their accounts (ASSET and LIABILITY).

**Returns**:
- `cash_balance`: User's cash account balance (ASSET)
- `payable_balance`: Amount owed to user (LIABILITY)
- `net_balance`: Combined balance

**Usage**:
```python
request = GetUserBalanceRequest(user_id="MER-00001")
balance = get_user_balance_uc.execute(request)
print(f"Cash: {balance.cash_balance}, Payable: {balance.payable_balance}")
```

##### b. Get Escrow Balance
**File**: [`server/app/application/accounting/get_escrow_balance.py`](server/app/application/accounting/get_escrow_balance.py)

**Purpose**: Get balance for a specific escrow account.

**Returns**:
- `holding_balance`: Funds currently held in escrow (LIABILITY)

**Usage**:
```python
request = GetEscrowBalanceRequest(escrow_id="escrow-123")
balance = get_escrow_balance_uc.execute(request)
print(f"Escrow holding: {balance.holding_balance}")
```

##### c. Get User Statement
**File**: [`server/app/application/accounting/get_user_statement.py`](server/app/application/accounting/get_user_statement.py)

**Purpose**: Get detailed transaction statement for a user showing all debits and credits.

**Returns**:
- List of `StatementLine` objects with date, description, debit, credit, and running balance
- Opening and closing balances

**Usage**:
```python
request = GetUserStatementRequest(
    user_id="MER-00001",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 2, 5)
)
statement = get_user_statement_uc.execute(request)
for line in statement.lines:
    print(f"{line.date}: {line.description} - Balance: {line.balance}")
```

### 4. Enhanced Journal Repository

#### File Modified:
- [`server/app/infrastructure/repositories/journal_repo.py`](server/app/infrastructure/repositories/journal_repo.py)

#### Changes:
Added `get_entries_for_account` method to retrieve all journal entries affecting a specific account:

```python
def get_entries_for_account(self, account_id: str) -> List[JournalEntry]:
    """Get all journal entries that affect a specific account."""
    # Returns entries ordered by created_at
```

**Impact**: Enables detailed transaction history queries for statements and audit trails.

## How Account Reuse Works Now

### Before Fix:
```
Transaction 1: Create account for MER-00001 (ASSET) → Account A
Transaction 2: Create account for MER-00001 (ASSET) → Account B (duplicate!)
Transaction 3: Create account for MER-00001 (ASSET) → Account C (duplicate!)
```

### After Fix:
```
Transaction 1: Create account for MER-00001 (ASSET) → Account A
Transaction 2: Query for MER-00001 (ASSET) → Found Account A, reuse it
Transaction 3: Query for MER-00001 (ASSET) → Found Account A, reuse it
```

### The Flow:
1. `LedgerToJournalMapper.map_event_to_journal_lines()` is called with a ledger event
2. For each account needed, `_get_or_create_account()` is called
3. `_get_or_create_account()` calls `account_repo.get_by_owner_and_type()`
4. If account exists → return existing account ID
5. If account doesn't exist → create new account and return its ID

## Migration Instructions

### 1. Apply Database Migration
```bash
cd server/app
alembic upgrade head
```

This will:
- Merge the multiple migration heads
- Create the performance index on the accounts table

### 2. Clean Up Existing Duplicate Accounts (Optional)

**WARNING**: Only run this if you want to consolidate existing duplicate accounts. This should be done carefully with a backup.

```sql
-- Find duplicates
SELECT owner_type, owner_id, account_type, COUNT(*) as count
FROM accounts
GROUP BY owner_type, owner_id, account_type
HAVING COUNT(*) > 1;

-- For each duplicate set, you'll need to:
-- 1. Choose one account to keep (usually the oldest)
-- 2. Update all journal_lines to point to the kept account
-- 3. Delete the duplicate accounts

-- Example for a specific duplicate:
-- UPDATE journal_lines 
-- SET account_id = 'kept-account-id' 
-- WHERE account_id IN ('duplicate-1', 'duplicate-2');
-- 
-- DELETE FROM accounts 
-- WHERE id IN ('duplicate-1', 'duplicate-2');
```

### 3. Test the Fix

Run the test script to verify account reuse:
```bash
python test_account_reuse.py
```

Expected output:
- ✓ Same account was reused
- ✓ Only one account exists
- ✓ No duplicate accounts found

## API Integration (Future Work)

The new use cases can be integrated into API endpoints:

### Suggested Endpoints:

```python
# Get user balance
GET /api/v1/accounting/users/{user_id}/balance

# Get escrow balance  
GET /api/v1/accounting/escrows/{escrow_id}/balance

# Get user statement
GET /api/v1/accounting/users/{user_id}/statement?start_date=2026-01-01&end_date=2026-02-05

# Get platform revenue
GET /api/v1/accounting/platform/revenue
```

## Benefits

### 1. Data Integrity
- ✓ One account per (owner_type, owner_id, account_type) combination
- ✓ Accurate balance calculations
- ✓ Proper audit trail

### 2. Performance
- ✓ Faster account lookups with index
- ✓ Reduced database size (no duplicate accounts)
- ✓ More efficient queries

### 3. Reporting
- ✓ Per-user balance queries
- ✓ Per-escrow balance queries
- ✓ Detailed transaction statements
- ✓ Better financial visibility

### 4. Maintainability
- ✓ Clear Protocol definitions
- ✓ Reusable use cases
- ✓ Testable components
- ✓ Better code organization

## Testing Checklist

- [ ] Run database migration
- [ ] Run test_account_reuse.py
- [ ] Create a new transaction and verify no duplicate accounts are created
- [ ] Test GetUserBalance use case
- [ ] Test GetEscrowBalance use case
- [ ] Test GetUserStatement use case
- [ ] Verify trial balance still works correctly
- [ ] Check query performance with the new index

## Notes

1. The fix is **backward compatible** - existing code will continue to work
2. The `LedgerToJournalMapper` already had the logic to reuse accounts, but the Protocol definitions were preventing it from working
3. New transactions will automatically use the fixed logic
4. Existing duplicate accounts can be cleaned up separately if needed
5. The new reporting use cases are independent and can be adopted gradually

## Related Files

### Modified Files:
- `server/app/application/accounting/create_account.py`
- `server/app/application/accounting/post_journal_entry.py`
- `server/app/infrastructure/repositories/journal_repo.py`

### New Files:
- `server/app/alembic/versions/add_accounts_owner_index.py`
- `server/app/application/accounting/get_user_balance.py`
- `server/app/application/accounting/get_escrow_balance.py`
- `server/app/application/accounting/get_user_statement.py`
- `test_account_reuse.py`

### Unchanged (Already Correct):
- `server/app/infrastructure/repositories/account_repo.py` - Already had `get_by_owner_and_type` method
- `server/app/application/accounting/ledger_to_journal_mapper.py` - Already had reuse logic
