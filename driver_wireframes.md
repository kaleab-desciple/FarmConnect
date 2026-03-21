# Delivery Driver Role - Mobile Wireframes & Screen Designs

This document visualizes the UI/UX decisions tailored for the **Delivery Driver** role. These screens are completely mobile-first, using the "Ride-Hailing" UI model (Component 9.1) for job discovery, and focusing heavily on the secure "QR Code Handshake" (Component 9.3) to transfer physical custody of goods.

---

## Screen 1: The "Ride-Hailing" Job Discovery Map
**Path:** `/delivery/available`
**Purpose:** Uber-style dynamic job assignment matching drivers with nearby Escrow-funded orders ready for pickup.

```text
+-------------------------------------------------------------+
| [☰]             Driver Mode: [ ONLINE 🟢 ]                  |
+-------------------------------------------------------------+
|                                                             |
| 🗺️ LIVE MAP (Your Area)                                     |
|                                                             |
|         [ 📦 $45.00 ]                                       |
|          (15km away)                                        |
|                                                             |
|                     📍(You)                                 |
|                                                             |
|                                       [ 📦 $12.50 ]         |
|                                        (3km away)           |
|                                                             |
+-------------------------------------------------------------+
| 🟢 NEW DELIVERY REQUEST                                     |
|                                                             |
| Route: Green Acres Farm ➔ Blue Ridge Market                 |
| Distance: 45km Total                                        |
| Cargo: 100KG Tomatoes (Requires medium truck/van)           |
| Payout: $45.00 (Escrow Guaranteed)                          |
|                                                             |
| [ DECLINE ]                     [ ➜ ACCEPT JOB ]            |
+-------------------------------------------------------------+
```

---

## Screen 2: Active Delivery Navigation & Background Tracking
**Path:** `/delivery/active/{id}`
**Purpose:** Guiding the driver to the farm and notifying the buyer via "Background Ping Hybrid" tracking (Component 9.2) without draining the driver's battery continuously.

```text
+-------------------------------------------------------------+
| [≡ Menu]           Active Delivery #882                     |
+-------------------------------------------------------------+
|                                                             |
| 📍 DESTINATION: Pick up at Green Acres Farm                 |
| 🕒 ETA: 22 Minutes                                          |
|                                                             |
|  [ 🗺️ OPEN IN GOOGLE MAPS / WAZE ]                          |
|                                                             |
+-------------------------------------------------------------+
| STATUS: EN ROUTE TO FARM                                    |
|                                                             |
| 📡 Location Tracking is ACTIVE.                             |
| (We ping your location every 30 seconds to update the buyer)|
|                                                             |
| Farmer: John Doe  [ 📞 Call ]                               |
| Support: Agent    [ 💬 Chat ]                               |
+-------------------------------------------------------------+
| WHEN YOU ARRIVE AT THE FARM:                                |
| [ SCAN FARMER'S QR CODE FOR PICKUP ]                        |
+-------------------------------------------------------------+
```

---

## Screen 3: QR Handshake (Farm Pickup)
**Path:** `/delivery/pickup/{id}`
**Purpose:** Enforcing the Chain of Custody (Component 9.3). The driver cannot start the journey to the buyer until the farmer presents the unique QR code confirming the goods were loaded.

```text
+-------------------------------------------------------------+
| [← Back]           Verify Pickup                            |
+-------------------------------------------------------------+
| STEP 1: LOAD CARGO                                          |
| Ensure you have received exactly:                           |
| - 100 KG Roma Tomatoes                                      |
|                                                             |
| STEP 2: SCAN FARMER'S CODE                                  |
| Ask the farmer to open their app and display the            |
| 'Handover QR Code' for Order #882.                          |
+-------------------------------------------------------------+
|                                                             |
|      +-----------------------------------------+            |
|      |                                         |            |
|      |          [ CAMERA VIEWFINDER ]          |            |
|      |        Align QR Code inside box         |            |
|      |                                         |            |
|      |             +-------------+             |            |
|      |             |             |             |            |
|      |             |             |             |            |
|      |             +-------------+             |            |
|      |                                         |            |
|      +-----------------------------------------+            |
|                                                             |
+-------------------------------------------------------------+
| If the camera fails, enter the 6-digit PIN manually:        |
| [ - - - - - - ] [ SUBMIT ]                                  |
+-------------------------------------------------------------+
```

---

## Screen 4: QR Handshake (Buyer Drop-off)
**Path:** `/delivery/dropoff/{id}`
**Purpose:** The final chain of custody link. The buyer scans their app to confirm receipt, which automatically completes the delivery and releases the driver's Escrow payment.

```text
+-------------------------------------------------------------+
| [← Back]           Complete Delivery                        |
+-------------------------------------------------------------+
| 📍 DESTINATION REACHED: Blue Ridge Market                   |
|                                                             |
| Buyer: Sarah Smith  [ 📞 Call ]                             |
+-------------------------------------------------------------+
| STEP 1: UNLOAD CARGO                                        |
| Buyer inspects the 100KG of Tomatoes.                       |
|                                                             |
| STEP 2: SCAN BUYER'S CODE                                   |
| Ask the buyer to open their app to confirm they accept      |
| the delivery. Scan their 'Completion QR Code'.              |
+-------------------------------------------------------------+
|                                                             |
|      +-----------------------------------------+            |
|      |                                         |            |
|      |          [ CAMERA VIEWFINDER ]          |            |
|      |                                         |            |
|      +-----------------------------------------+            |
|                                                             |
+-------------------------------------------------------------+
| 💰 Once scanned successfully, your $45.00 delivery fee will |
| instantly be unlocked from Escrow and added to your wallet. |
+-------------------------------------------------------------+
```
