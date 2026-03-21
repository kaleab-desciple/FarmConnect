from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_permission, get_enriched_user
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from app.application.accounting.get_trial_balance import GetTrialBalance, TrialBalance
from app.application.accounting.get_account_balance import GetAccountBalance, GetAccountBalanceRequest
from app.application.accounting.get_user_balance import GetUserBalance, GetUserBalanceRequest
from app.application.accounting.get_escrow_balance import GetEscrowBalance, GetEscrowBalanceRequest
from app.application.accounting.get_user_statement import GetUserStatement, GetUserStatementRequest
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional

# Use the same tag casing as `api_router.include_router(..., tags=["Accounting"])`
# so the OpenAPI UI groups endpoints under a single, consistent heading.
router = APIRouter(tags=["Accounting"])

@router.get("/trial-balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_trial_balance(db: Session = Depends(get_db)):
    """
    Get accounting trial balance.
    
    Retrieves the trial balance showing total assets, liabilities, and equity
    across all accounts in the system. Used for verifying accounting accuracy
    and ensuring the fundamental accounting equation (Assets = Liabilities + Equity).
    
    ## Authentication & Authorization
    Requires `ledger:read` permission. Typically restricted to:
    - Financial administrators
    - Accounting managers
    - System auditors
    
    ## Response Format
    ```json
    {
      "assets": 125000.50,
      "liabilities": 45000.25,
      "equity": 80000.25
    }
    ```
    
    ## Double-Entry Verification
    The accounting equation should always balance:
    - Assets = Liabilities + Equity
    - If this doesn't balance, there's an accounting error
    
    ## Responses
    - **200**: Trial balance retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing ledger:read permission)
    - **500**: Internal server error
    """
    journal_repo = JournalRepository(db)
    use_case = GetTrialBalance(journal_repo)
    balance = use_case.execute()
    return {
        "assets": float(balance.assets),
        "liabilities": float(balance.liabilities),
        "equity": float(balance.equity)
    }


@router.get("/accounts", response_model=list, dependencies=[Depends(require_permission("ledger:read"))])
def get_accounts(db: Session = Depends(get_db)):
    """
    List all accounts in the system.
    
    Retrieves all accounting ledger accounts including user cash accounts,
    payable accounts, and escrow holding accounts. Each account represents
    a book in the double-entry accounting system.
    
    ## Authentication & Authorization
    Requires `ledger:read` permission.
    
    ## Account Types
    - **CASH**: User cash/wallet accounts (asset)
    - **PAYABLE**: Amounts owed by users (liability)
    - **ESCROW_HOLDING**: Escrow fund holding (liability)
    - **REVENUE**: Platform revenue (equity)
    
    ## Owner Types
    - **USER**: Individual user account
    - **ESCROW**: Order escrow account
    - **PLATFORM**: System/platform account
    
    ## Response Format
    Returns array of account objects:
    ```json
    [
      {
        "id": "account_uuid",
        "owner_type": "USER",
        "owner_id": "user_uuid",
        "account_type": "CASH",
        "name": "User Cash Account",
        "currency": "USD",
        "created_at": "2024-01-15T10:00:00Z"
      }
    ]
    ```
    
    ## Responses
    - **200**: Accounts retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing ledger:read permission)
    - **500**: Internal server error
    """
    from app.infrastructure.db.models.account import AccountORM
    accounts = db.query(AccountORM).all()
    return [
        {
            "id": account.id,
            "owner_type": account.owner_type.value,
            "owner_id": account.owner_id,
            "account_type": account.account_type.value,
            "name": account.name,
            "currency": account.currency,
            "created_at": account.created_at.isoformat()
        }
        for account in accounts
    ]


@router.get("/accounts/{account_id}/balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_account_balance(account_id: str, db: Session = Depends(get_db)):
    """
    Get the current balance for a specific account.
    
    Calculates the account balance by summing all debits and credits
    in the journal entries for this account.
    
    ## Path Parameters
    - **account_id**: UUID of the account to query (required)
    
    ## Authentication & Authorization
    Requires `ledger:read` permission.
    
    ## Balance Calculation
    Balance is calculated based on account type:
    - **Asset accounts (CASH)**: Debits increase, Credits decrease
    - **Liability accounts (PAYABLE, ESCROW)**: Credits increase, Debits decrease
    - **Equity accounts (REVENUE)**: Credits increase, Debits decrease
    
    ## Response Format
    ```json
    {
      "balance": 1250.75
    }
    ```
    
    ## Responses
    - **200**: Balance retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing ledger:read permission)
    - **404**: Account not found
    - **500**: Internal server error
    """
    journal_repo = JournalRepository(db)
    use_case = GetAccountBalance(journal_repo)
    request = GetAccountBalanceRequest(account_id)
    balance = use_case.execute(request)
    return {"balance": float(balance)}


@router.get("/journal/{reference_type}/{reference_id}", response_model=list, dependencies=[Depends(require_permission("ledger:read"))])
def get_journal_entries(reference_type: str, reference_id: str, db: Session = Depends(get_db)):
    """
    Get journal entries for a specific business transaction.
    
    Retrieves all double-entry journal entries associated with a specific
    business transaction (order, payment, refund, etc.). Each entry contains
    balanced debits and credits across multiple accounts.
    
    ## Path Parameters
    - **reference_type**: Type of business transaction (required)
      - Examples: "ORDER", "PAYMENT", "REFUND", "ESCROW"
    - **reference_id**: UUID of the specific transaction (required)
    
    ## Authentication & Authorization
    Requires `ledger:read` permission.
    
    ## Double-Entry Bookkeeping
    Each journal entry contains multiple lines where:
    - Total debits = Total credits (always balanced)
    - Minimum 2 lines per entry (one debit, one credit)
    - Records the complete financial impact of a transaction
    
    ## Response Format
    ```json
    [
      {
        "id": "entry_uuid",
        "reference_type": "ORDER",
        "reference_id": "order_uuid",
        "description": "Order payment received",
        "created_at": "2024-01-15T10:00:00Z",
        "lines": [
          {
            "account_id": "cash_account_uuid",
            "debit_amount": 100.00,
            "credit_amount": 0.00
          },
          {
            "account_id": "revenue_account_uuid",
            "debit_amount": 0.00,
            "credit_amount": 100.00
          }
        ]
      }
    ]
    ```
    
    ## Responses
    - **200**: Journal entries retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing ledger:read permission)
    - **500**: Internal server error
    """
    journal_repo = JournalRepository(db)
    # Query journal entries by reference
    # For now, return a simple list - in production you'd implement proper repository method
    from app.infrastructure.db.models.journal_entry import JournalEntryORM, JournalLineORM
    from sqlalchemy.orm import joinedload

    entries = db.query(JournalEntryORM).options(joinedload(JournalEntryORM.lines)).filter(
        JournalEntryORM.reference_type == reference_type,
        JournalEntryORM.reference_id == reference_id
    ).all()

    result = []
    for entry in entries:
        result.append({
            "id": entry.id,
            "reference_type": entry.reference_type,
            "reference_id": entry.reference_id,
            "description": entry.description,
            "created_at": entry.created_at.isoformat(),
            "lines": [
                {
                    "account_id": line.account_id,
                    "debit_amount": float(line.debit_amount),
                    "credit_amount": float(line.credit_amount)
                }
                for line in entry.lines
            ]
        })
    return result


@router.get("/users/{user_id}/balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_user_balance(user_id: str, db: Session = Depends(get_db)):
    """
    Get consolidated balance for a user across all their accounts.
    
    Calculates the user's financial position by combining their cash account
    (assets) and payable account (liabilities) to determine net balance.
    
    ## Path Parameters
    - **user_id**: UUID of the user (required)
    
    ## Authentication & Authorization
    Requires `ledger:read` permission.
    
    ## Balance Components
    - **cash_balance**: Money available in user's wallet (asset)
    - **payable_balance**: Money owed by user (liability)
    - **net_balance**: cash_balance - payable_balance
    
    ## Response Format
    ```json
    {
      "user_id": "user_uuid",
      "cash_balance": 1500.00,
      "payable_balance": 200.00,
      "net_balance": 1300.00
    }
    ```
    
    ## Use Cases
    - Display user's wallet balance
    - Verify user has sufficient funds for purchase
    - Generate financial reports
    - Audit user account status
    
    ## Responses
    - **200**: User balance retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing ledger:read permission)
    - **404**: User not found or no accounts exist
    - **500**: Internal server error
    """
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    use_case = GetUserBalance(account_repo, journal_repo)
    request = GetUserBalanceRequest(user_id)
    
    try:
        balance = use_case.execute(request)
        return {
            "user_id": balance.user_id,
            "cash_balance": float(balance.cash_balance),
            "payable_balance": float(balance.payable_balance),
            "net_balance": float(balance.net_balance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/escrows/{escrow_id}/balance", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_escrow_balance(escrow_id: str, db: Session = Depends(get_db)):
    """
    Get balance for a specific escrow account.
    
    Retrieves the current funds held in escrow for an order. Escrow accounts
    hold buyer payments until order delivery is confirmed.
    
    ## Path Parameters
    - **escrow_id**: UUID of the escrow (typically same as order ID) (required)
    
    ## Authentication & Authorization
    Requires `ledger:read` permission.
    
    ## Escrow Account Purpose
    Escrow accounts temporarily hold order payments to protect both parties:
    - **Buyer protection**: Funds held until delivery confirmed
    - **Seller assurance**: Payment guaranteed once delivery verified
    - **Platform mediation**: Enables dispute resolution
    
    ## Response Format
    ```json
    {
      "escrow_id": "order_uuid",
      "holding_balance": 250.00
    }
    ```
    
    ## Balance States
    - **Positive balance**: Funds held, order in progress
    - **Zero balance**: Funds released (completed or refunded)
    
    ## Responses
    - **200**: Escrow balance retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing ledger:read permission)
    - **404**: Escrow not found
    - **500**: Internal server error
    """
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    use_case = GetEscrowBalance(account_repo, journal_repo)
    request = GetEscrowBalanceRequest(escrow_id)
    
    try:
        balance = use_case.execute(request)
        return {
            "escrow_id": balance.escrow_id,
            "holding_balance": float(balance.holding_balance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/statement", response_model=dict, dependencies=[Depends(require_permission("ledger:read"))])
def get_user_statement(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date in ISO format (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get detailed transaction statement for a user.
    
    Generates a comprehensive financial statement showing all transactions
    for a user's accounts within a specified date range, similar to a bank
    statement with running balance.
    
    ## Path Parameters
    - **user_id**: UUID of the user (required)
    
    ## Query Parameters
    - **start_date**: Statement start date in ISO format YYYY-MM-DD (optional)
      - If omitted: starts from account creation
    - **end_date**: Statement end date in ISO format YYYY-MM-DD (optional)
      - If omitted: includes all transactions up to now
    
    ## Authentication & Authorization
    Requires `ledger:read` permission.
    
    ## Response Format
    ```json
    {
      "user_id": "user_uuid",
      "opening_balance": 1000.00,
      "closing_balance": 1450.75,
      "lines": [
        {
          "date": "2024-01-15T10:00:00Z",
          "description": "Order payment",
          "debit": 0.00,
          "credit": 50.00,
          "balance": 950.00
        },
        {
          "date": "2024-01-16T14:30:00Z",
          "description": "Product sale",
          "debit": 500.75,
          "credit": 0.00,
          "balance": 1450.75
        }
      ]
    }
    ```
    
    ## Statement Components
    - **opening_balance**: Balance at start of period
    - **closing_balance**: Balance at end of period
    - **lines**: Chronological transactions with running balance
    
    ## Use Cases
    - User account statements
    - Financial audits
    - Reconciliation
    - Transaction history export
    
    ## Responses
    - **200**: Statement generated successfully
    - **400**: Invalid date format
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing ledger:read permission)
    - **404**: User not found
    - **500**: Internal server error
    """
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    use_case = GetUserStatement(account_repo, journal_repo)
    
    # Parse dates if provided - make them timezone-aware (UTC) to match database timestamps
    start_dt = None
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
    
    end_dt = None
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        if end_dt.tzinfo is None:
            # Set to end of day for inclusive date range
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            
    request = GetUserStatementRequest(user_id, start_dt, end_dt)
    
    try:
        statement = use_case.execute(request)
        return {
            "user_id": statement.user_id,
            "opening_balance": float(statement.opening_balance),
            "closing_balance": float(statement.closing_balance),
            "lines": [
                {
                    "date": line.date.isoformat(),
                    "description": line.description,
                    "debit": float(line.debit),
                    "credit": float(line.credit),
                    "balance": float(line.balance)
                }
                for line in statement.lines
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/farmer/earnings", response_model=dict)
def get_farmer_earnings(
    farmer_id: Optional[str] = Query(None, description="Filter by farmer ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_enriched_user)
):
    """
    Get farmer earnings summary.
    
    Returns earnings data for a farmer including:
    - Total earnings from completed orders
    - Pending payments
    - Recent transactions
    
    ## Authentication & Authorization
    Requires `ledger:read` permission.
    
    ## Query Parameters
    - **farmer_id**: Filter by farmer UUID (optional, defaults to current user)
    
    ## Response Format
    ```json
    {
      "total_earnings": 1500.00,
      "pending_payments": 250.00,
      "completed_payments": 1250.00,
      "recent_transactions": [
        {
          "date": "2024-01-15T10:00:00Z",
          "amount": 500.00,
          "description": "Order #12345 - Tomatoes"
        }
      ]
    }
    ```
    """
    from app.infrastructure.repositories.user_repo import UserRepository
    from app.infrastructure.repositories.account_repo import AccountRepository
    from app.infrastructure.repositories.journal_repo import JournalRepository
    from app.domain.accounting.entities import OwnerType, AccountType
    from sqlalchemy import func
    
    # Get internal user ID if farmer_id not specified
    internal_farmer_id = farmer_id
    if not internal_farmer_id:
        internal_farmer_id = current_user.system_user_id
    
    # Get user's cash account
    account_repo = AccountRepository(db)
    journal_repo = JournalRepository(db)
    
    # Find farmer's CASH account
    from app.infrastructure.db.models.account import AccountORM
    cash_account = db.query(AccountORM).filter(
        AccountORM.owner_type == OwnerType.USER.value,
        AccountORM.owner_id == internal_farmer_id,
        AccountORM.account_type == AccountType.ASSET.value,
     #   AccountORM.deleted_at.is_(None)
    ).first()
    
    earnings_data = {
        "total_earnings": 0.0,
        "pending_payments": 0.0,
        "completed_payments": 0.0,
        "recent_transactions": []
    }
    
    if cash_account:
        # Get journal entries for this account
        from app.infrastructure.db.models.journal_entry import JournalEntryORM, JournalLineORM
        
        # Get all credit entries (money received) - these are earnings
        credit_lines = db.query(JournalLineORM).join(
            JournalEntryORM, JournalLineORM.journal_entry == JournalEntryORM.id
        ).filter(
            JournalLineORM.account_id == cash_account.id,
            JournalLineORM.credit_amount > 0
        ).order_by(JournalEntryORM.created_at.desc()).limit(10).all()
        
        total_earnings = 0.0
        recent_transactions = []
        
        for line in credit_lines:
            entry = db.query(JournalEntryORM).filter(JournalEntryORM.id == line.entry_id).first()
            if entry:
                amount = float(line.credit_amount) if line.credit_amount else 0.0
                total_earnings += amount
                recent_transactions.append({
                    "date": entry.created_at.isoformat() if entry.created_at else "",
                    "amount": amount,
                    "description": entry.description or "Transaction"
                })
        
        earnings_data["total_earnings"] = total_earnings
        earnings_data["completed_payments"] = total_earnings
        earnings_data["recent_transactions"] = recent_transactions
    
    return earnings_data