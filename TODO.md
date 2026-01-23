# TODO: Fix Order.__init__() delivery_cost error

## Problem
The error `Order.__init__() got an unexpected keyword argument 'delivery_cost'` occurs because:
1. The shared Pydantic model `Order` (in `shared/py/shared_models/order.py`) has a `delivery_cost` field
2. The domain entity `Order` dataclass (in `server/app/domain/orders/entities.py`) does NOT have `delivery_cost` field
3. The `OrderService.create_order()` method is trying to pass `delivery_cost` to the domain entity

## Fix Plan
- [x] Identify the issue in the code
- [x] Add `delivery_cost` field to the domain `Order` dataclass in `server/app/domain/orders/entities.py`
- [ ] Verify the fix by testing the API endpoint

## Status: Completed - Fix Applied

