# FarmConnect Backend Implementation Plan & AI Prompts

This document breaks down the findings from the `backend_gap_analysis.md` into actionable development phases. For each phase, a **Copy-Paste AI Prompt** is provided. You can paste these directly into your AI assistant in future sessions to automatically execute the requested backend modifications.

---

## Phase 1: Core Enhancements & Quick Wins
**Goal:** Modify existing CRUD endpoints to fully support the frontend's visual requirements (Interactive Maps, Settings, and Farm-to-Table Catalog) before tackling complex new business logic.

### 1.1 Farm Settings & Interactive Map Support
* **Target Issue:** The frontend `FarmSettings.tsx` form needs to do partial updates, and the `CropColorLegend.tsx` needs a lightweight map endpoint.
* **Backend Components:** `/api/v1/farms/routes.py`, `FarmUpdate` schema.






---

## Phase 2: Actionable Workflows & Logistics
**Goal:** Implement the complex, multi-state workflow endpoints, specifically the "Action-Required Inbox" and the physical Delivery handshake protocols.

### 2.1 The "Actionable Inbox"
* **Target Issue:** Farmers and Merchants need a filtered view of orders that specifically demand an action from *them* based on their role.
* **Backend Components:** `orders/routes.py`, `order_service.py`.

> **Prompt for AI Agent:**
> ```text
> Act as an expert Python backend engineer. Implement Phase 2.1 of our backend gap analysis:
> 
> 1. Create a new endpoint `GET /api/v1/orders/actionable` in `orders/routes.py`. 
> 2. Implement the business logic in `order_service.py`. This endpoint should inspect the requesting user's `UserRole`. 
>    - If the user is a `FARMER`, return orders where the status is `FUNDED` (Escrow locked) and waiting for the farmer to initiate delivery.
>    - If the user is a `MERCHANT`, return orders where the status is `IN_DELIVERY` and waiting for the merchant to `complete` (confirm receipt).
> 
> Ensure this endpoint uses proper RBAC and returns the appropriate DTOs.
> ```

### 2.2 Logistics Tracking & QR Handshake
* **Target Issue:** Background ride-hailing pings and secure QR verification.
* **Backend Components:** `delivery/routes.py`, `delivery_service.py`.

> **Prompt for AI Agent:**
> ```text
> Act as an expert Python backend engineer. Implement Phase 2.2 of our backend gap analysis:
> 
> 1. In `delivery/routes.py`, create `POST /api/v1/delivery/{id}/location-ping`. It should accept a payload `DeliveryLocationUpdate` containing `{lat: float, lng: float, timestamp: datetime}` to support our background-ping tracking UX. 
> 2. Create `GET /api/v1/delivery/{id}/latest-location` to consume this data. Store this ping data efficiently (you may use a Redis cache or a dedicated fast-write SQL table).
> 3. Modify the existing `POST /api/v1/delivery/{delivery_id}/pickup` endpoint. It MUST require a `qr_verification_code` string parameter in its payload, matching our secure "QR Code Handshake" UI protocol. Add validation logic to verify this code against the order/escrow secret before changing the delivery status.
> ```

---

## Phase 3: Agronomic Intelligence (AI & Analytics)
**Goal:** Build out the missing domains for "Human-in-the-loop" AI tracking and end-of-season weather analytics.

### 3.1 AI Escalation (Advisory Tickets)
* **Target Issue:** The AI Diagnosis must be escalable to a human expert.
* **Backend Components:** `advisory` router (needs creation/uncommenting), `ai/routes.py`.

> **Prompt for AI Agent:**
> ```text
> Act as an expert Python backend engineer. Implement Phase 3.1 of our backend gap analysis:
> 
> 1. We need to implement the "Agronomist Escalation" path. Create a new router package for `advisory` (or uncomment existing ones) and register it in `api/v1/router.py`.
> 2. Create an endpoint `POST /api/v1/advisory/tickets`. It should accept a payload that includes an `InitialDiagnosisResponse` (from the AI service) and an Image URL/File.
> 3. Construct the domain entities and service logic to open a ticket (`AdvisoryStatus.OPEN`), assign it to an available user with the `AGRONOMIST` role, and link it to the diagnostic data so a human expert can review the AI's "Differential Diagnosis".
> ```

### 3.2 Weather Post-Mortem Analytics
* **Target Issue:** The frontend needs a single dense endpoint to render a PDF showing how weather impacted final harvest yields.
* **Backend Components:** `reports/routes.py`, `harvest/harvest_routes.py`, `weather/routes.py`.

> **Prompt for AI Agent:**
> ```text
> Act as an expert Python backend engineer. Implement Phase 3.2 of our backend gap analysis:
> 
> 1. In `reports/routes.py`, create a complex aggregation endpoint: `GET /api/v1/reports/crop-cycle/{cycle_id}/post-mortem`.
> 2. The service layer for this endpoint needs to orchestrate queries across multiple domains. It must return a structured payload `PostMortemReportDTO` that contains:
>    - The final registered Yield weight/quality.
>    - A summarized array of historical daily weather spanning from the cycle's `planted_date` to `harvested_date` (rainfall total, temperature median vs extremes).
>    - A log of major anomalies (e.g., severe frost alerts triggering intervention tasks) during that timeframe.
> 
> Focus heavily on cleanly structuring this cross-domain data aggregation so the frontend can easily inject it into a PDF generator.
> ```
