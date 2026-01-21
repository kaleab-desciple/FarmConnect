from decimal import Decimal
from app.domain.ledger.entities import LedgerEvent, LedgerEventType, AggregateType
from app.domain.accounting.entities import ReferenceType, JournalLine
from app.infrastructure.repositories.account_repo import AccountRepository
from app.domain.accounting.entities import AccountType, OwnerType
from uuid import UUID
from app.application.accounting.create_account import CreateAccount


class CreateAccountRequest:
    def __init__(self, owner_type: OwnerType, owner_id: str, account_type: AccountType, name: str, currency: str):
        self.owner_type = owner_type
        self.owner_id = owner_id
        self.account_type = account_type
        self.name = name
        self.currency = currency


class LedgerToJournalMapper:
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo
        self.create_account_uc = CreateAccount(account_repo)

    def map_event_to_journal_lines(self, event: LedgerEvent) -> list[dict]:
        """Map a ledger event to journal lines (double-entry)."""
        amount = Decimal(str(event.amount))

        if event.event_type == LedgerEventType.ESCROW_FUNDED:
            # Debit: Merchant Cash (ASSET)
            # Credit: Escrow Holding (LIABILITY)
            merchant_cash_id = self._get_or_create_account(
                OwnerType.USER, event.aggregate_id, AccountType.ASSET, "Merchant Cash"
            )
            escrow_holding_id = self._get_or_create_account(
                OwnerType.ESCROW, event.reference_id, AccountType.LIABILITY, "Escrow Holding"
            )
            return [
                {"account_id": str(merchant_cash_id), "debit_amount": str(amount), "credit_amount": "0"},
                {"account_id": str(escrow_holding_id), "debit_amount": "0", "credit_amount": str(amount)}
            ]

        elif event.event_type == LedgerEventType.ESCROW_RELEASED:
            # Debit: Escrow Holding (LIABILITY)
            # Credit: Farmer Payable (LIABILITY)
            escrow_holding_id = self._get_or_create_account(
                OwnerType.ESCROW, event.reference_id, AccountType.LIABILITY, "Escrow Holding"
            )
            farmer_payable_id = self._get_or_create_account(
                OwnerType.USER, event.aggregate_id, AccountType.LIABILITY, "Farmer Payable"
            )
            return [
                {"account_id": str(escrow_holding_id), "debit_amount": str(amount), "credit_amount": "0"},
                {"account_id": str(farmer_payable_id), "debit_amount": "0", "credit_amount": str(amount)}
            ]

        elif event.event_type == LedgerEventType.PLATFORM_FEE_COLLECTED:
            # Debit: Escrow Holding (LIABILITY)
            # Credit: Platform Revenue (REVENUE)
            escrow_holding_id = self._get_or_create_account(
                OwnerType.ESCROW, event.reference_id, AccountType.LIABILITY, "Escrow Holding"
            )
            platform_revenue_id = self._get_or_create_account(
                OwnerType.SYSTEM, "platform", AccountType.REVENUE, "Platform Revenue"
            )
            return [
                {"account_id": str(escrow_holding_id), "debit_amount": str(amount), "credit_amount": "0"},
                {"account_id": str(platform_revenue_id), "debit_amount": "0", "credit_amount": str(amount)}
            ]

        elif event.event_type == LedgerEventType.ESCROW_REFUNDED:
            # Debit: Escrow Holding (LIABILITY)
            # Credit: Merchant Cash (ASSET)
            escrow_holding_id = self._get_or_create_account(
                OwnerType.ESCROW, event.reference_id, AccountType.LIABILITY, "Escrow Holding"
            )
            merchant_cash_id = self._get_or_create_account(
                OwnerType.USER, event.aggregate_id, AccountType.ASSET, "Merchant Cash"
            )
            return [
                {"account_id": str(escrow_holding_id), "debit_amount": str(amount), "credit_amount": "0"},
                {"account_id": str(merchant_cash_id), "debit_amount": "0", "credit_amount": str(amount)}
            ]

        # Add more mappings for other event types as needed
        return []

    def _get_or_create_account(self, owner_type: OwnerType, owner_id: str, account_type: AccountType, name: str) -> UUID:
        """Get existing account or create if not exists."""
        # For now, create a deterministic name for lookup
        # In practice, you might have predefined accounts or a better way to identify them
        account_name = f"{owner_type.value}_{owner_id}_{account_type.value}_{name.replace(' ', '_')}"
        # Try to find existing account - but since we don't have a way to query by name, we'll create new ones
        # This is a simplification; in real implementation, you'd have a way to find accounts by criteria
        request = CreateAccountRequest(owner_type, owner_id, account_type, account_name, "ETB")
        account = self.create_account_uc.execute(request)
        return account.id