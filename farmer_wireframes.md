# Farmer Role - Mobile Wireframes & Screen Designs

This document visualizes the UI/UX decisions tailored for the **Farmer** role. Since farmers will primarily use the application in the field, these wireframes focus on a **Mobile-First** layout with large touch targets, high contrast, and offline-first indicators.

---

## Screen 1: The Universal Farmer Dashboard
**Path:** `/farmer/dashboard`
**Purpose:** The central hub. Combines the minimalist weather widget, the Interactive Map Layer, and the Action-Required Inbox.

```text
+-------------------------------------------------------------+
| [☰ Menu]                FarmConnect            [🔔 Alerts (2)] |
+-------------------------------------------------------------+
| [Offline Sync: Up to Date ✔]                                |
+-------------------------------------------------------------+
| ⛅ Weather Widget (Component 11.1 - Minimalist)             |
| Today: 25°C | 🌧️ 12mm rain expected at 14:00                |
+-------------------------------------------------------------+
| ⚠️ ACTION REQUIRED (Component 8.2 - Inbox)                  |
| [!] Order #882: Escrow Funded - Ready for Delivery Dispatch |
|     ➔ [DISPATCH DRIVER]                                     |
|                                                             |
| [!] CropCycle #A2: "Tomato North" needs Stage Check-in      |
|     ➔ [LOG CHECK-IN]                                        |
+-------------------------------------------------------------+
| 🗺️ FARM OVERVIEW (Component 2.2 - Interactive Map Layer)    |
| +---------------------------------------------------------+ |
| |                                                         | |
| |       [North Field]                   [East Field]      | |
| |       (Tomatoes - Gr)                 (Corn - Yl)       | |
| |             📍(You are here)                            | |
| |                                                         | |
| |       [South Field]                                     | |
| |       (Fallow - Br)                                     | |
| |                                                         | |
| +---------------------------------------------------------+ |
+-------------------------------------------------------------+
| QUICK ACTIONS:                                              |
| [ ➕ New Task ]  [ 📸 AI Scanner ]  [ 📝 End of Day Log ]   |
+-------------------------------------------------------------+
| Bottom Nav: [🏠 Home] [🌾 Fields] [📦 Inventory] [🛒 Orders]|
+-------------------------------------------------------------+
```

---

## Screen 2: Field Control Room (Detail View)
**Path:** `/farmer/fields/{id}`
**Purpose:** Managing a specific field, viewing crop lifecycle (Component 4.1), and real-time NDVI data (Component 5.2).

```text
+-------------------------------------------------------------+
| [← Back]           North Field (Tomatoes)          [⚙ Edit] |
+-------------------------------------------------------------+
| 📈 VIGOR TREND (Component 5.2 - NDVI Graph)                 |
| 1.0 |      /`--,                                            |
|     |  /`--     `--\   <-- (Tap for breakdown)              |
| 0.5 | /             \                                       |
|     |/               \__                                    |
|     +--------------------- (Past 30 Days)                   |
+-------------------------------------------------------------+
| 📋 FIELD SPECIFIC CLIPBOARD (Component 5.1 - Log)           |
|  [➕ Quick Add: Irrigation] [➕ Quick Add: Fertilizer/Chem] |
+-------------------------------------------------------------+
| ⏳ CROP LIFECYCLE TIMELINE (Component 4.1 - Vertical Feed)  |
|                                                             |
|  🟢 TODAY - [MANUAL CHECK-IN REQUIRED]                      |
|  |   Expected Stage: Fruiting                               |
|  |   ➔ [CONFIRM STAGE] or [REPORT DELAY]                    |
|  |                                                          |
|  🔵 YESTERDAY (14:30)                                       |
|  |   Applied 20L NPK Fertilizer (Worker: John)              |
|  |                                                          |
|  🔴 3 DAYS AGO (Automatic Weather Alert)                    |
|  |   Heavy Frost Detected (-2°C at 04:00)                   |
|  |                                                          |
|  🟢 12 DAYS AGO                                             |
|      Planted 5000 Seeds (Variety: Roma)                     |
+-------------------------------------------------------------+
```

---

## Screen 3: End of Day Harvest Log & Funnel
**Path:** `/farmer/harvest/new`
**Purpose:** Fast, friction-free yield recording from the field (Component 6.2 & 6.3), leading into the Inventory Funnel (Component 7.1).

```text
+-------------------------------------------------------------+
| [← Back]              End of Day Log               [Done]   |
+-------------------------------------------------------------+
| "Yield Only, Quality Later" (Component 6.3)                 |
|                                                             |
| Target Crop: [ Select: North Field - Tomatoes ▾ ]           |
|                                                             |
| Enter Gross Yield Weight:                                   |
| +---------------------------------------------------------+ |
| |  [ - ]            2,500               [ + ]   (KG)      | |
| +---------------------------------------------------------+ |
|                                                             |
| Notes (Optional):                                           |
| [ "A bit muddy today, might need washing..."            ]   |
+-------------------------------------------------------------+
| [ LOG HARVEST & MOVE TO QC WAITING AREA ]                   |
+-------------------------------------------------------------+
|                                                             |
| 📊 CURRENT INVENTORY FUNNEL (Component 7.1)                 |
|                                                             |
|  [=] Pending QC Grading:    2,500 KG  (Needs assessment)    |
|   \                                                         |
|    [=] Available to Sell:     800 KG  (Live on marketplace) |
|     \                                                       |
|      [=] Reserved in Carts:   200 KG  (Pending Escrow)      |
|       \                                                     |
|        [=] Sold & Pending:    400 KG  (Waiting Driver)      |
+-------------------------------------------------------------+
```

---

## Screen 4: AI Disease Diagnostic Scanner
**Path:** `/farmer/ai-diagnostics`
**Purpose:** Uploading photos offline (Component 10.1), Differential choices (10.2), and Human Escalation (10.3)

```text
+-------------------------------------------------------------+
| [← Cancel]           Pocket Agronomist                      |
+-------------------------------------------------------------+
| STEP 1: UPLOAD & ANNOTATE (Component 10.1)                  |
|                                                             |
| +---------------------------------------------------------+ |
| |                        o                                | |
| |                     o/ | \o    <-- User draws red       | |
| |                     |  |  |        circle over the bug  | |
| |                       / \                               | |
| |      [ PHOTO PREVIEW: Bitten Tomato Leaf ]              | |
| +---------------------------------------------------------+ |
| [ 🔄 Retake Photo ]               Crop: [ Tomatoes ▾ ]      |
+-------------------------------------------------------------+
| [ ANALYZE PHOTO ]                                           |
+-------------------------------------------------------------+
|                                                             |
| STEP 2: DIFFERENTIAL DIAGNOSIS (Component 10.2)             |
|                                                             |
| We found 2 possibilities. Which looks closest?              |
| [ ] Late Blight (85% Match) - [View Reference Photo]        |
| [ ] Spider Mite Damage (10%) - [View Reference Photo]       |
|                                                             |
+-------------------------------------------------------------+
| STEP 3: ACTION / ESCALATION (Component 10.3)                |
|                                                             |
| 💡 Recommendation: Apply Copper Fungicide.                  |
|                                                             |
| ⚠️ Highly Recommended for this severity:                   |
| [ 👨‍🌾 VERIFY WITH LOCAL AGRONOMIST (FREE) ]                |
| (Opens an Advisory Ticket with your nearest expert)         |
+-------------------------------------------------------------+
```
