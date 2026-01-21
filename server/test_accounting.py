import pytest
from decimal import Decimal
from app.domain.accounting.entities import JournalLine
from app.domain.accounting.policies import AccountingPolicy


def test_journal_entry_balanced():
    lines = [
        JournalLine(account_id="1", debit_amount=Decimal(100), credit_amount=Decimal(0)),
        JournalLine(account_id="2", debit_amount=Decimal(0), credit_amount=Decimal(100))
    ]
    # Should not raise
    AccountingPolicy.validate_journal_entry(lines)


def test_journal_entry_unbalanced():
    lines = [
        JournalLine(account_id="1", debit_amount=Decimal(100), credit_amount=Decimal(0)),
        JournalLine(account_id="2", debit_amount=Decimal(0), credit_amount=Decimal(50))
    ]
    with pytest.raises(ValueError, match="not balanced"):
        AccountingPolicy.validate_journal_entry(lines)


def test_journal_entry_both_amounts():
    lines = [
        JournalLine(account_id="1", debit_amount=Decimal(100), credit_amount=Decimal(50)),
        JournalLine(account_id="2", debit_amount=Decimal(0), credit_amount=Decimal(50))
    ]
    with pytest.raises(ValueError, match="cannot have both"):
        AccountingPolicy.validate_journal_entry(lines)


def test_journal_entry_zero_amounts():
    lines = [
        JournalLine(account_id="1", debit_amount=Decimal(0), credit_amount=Decimal(0)),
        JournalLine(account_id="2", debit_amount=Decimal(0), credit_amount=Decimal(100))
    ]
    with pytest.raises(ValueError, match="must have either"):
        AccountingPolicy.validate_journal_entry(lines)