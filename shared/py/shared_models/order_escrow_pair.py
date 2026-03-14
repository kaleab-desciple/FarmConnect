# shared/py/shared_models/order_escrow_pair.py
from pydantic import BaseModel
from .order import Order
from .escrow import Escrow

class OrderEscrowPair(BaseModel):
    order: Order
    escrow: Escrow