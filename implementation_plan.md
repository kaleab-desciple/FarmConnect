resolve
# Advanced Product & Order Management — Implementation Plan
Overhaul the FarmConnect backend to support real-life agricultural product workflows: **partial orders, concurrent merchants, cancellations, expiry, delivery failure, returns, spoilage, seasonal availability**, and **event-sourced inventory**.
> [!IMPORTANT]
> This plan makes significant schema changes (products, orders, new tables) and introduces new domain concepts. Review each phase carefully before approving.
---
## Architecture & Design Patterns Used
| Pattern | Where Applied |
|---------|---------------|
| **Event Sourcing** | `InventoryMovement` ledger — `available = SUM(movements)` |
| **Aggregate Root** | [Product](file:///home/kaleab/Downloads/Final_Project/FarmConnect/server/app/domain/products/entities.py#9-31) entity with quantity invariant methods |
| **State Machine** | `OrderStateMachine` — enum-driven valid transitions |
| **Specification** | `InventoryPolicy` — composable availability rules |
| **Pessimistic Locking** | `SELECT ... FOR UPDATE` on product row during reservation |
| **Unit of Work** | SQLAlchemy session scoping existing pattern, extended |
| **Soft Delete** | `deleted_at` column + listing query filter |
| **Optimistic Concurrency** | `version` column on products to detect stale writes |
---
## Phase 1 — Database Migration
### [NEW] Alembic migration
#### [NEW] [inventory_management.py](file:///home/kaleab/Downloads/Final_Project/FarmConnect/server/app/alembic/versions/inventory_management.py)
Single migration script that:
1. **Rename** `products.quantity_available` → `total_quantity`
2. **Add columns** to [products](file:///home/kaleab/Downloads/Final_Project/FarmConnect/server/app/api/v1/products/service.py#94-103):
   - `reserved_quantity DOUBLE PRECISION NOT NULL DEFAULT 0`
   - `sold_quantity DOUBLE PRECISION NOT NULL DEFAULT 0`
   - `spoiled_quantity DOUBLE PRECISION NOT NULL DEFAULT 0`
   - `deleted_at TIMESTAMPTZ NULL`
   - `version INTEGER NOT NULL DEFAULT 1` (optimistic concurrency)
3. **Extend `order_status_enum`** with new values:
   - `PENDING_PAYMENT`, `FUNDED`, `IN_DELIVERY`, `DELIVERY_FAILED`, `RETURNED`, `COMPLETED`, `EXPIRED`
4. **Create new enum** `inventory_movement_type_enum`:
   - `STOCK_IN`, `RESERVATION`, `RESERVATION_RELEASE`, `SALE_CONFIRMED`, `SPOILAGE`, `RETURN`, `ADJUSTMENT`, `EXPIRY`
5. **Create table `inventory_movements`**:
```sql
CREATE TABLE inventory_movements (
    id              VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      VARCHAR NOT NULL REFERENCES products(id),
    batch_id        VARCHAR NULL REFERENCES product_batches(id),
    movement_type   inventory_movement_type_enum NOT NULL,
    quantity         DOUBLE PRECISION NOT NULL,  -- positive = stock in, negative = stock out
    reference_type  VARCHAR(50) NOT NULL,        -- 'ORDER', 'SPOILAGE', 'ADJUSTMENT', 'RETURN'
    reference_id    VARCHAR NOT NULL,
    notes           TEXT NULL,
    created_by      VARCHAR NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_inv_movements_product ON inventory_movements(product_id);
CREATE INDEX idx_inv_movements_ref ON inventory_movements(reference_type, reference_id);

=================================

1. Create table product_batches:
sql
CREATE TABLE product_batches (
    id              VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      VARCHAR NOT NULL REFERENCES products(id),
    batch_code      VARCHAR(50) NOT NULL,
    total_quantity   DOUBLE PRECISION NOT NULL DEFAULT 0,
    reserved_quantity DOUBLE PRECISION NOT NULL DEFAULT 0,
    sold_quantity    DOUBLE PRECISION NOT NULL DEFAULT 0,
    spoiled_quantity DOUBLE PRECISION NOT NULL DEFAULT 0,
    harvest_date    DATE NULL,
    expiry_date     DATE NULL,
    quality_grade   quality_grade_enum NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(product_id, batch_code)
);
CREATE INDEX idx_batches_product ON product_batches(product_id);

2. Add columns to 
orders
:

batch_id VARCHAR NULL REFERENCES product_batches(id)
cancelled_at TIMESTAMPTZ NULL
cancelled_reason VARCHAR(500) NULL
delivered_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()



3. Data migration: Copy existing quantity_available values into total_quantity (handled by rename).

Phase 2 — Domain Layer
Enums
[MODIFY] 
enums.py
Expand 
OrderStatus
 with: PENDING_PAYMENT, FUNDED, IN_DELIVERY, DELIVERY_FAILED, RETURNED, COMPLETED, EXPIRED
Add InventoryMovementType enum: STOCK_IN, RESERVATION, RESERVATION_RELEASE, SALE_CONFIRMED, SPOILAGE, RETURN, ADJUSTMENT, EXPIRY
Add ProductStatus enum: AVAILABLE, LOW_STOCK, SOLD_OUT, EXPIRED, DISCONTINUED
Product Aggregate Root
[MODIFY] 
entities.py
Replace the simple dataclass with a rich Aggregate Root:



@dataclass
class Product:
    # ... existing fields ...
    total_quantity: Decimal = Decimal(0)
    reserved_quantity: Decimal = Decimal(0)
    sold_quantity: Decimal = Decimal(0)
    spoiled_quantity: Decimal = Decimal(0)
    deleted_at: Optional[datetime] = None
    version: int = 1

    @property
    def available_quantity(self) -> Decimal:
        """Derived: never stored in DB."""
        return self.total_quantity - self.reserved_quantity - self.sold_quantity - self.spoiled_quantity

    @property
    def status(self) -> ProductStatus:
        if self.deleted_at:
            return ProductStatus.DISCONTINUED
        if self.expiry_date and self.expiry_date < date.today():
            return ProductStatus.EXPIRED
        if self.available_quantity <= 0:
            return ProductStatus.SOLD_OUT
        if self.available_quantity < self.total_quantity * Decimal("0.1"):
            return ProductStatus.LOW_STOCK
        return ProductStatus.AVAILABLE

    def reserve(self, qty: Decimal) -> None:
        if qty > self.available_quantity:
            raise InsufficientStockError(self.id, self.available_quantity, qty)
        self.reserved_quantity += qty

    def confirm_sale(self, qty: Decimal) -> None:
        if qty > self.reserved_quantity:
            raise InvalidQuantityError("Cannot confirm more than reserved")
        self.reserved_quantity -= qty
        self.sold_quantity += qty

    def release_reservation(self, qty: Decimal) -> None:
        self.reserved_quantity = max(Decimal(0), self.reserved_quantity - qty)

    def record_spoilage(self, qty: Decimal) -> None:
        if qty > self.available_quantity:
            raise InvalidQuantityError("Spoilage exceeds available quantity")
        self.spoiled_quantity += qty

    def add_stock(self, qty: Decimal) -> None:
        self.total_quantity += qty

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
        self.is_active = False


New Domain Entities
@dataclass(frozen=True)
class InventoryMovement:
    product_id: str
    movement_type: InventoryMovementType
    quantity: Decimal           # positive = in, negative = out
    reference_type: str         # 'ORDER', 'SPOILAGE', 'ADJUSTMENT', 'RETURN'
    reference_id: str
    id: Optional[str] = None
    batch_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass(frozen=True)
class ProductBatch:
    product_id: str
    batch_code: str
    total_quantity: Decimal = Decimal(0)
    reserved_quantity: Decimal = Decimal(0)
    sold_quantity: Decimal = Decimal(0)
    spoiled_quantity: Decimal = Decimal(0)
    id: Optional[str] = None
    harvest_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quality_grade: Optional[QualityGrade] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


Order State Machine
[MODIFY] 
entities.py
Add state machine logic and new fields:
@dataclass
class Order:
    # ... existing fields ...
    batch_id: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancelled_reason: Optional[str] = None
    delivered_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


[NEW] 
state_machine.py
class OrderStateMachine:
    """Enum-driven valid state transitions."""
    TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
        OrderStatus.CREATED:          [OrderStatus.PENDING_PAYMENT, OrderStatus.CANCELLED],
        OrderStatus.PENDING_PAYMENT:  [OrderStatus.FUNDED, OrderStatus.CANCELLED],
        OrderStatus.FUNDED:           [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED:        [OrderStatus.IN_DELIVERY, OrderStatus.CANCELLED],
        OrderStatus.IN_DELIVERY:      [OrderStatus.DELIVERED, OrderStatus.DELIVERY_FAILED],
        OrderStatus.DELIVERED:        [OrderStatus.COMPLETED, OrderStatus.RETURNED],
        OrderStatus.DELIVERY_FAILED:  [OrderStatus.IN_DELIVERY, OrderStatus.CANCELLED, OrderStatus.RETURNED],
        OrderStatus.RETURNED:         [OrderStatus.COMPLETED],   # after refund processing
        OrderStatus.COMPLETED:        [],                        # terminal
        OrderStatus.CANCELLED:        [],                        # terminal
        OrderStatus.EXPIRED:          [],                        # terminal
    }

    @classmethod
    def validate_transition(cls, current: OrderStatus, target: OrderStatus) -> bool:
        return target in cls.TRANSITIONS.get(current, [])

    @classmethod
    def transition(cls, current: OrderStatus, target: OrderStatus) -> OrderStatus:
        if not cls.validate_transition(current, target):
            raise InvalidStateTransitionError(current, target)
        return target


Specification Pattern for Business Rules
[MODIFY] 
rules.py
class InventoryPolicy:
    """Specification pattern: composable checks."""

    @staticmethod
    def can_reserve(product: Product, requested_qty: Decimal) -> tuple[bool, str]:
        if product.deleted_at:
            return False, "Product is no longer available"
        if product.expiry_date and product.expiry_date < date.today():
            return False, "Product has expired"
        if not product.is_active:
            return False, "Product listing is inactive"
        if requested_qty > product.available_quantity:
            return False, f"Insufficient stock: {product.available_quantity} available, {requested_qty} requested"
        return True, ""


Domain Events
[MODIFY] 
events.py
Add events for the full lifecycle:
@dataclass
class QuantityReserved:
    order_id: str
    product_id: str
    quantity: Decimal
    timestamp: datetime

@dataclass
class SaleConfirmed:
    order_id: str
    product_id: str
    quantity: Decimal
    timestamp: datetime

@dataclass
class ReservationReleased:
    order_id: str
    product_id: str
    quantity: Decimal
    reason: str
    timestamp: datetime

@dataclass
class SpoilageRecorded:
    product_id: str
    quantity: Decimal
    reason: str
    timestamp: datetime

@dataclass
class OrderCancelled:
    order_id: str
    reason: str
    timestamp: datetime


Phase 3 — Infrastructure Layer
ORM Models
[MODIFY] 
product.py
Rename quantity_available → total_quantity
Add reserved_quantity, sold_quantity, spoiled_quantity, deleted_at, version
Add hybrid property available_quantity for read convenience (not persisted)
[NEW] 
inventory.py
New ORM models: InventoryMovementORM, ProductBatchORM

[MODIFY] 
order.py
Add batch_id, cancelled_at, cancelled_reason, delivered_at, updated_at

[MODIFY] 
__init__.py
Register new ORM models

Repositories
[NEW] 
inventory_repo.py

class InventoryMovementRepository:
    def append(self, movement: InventoryMovement) -> InventoryMovement: ...
    def get_by_product(self, product_id: str) -> list[InventoryMovement]: ...
    def get_balance(self, product_id: str) -> Decimal:
        """SUM(quantity) — the event-sourced truth."""

class ProductBatchRepository:
    def save(self, batch: ProductBatch) -> ProductBatch: ...
    def get_active_by_product(self, product_id: str) -> list[ProductBatch]: ...




[MODIFY] 
product_repo.py
Add get_for_update(product_id) — uses SELECT ... FOR UPDATE (pessimistic lock)
Modify 
list_active()
 to filter out deleted_at IS NOT NULL
Modify 
delete()
 → soft_delete() (sets deleted_at, does NOT remove row)
Add increment_version() for optimistic concurrency check on save
[MODIFY] 
order_repo.py
Update mappers to handle new fields

Mappers
[MODIFY] 
mappers.py
Add mappings for InventoryMovement ↔ InventoryMovementORM and ProductBatch ↔ ProductBatchORM

Phase 4 — Application Layer (Use Cases)
[NEW] 
inventory_service.py
The core orchestrator for all quantity operations:


class InventoryService:
    """Application service: orchestrates inventory with concurrency control."""

    def reserve_stock(self, product_id: str, order_id: str, qty: Decimal) -> None:
        """
        1. BEGIN TRANSACTION
        2. SELECT product FOR UPDATE (pessimistic lock)
        3. InventoryPolicy.can_reserve(product, qty)
        4. product.reserve(qty)
        5. Append InventoryMovement(RESERVATION, -qty, ref=ORDER)
        6. Save product
        7. COMMIT
        """

    def confirm_sale(self, product_id: str, order_id: str, qty: Decimal) -> None:
        """When escrow FUNDED: reserved → sold."""

    def release_reservation(self, product_id: str, order_id: str, qty: Decimal, reason: str) -> None:
        """When order cancelled pre-funding: release reserved."""

    def record_spoilage(self, product_id: str, qty: Decimal, reason: str, user_id: str) -> None:
        """Farmer reports spoilage."""

    def adjust_stock(self, product_id: str, qty: Decimal, reason: str, user_id: str) -> None:
        """Farmer adds partial harvest / admin correction."""

    def process_return(self, product_id: str, order_id: str, qty: Decimal, reason: str) -> None:
        """Delivery failure / return: re-add to available."""


[MODIFY] 
escrow_lifecycle_service.py
On 
fund_escrow()
: call InventoryService.confirm_sale() — moves reserved → sold
On 
refund_escrow()
: call InventoryService.release_reservation() — frees reserved qty
[MODIFY] 
order_service.py
On 
create_order()
: call InventoryService.reserve_stock() before creating escrow
Integrate OrderStateMachine for all status transitions
On cancel: call InventoryService.release_reservation()
Phase 5 — API Layer
[MODIFY] 
routes.py
New endpoints:

POST /orders/{order_id}/cancel — cancel order, release reservation
POST /orders/{order_id}/confirm-delivery — mark delivered
POST /orders/{order_id}/report-delivery-failure — trigger return flow
[MODIFY] 
routes.py
New endpoints:

POST /products/{product_id}/adjust-stock — farmer adds/adjusts inventory
POST /products/{product_id}/report-spoilage — record spoilage
POST /products/{product_id}/soft-delete — soft delete product
GET  /products/{product_id}/inventory-history — view InventoryMovement ledger
POST /products/{product_id}/batches — create product batch
GET  /products/{product_id}/batches — list batches
Modify listing endpoints to filter out soft-deleted products.

[MODIFY] 
service.py
Integrate InventoryService and OrderStateMachine.

[MODIFY] 
service.py
Use new InventoryService for stock adjustment operations.

Phase 6 — Shared Models (DTOs)
[MODIFY] 
product.py
Rename quantity_available → total_quantity
Add reserved_quantity, sold_quantity, spoiled_quantity, available_quantity (computed), deleted_at, version
Add ProductStatus field (computed from backend)
[MODIFY] 
order.py
Add new 
OrderStatus
 values
Add batch_id, cancelled_at, cancelled_reason, delivered_at, updated_at

Order Lifecycle Flow (Complete) using mermeid code
stateDiagram-v2
    direction TB

    [*] --> CREATED : Merchant places order
    
    CREATED --> PENDING_PAYMENT : reserve_stock ✅
    CREATED --> CANCELLED : merchant cancels
    
    PENDING_PAYMENT --> FUNDED : escrow.fund()
    PENDING_PAYMENT --> CANCELLED : escrow fails -> release_reserve
    
    FUNDED --> CONFIRMED : confirm_sale() -> reserved-
    FUNDED --> CANCELLED : cancel before dispatch -> release
    
    CONFIRMED --> IN_DELIVERY : dispatch
    CONFIRMED --> CANCELLED : cancel mid-process
    
    IN_DELIVERY --> DELIVERY_FAILED : delivery issue
    IN_DELIVERY --> DELIVERED : arrival confirmed
    
    DELIVERY_FAILED --> IN_DELIVERY : retry
    DELIVERY_FAILED --> CANCELLED : give up
    DELIVERY_FAILED --> RETURNED : goods returned
    
    DELIVERED --> RETURNED : quality issue
    DELIVERED --> COMPLETED : escrow.release()
    
    RETURNED --> COMPLETED : after refund processed
    
    CANCELLED --> [*]
    COMPLETED --> [*]
    EXPIRED --> [*]



    Concurrency Control Flow

    participant M1 as Merchant A
    participant M2 as Merchant B
    participant API as API Server
    participant DB as PostgreSQL

    M1->>API: POST /orders (200kg maize)
    M2->>API: POST /orders (900kg maize)
    
    API->>DB: BEGIN; SELECT * FROM products WHERE id=? FOR UPDATE
    Note over DB: Row locked for M1
    DB-->>API: product (total=1000, reserved=0, sold=0)
    API->>API: available = 1000-0-0 = 1000 ≥ 200 ✅
    API->>DB: UPDATE products SET reserved_quantity=200; INSERT inventory_movement
    API->>DB: COMMIT
    
    Note over DB: Lock released, M2 proceeds
    API->>DB: BEGIN; SELECT * FROM products WHERE id=? FOR UPDATE
    DB-->>API: product (total=1000, reserved=200, sold=0)
    API->>API: available = 1000-200-0 = 800 ≥ 900 ❌
    API-->>M2: 409 Conflict: Insufficient stock (800 available)


    Phase 8 — Edge Cases Handled
Scenario	what_it_Handling
Partial Harvest	Farmer calls POST /products/{id}/adjust-stock → add_stock() → InventoryMovement(STOCK_IN, +qty)

Spoilage	Farmer calls POST /products/{id}/report-spoilage → record_spoilage() → InventoryMovement(SPOILAGE, -qty)

Batch Tracking	Each batch has independent quantities; orders reference batch_id

Product Expiry	Product.status checks expiry_date dynamically; listing queries filter expired; background job can soft-delete

Concurrent Orders	SELECT ... FOR UPDATE prevents overselling

Cancellation pre-funding	release_reservation() frees reserved qty

Cancellation post-funding	release_reservation() + 
refund_escrow()

Delivery Failure	Order → DELIVERY_FAILED → retry or RETURNED → process_return() re-adds quantity

Return after delivery	DELIVERED → RETURNED → refund + process_return()

Product soft delete	deleted_at set; is_active = False; hidden from listing; audit trail preserved

SOLD_OUT	When available_quantity == 0, Product.status returns SOLD_OUT

Seasonal availability	is_active toggled by farmer; listing query respects it



Verification Plan
Automated Tests
Run from project root inside Docker:

bash
docker-compose exec api python -m pytest app/tests/ -v
New test file to create:

[NEW] 
test_inventory_management.py
Tests to write:

Product.available_quantity computed correctly
Product.reserve() succeeds when stock sufficient
Product.reserve() raises InsufficientStockError when stock insufficient
Product.confirm_sale() moves reserved → sold
Product.release_reservation() frees reserved quantity
Product.record_spoilage() reduces available
OrderStateMachine validates all transitions and rejects invalid ones
InventoryPolicy.can_reserve() rejects expired/deleted/inactive products
Concurrency: simulate two concurrent reservations (integration test with DB)
Soft delete: verify product hidden from active listing but still queryable


Database Migration Verification
# Apply migration
docker-compose exec api alembic -c app/alembic.ini upgrade head

# Verify schema
docker-compose exec db psql -U postgres -d agri_db -c "\d products"
docker-compose exec db psql -U postgres -d agri_db -c "\d inventory_movements"
docker-compose exec db psql -U postgres -d agri_db -c "\d product_batches"
docker-compose exec db psql -U postgres -d agri_db -c "\d orders"

# Verify rollback
docker-compose exec api alembic -c app/alembic.ini downgrade -1
docker-compose exec api alembic -c app/alembic.ini upgrade head





Manual Verification
TIP

After implementation, test the complete order lifecycle via the API:

Create product → POST /api/v1/products/ with total_quantity: 1000
Place order → POST /api/v1/orders/ with quantity: 200 → verify reserved_quantity = 200
Fund escrow → verify reserved → sold (reserved=0, sold=200)
Place second order for 900 → verify 409 Conflict (only 800 available)
Cancel order → verify reserved quantity released
Report spoilage → verify available reduced
Soft delete → verify product hidden from listing but accessible by ID
Implementation Order
Migration (Phase 1) — schema first
Domain enums + entities (Phase 2) — define the rules
ORM models (Phase 3 — models) — match schema
Shared DTOs (Phase 6) — API contracts
Mappers (Phase 3 — mappers) — wire domain ↔ ORM ↔ DTO
Repositories (Phase 3 — repos) — data access with locking
Application services (Phase 4) — orchestration
API endpoints (Phase 5) — expose to clients
Tests (Phase 8) — verify everything