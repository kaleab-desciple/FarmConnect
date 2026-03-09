# Farmer Role - Wireframes & Screen Designs

## FarmConnect AgriManagement

This document outlines the wireframes and screen designs for the **Farmer** role, based on the UI/UX decisions in `ui_ux_decisions_summary.md`.

---

## 1. Authentication & Onboarding Screens

### 1.1 Login Screen
```
┌─────────────────────────────────────┐
│          [FarmConnect Logo]          │
│         "Farm Your Way"             │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📧 Email or Phone              ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🔒 Password                    ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │         [SIGN IN]              ││
│  └─────────────────────────────────┘│
│                                     │
│  "Don't have an account? Sign Up"   │
│                                     │
│  🌐 English ▼  |  🔊 Audio On       │
└─────────────────────────────────────┘
```

### 1.2 Registration Screen
```
┌─────────────────────────────────────┐
│  [←]  Create Account                │
│                                     │
│  Select Your Role:                 │
│  ┌───────────┐  ┌───────────┐      │
│  │  👨‍🌾      │  │  🏪      │      │
│  │  Farmer   │  │ Merchant  │      │
│  │    ○      │  │    ○      │      │
│  └───────────┘  └───────────┘      │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 Full Name                   ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  📧 Email                        ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  📱 Phone Number                 ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  🔒 Create Password             ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  🔒 Confirm Password            ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │        [CREATE ACCOUNT]         ││
│  └─────────────────────────────────┘│
│                                     │
│  "Already have an account? Sign In" │
└─────────────────────────────────────┘
```

### 1.3 Guided Tour Overlay (First Login)
```
┌─────────────────────────────────────┐
│                                     │
│         🎯 STEP 1 of 4              │
│                                     │
│    ┌───────────────────────────┐    │
│    │                           │    │
│    │   [Map Icon]              │    │
│    │                           │    │
│    └───────────────────────────┘    │
│                                     │
│     "First, let's map your farm"    │
│                                     │
│    Tap anywhere on the map to       │
│    set your farm location           │
│                                     │
│           [Skip]  [Next →]          │
│                                     │
└─────────────────────────────────────┘
```

---

## 2. Farm Dashboard (Main Screen)

### 2.1 Interactive Map Dashboard
```
┌─────────────────────────────────────┐
│ 👨‍🌾 John Farm          [🔔3] [⚙️]   │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │                             │   │
│   │     🗺️  Interactive Map    │   │
│   │                             │   │
│   │   [Field A]──┐              │   │
│   │   (Maize)    │              │   │
│   │              ├──[Field B]   │   │
│   │              │  (Cabbage)   │   │
│   │              │              │   │
│   │   [Field C]──┘              │   │
│   │   (Tomato)                   │   │
│   │                             │   │
│   └─────────────────────────────┘   │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 📊 Today's Overview      [📈] │ │
│ ├─────────────────────────────────┤ │
│ │ 🌱 3 Active Crops   |  ⚠️ 1 Alert │ │
│ │ 📦 150kg Harvested  |  💰 $450   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [🏠]  [🗺️]  [📦]  [🤖]  [👤]       │
│ Home  Map   Orders AI    Profile    │
└─────────────────────────────────────┘
```

