from decimal import Decimal
from typing import List
from .entities import JournalLine, Account


class AccountingPolicy:
    @staticmethod
    def validate_journal_entry(lines: List[JournalLine]) -> None:
        """Validate that journal entry is balanced and follows rules."""
        total_debit = Decimal(0)
        total_credit = Decimal(0)

        for line in lines:
            if line.debit_amount < 0 or line.credit_amount < 0:
                raise ValueError("Amounts cannot be negative")

            if line.debit_amount > 0 and line.credit_amount > 0:
                raise ValueError("Line cannot have both debit and credit amounts")

            if line.debit_amount == 0 and line.credit_amount == 0:
                raise ValueError("Line must have either debit or credit amount")

            total_debit += line.debit_amount
            total_credit += line.credit_amount

        if total_debit != total_credit:
            raise ValueError(f"Journal entry not balanced: debits={total_debit}, credits={total_credit}")

    @staticmethod
    def validate_account_combination(debit_account: Account, credit_account: Account) -> None:
        """Validate that account combination is valid for double-entry."""
        # For now, allow all combinations, but can add business rules later
        pass

    @staticmethod
    def validate_currency_match(accounts: List[Account], currency: str) -> None:
        """Ensure all accounts have the same currency."""
        for account in accounts:
            if account.currency != currency:
                raise ValueError(f"Currency mismatch: expected {currency}, got {account.currency}")