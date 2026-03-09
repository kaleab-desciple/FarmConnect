# Farmer-Merchant Connector UI/UX Design Specification 

This document outlines the cumulative UI/UX design decisions made for the Farmer-Merchant Connector platform across its core functional areas. 

## 1. User Authentication & Role-Based Access Control
The authentication strategy balances broad accessibility for rural users with robust security for corporate roles, leveraging Keycloak integration.

*   **Registration & Authentication (Initial Login uses standard Email/Password):** The platform utilizes a standard, universally understood email/password combination for initial account generation, ensuring cross-platform compatibility and leveraging Keycloak's core capabilities.
*   **Role Selection & Routing (The "Super App" Architecture):** A unified frontend application that dynamically renders role-specific interfaces (e.g., Farmer vs. Merchant) based on the JSON Web Token (JWT) returned by Keycloak. This minimizes deployment overhead while delivering tailored experiences.
*   **Initialization (The "Guided Tour" Overlay):** Upon first login, users land on a functional dashboard but are guided through 3-4 critical features via an interactive modal overlay. This approach is supplemented with localized audio voiceovers to assist users with lower digital literacy.

## 2. Farm Profile & Operations Management
The farm profile serves as the digital twin of the physical operation, prioritizing spatial context and ease of data management.

*   **Farm Creation (Map-First Creation Flow):** The onboarding process prioritizes spatial reality. Users drop a pin or draw their farm boundary on a map, allowing the system to automatically infer location data before asking for manual text input via a progressive bottom sheet.
*   **Profile Dashboard (Interactive Map Dashboard Layer):** The primary view is an interactive map of the farm. High-level metrics and operational data are presented as floating panels or slide-up sheets layered over the geographical context, reinforcing the connection between data and the physical land.
*   **Managing Characteristics (Settings & Preferences Approach):** Static or infrequently changed attributes (e.g., irrigation type, soil history) are organized within a dedicated "Farm Settings" menu to keep the main operational dashboard uncluttered.

## 3. Individual Field Tracking & Mapping
Granular management of specific plots to enable precision agriculture, NDVI monitoring, and focused tasking.

*   **Field Delineation (Tap and Draw Satellite Interface):** Users define field boundaries by tapping points on a high-resolution satellite map. This allows for rapid, precise polygon creation from any location, without requiring the user to physically walk the perimeter.
*   **Field Details (Dedicated "Field Control Room" Page):** Tapping a specific field navigates to a comprehensive, full-screen deep dive. This dedicated dashboard includes tabs for the current crop cycle, ongoing tasks, sensor data, and historical records, favoring detailed analysis over quick actions.
*   **Visualizing Status (Crop Type Color Coding):** The farm map visualizes fields colored by the *currently planted crop* (e.g., Yellow for Maize, Green for Cabbage). Immediate health alerts or warnings are surfaced as overlaid icons (e.g., ⚠️), providing a quick understanding of farm composition and rotation at a glance.

## 4. Complete Crop Lifecycle Monitoring
Tracking the chronological progression of a crop from seed to harvest alongside agronomic events.

*   **Lifecycle Timeline (The "Vertical Activity Feed"):** The lifecycle is visualized as a mobile-friendly, downward-scrolling chronological feed. It acts as an operational journal, intermixing system events, completed tasks, and farmer notes (e.g., similar to a social media timeline).
*   **New Cycle Setup ("Blank Canvas" Manual Entry):** Starting a new cycle prioritizes flexibility. The user manually defines parameters like crop type, seed variety, and target harvest dates without the system auto-generating restrictive task templates, catering to experienced farmers who want total control.
*   **Stage Transition (Manual "Check-in" Gates):** The system relies on ground-truth verification rather than predictive algorithms. Farmers are prompted to manually confirm when a crop transitions between major growth stages (e.g., entering the flowering stage), ensuring high data accuracy.

## 5. Real-Time Field Monitoring & Data Entry
Capturing in-the-moment observations (pests, disease, soil) and visualizing remote sensing data.

*   **Log Observation ("Field-Specific" Clipboard):** Data entry is highly structured. Users must navigate to a specific Field's dashboard before logging an observation, ensuring every data point (e.g., pest severity) is explicitly and accurately tied to the correct geographic polygon.
*   **NDVI Visualization ("Vigor Trend Graph"):** Satellite vegetative index data is distilled into an accessible, 2D line graph showing the average vigor score over time. This approach guarantees extremely fast loading times on weak rural networks while still delivering critical trend insights.

## 6. Harvest Planning, Execution & Yield Recording
Managing the critical transition from field biology to marketplace inventory.