### 2.2 Farm Stats Panel (Slide-up Sheet)
```
┌─────────────────────────────────────┐
│            ═══════════             │  ← Drag handle
│                                     │
│   📊 Farm Statistics                │
│                                     │
│   ┌──────────┐ ┌──────────┐        │
│   │ 12.5 ha  │ │   3      │        │
│   │Total Area│ │Fields    │        │
│   └──────────┘ └──────────┘        │
│                                     │
│   ┌──────────┐ ┌──────────┐        │
│   │ 3        │ │   2      │        │
│   │Active    │ │Harvested │        │
│   │Cycles    │ │This Season│       │
│   └──────────┘ └──────────┘        │
│                                     │
│   ─── Recent Activity ───          │
│   • Field A: Irrigation done      │
│   • Field B: Pest spotted ⚠️        │
│   • Harvest: 50kg Tomatoes         │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. Farm Creation Flow

### 3.1 Map-First Creation
```
┌─────────────────────────────────────┐
│ [←]  Create Your Farm        [Skip] │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │  🗺️                        │   │
│   │                            │   │
│   │        📍                  │   │
│   │       (You)               │   │
│   │                            │   │
│   │   "Drop a pin or draw     │   │
│   │    your farm boundary"    │   │
│   │                            │   │
│   │   [Draw Boundary] [Use GPS]│   │
│   └─────────────────────────────┘   │
│                                     │
│   Accuracy: ████████░░ 85%          │
│                                     │
│              [Next →]               │
│                                     │
└─────────────────────────────────────┘
```

### 3.2 Farm Details Form (Progressive Bottom Sheet)
```
┌─────────────────────────────────────┐
│ [←]  Farm Details         [2/3]     │
├─────────────────────────────────────┤
│                                     │
│  Progress: ████████░░ 66%          │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🏡 Farm Name                   ││
│  │  "My Family Farm"               ││
│  └─────────────────────────────────┘│
│                                     │
│  📍 Location                        │
│  ┌─────────────────────────────────┐│
│  │ 9.1456° N, 40.4567° E           ││
│  │ [📍 Change Location]            ││
│  └─────────────────────────────────┘│
│                                     │
│  📏 Total Area (hectares)          │
│  ┌─────────────────────────────────┐│
│  │  12.5                           ││
│  └─────────────────────────────────┘│
│                                     │
│  🏠 Address (Optional)              │
│  ┌─────────────────────────────────┐│
│  │  Oromia Region, Ethiopia        ││
│  └─────────────────────────────────┘│
│                                     │
│           [Back]    [Create Farm]   │
│                                     │
└─────────────────────────────────────┘
```

---

## 4. Field Management Screens

### 4.1 Field List View
```
┌─────────────────────────────────────┐
│ [←]  My Fields           [+ Add]   │
├─────────────────────────────────────┤
│                                     │
│  Search fields...                   │
│  ┌─────────────────────────────────┐│
│  │  🔍  ───────────────────────    ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🟡 Field A - Maize             ││
│  │  5.2 ha | 🌱 Growing            ││
│  │  [View Details →]               ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🟢 Field B - Cabbage           ││
│  │  3.1 ha | 🌱 Growing             ││
│  │  [View Details →]               ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🔴 Field C - Tomato             ││
│  │  4.2 ha | ⚠️ Needs Attention     ││
│  │  [View Details →]               ││
│  └─────────────────────────────────┘│
│                                     │
│  [🏠]  [🗺️]  [📦]  [🤖]  [👤]       │
└─────────────────────────────────────┘
```

### 4.2 Field Delineation (Tap and Draw)
```
┌─────────────────────────────────────┐
│ [←]  Add New Field        [Save]   │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │  🗺️  Satellite View         │   │
│   │                             │   │
│   │      ●────●                 │   │
│   │     ╱      ╲                │   │
│   │    ●        ●              │   │
│   │     ╲      ╱                │   │
│   │      ●────●                 │   │
│   │                             │   │
│   │  [Clear]  [Undo]           │   │
│   └─────────────────────────────┘   │
│                                     │
│  Points: 4  |  Area: 2.5 ha         │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌱 Field Name                  ││
│  │  "North Plot"                  ││
│  └─────────────────────────────────┘│
│                                     │
│  [Start Drawing]  [Use GPS Track]   │
│                                     │
└─────────────────────────────────────┘
```

### 4.3 Field Control Room (Detail Page)
```
┌─────────────────────────────────────┐
│ [←]  Field A: Maize      [⚙️] [📷] │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │  🗺️  Field Map              │   │
│   │  [🟡 Maize - Growing]        │   │
│   │                             │   │
│   │      🌱🌱🌱🌱               │   │
│   │      🌱🌱⚠️🌱               │   │
│   │      🌱🌱🌱🌱               │   │
│   └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📊 Overview     📅 Tasks      ││
│  │  📈 Monitoring   📋 History    ││
│  ├─────────────────────────────────┤│
│  │  Crop: Maize (Var: BH-660)     ││
│  │  Planted: 45 days ago          ││
│  │  Expected Harvest: 15 days    ││
│  │  Expected Yield: 5,200 kg      ││
│  │                                ││
│  │  📊 NDVI: 0.72 (Healthy)       ││
│  │  [View Trend Graph]           ││
│  │                                ││
│  │  ⚠️ Alert: Possible pest      ││
│  │  detected in northwest area   ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [📝 Log Observation]          ││
│  │  [🚜 Record Task]             ││
│  │  [📦 Start Harvest]            ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Crop Lifecycle Screens

