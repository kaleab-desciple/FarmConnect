# FarmConnect Database Schema Documentation

> **Database Engine:** PostgreSQL (with `pgcrypto` extension for `gen_random_uuid()`)
> **Migration Tool:** Alembic
> **Current Head Revision:** `add_delivery_workflow`

---

## Table of Contents

1. [Core Tables](#1-core-tables)
   - [users](#11-users)
   - [products](#12-products)
   - [product_batches](#13-product_batches)
   - [orders](#14-orders)
   - [escrows](#15-escrows)
2. [Pricing & Accounting](#2-pricing--accounting)
   - [pricing_rules](#21-pricing_rules)
   - [ledger_events](#22-ledger_events)
   - [accounts](#23-accounts)
   - [journal_entries](#24-journal_entries)
   - [journal_lines](#25-journal_lines)
3. [Agricultural Intelligence](#3-agricultural-intelligence)
   - [farms](#31-farms)
   - [fields](#32-fields)
   - [crop_cycles](#33-crop_cycles)
   - [harvests](#34-harvests)
4. [Monitoring & Health](#4-monitoring--health)
   - [ndvi_snapshots](#41-ndvi_snapshots)
   - [pest_disease_reports](#42-pest_disease_reports)
   - [treatment_recommendations](#43-treatment_recommendations)
   - [soil_readings](#44-soil_readings)
5. [Weather Services](#5-weather-services)
   - [weather_forecasts](#51-weather_forecasts)
   - [weather_snapshots](#52-weather_snapshots)
   - [weather_alert_subscriptions](#53-weather_alert_subscriptions)
6. [Supply Chain & Traceability](#6-supply-chain--traceability)
   - [crop_cycle_products](#61-crop_cycle_products)
   - [order_field_sources](#62-order_field_sources)
   - [escrow_field_conditions](#63-escrow_field_conditions)
7. [Risk & Alerts](#7-risk--alerts)
   - [field_risk_scores](#71-field_risk_scores)
   - [alerts](#72-alerts)
8. [Harvest Event Tracking & QC](#8-harvest-event-tracking--qc)
   - [harvest_events](#81-harvest_events)
   - [harvest_batches](#82-harvest_batches)
   - [harvest_batch_contributions](#83-harvest_batch_contributions)
   - [product_batch_sources](#84-product_batch_sources)
   - [audit_events](#85-audit_events)
   - [lab_providers](#86-lab_providers)
   - [samples](#87-samples)
   - [batch_qc_reports](#88-batch_qc_reports)
   - [certifications](#89-certifications)
   - [qc_grade_rules](#810-qc_grade_rules)
9. [Inventory Management](#9-inventory-management)
   - [inventory_movements](#91-inventory_movements)
10. [Delivery Workflow](#10-delivery-workflow)
    - [deliveries](#101-deliveries)
11. [Enum Types Reference](#11-enum-types-reference)

---

## 1. Core Tables

### 1.1 `users`

The central user table for all platform participants — farmers, merchants, delivery personnel, agents, managers, admins, moderators, agronomists, and field analysts.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique user identifier (UUID string) |
| `role` | `user_role_enum` | YES | — | User's platform role (FARMER, MERCHANT, DELIVERY, AGENT, MANAGER, ADMIN, MODERATOR, AGRONOMIST, FIELD_ANALYST) |
| `name` | `VARCHAR` | YES | — | Full name of the user |
| `email` | `VARCHAR` (UNIQUE) | YES | — | Email address; unique across all users |
| `phone` | `VARCHAR` (UNIQUE) | YES | — | Phone number; unique across all users |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Account creation timestamp |
| `metadata` | `JSONB` | YES | — | Flexible JSON metadata (e.g., profile details, preferences) |
| `keycloak_id` | `VARCHAR` (UNIQUE) | YES | — | Keycloak SSO identity provider ID (added in migration `dae300f4c591`) |
| `onboarding_status` | `onboarding_status_enum` | YES | `'ACTIVE'` | Onboarding approval state: PENDING_REVIEW, ACTIVE, REJECTED (added in `dispute_and_user_onboarding_v1`) |
| `onboarding_agent_id` | `VARCHAR` | YES | — | ID of the agent who reviewed/approved the user's onboarding |

**Constraints:** `uq_users_keycloak_id` (unique on `keycloak_id`)

---

### 1.2 `products`

Represents agricultural products listed by farmers for sale on the marketplace.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique product identifier |
| `farmer_id` | `VARCHAR` | NO | — | ID of the farmer who owns this product listing |
| `name` | `VARCHAR(100)` | NO | — | Product name (e.g., "Organic Maize") |
| `description` | `VARCHAR(1000)` | YES | — | Detailed product description |
| `category` | `category_enum` | NO | — | Product category: GRAINS, VEGETABLES, FRUITS, DAIRY, MEAT, SPICES, OTHER |
| `unit` | `unit_enum` | YES | — | Measurement unit: KG, TON, LITER, UNIT, CRATE, BAG |
| `base_price` | `FLOAT` | NO | — | Base price per unit (must be > 0) |
| `currency` | `VARCHAR(3)` | NO | `'USD'` | ISO 4217 currency code |
| `total_quantity` | `FLOAT` | YES | — | Total available quantity in stock |
| `quality_grade` | `quality_grade_enum` | YES | — | Quality grade: GRADE_A, GRADE_B, GRADE_C, PREMIUM, STANDARD, A, B, C |
| `harvest_date` | `DATE` | YES | — | Date the product was harvested |
| `expiry_date` | `DATE` | YES | — | Product expiration date |
| `location` | `JSONB` | YES | — | GeoJSON or structured location data for the product origin |
| `images` | `JSONB` | YES | — | Array of image URLs/metadata |
| `is_active` | `BOOLEAN` | YES | `true` | Whether the product listing is active |
| `metadata` | `JSONB` | YES | — | Flexible JSON metadata |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |
| `harvest_id` | `UUID` | YES | — | FK → `harvests.id`; links product to a specific harvest record (added in `harvest_mgmt_v1`) |
| `crop_cycle_id` | `UUID` | YES | — | FK → `crop_cycles.id`; links product to a crop cycle (added in `harvest_mgmt_v1`) |
| `reserved_quantity` | `FLOAT` | NO | `0` | Quantity currently reserved by pending orders (added in `inventory_mgmt_v1`) |
| `sold_quantity` | `FLOAT` | NO | `0` | Quantity already sold (added in `inventory_mgmt_v1`) |
| `spoiled_quantity` | `FLOAT` | NO | `0` | Quantity lost to spoilage (added in `inventory_mgmt_v1`) |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft-delete timestamp (added in `inventory_mgmt_v1`) |
| `version` | `INTEGER` | NO | `1` | Optimistic concurrency version counter (added in `inventory_mgmt_v1`) |

**Indexes:** `idx_products_harvest_id` (on `harvest_id`)

---

### 1.3 `product_batches`

Tracks individual batches of a product for granular inventory management, quality tracking, and traceability.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique batch identifier |
| `product_id` | `VARCHAR` | NO | — | FK → `products.id`; the parent product |
| `batch_code` | `VARCHAR(50)` | NO | — | Human-readable batch code (unique per product) |
| `total_quantity` | `FLOAT` | NO | `0` | Total quantity in this batch |
| `reserved_quantity` | `FLOAT` | NO | `0` | Quantity reserved by pending orders |
| `sold_quantity` | `FLOAT` | NO | `0` | Quantity sold from this batch |
| `spoiled_quantity` | `FLOAT` | NO | `0` | Quantity lost to spoilage |
| `harvest_date` | `DATE` | YES | — | Harvest date for this batch |
| `expiry_date` | `DATE` | YES | — | Expiry date for this batch |
| `quality_grade` | `quality_grade_enum` | YES | — | Quality grade of this batch |
| `is_active` | `BOOLEAN` | NO | `true` | Whether the batch is active |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Record creation timestamp |
| `harvest_batch_id` | `VARCHAR` | YES | — | FK → `harvest_batches.id`; links to the harvest batch origin (added in `harvest_events_v1`) |

**Constraints:** `uq_product_batch_code` (unique on `[product_id, batch_code]`)
**Indexes:** `idx_batches_product` (on `product_id`), `idx_product_batches_harvest_batch` (on `harvest_batch_id`)

---

### 1.4 `orders`

Represents purchase orders placed by merchants for farmer products. Tracks the full order lifecycle from creation through payment, delivery, and completion.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique order identifier |
| `farmer_id` | `VARCHAR` | YES | — | ID of the selling farmer |
| `merchant_id` | `VARCHAR` | YES | — | ID of the buying merchant |
| `product_id` | `VARCHAR` | YES | — | ID of the product being ordered |
| `quantity` | `FLOAT` | YES | — | Quantity ordered |
| `unit_price` | `FLOAT` | YES | — | Price per unit at time of order |
| `delivery_cost` | `FLOAT` | YES | — | Calculated delivery cost |
| `platform_fee` | `FLOAT` | YES | — | Platform fee amount |
| `subtotal` | `FLOAT` | YES | — | Subtotal before fees (quantity × unit_price) |
| `delivery_fee` | `FLOAT` | YES | — | Delivery fee charged to buyer |
| `delivery_margin` | `FLOAT` | YES | — | Platform margin on delivery |
| `quality_fee` | `FLOAT` | YES | — | Quality premium/discount fee |
| `total_price` | `FLOAT` | YES | — | Final total price including all fees |
| `status` | `order_status_enum` | YES | — | Order lifecycle status: CREATED, PENDING_PAYMENT, FUNDED, CONFIRMED, IN_DELIVERY, DELIVERED, DELIVERY_FAILED, RETURNED, COMPLETED, CANCELLED, EXPIRED |
| `escrow_id` | `VARCHAR` | YES | — | Associated escrow account ID |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Order creation timestamp |
| `batch_id` | `VARCHAR` | YES | — | FK → `product_batches.id`; specific batch allocated to this order (added in `inventory_mgmt_v1`) |
| `cancelled_at` | `TIMESTAMPTZ` | YES | — | Cancellation timestamp (added in `inventory_mgmt_v1`) |
| `cancelled_reason` | `VARCHAR(500)` | YES | — | Reason for cancellation (added in `inventory_mgmt_v1`) |
| `delivered_at` | `TIMESTAMPTZ` | YES | — | Delivery confirmation timestamp (added in `inventory_mgmt_v1`) |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp (added in `inventory_mgmt_v1`) |

---

### 1.5 `escrows`

Manages escrow accounts that hold funds between buyer payment and seller release. Ensures secure transactions with dispute support.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique escrow identifier |
| `order_id` | `VARCHAR` | YES | — | Associated order ID |
| `state` | `escrow_state_enum` | YES | — | Escrow lifecycle state: CREATED, FUNDED, RELEASED, REFUNDED, DISPUTED, SETTLED, REVERSED |
| `amount` | `FLOAT` | YES | — | Escrowed amount |
| `provider` | `provider_enum` | YES | — | Payment provider: BANK, WALLET |
| `funded_at` | `TIMESTAMPTZ` | YES | — | When funds were deposited |
| `provider_reference` | `VARCHAR` | YES | — | External payment provider reference/transaction ID |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |
| `released_at` | `TIMESTAMPTZ` | YES | — | When funds were released to the seller |

---

## 2. Pricing & Accounting

### 2.1 `pricing_rules`

Configurable rules engine for calculating platform fees, delivery costs, quality premiums, and distance-based pricing.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | — | Unique rule identifier |
| `rule_type` | `rule_type_enum` | NO | — | Type of pricing rule: PLATFORM_FEE, DELIVERY, QUALITY, DISTANCE |
| `product_category` | `VARCHAR` | YES | — | Optional category filter (e.g., "GRAINS") |
| `quality_grade` | `VARCHAR` | YES | — | Optional quality grade filter (e.g., "A") |
| `region` | `VARCHAR` | YES | — | Optional region filter |
| `min_distance_km` | `FLOAT` | YES | — | Minimum distance threshold for distance-based rules |
| `max_distance_km` | `FLOAT` | YES | — | Maximum distance threshold for distance-based rules |
| `fee_type` | `fee_type_enum` | NO | — | How the fee is calculated: PERCENTAGE or FIXED |
| `fee_value` | `FLOAT` | NO | — | The fee amount (percentage value or fixed amount) |
| `priority` | `INTEGER` | NO | — | Rule evaluation priority (lower = higher priority) |
| `active` | `BOOLEAN` | NO | `true` | Whether the rule is currently active |
| `valid_from` | `TIMESTAMPTZ` | NO | — | Rule effective start date |
| `valid_to` | `TIMESTAMPTZ` | YES | — | Rule expiration date (null = no expiry) |

**Seeded Data:** 5 default rules (platform fee 5%, delivery flat $10, quality premium 2% for grade A, distance tiers $5/$15)

---

### 2.2 `ledger_events`

Event-sourced financial ledger tracking all monetary movements in the system (escrow funding, releases, refunds, fees, penalties, loans).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | — | Unique event identifier |
| `aggregate_type` | `aggregate_type_enum` | NO | — | Entity type: USER, ESCROW, SYSTEM |
| `aggregate_id` | `VARCHAR` | NO | — | ID of the aggregate entity |
| `event_type` | `ledger_event_type_enum` | NO | — | Event type: ESCROW_FUNDED, ESCROW_RELEASED, ESCROW_REFUNDED, PLATFORM_FEE_COLLECTED, PENALTY_APPLIED, LOAN_DISBURSED, LOAN_REPAID |
| `amount` | `FLOAT` | NO | — | Monetary amount of the event |
| `currency` | `VARCHAR` | NO | `'ETB'` | Currency code (defaults to Ethiopian Birr) |
| `direction` | `direction_enum` | NO | — | DEBIT or CREDIT |
| `reference_type` | `reference_type_enum` | NO | — | What the event references: ORDER, ESCROW, DISPUTE, LOAN |
| `reference_id` | `VARCHAR` | NO | — | ID of the referenced entity |
| `event_metadata` | `JSONB` | YES | — | Additional event context/details |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Event timestamp |

---

### 2.3 `accounts`

Double-entry accounting accounts for users, escrows, and the system. Each account has a type (ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | — | Unique account identifier |
| `owner_type` | `owner_type_enum` | NO | — | Account owner type: USER, ESCROW, SYSTEM |
| `owner_id` | `VARCHAR` | NO | — | ID of the account owner |
| `account_type` | `account_type_enum` | NO | — | Accounting type: ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| `name` | `VARCHAR` | NO | — | Human-readable account name |
| `currency` | `VARCHAR` | NO | `'ETB'` | Account currency |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Account creation timestamp |

**Indexes:** `idx_accounts_owner_type_id_account_type` (composite on `[owner_type, owner_id, account_type]`)

---

### 2.4 `journal_entries`

Double-entry journal entries that group related debit/credit lines for a single financial transaction.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | — | Unique journal entry identifier |
| `reference_type` | `VARCHAR` | NO | — | Type of business event (e.g., "ORDER", "ESCROW") |
| `reference_id` | `VARCHAR` | NO | — | ID of the referenced business entity |
| `description` | `TEXT` | NO | — | Human-readable description of the transaction |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Entry creation timestamp |

---

### 2.5 `journal_lines`

Individual debit/credit lines within a journal entry. Each line affects one account. Total debits must equal total credits per entry.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `INTEGER` (PK) | NO | auto-increment | Unique line identifier |
| `journal_entry_id` | `VARCHAR` | NO | — | FK → `journal_entries.id`; parent journal entry |
| `account_id` | `VARCHAR` | NO | — | FK → `accounts.id`; the account being debited/credited |
| `debit_amount` | `NUMERIC(15,2)` | NO | `0` | Debit amount (0 if this is a credit line) |
| `credit_amount` | `NUMERIC(15,2)` | NO | `0` | Credit amount (0 if this is a debit line) |

---

## 3. Agricultural Intelligence

### 3.1 `farms`

Represents a farmer's farm — the top-level geographic entity containing one or more fields.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique farm identifier |
| `farmer_id` | `VARCHAR` | NO | — | FK → `users.id`; the owning farmer (CASCADE delete) |
| `name` | `VARCHAR(255)` | NO | — | Farm name |
| `location_lat` | `NUMERIC(10,8)` | NO | — | Latitude coordinate (−90 to 90) |
| `location_lng` | `NUMERIC(11,8)` | NO | — | Longitude coordinate (−180 to 180) |
| `location_address` | `TEXT` | YES | — | Human-readable address |
| `total_area_ha` | `NUMERIC(10,4)` | YES | — | Total farm area in hectares (must be > 0) |
| `boundary_geojson` | `JSONB` | YES | — | GeoJSON polygon of farm boundary |
| `centroid_geojson` | `JSONB` | YES | — | GeoJSON point of farm centroid |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft-delete timestamp |

**Constraints:** `valid_coordinates` (lat between −90/90, lng between −180/180)
**Indexes:** `idx_farms_farmer_active` (on `farmer_id` WHERE `deleted_at IS NULL`)

---

### 3.2 `fields`

Individual agricultural fields within a farm. Each field has its own soil characteristics, boundaries, and irrigation setup.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique field identifier |
| `farm_id` | `UUID` | NO | — | FK → `farms.id`; parent farm (CASCADE delete) |
| `name` | `VARCHAR(255)` | NO | — | Field name |
| `area_ha` | `NUMERIC(10,4)` | NO | — | Field area in hectares (must be > 0) |
| `boundary_geojson` | `JSONB` | NO | — | GeoJSON polygon of field boundary |
| `centroid_geojson` | `JSONB` | YES | — | GeoJSON point of field centroid |
| `soil_type` | `VARCHAR(100)` | YES | — | Soil type (e.g., "clay", "loam", "sandy") |
| `soil_classification` | `VARCHAR(100)` | YES | — | Formal soil classification |
| `elevation_m` | `NUMERIC(8,2)` | YES | — | Elevation in meters |
| `slope_degree` | `NUMERIC(5,2)` | YES | — | Slope in degrees (0–90) |
| `irrigation_type` | `VARCHAR(50)` | YES | — | Irrigation method (e.g., "drip", "sprinkler", "flood") |
| `drainage_type` | `VARCHAR(50)` | YES | — | Drainage system type |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft-delete timestamp |

**Indexes:** `idx_fields_farm` (on `farm_id` WHERE `deleted_at IS NULL`), `idx_fields_farm_id` (on `farm_id`)

---

### 3.3 `crop_cycles`

Tracks the lifecycle of a crop from planting through harvest on a specific field. Supports yield tracking and quality grading.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique crop cycle identifier |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the field being cultivated (CASCADE delete) |
| `product_category` | `VARCHAR(50)` | NO | — | Category of crop (e.g., "GRAINS") |
| `crop_name` | `VARCHAR(255)` | NO | — | Name of the crop (e.g., "Maize") |
| `variety` | `VARCHAR(255)` | YES | — | Crop variety |
| `cultivar` | `VARCHAR(255)` | YES | — | Specific cultivar |
| `planting_date` | `DATE` | NO | — | Date of planting |
| `expected_harvest_date` | `DATE` | YES | — | Projected harvest date (must be after planting_date) |
| `actual_harvest_date` | `DATE` | YES | — | Actual harvest date (must be ≥ planting_date) |
| `status` | `crop_cycle_status` | YES | `'PLANNED'` | Lifecycle status: PLANNED, PLANTED, GROWING, HARVESTED, PARTIALLY_HARVESTED, FAILED, ABANDONED |
| `expected_yield_kg` | `NUMERIC(12,2)` | YES | — | Expected yield in kilograms (≥ 0) |
| `actual_yield_kg` | `NUMERIC(12,2)` | YES | — | Actual yield in kilograms (≥ 0) |
| `yield_quality_grade` | `VARCHAR(50)` | YES | — | Overall quality grade of the yield |
| `seed_source` | `VARCHAR(255)` | YES | — | Source of seeds used |
| `planting_density_per_ha` | `INTEGER` | YES | — | Number of plants per hectare |
| `seed_cost_usd` | `NUMERIC(10,2)` | YES | — | Cost of seeds in USD |
| `notes` | `TEXT` | YES | — | Free-text notes |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft-delete timestamp |

**Constraints:** `valid_harvest_dates`, `valid_actual_harvest`
**Indexes:** `idx_crop_cycles_field` (on `field_id` WHERE `deleted_at IS NULL`)

---

### 3.4 `harvests`

Records individual harvest events linked to a crop cycle and field. Bridges the gap between crop cycles and product listings.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique harvest identifier |
| `farmer_id` | `VARCHAR` | NO | — | FK → `users.id`; the farmer who performed the harvest (CASCADE delete) |
| `crop_cycle_id` | `UUID` | YES | — | FK → `crop_cycles.id`; associated crop cycle (SET NULL on delete) |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the field harvested (CASCADE delete) |
| `harvest_date` | `DATE` | NO | — | Date of harvest |
| `quantity_harvested` | `NUMERIC(12,2)` | NO | — | Amount harvested |
| `unit` | `unit_enum` | YES | — | Unit of measurement: KG, TON, LITER, UNIT, CRATE, BAG |
| `quality_grade` | `quality_grade_enum` | YES | — | Quality grade of the harvest |
| `notes` | `TEXT` | YES | — | Free-text notes |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

**Indexes:** `idx_harvests_farmer_id`, `idx_harvests_crop_cycle_id`, `idx_harvests_field_id`

---

## 4. Monitoring & Health

### 4.1 `ndvi_snapshots`

Stores Normalized Difference Vegetation Index (NDVI) satellite imagery data for monitoring crop health and vegetation stress.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique snapshot identifier |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the monitored field |
| `crop_cycle_id` | `UUID` | YES | — | FK → `crop_cycles.id`; associated crop cycle |
| `source` | `ndvi_source` | NO | — | Data source: SENTINEL_2, LANDSAT_8, LANDSAT_9, MODIS, MANUAL |
| `source_metadata` | `JSONB` | YES | `'{}'` | Source-specific metadata (scene ID, tile, etc.) |
| `captured_at` | `TIMESTAMPTZ` | NO | — | When the satellite image was captured |
| `processed_at` | `TIMESTAMPTZ` | YES | `now()` | When the NDVI was computed |
| `ndvi_mean` | `NUMERIC(5,4)` | NO | — | Mean NDVI value (−1 to 1) |
| `ndvi_min` | `NUMERIC(5,4)` | YES | — | Minimum NDVI value (−1 to 1) |
| `ndvi_max` | `NUMERIC(5,4)` | YES | — | Maximum NDVI value (−1 to 1) |
| `ndvi_stddev` | `NUMERIC(5,4)` | YES | — | Standard deviation of NDVI |
| `stress_level` | `stress_level` | YES | — | Derived stress level: NONE, LOW, MEDIUM, HIGH, CRITICAL |
| `cloud_cover_pct` | `NUMERIC(5,2)` | YES | — | Cloud cover percentage (0–100) |
| `data_quality_score` | `NUMERIC(3,2)` | YES | — | Data quality score |
| `tile_urls` | `JSONB` | YES | — | URLs to NDVI tile images |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

---

### 4.2 `pest_disease_reports`

Reports of pest or disease observations in fields, supporting AI-assisted diagnosis and expert verification.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique report identifier |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; affected field |
| `crop_cycle_id` | `UUID` | YES | — | FK → `crop_cycles.id`; affected crop cycle |
| `reported_by` | `VARCHAR` | NO | — | FK → `users.id`; user who filed the report |
| `location_geojson` | `JSONB` | YES | — | GeoJSON point of observation location |
| `image_urls` | `TEXT[]` | YES | — | Array of image URLs showing the issue |
| `drone_flight_id` | `UUID` | YES | — | Associated drone flight ID (if detected by drone) |
| `suspected_issue` | `VARCHAR(255)` | NO | — | Description of the suspected pest/disease |
| `issue_type` | `VARCHAR(50)` | YES | — | Classification: "pest", "disease", "nutrient_deficiency", etc. |
| `scientific_name` | `VARCHAR(255)` | YES | — | Scientific name of the pest/disease |
| `common_names` | `TEXT[]` | YES | — | Array of common names |
| `ai_diagnosis_id` | `UUID` | YES | — | Reference to AI diagnosis result |
| `confidence_pct` | `NUMERIC(5,2)` | YES | — | AI confidence percentage (0–100) |
| `severity` | `severity_level` | YES | — | Severity: TRACE, LOW, MEDIUM, HIGH, SEVERE |
| `affected_area_ha` | `NUMERIC(10,4)` | YES | — | Affected area in hectares (> 0) |
| `affected_plant_count` | `INTEGER` | YES | — | Number of affected plants |
| `symptoms` | `TEXT` | YES | — | Description of observed symptoms |
| `spread_pattern` | `VARCHAR(100)` | YES | — | Pattern of spread (e.g., "clustered", "random") |
| `verified_by` | `VARCHAR` | YES | — | FK → `users.id`; expert who verified the report |
| `verified_at` | `TIMESTAMPTZ` | YES | — | Verification timestamp |
| `verification_notes` | `TEXT` | YES | — | Expert verification notes |
| `first_observed_date` | `DATE` | YES | — | When the issue was first noticed |
| `detected_at` | `TIMESTAMPTZ` | NO | — | Detection timestamp |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |

---

### 4.3 `treatment_recommendations`

Treatment recommendations for pest/disease reports, from agronomists, AI models, or community sources.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique recommendation identifier |
| `report_id` | `UUID` | NO | — | FK → `pest_disease_reports.id`; the report being addressed |
| `recommended_by` | `VARCHAR` | NO | — | FK → `users.id`; who made the recommendation |
| `recommendation_source` | `recommendation_source` | NO | — | Source: AGRONOMIST, SYSTEM, AI_MODEL, COMMUNITY |
| `description` | `TEXT` | NO | — | Detailed treatment description |
| `treatment_type` | `VARCHAR(100)` | YES | — | Type of treatment (e.g., "chemical", "biological", "cultural") |
| `chemical_name` | `VARCHAR(255)` | YES | — | Name of chemical product |
| `active_ingredient` | `VARCHAR(255)` | YES | — | Active ingredient |
| `formulation` | `VARCHAR(100)` | YES | — | Chemical formulation type |
| `dosage_per_ha` | `VARCHAR(255)` | YES | — | Recommended dosage per hectare |
| `application_method` | `VARCHAR(100)` | YES | — | How to apply (e.g., "foliar spray", "soil drench") |
| `application_timing` | `VARCHAR(255)` | YES | — | When to apply |
| `organic` | `BOOLEAN` | YES | `false` | Whether the treatment is organic-certified |
| `restricted_use` | `BOOLEAN` | YES | `false` | Whether the chemical is restricted-use |
| `required_ppe` | `TEXT[]` | YES | — | Required personal protective equipment |
| `reentry_interval_hours` | `INTEGER` | YES | — | Hours before field re-entry is safe |
| `pre_harvest_interval_days` | `INTEGER` | YES | — | Days before harvest when application must stop |
| `withdrawal_period_days` | `INTEGER` | YES | — | Withdrawal period in days |
| `estimated_cost_per_ha_usd` | `NUMERIC(10,2)` | YES | — | Estimated treatment cost per hectare |
| `effectiveness_rating` | `NUMERIC(3,2)` | YES | — | Effectiveness rating (0–5) |
| `expected_results_days` | `INTEGER` | YES | — | Expected days until results are visible |
| `accepted_by_farmer` | `BOOLEAN` | YES | — | Whether the farmer accepted the recommendation |
| `accepted_at` | `TIMESTAMPTZ` | YES | — | When the farmer accepted |
| `applied` | `BOOLEAN` | YES | `false` | Whether the treatment was applied |
| `applied_at` | `TIMESTAMPTZ` | YES | — | When the treatment was applied |
| `application_notes` | `TEXT` | YES | — | Notes from the application |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |

---

### 4.4 `soil_readings`

Soil analysis data from IoT sensors, manual tests, or lab analyses. Tracks moisture, pH, nutrients, and other soil health indicators.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique reading identifier |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the field sampled |
| `location_geojson` | `JSONB` | YES | — | GeoJSON point of sample location |
| `sample_depth_cm` | `INTEGER` | YES | — | Sampling depth in centimeters (> 0) |
| `sample_depth_range` | `VARCHAR(50)` | YES | — | Depth range description (e.g., "0-15cm") |
| `moisture_pct` | `NUMERIC(5,2)` | YES | — | Soil moisture percentage (0–100) |
| `temperature_c` | `NUMERIC(5,2)` | YES | — | Soil temperature in Celsius |
| `ph` | `NUMERIC(4,2)` | YES | — | Soil pH (0–14) |
| `nitrogen_ppm` | `NUMERIC(8,2)` | YES | — | Nitrogen content in parts per million |
| `phosphorus_ppm` | `NUMERIC(8,2)` | YES | — | Phosphorus content in ppm |
| `potassium_ppm` | `NUMERIC(8,2)` | YES | — | Potassium content in ppm |
| `organic_matter_pct` | `NUMERIC(5,2)` | YES | — | Organic matter percentage |
| `cation_exchange_capacity` | `NUMERIC(6,2)` | YES | — | CEC value |
| `electrical_conductivity_ms_cm` | `NUMERIC(8,2)` | YES | — | Electrical conductivity in mS/cm |
| `texture_analysis` | `JSONB` | YES | — | Soil texture breakdown (sand/silt/clay percentages) |
| `source` | `soil_reading_source` | NO | — | Data source: IOT_SENSOR, MANUAL_TEST, LAB_ANALYSIS, ESTIMATED |
| `lab_name` | `VARCHAR(255)` | YES | — | Name of the testing laboratory |
| `lab_report_url` | `TEXT` | YES | — | URL to the lab report |
| `recorded_by` | `VARCHAR` | YES | — | FK → `users.id`; who recorded the reading |
| `recorded_at` | `TIMESTAMPTZ` | NO | — | When the reading was taken |
| `weather_conditions` | `VARCHAR(255)` | YES | — | Weather at time of sampling |
| `days_since_rain` | `INTEGER` | YES | — | Days since last rainfall |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

---

## 5. Weather Services

### 5.1 `weather_forecasts`

Weather forecast data for fields, sourced from various meteorological services. Includes risk assessment for agricultural planning.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique forecast identifier |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the field this forecast applies to |
| `source` | `weather_source` | NO | — | Data source: NOAA_GFS, NOAA_HRRR, OPEN_METEO, LOCAL_STATION, MANUAL |
| `forecast_date` | `DATE` | NO | — | Date the forecast is for |
| `forecast_hour` | `INTEGER` | YES | — | Specific hour (0–23) if hourly forecast |
| `forecast_horizon_hours` | `INTEGER` | YES | — | How far ahead the forecast looks |
| `issued_at` | `TIMESTAMPTZ` | NO | — | When the forecast was issued |
| `temperature_min_c` | `NUMERIC(5,2)` | YES | — | Minimum temperature in Celsius |
| `temperature_max_c` | `NUMERIC(5,2)` | YES | — | Maximum temperature in Celsius |
| `temperature_avg_c` | `NUMERIC(5,2)` | YES | — | Average temperature in Celsius |
| `precipitation_probability_pct` | `NUMERIC(5,2)` | YES | — | Precipitation probability (0–100) |
| `precipitation_mm` | `NUMERIC(8,2)` | YES | — | Expected precipitation in millimeters |
| `precipitation_type` | `VARCHAR(50)` | YES | — | Type: "rain", "snow", "sleet", etc. |
| `wind_speed_max_mps` | `NUMERIC(6,2)` | YES | — | Maximum wind speed in meters/second |
| `wind_direction_deg` | `INTEGER` | YES | — | Wind direction in degrees |
| `humidity_avg_pct` | `NUMERIC(5,2)` | YES | — | Average humidity percentage |
| `pressure_hpa` | `NUMERIC(7,2)` | YES | — | Atmospheric pressure in hectopascals |
| `growing_degree_days_accumulated` | `NUMERIC(8,2)` | YES | — | Accumulated growing degree days |
| `evapotranspiration_mm` | `NUMERIC(6,2)` | YES | — | Evapotranspiration in millimeters |
| `risk_type` | `risk_type` | YES | — | Agricultural risk type (FROST, DROUGHT, FLOOD, etc.) |
| `risk_level` | `risk_level` | YES | — | Risk severity: MINIMAL, LOW, MEDIUM, HIGH, CRITICAL |
| `risk_description` | `TEXT` | YES | — | Human-readable risk description |
| `risk_confidence_pct` | `NUMERIC(5,2)` | YES | — | Confidence in risk assessment |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |
| `expires_at` | `TIMESTAMPTZ` | YES | — | TTL expiration for data retention (added in `weather_service_improvements`) |

**Indexes:** `ix_weather_forecasts_field_date`, `ix_weather_forecasts_field_issued`, `ix_weather_forecasts_risk`, `idx_weather_forecasts_field_date`

---

### 5.2 `weather_snapshots`

Actual observed weather data for fields — current conditions recorded from weather stations and sensors.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique snapshot identifier |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the field this observation applies to |
| `source` | `weather_source` | NO | — | Data source |
| `source_station_id` | `VARCHAR(100)` | YES | — | Weather station identifier |
| `source_station_distance_km` | `NUMERIC(6,2)` | YES | — | Distance from field to weather station |
| `recorded_at` | `TIMESTAMPTZ` | NO | — | When the observation was recorded |
| `temperature_c` | `NUMERIC(5,2)` | YES | — | Temperature in Celsius |
| `feels_like_c` | `NUMERIC(5,2)` | YES | — | "Feels like" temperature |
| `humidity_pct` | `NUMERIC(5,2)` | YES | — | Humidity percentage (0–100) |
| `pressure_hpa` | `NUMERIC(7,2)` | YES | — | Atmospheric pressure |
| `wind_speed_mps` | `NUMERIC(6,2)` | YES | — | Wind speed in meters/second |
| `wind_direction_deg` | `INTEGER` | YES | — | Wind direction in degrees (0–360) |
| `wind_gust_mps` | `NUMERIC(6,2)` | YES | — | Wind gust speed |
| `rainfall_mm` | `NUMERIC(8,2)` | YES | — | Rainfall in millimeters |
| `rainfall_intensity` | `VARCHAR(50)` | YES | — | Rainfall intensity description |
| `snowfall_mm` | `NUMERIC(6,2)` | YES | — | Snowfall in millimeters |
| `cloud_cover_pct` | `NUMERIC(5,2)` | YES | — | Cloud cover percentage (0–100) |
| `visibility_m` | `NUMERIC(8,2)` | YES | — | Visibility in meters |
| `uv_index` | `NUMERIC(4,2)` | YES | — | UV index |
| `soil_temperature_c` | `NUMERIC(5,2)` | YES | — | Soil temperature |
| `soil_moisture_pct` | `NUMERIC(5,2)` | YES | — | Soil moisture percentage |
| `leaf_wetness_hours` | `NUMERIC(4,1)` | YES | — | Hours of leaf wetness |
| `evapotranspiration_mm` | `NUMERIC(6,2)` | YES | — | Evapotranspiration |
| `growing_degree_days` | `NUMERIC(8,2)` | YES | — | Growing degree days |
| `raw_data` | `JSONB` | YES | — | Raw API response data |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |
| `expires_at` | `TIMESTAMPTZ` | YES | — | TTL expiration for data retention (added in `weather_service_improvements`) |

**Indexes:** `ix_weather_snapshots_field_recorded`, `ix_weather_snapshots_field_latest`, `idx_weather_snapshots_field_date`, `idx_weather_snapshots_source`

---

### 5.3 `weather_alert_subscriptions`

Per-user, per-field subscriptions for weather alert notifications with configurable thresholds and notification channels.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique subscription identifier |
| `user_id` | `VARCHAR` | NO | — | FK → `users.id`; the subscribing user (CASCADE delete) |
| `field_id` | `UUID` | YES | — | FK → `fields.id`; the field to monitor (CASCADE delete) |
| `alert_type` | `VARCHAR(50)` | NO | — | Type of alert to subscribe to |
| `enabled` | `BOOLEAN` | YES | `true` | Whether the subscription is active |
| `notify_email` | `BOOLEAN` | YES | `true` | Send email notifications |
| `notify_sms` | `BOOLEAN` | YES | `false` | Send SMS notifications |
| `notify_push` | `BOOLEAN` | YES | `true` | Send push notifications |
| `threshold_value` | `NUMERIC` | YES | — | Custom threshold value for triggering alerts |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |

**Constraints:** UNIQUE on `(user_id, field_id, alert_type)`
**Indexes:** `ix_weather_subscriptions_user`, `ix_weather_subscriptions_field`

---

## 6. Supply Chain & Traceability

### 6.1 `crop_cycle_products`

Links crop cycles to marketplace products, tracking how much of a harvest was converted into a product listing.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique link identifier |
| `crop_cycle_id` | `UUID` | NO | — | FK → `crop_cycles.id`; source crop cycle |
| `product_id` | `VARCHAR` | NO | — | FK → `products.id`; resulting product listing |
| `quantity_kg` | `NUMERIC(12,2)` | NO | — | Quantity in kilograms (> 0) |
| `quality_grade` | `VARCHAR(50)` | YES | — | Quality grade of this portion |
| `harvest_date` | `DATE` | NO | — | Harvest date |
| `lot_number` | `VARCHAR(100)` | YES | — | Lot/batch number |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

**Constraints:** UNIQUE on `(crop_cycle_id, product_id, harvest_date, lot_number)`

---

### 6.2 `order_field_sources`

Tracks which fields (and crop cycles) contributed to fulfilling a specific order — enabling field-to-fork traceability.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique link identifier |
| `order_id` | `VARCHAR` | NO | — | FK → `orders.id`; the order being fulfilled |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the source field |
| `crop_cycle_id` | `UUID` | YES | — | FK → `crop_cycles.id`; the source crop cycle |
| `quantity_kg` | `NUMERIC(12,2)` | NO | — | Quantity sourced from this field (> 0) |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

---

### 6.3 `escrow_field_conditions`

Defines field-level conditions that must be met before escrow funds can be released (e.g., quality verification, delivery confirmation).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique condition identifier |
| `escrow_id` | `VARCHAR` | NO | — | FK → `escrows.id`; the escrow account |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the field this condition applies to |
| `condition_type` | `VARCHAR(100)` | NO | — | Type of condition (e.g., "QC_PASSED", "DELIVERY_CONFIRMED") |
| `met` | `BOOLEAN` | YES | `false` | Whether the condition has been satisfied |
| `met_at` | `TIMESTAMPTZ` | YES | — | When the condition was met |
| `metadata` | `JSONB` | YES | `'{}'` | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

---

## 7. Risk & Alerts

### 7.1 `field_risk_scores`

Composite risk scores for fields, aggregating weather, pest, soil, and other risk factors into a single 0–100 score.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique score identifier |
| `field_id` | `UUID` | NO | — | FK → `fields.id`; the assessed field |
| `crop_cycle_id` | `UUID` | YES | — | FK → `crop_cycles.id`; associated crop cycle |
| `score_date` | `DATE` | NO | — | Date of the risk assessment |
| `overall_score` | `NUMERIC(5,2)` | NO | — | Overall risk score (0–100, higher = riskier) |
| `risk_trend` | `VARCHAR(20)` | YES | — | Trend direction (e.g., "increasing", "stable", "decreasing") |
| `metadata` | `JSONB` | YES | `'{}'` | Breakdown of individual risk factors |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

**Indexes:** `ix_field_risk_scores_field_date`, `ix_field_risk_scores_crop_cycle`

---

### 7.2 `alerts`

User-facing alerts and notifications for weather warnings, pest detections, task reminders, financial events, and system notifications.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` (PK) | NO | `gen_random_uuid()` | Unique alert identifier |
| `user_id` | `VARCHAR` | NO | — | FK → `users.id`; the recipient user |
| `field_id` | `UUID` | YES | — | FK → `fields.id`; related field (if applicable) |
| `alert_type` | `alert_type` | NO | — | Alert category: WEATHER_WARNING, FROST_ALERT, DROUGHT_ALERT, PEST_DETECTED, DISEASE_DETECTED, NDVI_ANOMALY, SOIL_MOISTURE_LOW/HIGH, TASK_OVERDUE, HARVEST_READY, LOAN_RISK, PAYMENT_DUE, ESCROW_HOLD, PRICE_ALERT, SYSTEM_NOTIFICATION |
| `severity` | `alert_severity` | NO | — | Severity: INFO, WARNING, CRITICAL, EMERGENCY |
| `title` | `VARCHAR(255)` | NO | — | Alert title |
| `message` | `TEXT` | NO | — | Alert message body |
| `acknowledged` | `BOOLEAN` | YES | `false` | Whether the user has acknowledged the alert |
| `metadata` | `JSONB` | YES | `'{}'` | Additional alert context |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Alert creation timestamp |
| `is_active` | `BOOLEAN` | NO | `true` | Whether the alert is still active (added in `weather_service_improvements`) |

**Indexes:** `ix_alerts_user_active`, `ix_alerts_field`, `ix_alerts_type_severity`

---

## 8. Harvest Event Tracking & QC

### 8.1 `harvest_events`

Granular field-level harvest event records with weight, moisture, photos, and GPS data. Feeds into batch aggregation.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique event identifier |
| `farm_id` | `VARCHAR` | NO | — | FK → `users.id`; the farm owner (CASCADE delete) |
| `field_id` | `VARCHAR` | NO | — | Field identifier |
| `crop_cycle_id` | `VARCHAR` | YES | — | Associated crop cycle ID |
| `collected_by` | `VARCHAR` | YES | — | FK → `users.id`; who collected the harvest (SET NULL on delete) |
| `harvested_at` | `TIMESTAMPTZ` | NO | — | Harvest timestamp |
| `gross_weight_kg` | `FLOAT` | NO | — | Gross weight in kilograms |
| `moisture_pct` | `FLOAT` | YES | — | Moisture percentage at harvest |
| `loss_kg` | `FLOAT` | YES | — | Post-harvest loss in kilograms |
| `photos` | `JSONB` | YES | — | Array of photo metadata with EXIF/geo data |
| `weighbridge_receipt` | `JSONB` | YES | — | Weighbridge receipt metadata |
| `location` | `JSONB` | YES | — | GeoJSON location of harvest |
| `notes` | `TEXT` | YES | — | Free-text notes |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

**Indexes:** `idx_harvest_events_farm_id`, `idx_harvest_events_field_id`, `idx_harvest_events_crop_cycle_id`, `idx_harvest_events_harvested_at`

---

### 8.2 `harvest_batches`

Aggregated batches of multiple harvest events. Supports sealing (immutability), lineage hashing for tamper detection, and QC workflow.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique batch identifier |
| `batch_code` | `VARCHAR(100)` (UNIQUE) | NO | — | Human-readable batch code |
| `aggregator_id` | `VARCHAR` | YES | — | FK → `users.id`; who aggregated the batch |
| `status` | `harvest_batch_state_enum` | NO | `'DRAFT'` | Batch state: DRAFT, SEALED, QC_PENDING, QC_PASSED, QC_FAILED, ARCHIVED |
| `aggregated_weight_kg` | `FLOAT` | YES | — | Total aggregated weight |
| `moisture_avg` | `FLOAT` | YES | — | Average moisture across contributions |
| `sealed_at` | `TIMESTAMPTZ` | YES | — | When the batch was sealed (made immutable) |
| `sealed_by` | `VARCHAR` | YES | — | Who sealed the batch |
| `seal_evidence` | `JSONB` | YES | — | References to receipts, photos, signatures used for sealing |
| `lineage_hash` | `VARCHAR(200)` | YES | — | SHA-256 hash of canonical JSON for tamper detection |
| `lineage_signature` | `VARCHAR(500)` | YES | — | Optional cryptographic signature |
| `notes` | `TEXT` | YES | — | Free-text notes |
| `metadata` | `JSONB` | YES | — | Flexible metadata |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

**Constraints:** `uq_harvest_batch_code` (unique on `batch_code`)
**Indexes:** `idx_harvest_batches_aggregator_id`, `idx_harvest_batches_status`
**Triggers:** `trg_prevent_sealed_contribution` — prevents INSERT/UPDATE/DELETE on contributions when the batch status is `SEALED`

---

### 8.3 `harvest_batch_contributions`

Many-to-many join table linking individual harvest events to harvest batches, tracking each farmer's contribution.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique contribution identifier |
| `harvest_batch_id` | `VARCHAR` | NO | — | FK → `harvest_batches.id`; the batch (CASCADE delete) |
| `harvest_event_id` | `VARCHAR` | NO | — | FK → `harvest_events.id`; the harvest event (CASCADE delete) |
| `farmer_id` | `VARCHAR` | NO | — | FK → `users.id`; the contributing farmer (CASCADE delete) |
| `contributed_weight_kg` | `FLOAT` | NO | — | Weight contributed from this event |
| `reported_moisture_pct` | `FLOAT` | YES | — | Moisture percentage reported at contribution |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Record creation timestamp |

**Constraints:** `uq_batch_event_contribution` (unique on `[harvest_batch_id, harvest_event_id]`)
**Indexes:** `idx_contributions_batch_id`, `idx_contributions_event_id`, `idx_contributions_farmer_id`
**Protected by:** `trg_prevent_sealed_contribution` trigger (append-only after batch sealing)

---

### 8.4 `product_batch_sources`

Many-to-many join table linking product batches (marketplace) to harvest batches (supply chain), enabling full traceability from product to field.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique link identifier |
| `product_batch_id` | `VARCHAR` | NO | — | FK → `product_batches.id`; the product batch (CASCADE delete) |
| `harvest_batch_id` | `VARCHAR` | NO | — | FK → `harvest_batches.id`; the source harvest batch (CASCADE delete) |
| `contribution_weight_kg` | `FLOAT` | NO | — | Weight contributed from the harvest batch |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Record creation timestamp |

**Constraints:** `uq_product_batch_source` (unique on `[product_batch_id, harvest_batch_id]`)
**Indexes:** `idx_product_batch_sources_product`, `idx_product_batch_sources_harvest`

---

### 8.5 `audit_events`

Immutable audit trail for traceability. Records all significant events with payload hashing and chain-linking for tamper detection.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique audit event identifier |
| `event_type` | `VARCHAR(100)` | NO | — | Event type (e.g., "batch.created", "batch.sealed", "qc.passed") |
| `entity_type` | `VARCHAR(50)` | NO | — | Entity type (e.g., "harvest_batch", "product_listing") |
| `entity_id` | `VARCHAR` | NO | — | ID of the entity this event relates to |
| `payload` | `JSONB` | YES | — | Event payload data |
| `payload_hash` | `VARCHAR(200)` | YES | — | Hash of the payload for verification |
| `previous_event_hash` | `VARCHAR(200)` | YES | — | Hash of the previous event (blockchain-style chain) |
| `user_id` | `VARCHAR` | YES | — | User who triggered the event |
| `signature` | `VARCHAR(500)` | YES | — | Optional cryptographic signature |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Event timestamp |

**Indexes:** `idx_audit_events_entity` (on `[entity_type, entity_id]`), `idx_audit_events_type`, `idx_audit_events_created`

---

### 8.6 `lab_providers`

Registry of laboratory providers that perform quality control testing on harvest batches.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique lab provider identifier |
| `name` | `VARCHAR(255)` | NO | — | Laboratory name |
| `public_key` | `TEXT` | YES | — | PEM-encoded public key for verifying lab-signed QC reports |
| `metadata` | `JSONB` | YES | — | Additional lab information |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

**Indexes:** `idx_lab_providers_name`

---

### 8.7 `samples`

Physical samples collected from harvest batches and sent to labs for quality testing. Tracks chain of custody.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique sample identifier |
| `sample_code` | `VARCHAR(100)` (UNIQUE) | NO | — | Human-readable sample code |
| `harvest_batch_id` | `VARCHAR` | NO | — | FK → `harvest_batches.id`; the batch sampled (CASCADE delete) |
| `collected_by` | `VARCHAR` | YES | — | FK → `users.id`; who collected the sample |
| `collected_at` | `TIMESTAMPTZ` | YES | — | When the sample was collected |
| `sample_points` | `JSONB` | YES | — | GPS points or summary of where samples were taken |
| `photos` | `JSONB` | YES | — | Array of photo metadata `{url, hash, exif}` |
| `chain_of_custody` | `JSONB` | YES | — | Chain of custody records |
| `submitted_to_lab` | `BOOLEAN` | NO | `false` | Whether the sample has been submitted to a lab |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

**Indexes:** `idx_samples_harvest_batch_id`, `idx_samples_sample_code` (unique)

---

### 8.8 `batch_qc_reports`

Quality control test results for harvest batches, including lab metrics, grading, and digital signatures for verification.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique QC report identifier |
| `batch_id` | `VARCHAR` | NO | — | FK → `harvest_batches.id`; the tested batch (CASCADE delete) |
| `sample_id` | `VARCHAR` | YES | — | FK → `samples.id`; the sample tested (SET NULL on delete) |
| `lab_id` | `VARCHAR` | YES | — | FK → `lab_providers.id`; the testing lab (SET NULL on delete) |
| `tested_at` | `TIMESTAMPTZ` | NO | — | When the test was performed |
| `metrics` | `JSONB` | YES | — | Test results: `{moisture_pct, aflatoxin_ppb, foreign_matter_pct, ...}` |
| `grade` | `qc_grade_enum` | YES | — | Assigned grade: GRADE_A, GRADE_B, GRADE_C, REJECT |
| `passed` | `BOOLEAN` | NO | — | Whether the batch passed QC |
| `report_url` | `VARCHAR(500)` | YES | — | URL to the full lab report |
| `signed_hash` | `VARCHAR(200)` | YES | — | Lab-supplied digital signature or hash |
| `verified` | `BOOLEAN` | NO | `false` | Whether the signature was successfully verified |
| `notes` | `TEXT` | YES | — | Additional notes |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

**Indexes:** `idx_qc_reports_batch_id`, `idx_qc_reports_lab_id`, `idx_qc_reports_sample_id`

---

### 8.9 `certifications`

Certifications attached to harvest batches (organic, fair trade, etc.) with validity periods and digital signatures.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique certification identifier |
| `harvest_batch_id` | `VARCHAR` | NO | — | FK → `harvest_batches.id`; the certified batch (CASCADE delete) |
| `issuer` | `VARCHAR(255)` | NO | — | Certifying organization name |
| `cert_type` | `certification_type_enum` | NO | — | Certification type: ORGANIC, FAIRTRADE, RAINFOREST_ALLIANCE, GLOBALGAP, OTHER |
| `cert_number` | `VARCHAR(100)` | YES | — | Certificate number |
| `valid_from` | `TIMESTAMPTZ` | NO | — | Certification validity start |
| `valid_to` | `TIMESTAMPTZ` | NO | — | Certification validity end |
| `cert_url` | `VARCHAR(500)` | YES | — | URL to the certificate document |
| `signed_hash` | `VARCHAR(200)` | YES | — | Digital signature of the certificate |
| `metadata` | `JSONB` | YES | — | Additional certification data |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |

**Indexes:** `idx_certifications_harvest_batch_id`, `idx_certifications_type`

---

### 8.10 `qc_grade_rules`

Configurable threshold rules for automatic QC grading. Defines what metrics and thresholds determine each grade for each commodity.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique rule identifier |
| `commodity` | `VARCHAR(100)` | NO | — | Commodity name (e.g., "maize", "coffee", "wheat") |
| `grade` | `qc_grade_enum` | NO | — | Target grade: GRADE_A, GRADE_B, GRADE_C, REJECT |
| `rules` | `JSONB` | NO | — | Array of threshold rules: `[{"metric":"moisture_pct","op":"<=","value":13.0}, ...]` |
| `is_active` | `BOOLEAN` | NO | `true` | Whether the rule is active |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |

**Indexes:** `idx_qc_grade_rules_commodity`
**Seeded Data:** 7 default rules for maize (A/B/C), wheat (A/B), and coffee (A/B)

---

## 9. Inventory Management

### 9.1 `inventory_movements`

Event-sourced inventory ledger tracking every stock change (additions, reservations, sales, spoilage, returns, adjustments).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | `gen_random_uuid()` | Unique movement identifier |
| `product_id` | `VARCHAR` | NO | — | FK → `products.id`; the affected product |
| `batch_id` | `VARCHAR` | YES | — | FK → `product_batches.id`; the affected batch (if batch-level) |
| `movement_type` | `inventory_movement_type_enum` | NO | — | Type: STOCK_IN, RESERVATION, RESERVATION_RELEASE, SALE_CONFIRMED, SPOILAGE, RETURN, ADJUSTMENT, EXPIRY |
| `quantity` | `FLOAT` | NO | — | Quantity moved (positive value; direction implied by type) |
| `reference_type` | `VARCHAR(50)` | NO | — | What triggered this movement (e.g., "ORDER", "MANUAL", "SYSTEM") |
| `reference_id` | `VARCHAR` | NO | — | ID of the triggering entity |
| `notes` | `TEXT` | YES | — | Free-text notes |
| `created_by` | `VARCHAR` | YES | — | User who initiated the movement |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Movement timestamp |

**Indexes:** `idx_inv_movements_product` (on `product_id`), `idx_inv_movements_ref` (on `[reference_type, reference_id]`)

---

## 10. Delivery Workflow

### 10.1 `deliveries`

Tracks the delivery lifecycle for orders, including carrier assignment, pickup/delivery timestamps, and proof of delivery.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR` (PK) | NO | — | Unique delivery identifier |
| `order_id` | `VARCHAR` | NO | — | Associated order ID (indexed) |
| `carrier_id` | `VARCHAR` | NO | — | ID of the delivery carrier/driver (indexed) |
| `status` | `delivery_status_enum` | NO | `'ASSIGNED'` | Delivery status: ASSIGNED, PICKED_UP, IN_TRANSIT, DELIVERED, FAILED, CANCELLED |
| `pickup_time` | `TIMESTAMPTZ` | YES | — | When the carrier picked up the goods |
| `delivered_time` | `TIMESTAMPTZ` | YES | — | When the goods were delivered |
| `pickup_photo_url` | `VARCHAR` | YES | — | Photo proof of pickup |
| `delivery_photo_url` | `VARCHAR` | YES | — | Photo proof of delivery |
| `recipient_signature_url` | `VARCHAR` | YES | — | Digital signature from the recipient |
| `notes` | `VARCHAR` | YES | — | Delivery notes |
| `created_at` | `TIMESTAMPTZ` | YES | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | YES | `now()` | Last update timestamp |

---

## 11. Enum Types Reference

| Enum Name | Values | Used In |
|-----------|--------|---------|
| `user_role_enum` | FARMER, MERCHANT, DELIVERY, AGENT, MANAGER, ADMIN, MODERATOR, AGRONOMIST, FIELD_ANALYST | `users.role` |
| `onboarding_status_enum` | PENDING_REVIEW, ACTIVE, REJECTED | `users.onboarding_status` |
| `category_enum` | GRAINS, VEGETABLES, FRUITS, DAIRY, MEAT, SPICES, OTHER | `products.category` |
| `unit_enum` | KG, TON, LITER, UNIT, CRATE, BAG | `products.unit`, `harvests.unit` |
| `quality_grade_enum` | GRADE_A, GRADE_B, GRADE_C, PREMIUM, STANDARD, A, B, C | `products.quality_grade`, `product_batches.quality_grade`, `harvests.quality_grade` |
| `order_status_enum` | CREATED, PENDING_PAYMENT, FUNDED, CONFIRMED, IN_DELIVERY, DELIVERED, DELIVERY_FAILED, RETURNED, COMPLETED, CANCELLED, EXPIRED | `orders.status` |
| `escrow_state_enum` | CREATED, FUNDED, RELEASED, REFUNDED, DISPUTED, SETTLED, REVERSED | `escrows.state` |
| `provider_enum` | BANK, WALLET | `escrows.provider` |
| `delivery_status_enum` | ASSIGNED, PICKED_UP, IN_TRANSIT, DELIVERED, FAILED, CANCELLED | `deliveries.status` |
| `dispute_resolution_enum` | RELEASE, PARTIAL_RELEASE, REFUND | (defined but disputes table is commented out) |
| `rule_type_enum` | PLATFORM_FEE, DELIVERY, QUALITY, DISTANCE | `pricing_rules.rule_type` |
| `fee_type_enum` | PERCENTAGE, FIXED | `pricing_rules.fee_type` |
| `aggregate_type_enum` | USER, ESCROW, SYSTEM | `ledger_events.aggregate_type` |
| `ledger_event_type_enum` | ESCROW_FUNDED, ESCROW_RELEASED, ESCROW_REFUNDED, PLATFORM_FEE_COLLECTED, PENALTY_APPLIED, LOAN_DISBURSED, LOAN_REPAID | `ledger_events.event_type` |
| `direction_enum` | DEBIT, CREDIT | `ledger_events.direction` |
| `reference_type_enum` | ORDER, ESCROW, DISPUTE, LOAN | `ledger_events.reference_type` |
| `owner_type_enum` | USER, ESCROW, SYSTEM | `accounts.owner_type` |
| `account_type_enum` | ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE | `accounts.account_type` |
| `inventory_movement_type_enum` | STOCK_IN, RESERVATION, RESERVATION_RELEASE, SALE_CONFIRMED, SPOILAGE, RETURN, ADJUSTMENT, EXPIRY | `inventory_movements.movement_type` |
| `crop_cycle_status` | PLANNED, PLANTED, GROWING, HARVESTED, PARTIALLY_HARVESTED, FAILED, ABANDONED | `crop_cycles.status` |
| `ndvi_source` | SENTINEL_2, LANDSAT_8, LANDSAT_9, MODIS, MANUAL | `ndvi_snapshots.source` |
| `stress_level` | NONE, LOW, MEDIUM, HIGH, CRITICAL | `ndvi_snapshots.stress_level` |
| `soil_reading_source` | IOT_SENSOR, MANUAL_TEST, LAB_ANALYSIS, ESTIMATED | `soil_readings.source` |
| `severity_level` | TRACE, LOW, MEDIUM, HIGH, SEVERE | `pest_disease_reports.severity` |
| `recommendation_source` | AGRONOMIST, SYSTEM, AI_MODEL, COMMUNITY | `treatment_recommendations.recommendation_source` |
| `task_type` | LAND_PREPARATION, SOWING, PLANTING, IRRIGATION, FERTILIZATION, WEEDING, PEST_CONTROL, DISEASE_CONTROL, PRUNING, THINNING, HARVESTING, POST_HARVEST, INSPECTION, MAINTENANCE, OTHER | (defined for task management) |
| `task_status` | PENDING, SCHEDULED, IN_PROGRESS, COMPLETED, SKIPPED, CANCELLED, OVERDUE | (defined for task management) |
| `task_priority` | LOW, MEDIUM, HIGH, URGENT | (defined for task management) |
| `weather_source` | NOAA_GFS, NOAA_HRRR, OPEN_METEO, LOCAL_STATION, MANUAL | `weather_forecasts.source`, `weather_snapshots.source` |
| `risk_type` | FROST, FREEZE, HEAT_STRESS, DROUGHT, HEAVY_RAIN, FLOOD, HAIL, STRONG_WIND, STORM, HURRICANE, TORNADO, WILDFIRE, PEST_OUTBREAK, DISEASE_OUTBREAK | `weather_forecasts.risk_type` |
| `risk_level` | MINIMAL, LOW, MEDIUM, HIGH, CRITICAL | `weather_forecasts.risk_level` |
| `alert_type` | WEATHER_WARNING, FROST_ALERT, DROUGHT_ALERT, PEST_DETECTED, DISEASE_DETECTED, NDVI_ANOMALY, SOIL_MOISTURE_LOW, SOIL_MOISTURE_HIGH, TASK_OVERDUE, HARVEST_READY, LOAN_RISK, PAYMENT_DUE, ESCROW_HOLD, PRICE_ALERT, SYSTEM_NOTIFICATION | `alerts.alert_type` |
| `alert_severity` | INFO, WARNING, CRITICAL, EMERGENCY | `alerts.severity` |
| `advisory_status` | REQUESTED, SCHEDULED, OPEN, IN_PROGRESS, RESOLVED, CLOSED, CANCELLED | (defined for advisory service) |
| `advisory_topic` | CROP_SELECTION, PEST_MANAGEMENT, DISEASE_MANAGEMENT, SOIL_HEALTH, IRRIGATION, FERTILIZATION, HARVEST_TIMING, POST_HARVEST, MARKET_ADVICE, FINANCIAL_PLANNING, GENERAL | (defined for advisory service) |
| `message_type` | TEXT, IMAGE, DOCUMENT, VOICE, VIDEO, LOCATION, SYSTEM | (defined for messaging) |
| `harvest_batch_state_enum` | DRAFT, SEALED, QC_PENDING, QC_PASSED, QC_FAILED, ARCHIVED | `harvest_batches.status` |
| `qc_grade_enum` | GRADE_A, GRADE_B, GRADE_C, REJECT | `batch_qc_reports.grade`, `qc_grade_rules.grade` |
| `batch_qc_state_enum` | QC_PENDING, QC_PASSED, QC_FAILED | (defined for batch QC workflow) |
| `certification_type_enum` | ORGANIC, FAIRTRADE, RAINFOREST_ALLIANCE, GLOBALGAP, OTHER | `certifications.cert_type` |

---

## 12. Database Triggers & Functions

| Trigger | Table | Function | Description |
|---------|-------|----------|-------------|
| `trg_prevent_sealed_contribution` | `harvest_batch_contributions` | `prevent_sealed_batch_contribution()` | Prevents INSERT, UPDATE, or DELETE on contributions when the parent `harvest_batches` record has status = `'SEALED'`. Enforces append-only immutability after batch sealing. |

---

## 13. Migration History (Chronological Order)

| # | Revision | Description |
|---|----------|-------------|
| 1 | `001_create_core_tables` | Creates `users`, `products`, `product_batches`, `orders`, `escrows` tables and core enums |
| 2 | `add_pricing_rules` | Creates `pricing_rules` table with fee/delivery/quality/distance rules |
| 3 | `835594adc649` | Creates accounting tables: `ledger_events`, `accounts`, `journal_entries`, `journal_lines` |
| 4 | `dae300f4c591` | Adds `keycloak_id` column to `users` for SSO integration |
| 5 | `a8391ae9c1a3` | Agricultural Intelligence: creates `farms`, `fields`, `crop_cycles`, `ndvi_snapshots`, `pest_disease_reports`, `treatment_recommendations`, `soil_readings`, `weather_forecasts`, `weather_snapshots`, `crop_cycle_products`, `order_field_sources`, `escrow_field_conditions`, `field_risk_scores`, `alerts` |
| 6 | `dbaab859c21c` | Adds MODERATOR, AGRONOMIST, FIELD_ANALYST to `user_role_enum` |
| 7 | `add_accounts_owner_index` | Adds composite index on `accounts` for efficient lookups |
| 8 | `weather_service_improvements` | Adds weather indexes, TTL columns, `weather_alert_subscriptions` table, `is_active` to alerts |
| 9 | `weather_indexes` | Adds additional performance indexes for weather queries |
| 10 | `harvest_mgmt_v1` | Creates `harvests` table, adds `harvest_id`/`crop_cycle_id` to products |
| 11 | `5c3bb23bb69d` | Adds DAIRY, MEAT, SPICES, OTHER to `category_enum` |
| 12 | `5b1a6834b62d` | Enforces NOT NULL on `products.category` and `products.base_price` |
| 13 | `inventory_mgmt_v1` | Creates `inventory_movements`, adds inventory tracking columns to products and orders |
| 14 | `harvest_events_v1` | Creates `harvest_events`, `harvest_batches`, `harvest_batch_contributions`, `product_batch_sources`, `audit_events` with sealed-batch trigger |
| 15 | `harvest_events_v2` | Creates `lab_providers`, `samples`, `batch_qc_reports`, `certifications`, `qc_grade_rules` |
| 16 | `dispute_and_user_onboarding_v1` | Adds `onboarding_status`/`onboarding_agent_id` to users (disputes table commented out) |
| 17 | `add_delivery_workflow` | Creates `deliveries` table with delivery status tracking |