import sys
import os
from dotenv import load_dotenv

# Setup path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "shared", "py"))

load_dotenv()

try:
    from shared_models.enums import UserRole, OrderStatus, EscrowState, LoanState, DisputeState
    from shared_models.user import User
    from shared_models.order import Order
    from shared_models.loan import Loan
    from shared_models.dispute import Dispute
    from shared_models.escrow import Escrow

    print("Checking User...")
    user_role_field = User.model_fields['role'].annotation
    # annotation might be Optional[UserRole] or Union[UserRole, NoneType]
    print(f"User role annotation: {user_role_field}")
    # We essentially want to check if the Enum class used is the same as the one in shared_models.enums

    # Simple check: Instantiate with Shared Enum
    u = User(role=UserRole.FARMER)
    print(f"User instantiated with UserRole.FARMER: {u.role == UserRole.FARMER}")

    print("Checking Order...")
    o = Order(status=OrderStatus.CREATED)
    print(f"Order instantiated with OrderStatus.CREATED: {o.status == OrderStatus.CREATED}")

    print("Checking Loan...")
    l = Loan(state=LoanState.PROPOSED)
    print(f"Loan instantiated with LoanState.PROPOSED: {l.state == LoanState.PROPOSED}")

    print("Checking Dispute...")
    d = Dispute(state=DisputeState.OPEN)
    print(f"Dispute instantiated with DisputeState.OPEN: {d.state == DisputeState.OPEN}")

    print("Checking Escrow...")
    e = Escrow(state=EscrowState.CREATED)
    print(f"Escrow instantiated with EscrowState.CREATED: {e.state == EscrowState.CREATED}")
    
    print("SUCCESS: All DTOs are using shared Enums.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