### 5.1 Crop Cycle Timeline (Vertical Activity Feed)
```
┌─────────────────────────────────────┐
│ [←]  Field A: Maize - Cycle #2    │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌱 Started: Jan 15, 2026       ││
│  │  Expected Harvest: Mar 30      ││
│  │  Status: Growing  ████████░░ 70%│
│  └─────────────────────────────────┘│
│                                     │
│  ─── Today ───                      │
│                                     │
│  ┌───┐                              │
│  │ ⚠️│  2:30 PM - Pest Alert       │
│  └───┘  NDVI detected unusual       │
│       activity. Possible pest       │
│       [View Details] [Mark Seen]    │
│                                     │
│  ┌───┐                              │
│  │ ✓│  10:00 AM - Task Completed  │
│  └───┘  Fertilization (Urea)       │
│       Applied 50kg per hectare      │
│       [View Details]               │
│                                     │
│  ─── Yesterday ───                  │
│                                     │
│  ┌───┐                              │
│  │ 📷│  3:15 PM - Photo Log        │
│  └───┘  Field inspection photos    │
│       [View Photos (3)]            │
│                                     │
│  ┌───┐                              │
│  │ 📝│  9:00 AM - Observation      │
│  └───┘  Noted: Slight yellowing    │
│       on leaf edges                │
│                                     │
│              [Load More]            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [✏️ Add📷 Add Photo]  Note] [ ││
│  │  [✅ Complete Task]             ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 5.2 New Cycle Setup (Blank Canvas)
```
┌─────────────────────────────────────┐
│ [←]  Start New Crop Cycle           │
├─────────────────────────────────────┤
│                                     │
│  Field: Field A (5.2 ha)            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌾 Crop Type                   ││
│  │  [Select Crop ▼]               ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Variety                     ││
│  │  [Enter variety name...]       ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🏭 Cultivar (Optional)        ││
│  │  [Enter cultivar...]           ││
│  └─────────────────────────────────┘│
│                                     │
│  📅 Planting Date                  │
│  ┌─────────────────────────────────┐│
│  │  📅 January 15, 2026           ││
│  └─────────────────────────────────┘│
│                                     │
│  📅 Expected Harvest Date           │
│  ┌─────────────────────────────────┐│
│  │  📅 March 30, 2026             ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🎯 Expected Yield (kg)        ││
│  │  [5000]                        ││
│  └─────────────────────────────────┘│
│                                     │
│  📝 Notes (Optional)               │
│  ┌─────────────────────────────────┐│
│  │  [Additional notes...]         ││
│  └─────────────────────────────────┘│
│                                     │
│       [Start Cycle]                 │
│                                     │
└─────────────────────────────────────┘
```

### 5.3 Stage Transition Check-in
```
┌─────────────────────────────────────┐
│  ⚠️  Stage Confirmation Required    │
├─────────────────────────────────────┤
│                                     │
│   Current Stage: 🌱 Vegetative      │
│                                     │
│   Moving to: 🌸 Flowering           │
│                                     │
│   ┌─────────────────────────────┐   │
│   │  📷                         │   │
│   │  Please take a photo of     │   │
│   │  your crop to confirm       │   │
│   │  the growth stage           │   │
│   │                             │   │
│   │     [Take Photo]            │   │
│   └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📝 Notes (Optional)           ││
│  │  [Any observations...]         ││
│  └─────────────────────────────────┘│
│                                     │
│       [Confirm Stage]               │
│                                     │
│   "This confirms your crop has      │
│    transitioned to the flowering    │
│    stage based on your observation" │
│                                     │
└─────────────────────────────────────┘
```

---

## 6. Harvest Management Screens

### 6.1 Harvest Calendar View
```
┌─────────────────────────────────────┐
│ [←]  Harvest Calendar      [List]  │
├─────────────────────────────────────┤
│       ◀  February 2026  ▶          │
│                                     │
│  M  T  W  T  F  S  S               │
│        1  2  3  4  5               │
│  6  7  8  9  10 11 12              │
│  13 14 15 16 17 18 19              │
│  20 21 22 23 24 25 26              │
│     [28] 29 30                     │
│                                     │
│  ─── Scheduled Harvests ───        │
│                                     │
│  📅 Feb 28 - Field A (Maize)       │
│     Expected: 5,200 kg             │
│     [Mark Complete]                │
│                                     │
│  📅 Feb 15 - Field B (Cabbage)     │
│     Expected: 3,100 kg             │
│     ✓ Completed                    │
│                                     │
│  ─── Quick Actions ───             │
│  [+ Schedule Harvest]              │
│  [+ Log Unplanned Harvest]         │
│                                     │
└─────────────────────────────────────┘
```

### 6.2 End of Day Harvest Log
```
┌─────────────────────────────────────┐
│ [←]  Log Today's Harvest            │
├─────────────────────────────────────┤
│                                     │
│  Field: Field A                     │
│  Crop: Maize                        │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ⚖️ Total Harvested Weight      ││
│  │                                 ││
│  │      [  4,850  ]  kg           ││
│  │     -100   +100                ││
│  └─────────────────────────────────┘│
│                                     │
│  Quality Assessment:                │
│  ┌─────────────────────────────────┐│
│  │  Grade A (Premium)    ○        ││
│  │  Grade B (Standard)   ●        ││
│  │  Grade C (Low)        ○        ││
│  └─────────────────────────────────┘│
│                                     │
│  📝 Notes (Optional)                │
│  ┌─────────────────────────────────┐│
│  │  Some pest damage on outer     ││
│  │  cobs, but overall good yield  ││
│  └─────────────────────────────────┘│
│                                     │
│  📷 Photos (Optional)              │
│  ┌────┐ ┌────┐ ┌────┐ [+ Add]     │
│  │ 📷 │ │ 📷 │ │ 📷 │             │
│  └────┘ └────┘ └────┘             │
│                                     │
│     [Save Harvest Log]              │
│                                     │
│  "Inventory will be created after   │
│   quality control assessment"       │
│                                     │
└─────────────────────────────────────┘
```

### 6.3 Harvest Yield Recording
```
┌─────────────────────────────────────┐
│ [←]  Yield Recording                │
├─────────────────────────────────────┤
│                                     │
│  Field: Field A                     │
│  Crop: Maize (BH-660)               │
│  Harvest Date: Feb 28, 2026        │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Gross Yield: 4,850 kg         ││
│  │  ✓ Recorded                    ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Quality Grading ───           │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Grade A: [  2,900  ] kg       ││
│  │  (Premium - 60%)               ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Grade B: [  1,450  ] kg       ││
│  │  (Standard - 30%)              ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Grade C: [    500  ] kg       ││
│  │  (Low Quality - 10%)           ││
│  └─────────────────────────────────┘│
│                                     │
│  Total: 4,850 kg ✓                  │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [Submit for QC Review]         ││
│  └─────────────────────────────────┘│
│                                     │
│  "Once submitted, inventory will    │
│   be listed in your product catalog"│
│                                     │
└─────────────────────────────────────┘
```

---

## 7. Field Monitoring & Data Entry

### 7.1 Field Observation Log
```
┌─────────────────────────────────────┐
│ [←]  Log Observation - Field A      │
├─────────────────────────────────────┤
│                                     │
│  Observation Type:                  │
│  ┌─────────────────────────────────┐│
│  │  🐛 Pest      ○                ││
│  │  🍂 Disease   ○                ││
│  │  💧 Water     ○                ││
│  │  🌱 Growth    ●                ││
│  │  📊 Other     ○                ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🔍 Severity                    ││
│  │  ○ Low    ● Medium   ○ High    ││
│  └─────────────────────────────────┘│
│                                     │
│  Description:                       │
│  ┌─────────────────────────────────┐│
│  │  Leaves showing yellowing at    ││
│  │  tips, possible nitrogen        ││
│  │  deficiency                    ││
│  └─────────────────────────────────┘│
│                                     │
│  📍 Location in Field:              │
│  ┌─────────────────────────────────┐│
│  │  📍 North-West Corner          ││
│  │  [Pin on Map]                  ││
│  └─────────────────────────────────┘│
│                                     │
│  📷 Photos (Required)               │
│  ┌────┐ ┌────┐                     │
│  │ 📷 │ │ 📷 │  [+ Add Photo]      │
│  └────┘ └────┘                     │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [Save Observation]             ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 7.2 NDVI Visualization (Vigor Trend Graph)
```
┌─────────────────────────────────────┐
│ [←]  Field A - Vegetation Health    │
├─────────────────────────────────────┤
│                                     │
│   Crop: Maize | Stage: Growing      │
│                                     │
│  1.0 ┤                    ●───●    │
│      │               ●───           │
│  0.8 ┤          ●───                │
│      │       ●─                     │
│  0.6 ┤    ●─                        │
│      │  ●─                          │
│  0.4 ┤─                             │
│      │                              │
│      └────┬────┬────┬────┬────┬────  │
│          Jan  Feb  Mar  Apr        │
│                                     │
│  ─── Recent Readings ───           │
│                                     │
│  📅 Feb 28: 0.72 (Healthy)         │
│  📅 Feb 21: 0.68 (Healthy)         │
│  📅 Feb 14: 0.65 (Moderate)        │
│  📅 Feb 7:  0.58 (Moderate)        │
│                                     │
│  ─── Analysis ───                  │
│  Trend: ↗ Improving (+14%)         │
│  Status: Above average for stage   │
│                                     │
│  [View Historical Report]           │
│                                     │
└─────────────────────────────────────┘
```