*   **Planning (The "Calendar View" Scheduler):** Harvest forecasting is visualized on a traditional monthly calendar interface, providing excellent long-term visibility for organizing seasonal labor and equipment requirements.
*   **Execution (The "End of Day" Log):** Acknowledging the chaotic reality of harvest day, the act of harvesting is logged retroactively at the end of the day via a simple form, reducing friction during physical work.
*   **Yield Recording ("Yield Only, Quality Later" Approach):** In the field, only the gross harvested volume is recorded, classifying the inventory as pending quality control. Quality grading happens later in a controlled environment, protecting the integrity of the marketplace catalog.

## 7. Agricultural Product Catalog & Inventory
Managing what is available to sell and how buyers discover products.

*   **Farmer Inventory View (The "Funnel" View):** Sellers view their stock through a clear funnel: Total Harvested $\rightarrow$ Reserved (in someone's cart/escrow) $\rightarrow$ Sold. This provides absolute clarity on exactly how much inventory remains available to list publicly.
*   **Merchant Discovery (The "Farm-to-Table" Visual Grid):** The buyer's experience mimics modern, high-end e-commerce. A visually rich, card-based grid heavily features photos of the crop, the farmer, and the farm origin, prioritizing trust and provenance for premium buyers.
*   **Handling Stock-outs ("Optimistic Checkout" Model):** To keep the UI fast and clean, the system assumes inventory is available until the final moment of payment. If two buyers attempt to purchase the same limited stock simultaneously, the slower buyer receives an error modal upon clicking 'Pay', avoiding the complexity of locking inventory during browsing.

## 8. Order Processing & Marketplace Transactions
The financial engine handling the mechanics of B2B agricultural trade and dispute resolution.

*   **Checkout & Payment (Traditional E-Commerce Flow):** A standard, high-familiarity "Add to Cart $\rightarrow$ Review $\rightarrow$ Pay" checkout wizard. It clearly defines the produce price alongside platform and delivery fees before immediate capture via integrated providers (Bank/Wallet).
*   **Farmer Tracking (The "Action-Required" Inbox):** Sellers manage incoming orders through a focused, task-based inbox that only displays orders requiring their immediate physical intervention (e.g., "Schedule Pickup" for a funded order), hiding inactive orders to reduce cognitive load.
*   **Disputes (The "Agent Mediation" Flow):** Disputes are high-friction by design to prevent abuse. Rather than hitting an automated "Reject" button, merchants must initiate a chat with a platform Agent or Moderator who manually investigates and formally opens the dispute, protecting the integrity of the escrow system.

## 9. Delivery Logistics & Tracking
Managing the physical movement of goods and the associated chain of custody.

*   **Driver UI (The "Ride-Hailing" Model):** The delivery app operates like a gig-economy platform (e.g., Uber Freight). Drivers see a map with available jobs popping up dynamically, allowing them to rapidly accept or decline. This maximizes efficiency for a decentralized fleet.
*   **Tracking (Background Ping Hybrid):** Buyers track shipments via confirmed milestones (e.g., "Picked Up"). However, to prevent anxiety during long transits, the driver's app quietly pings its GPS every 15 minutes, allowing buyers to see a static "Last Known Location" without draining the driver's battery with continuous live-tracking.
*   **Handover Protocol (The QR Code Handshake):** Chain of custody relies on a physical, in-person digital handshake. The receiver displays a unique QR code on their device, which the driver must scan to officially transfer liability and update the escrow status, preventing fraudulent delivery claims.

## 10. AI-Powered Crop Disease Diagnosis & Treatment
Acting as a field-level pocket agronomist.

*   **Diagnostic Input (Upload & Annotate Flow):** The tool is designed for offline resilience. Farmers take a photo using their default camera app and upload it later. They are prompted to manually draw a circle around the anomaly and input the crop type, providing the AI with high-quality, localized context before analysis.
*   **Results Display (Differential Diagnosis):** The AI does not present a single definitive answer, which can be dangerous. Instead, it presents the top 3 most likely diagnoses with confidence percentages and reference images, educating the farmer and keeping the human in the decision loop.
*   **Recommendation Action (Agronomist Escalation):** While the AI provides general advice, the UX heavily emphasizes verifying the diagnosis with a human. A prominent action button allows the farmer to immediately open an `AdvisoryTopic` ticket, attaching the AI's findings and photo to a local Agronomist for verified treatment protocols.

## 11. Weather Data Integration & Forecasting
Translating meteorological data into agronomic outcomes.

*   **Core Dashboard (Minimalist SMS/Widget):** The platform avoids duplicating full weather apps. The dashboard features a tiny, lightweight widget showing today's temperature and rain. It saves development effort and UI space for core proprietary features.
*   **Action Alerts (Passive Notification):** Impending severe weather triggers a standard, non-intrusive notification in the user's alerts inbox. It trusts the farmer to review their alerts without blocking their current workflow with intrusive pop-ups.
*   **Historical Analysis (Season Post-Mortem Report):** At the end of a crop cycle, the system automatically generates a formatted PDF report correlating total rainfall, temperature anomalies, and the final Yield. This provides an excellent, shareable static artifact for securing future loans or insurance claims.
