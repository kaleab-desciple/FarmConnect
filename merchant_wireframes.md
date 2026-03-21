# Merchant Role - Wireframes & Screen Designs

This document visualizes the UI/UX decisions tailored for the **Merchant / Buyer** role. The focus here is on trust-building, clear e-commerce flows (Component 8.1), and robust dispute resolution (Component 8.3). These screens are optimized for both mobile and desktop views, as merchants may order from an office or on the go.

---

## Screen 1: The "Farm-to-Table" Visual Grid (Product Catalog)
**Path:** `/merchant/marketplace`
**Purpose:** Discovery of agricultural products with high provenance and trust signals (Component 7.2).

```text
+-------------------------------------------------------------+
| [☰ Menu]           FarmConnect Marketplace           [🛒 (1)]|
+-------------------------------------------------------------+
| 🔍 Search: [ "Grade A Tomatoes"                      ] [Find] |
| 🏷️ Filters: [ Region: Amhara ▾ ] [ Rating: 4★+ ▾ ]            |
+-------------------------------------------------------------+
|                                                             |
| +-------------------------+   +-------------------------+   |
| | [ IMAGE: Fresh Romas  ] |   | [ IMAGE: Teff Grain   ] |   |
| |                         |   |                         |   |
| | Roma Tomatoes (Grade A) |   | White Teff (Premium)    |   |
| | $15.00 / KG             |   | $45.00 / 100KG          |   |
| |                         |   |                         |   |
| | 👨‍🌾 Farm: Green Acres    |   | 👨‍🌾 Farm: Highland Agri  |   |
| | 📍 15km Away            |   | 📍 220km Away           |   |
| | ⭐ 4.9 (120 reviews)    |   | ⭐ 4.8 (85 reviews)     |   |
| |                         |   |                         |   |
| | Available: 400 KG       |   | Available: 2,000 KG     |   |
| | [ ADD TO CART ]         |   | [ ADD TO CART ]         |   |
| +-------------------------+   +-------------------------+   |
|                                                             |
+-------------------------------------------------------------+
```

---

## Screen 2: Traditional E-commerce Checkout & Escrow
**Path:** `/merchant/checkout`
**Purpose:** A familiar cart and payment flow, utilizing the "Optimistic Checkout" model (Component 7.3) and securing funds in Escrow.

```text
+-------------------------------------------------------------+
| [← Back]                 Checkout                           |
+-------------------------------------------------------------+
| 📦 ORDER SUMMARY                                            |
|                                                             |
| Roma Tomatoes (Grade A)                                     |
| Qty: 100 KG  x  $15.00/KG = $1,500.00                       |
| Farm: Green Acres (Verified)                                |
|                                                             |
| Subtotal:      $1,500.00                                    |
| Service Fee:      $15.00                                    |
| Delivery:         $45.00 (Uber-style matching)              |
| --------------------------------------                      |
| TOTAL:         $1,560.00                                    |
+-------------------------------------------------------------+
| 💳 PAYMENT / ESCROW DEPOSIT                                 |
|                                                             |
| Funding Source: [ Bank Account ****4492 ▾ ]                 |
|                                                             |
| ℹ️ Your funds will be held securely in ESCROW. The farmer  |
| and driver are not paid until you inspect and confirm       |
| delivery.                                                   |
+-------------------------------------------------------------+
| [ PAY $1,560.00 TO SECURE ORDER ]                           |
+-------------------------------------------------------------+
```

---

## Screen 3: Order Tracking & Delivery Milestone Tracker
**Path:** `/merchant/orders/{id}`
**Purpose:** Tracking the physical handover of goods.

```text
+-------------------------------------------------------------+
| [← Back]           Order Tracking: #882                     |
+-------------------------------------------------------------+
| Status: IN TRANSIT 🚚                                       |
| Driver: Samuel T. (⭐ 4.9)   [ 📞 Call Driver ]             |
+-------------------------------------------------------------+
| 🗺️ LIVE TRACKING MAP                                        |
|                                                             |
|  [ Farm ] = = = = = = 📍(Driver) - - - - [ Your Store ]     |
|                                                             |
| ETA: 45 Minutes                                             |
+-------------------------------------------------------------+
| 📌 MILESTONES                                               |
|                                                             |
| [✔] 10:00 AM - Order Funded (Escrow Locked)                 |
| [✔] 11:30 AM - Driver Matched                               |
| [✔] 12:15 PM - QR Handshake Complete at Farm (Picked up)    |
| [●] Driver en route...                                      |
| [ ] Pending Delivery Confirmation                           |
+-------------------------------------------------------------+
| WHEN DRIVER ARRIVES:                                        |
| [ CONFIRM RECEIPT & RELEASE ESCROW ]                        |
|                                                             |
| (Found an issue? [ Open Dispute ])                          |
+-------------------------------------------------------------+
```

---

## Screen 4: Agent Mediation Flow (Disputes)
**Path:** `/merchant/disputes/new`
**Purpose:** High-friction dispute resolution path (Component 8.3) requiring photographic evidence.

```text
+-------------------------------------------------------------+
| [← Cancel]           Open a Dispute                         |
+-------------------------------------------------------------+
| ⚠️ ESCROW IS FROZEN ⚠️                                      |
| This order #882 is now locked in mediation.                 |
+-------------------------------------------------------------+
| STEP 1: WHAT WENT WRONG?                                    |
| [ Missing Quantity ▾ ]                                      |
|                                                             |
| Describe the issue:                                         |
| [ I ordered 100KG of Tomatoes, but the driver only       ]  |
| [ delivered 80KG. 4 crates were missing entirely.        ]  |
|                                                             |
| STEP 2: UPLOAD EVIDENCE (Required)                          |
| [ 📷 Take Photo of Received Goods ] (2 photos attached)     |
| [ 📷 Take Photo of Delivery Waybill ] (1 photo attached)    |
+-------------------------------------------------------------+
| STEP 3: PLATFORM MEDIATION                                  |
|                                                             |
| ℹ️ By submitting this, an independent FarmConnect Agent     |
| will review the evidence, contact the driver and farmer,    |
| and make a binding decision on the escrow funds within      |
| 24 hours.                                                   |
+-------------------------------------------------------------+
| [ SUBMIT TO AGENT FOR MEDIATION ]                           |
+-------------------------------------------------------------+
```