---

## 8. AI Disease Diagnosis

### 8.1 Diagnostic Input (Upload & Annotate)
```
┌─────────────────────────────────────┐
│ [←]  Crop Disease Diagnosis         │
├─────────────────────────────────────┤
│                                     │
│  Step 1: Select Crop Type           │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize                    ▼  ││
│  └─────────────────────────────────┘│
│                                     │
│  Step 2: Upload Photo               │
│  ┌─────────────────────────────────┐│
│  │                                 ││
│  │         📷                      ││
│  │                                 ││
│  │    Tap to upload or take        ││
│  │         photo                   ││
│  │                                 ││
│  │     [Choose from Gallery]       ││
│  │     [Take Photo]                ││
│  │                                 ││
│  └─────────────────────────────────┘│
│                                     │
│  Step 3: Annotate Issue (Optional)  │
│  ┌─────────────────────────────────┐│
│  │                                 ││
│  │    [Photo Preview with         ││
│  │     circle drawing tool]        ││
│  │                                 ││
│  │  Tap and drag to circle        ││
│  │  the affected area              ││
│  │                                 ││
│  │  [Clear Annotation]            ││
│  └─────────────────────────────────┘│
│                                     │
│       [Analyze Image]               │
│                                     │
└─────────────────────────────────────┘
```

