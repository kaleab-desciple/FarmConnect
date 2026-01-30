"""
Domain service for escrow state transitions.

This service validates state transitions and returns accounting instructions
without side effects.
"""

from typing import List, Dict, Any
from decimal import Decimal
from ..entities import Escrow, EscrowState
from ..exceptions import InvalidEscrowTransitionError


class AccountingInstruction:
    """Represents an accounting entry instruction."""
    def __init__(self, account_type: str, account_owner: str, debit: Decimal = Decimal(0), credit: Decimal = Decimal(0)):
        self.account_type = account_type
        self.account_owner = account_owner
        self.debit = debit
        self.credit = credit


class EscrowTransitionResult:
    """Result of a valid escrow state transition."""
    def __init__(self, new_state: EscrowState, accounting_instructions: List[AccountingInstruction]):
        self.new_state = new_state
        self.accounting_instructions = accounting_instructions


class EscrowDomainService:
    """
    Domain service handling escrow state transitions.

    Validates transitions and provides accounting instructions.
    """

    @staticmethod
    def fund_escrow(escrow: Escrow, merchant_id: str, provider_reference: str) -> EscrowTransitionResult:
        """
        Validate and prepare funding transition.

        CREATED → FUNDED
        """
        if escrow.state != EscrowState.CREATED:
            raise InvalidEscrowTransitionError(
                f"Cannot fund escrow in state {escrow.state}, must be CREATED"
            )

        # Accounting: Customer payment obligation
        # Debit: Customer Receivable (Asset) - they owe us money
        # Credit: Escrow Liability - we hold it in escrow
        instructions = [
            AccountingInstruction(
                account_type="ASSET",
                account_owner=f"USER_{merchant_id}_ASSET_Merchant_Cash",
                debit=escrow.amount
            ),
            AccountingInstruction(
                account_type="LIABILITY",
                account_owner=f"ESCROW_{escrow.id}_LIABILITY_Escrow_Holding",
                credit=escrow.amount
            )
        ]

        return EscrowTransitionResult(EscrowState.FUNDED, instructions)

    @staticmethod
    def release_escrow(escrow: Escrow, farmer_id: str, provider_reference: str) -> EscrowTransitionResult:
        """
        Validate and prepare release transition.

        FUNDED → RELEASED
        """
        if escrow.state != EscrowState.FUNDED:
            raise InvalidEscrowTransitionError(
                f"Cannot release escrow in state {escrow.state}, must be FUNDED"
            )

        # Calculate platform fee (assuming 5% for now, ideally passed in or from configuration)
        # Note: in a real system, the fee might be stored on the escrow or order entity from creation
        fee_percent = Decimal('0.05')
        platform_fee = (escrow.amount * fee_percent).quantize(Decimal('0.01'))
        farmer_amount = escrow.amount - platform_fee

        # Accounting: Release to farmer and platform fee
        # Debit: Escrow Holding (Full Amount)
        # Credit: Farmer Payable (Amount - Fee)
        # Credit: Platform Revenue (Fee)
        instructions = [
            AccountingInstruction(
                account_type="LIABILITY",
                account_owner=f"ESCROW_{escrow.id}_LIABILITY_Escrow_Holding",
                debit=escrow.amount
            ),
            AccountingInstruction(
                account_type="LIABILITY",
                account_owner=f"USER_{farmer_id}_LIABILITY_Farmer_Payable",
                credit=farmer_amount
            ),
            AccountingInstruction(
                account_type="REVENUE",
                account_owner="SYSTEM_platform_REVENUE_Platform_Revenue",
                credit=platform_fee
            )
        ]

        return EscrowTransitionResult(EscrowState.RELEASED, instructions)

    @staticmethod
    def refund_escrow(escrow: Escrow, merchant_id: str, provider_reference: str) -> EscrowTransitionResult:
        """
        Validate and prepare refund transition.

        FUNDED → REFUNDED
        """
        if escrow.state != EscrowState.FUNDED:
            raise InvalidEscrowTransitionError(
                f"Cannot refund escrow in state {escrow.state}, must be FUNDED"
            )

        # Accounting: Refund to customer
        # Debit: Escrow Liability (reduce liability)
        # Credit: Customer Refund Payable (increase payable)
        instructions = [
            AccountingInstruction(
                account_type="LIABILITY",
                account_owner=f"ESCROW_{escrow.id}_LIABILITY_Escrow_Holding",
                debit=escrow.amount
            ),
            AccountingInstruction(
                account_type="LIABILITY",
                account_owner=f"USER_{merchant_id}_LIABILITY_Customer_Refund",
                credit=escrow.amount
            )
        ]

        return EscrowTransitionResult(EscrowState.REFUNDED, instructions)