### 8.2 Results Display (Differential Diagnosis)
```
┌─────────────────────────────────────┐
│ [←]  Diagnosis Results              │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Crop: Maize                 ││
│  │  📷 Photo analyzed              ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Possible Diagnoses ───        │
│                                     │
│  1️⃣  Northern Leaf Blight           │
│      Confidence: 78%                │
│      ━━━━━━━━━━━━━━━━━━━━━━ 78%    │
│                                     │
│      Reference:                     │
│      ┌────┐ ┌────┐ ┌────┐          │
│      │img │ │img │ │img │          │
│      └────┘ └────┘ └────┘          │
│                                     │
│  2️⃣  Common Rust                    │
│      Confidence: 52%                │
│      ━━━━━━━━━━━━━━━━━━━━━ 52%     │
│                                     │
│  3️⃣  Grey Leaf Spot                │
│      Confidence: 23%                │
│      ━━━━━━━━━━━━━━ 23%            │
│                                     │
│  ─── Recommended Actions ───       │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [💊 Get Treatment Advice]     ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [👨‍🌾 Consult Agronomist]        ││
│  │  "Verify with local expert"    ││
│  └─────────────────────────────────┘│
│                                     │
│  ⚠️  "These are AI suggestions.    │
│     Always verify with local experts"│
│                                     │
└─────────────────────────────────────┘
```

### 8.3 Agronomist Escalation
```
┌─────────────────────────────────────┐
│  👨‍🌾 Consult Agronomist              │
├─────────────────────────────────────┤
│                                     │
│  Your diagnosis will be attached:   │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Northern Leaf Blight (78%)  ││
│  │  📷 [Photo Attached]            ││
│  │  📍 Field A - Maize             ││
│  └─────────────────────────────────┘│
│                                     │
│  Select Topic:                      │
│  ┌─────────────────────────────────┐│
│  │  AdvisoryTopic: DISEASE_TREAT  ││
│  │  ▼                              ││
│  └─────────────────────────────────┘│
│                                     │
│  Additional Notes:                   │
│  ┌─────────────────────────────────┐│
│  │  Noticed this 3 days ago,      ││
│  │  spreading quickly after        ││
│  │  recent rain...                 ││
│  └─────────────────────────────────┘│
│                                     │
│  Select Agronomist:                 │
│  ┌─────────────────────────────────┐│
│  │  👤 Dr. Alemayehu (⭐4.8)      ││
│  │     Available: Today            ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 Mrs. Tigist (⭐4.5)        ││
│  │     Available: Tomorrow         ││
│  └─────────────────────────────────┘│
│                                     │
│      [Submit Request]               │
│                                     │
└─────────────────────────────────────┘
```

---

## 9. Product Inventory & Orders

### 9.1 Farmer Inventory View (The Funnel)
```
┌─────────────────────────────────────┐
│ [←]  My Inventory         [+ List] │
├─────────────────────────────────────┤
│                                     │
│  ─── Inventory Funnel ───           │
│                                     │
│  Total Harvested                    │
│  ┌─────────────────────────────────┐│
│  │     4,850 kg                    ││
│  │     (Maize Grade A)             ││
│  └─────────────────────────────────┘│
│          │                          │
│          ▼                          │
│  Reserved (In Escrow)               │
│  ┌─────────────────────────────────┐│
│  │     1,200 kg                    ││
│  │     → Order #ORD-2026-001       ││
│  └─────────────────────────────────┘│
│          │                          │
│          ▼                          │
│  Available to Sell                  │
│  ┌─────────────────────────────────┐│
│  │     3,650 kg                    ││
│  │     [List for Sale]             ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Listed Products ───            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize Grade A              ││
│  │  2,000 kg @ $0.45/kg           ││
│  │  Status: Active | 5 views       ││
│  │  [Edit] [Remove]                ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize Grade B              ││
│  │  1,650 kg @ $0.35/kg           ││
│  │  Status: Active | 2 views       ││
│  │  [Edit] [Remove]                ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 9.2 Order Inbox (Action-Required)
```
┌─────────────────────────────────────┐
│ [←]  Orders               [All (5)] │
├─────────────────────────────────────┤
│                                     │
│  Filter:                            │
│  [All] [Action Required] [Pending]  │
│                                     │
│  ─── Action Required ───            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Order #ORD-2026-001         ││
│  │  ─────────────────────────────  ││
│  │  Buyer: ABC Market              ││
│  │  Product: Maize Grade A        ││
│  │  Quantity: 1,200 kg             ││
│  │  💰 $540.00                     ││
│  │  ─────────────────────────────  ││
│  │  ⏰ Funded - Awaiting Pickup    ││
│  │                                 ││
│  │  ⚠️ Schedule pickup within     ││
│  │     24 hours                   ││
│  │                                 ││
│  │  [📅 Schedule Pickup]          ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Pending Payment ───            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Order #ORD-2026-002         ││
│  │  ─────────────────────────────  ││
│  │  Buyer: Fresh Grocery Co        ││
│  │  Product: Tomatoes              ││
│  │  Quantity: 500 kg               ││
│  │  Status: Awaiting Payment      ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Completed ───                  │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ✓ Order #ORD-2026-099         ││
│  │  Delivered - Feb 25, 2026      ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## 10. Settings & Profile

### 10.1 Profile Settings
```
┌─────────────────────────────────────┐
│ [←]  Profile Settings              │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │         👤                      ││
│  │    John Doe                     ││
│  │    👨‍🌾 Farmer                   ││
│  │    [Change Photo]              ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Account ───                   │
│                                     │
│  📧 Email                          │
│  ┌─────────────────────────────────┐│
│  │  john@farm.com                  ││
│  └─────────────────────────────────┘│
│                                     │
│  📱 Phone                          │
│  ┌─────────────────────────────────┐│
│  │  +251 912 345 678               ││
│  └─────────────────────────────────┘│
│                                     │
│  🔐 Password                       │
│  ┌─────────────────────────────────┐│
│  │  ••••••••••  [Change]           ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Preferences ───               │
│                                     │
│  🔔 Notifications                  │
│  ┌─────────────────────────────────┐│
│  │  Order Updates        [ON]     ││
│  │  Weather Alerts       [ON]     ││
│  │  Task Reminders       [ON]     ││
│  │  Marketing            [OFF]    ││
│  └─────────────────────────────────┘│
│                                     │
│  🌐 Language                       │
│  ┌─────────────────────────────────┐│
│  │  English (US)              ▼    ││
│  └─────────────────────────────────┘│
│                                     │
│  🔊 Audio Guidance                 │
│  ┌─────────────────────────────────┐│
│  │  Enable Voice Instructions [ON]││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Support ───                    │
│                                     │
│  ❓ Help Center                     │
│  📞 Contact Support                 │
│  📋 Terms & Privacy                │
│                                     │
│  🚪 [Log Out]                       │
│                                     │
└─────────────────────────────────────┘
```

---

## 11. Navigation Structure Summary

```
┌─────────────────────────────────────┐
│         BOTTOM NAVIGATION           │
├──────┬──────┬──────┬──────┬────────┤
│ 🏠   │ 🗺️   │ 📦   │ 🤖   │  👤   │
│Home  │ Map  │Orders│ AI   │Profile│
│      │      │      │      │       │
│Dash- │Farm  │Order │Diag- │Settings│
│board │View  │Inbox │nosis │Profile│
│      │Field │Pro-  │      │       │
│      │Detail│duct  │      │       │
│      │      │List  │      │       │
└──────┴──────┴──────┴──────┴────────┘
```

### Screen Flow Diagram
```
Login → Onboarding (1st time)
          ↓
     Farm Dashboard
          ↓
    ┌──────────────┬──────────────┐
    ↓              ↓              ↓
Fields        Orders         AI Tool
  ↓              ↓
Field Detail  Order Inbox
  ↓
Crop Cycle Timeline
  ↓
Harvest → Inventory → List Product
```

---

*Document Version: 1.0*
*Generated for: FarmConnect AgriManagement*
*Target: React + TypeScript Frontend*
