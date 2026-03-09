# Manager/Admin Role - Wireframes & Screen Designs

## FarmConnect AgriManagement

This document outlines the wireframes and screen designs for the **Manager/Admin** role, based on the UI/UX decisions in `ui_ux_decisions_summary.md`.

---

## 1. Authentication & Access

### 1.1 Admin Login Screen
```
┌─────────────────────────────────────┐
│         [FarmConnect Logo]          │
│       "AgriManagement Admin"        │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🔐 Keycloak SSO                ││
│  │     Sign in with your           ││
│  │     organization credentials    ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📧 Email / Username            ││
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
│  🔒 Secure Admin Portal              │
│  Two-factor authentication enabled   │
│                                     │
└─────────────────────────────────────┘
```

---

## 2. Executive Dashboard

### 2.1 Main Dashboard Overview
```
┌─────────────────────────────────────┐
│ 👑 Admin Dashboard    [🔔] [⚙️] [👤]│
├─────────────────────────────────────┤
│                                     │
│  Welcome back, Administrator        │
│  Today: Monday, March 6, 2026     │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  1,247   │ │   89%    │        │
│  │  Total   │ │  Active  │        │
│  │  Users   │ │  Rate    │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │   342    │ │  $45.2K  │        │
│  │  Active  │ │  Volume  │        │
│  │  Orders  │ │  Today   │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ─── Platform Overview ───          │
│                                     │
│  📊 Orders This Week        [📈]   │
│  ████████████████████░░ 89%        │
│  Goal: 400 orders                   │
│                                     │
│  🌾 Harvest Volume         [📈]   │
│  █████████████████░░░░ 72%        │
│  Goal: 50,000 kg                   │
│                                     │
│  ─── Alerts & Notifications ───    │
│                                     │
│  ⚠️  3 pending disputes            │
│  ⚠️  12 farms need QC review       │
│  ℹ️  New farmers registered: 15     │
│                                     │
│  ─── Quick Actions ───              │
│  [👥 Users] [📊 Reports] [⚙️ Config]│
│                                     │
└─────────────────────────────────────┘
```

### 2.2 Analytics Widgets Row
```
┌─────────────────────────────────────┐
│  📊 Platform Analytics              │
├─────────────────────────────────────┤
│                                     │
│  [Today] [Week] [Month] [Quarter]  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Orders Trend               │   │
│  │  ──────────────────────     │   │
│  │      📈                     │   │
│  │     ╱                       │   │
│  │  ──╱──────────────         │   │
│  │  M  T  W  T  F  S  S       │   │
│  │  45 52 48 61 73 82 94      │   │
│  │                             │   │
│  │  Total: 455 orders          │   │
│  │  +12% vs last week          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Revenue Distribution       │   │
│  │                             │   │
│  │    Maize ████████ 45%      │   │
│  │  Tomato █████ 25%           │   │
│  │ Cabbage ████ 18%            │   │
│  │  Other  ███ 12%             │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. User Management

### 3.1 User List View
```
┌─────────────────────────────────────┐
│ [←]  User Management        [+ Add] │
├─────────────────────────────────────┤
│                                     │
│  Search users...                     │
│  ┌─────────────────────────────────┐│
│  │  🔍  ─────────────────────     ││
│  └─────────────────────────────────┘│
│                                     │
│  Filter:                            │
│  [All] [Farmers] [Merchants] [Agents]│
│                                     │
│  ─── Users (1,247) ───              │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 John Doe                   ││
│  │  👨‍🌾 Farmer | john@farm.com    ││
│  │  📍 Oromia Region             ││
│  │  ✅ Active | Joined Jan 2026  ││
│  │  [View] [Edit] [Disable]      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 ABC Market LLC            ││
│  │  🏪 Merchant | buyer@abc.com   ││
│  │  📍 Addis Ababa               ││
│  │  ✅ Active | Joined Dec 2025   ││
│  │  [View] [Edit] [Disable]      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 Dr. Alemayehu             ││
│  │  👨‍🌾 Agronomist | ale@expert.com││
│  │  📍 All Regions               ││
│  │  ✅ Active | Joined Nov 2025  ││
│  │  [View] [Edit] [Disable]      ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Pagination ───                 │
│  [<] Page 1 of 125 [>]             │
│                                     │
└─────────────────────────────────────┘
```

### 3.2 User Detail View
```
┌─────────────────────────────────────┐
│ [←]  User Details                   │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │         👤                      ││
│  │    John Doe                     ││
│  │    👨‍🌾 Farmer                  ││
│  │    ID: USR-2026-001            ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Account Information ───         │
│                                     │
│  📧 Email: john@farm.com            │
│  📱 Phone: +251 912 345 678         │
│  📍 Region: Oromia                   │
│  🏠 District: East Hararghe         │
│                                     │
│  ─── Farm Information ───           │
│                                     │
│  Farms: 2 (View)                    │
│  Total Area: 24.5 ha                │
│                                     │
│  ─── Order Statistics ───           │
│                                     │
│  Total Orders: 45                   │
│  Completed: 42                      │
│  Cancelled: 3                       │
│  Reputation: ⭐ 4.7                  │
│                                     │
│  ─── Account Status ───             │
│                                     │
│  Status: ✅ Active                  │
│  Joined: January 15, 2026           │
│  Last Login: Today, 10:30 AM       │
│                                     │
│  ─── Actions ───                    │
│  [✏️ Edit User] [🔒 Reset Password] │
│  [❌ Disable Account] [🗑️ Delete]   │
│                                     │
└─────────────────────────────────────┘
```

### 3.3 Create/Edit User Modal
```
┌─────────────────────────────────────┐
│  ✏️ Create User                      │
├─────────────────────────────────────┤
│                                     │
│  Role:                              │
│  ┌─────────────────────────────────┐│
│  │  [Select Role ▼]               ││
│  │  ○ Farmer                      ││
│  │  ○ Merchant                    ││
│  │  ○ Agent                      ││
│  │  ○ Agronomist                 ││
│  │  ○ Manager                    ││
│  │  ● Admin                      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 Full Name                   ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📧 Email                       ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📱 Phone Number                 ││
│  └─────────────────────────────────┘│
│                                     │
│  Keycloak ID (if linking existing): │
│  ┌─────────────────────────────────┐│
│  │  [Auto-generated or enter UUID] ││
│  └─────────────────────────────────┘│
│                                     │
│  Region Assignment:                 │
│  ┌─────────────────────────────────┐│
│  │  [Select Region ▼]              ││
│  └─────────────────────────────────┘│
│                                     │
│  Permissions:                       │
│  ┌─────────────────────────────────┐│
│  │  ☐ Can approve listings        ││
│  │  ☐ Can resolve disputes        ││
│  │  ☐ Can view financial reports  ││
│  │  ☐ Can manage users           ││
│  └─────────────────────────────────┘│
│                                     │
│       [Cancel]    [Create User]     │
│                                     │
└─────────────────────────────────────┘
```

---

## 4. Reports & Analytics

### 4.1 Reports Dashboard
```
┌─────────────────────────────────────┐
│ [←]  Reports & Analytics           │
├─────────────────────────────────────┤
│                                     │
│  Report Categories:                 │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📊 Platform Performance       ││
│  │  Overview, trends, KPIs         ││
│  │  [Generate Report]             ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌾 Harvest Analytics          ││
│  │  Yields, cycles, predictions   ││
│  │  [Generate Report]             ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Order Analytics            ││
│  │  Volume, revenue, fulfillment  ││
│  │  [Generate Report]             ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  💰 Financial Summary           ││
│  │  Revenue, fees, transactions   ││
│  │  [Generate Report]             ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👥 User Activity              ││
│  │  Engagement, retention, growth ││
│  │  [Generate Report]             ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🗺️ Regional Analytics          ││
│  │  Geographic distribution       ││
│  │  [Generate Report]             ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Recent Reports ───             │
│                                     │
│  📄 Platform_Report_Feb2026.pdf    │
│  Generated: Feb 28, 2026           │
│  [Download] [View]                 │
│                                     │
└─────────────────────────────────────┘
```

### 4.2 Detailed Report View
```
┌─────────────────────────────────────┐
│ [←]  Platform Performance Report   │
├─────────────────────────────────────┤
│                                     │
│  📅 Period: February 2026          │
│  Generated: March 1, 2026          │
│                                     │
│  ─── Executive Summary ───         │
│                                     │
│  Platform performed well with      │
│  12% growth in orders and 8%        │
│  increase in active farmers.       │
│                                     │
│  ─── Key Metrics ───               │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  1,247  │ │   +12%   │        │
│  │  Total   │ │  Growth  │        │
│  │  Users   │ │  MoM     │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  3,450   │ │  $285K   │        │
│  │  Orders  │ │  GMV     │        │
│  │  +15%    │ │  +18%    │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ─── Charts ───                    │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Order Volume by Day       │   │
│  │  ████████████              │   │
│  │  █████████████             │   │
│  │  █████████████████         │   │
│  │  Week 1-4 progression     │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Top Product Categories     │   │
│  │  Maize: 45%                 │   │
│  │  Tomato: 25%                │   │
│  │  Cabbage: 18%               │   │
│  │  Other: 12%                 │   │
│  └─────────────────────────────┘   │
│                                     │
│       [Export PDF] [Share]          │
│                                     │
└─────────────────────────────────────┘
```

### 4.3 Financial Report
```
┌─────────────────────────────────────┐
│ [←]  Financial Summary Report       │
├─────────────────────────────────────┤
│                                     │
│  📅 Period: Q1 2026 (Jan - Mar)    │
│                                     │
│  ─── Revenue Summary ───            │
│                                     │
│  Gross Merchandise Value:           │
│  ┌─────────────────────────────────┐│
│  │      $1,245,000.00             ││
│  └─────────────────────────────────┘│
│                                     │
│  Platform Fees:                     │
│  ┌─────────────────────────────────┐│
│  │    $62,250.00 (5%)             ││
│  └─────────────────────────────────┘│
│                                     │
│  Delivery Fees:                     │
│  ┌─────────────────────────────────┐│
│  │    $24,500.00 (collected)      ││
│  └─────────────────────────────────┘│
│                                     │
│  Net Revenue:                      │
│  ┌─────────────────────────────────┐│
│  │    $86,750.00                  ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Transaction Volume ───        │
│                                     │
│  Total Transactions: 4,521         │
│  Average Order Value: $275.38      │
│                                     │
│  ─── Escrow Balances ───           │
│                                     │
│  Active Escrow: $45,230.00         │
 Period│  Released This: $198,450.00 │
│                                     │
│       [Export PDF] [Export Excel]   │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Dispute Management

### 5.2 Dispute Resolution Dashboard
```
┌─────────────────────────────────────┐
│ [←]  Dispute Management             │
├─────────────────────────────────────┤
│                                     │
│  Filter: [All] [Open] [Resolved]   │
│                                     │
│  ─── Open Disputes (3) ───         │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ⚠️  DSP-2026-089              ││
│  │  ───────────────────────────   ││
│  │  Farmer: John Doe              ││
│  │  Merchant: ABC Market           ││
│  │  Product: Maize (500kg)        ││
│  │  Amount: $225.00               ││
│  │  Issue: Quality dispute         ││
│  │  Status: Under Review          ││
│  │                                ││
│  │  Assigned: Agent Tekle         ││
│  │  [View Details] [Resolve]     ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ⚠️  DSP-2026-085              ││
│  │  ───────────────────────────   ││
│  │  Farmer: Maryam Ahmed          ││
│  │  Merchant: Fresh Co            ││
│  │  Product: Tomatoes (200kg)     ││
│  │  Amount: $180.00               ││
│  │  Issue: Delayed delivery        ││
│  │  Status: Awaiting Evidence      ││
│  │                                ││
│  │  [View Details]                ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Resolved This Month (12) ───   │
│                                     │
│  ✓ DSP-2026-082 - Resolved in favor │
│    of merchant                     │
│  ✓ DSP-2026-078 - Resolved in favor │
│    of farmer                       │
│                                     │
└─────────────────────────────────────┘
```

### 5.2 Dispute Detail & Resolution
```
┌─────────────────────────────────────┐
│ [←]  Dispute DSP-2026-089          │
├─────────────────────────────────────┤
│                                     │
│  ─── Case Overview ───              │
│                                     │
│  Status: Under Review               │
│  Priority: ⚡ High                  │
│  Created: March 2, 2026            │
│  Assigned To: Agent Tekle          │
│                                     │
│  ─── Parties Involved ───           │
│                                     │
│  👨‍🌾 Farmer: John Doe              │
│     Farm: My Family Farm            │
│     Contact: +251 912 345 678       │
│                                     │
│  🏪 Merchant: ABC Market LLC       │
│     Contact: buyer@abc.com          │
│                                     │
│  ─── Order Details ───              │
│                                     │
│  Order: #ORD-2026-156               │
│  Product: Maize Grade A            │
│  Quantity: 500 kg                   │
│  Amount: $225.00                   │
│                                     │
│  ─── Dispute Details ───            │
│                                     │
│  Type: Quality Dispute              │
│  Reason: "Delivered maize does not  │
│           match agreed quality grade"│
│                                     │
│  Evidence Submitted:               │
│  📷 photo_1.jpg                     │
│  📷 photo_2.jpg                     │
│  📄 quality_report.pdf              │
│                                     │
│  ─── Timeline ───                   │
│                                     │
│  Mar 2, 10:00 AM - Dispute opened  │
│  Mar 2, 02:30 PM - Evidence reviewed│
│  Mar 3, 09:00 AM - Agent assigned  │
│                                     │
│  ─── Resolution Actions ───         │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  💬 Contact Farmer              ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  💬 Contact Merchant            ││
│  └─────────────────────────────────┘│
│                                     │
│  Resolution:                       │
│  ┌─────────────────────────────────┐│
│  │  ○ Release funds to farmer     ││
│  │  ○ Refund to merchant          ││
│  │  ○ Split 50/50                ││
│  │  ○ Partial refund: $________   ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📝 Resolution Notes            ││
│  │  [Enter reasoning...]           ││
│  └─────────────────────────────────┘│
│                                     │
│      [Cancel]    [Resolve Dispute] │
│                                     │
└─────────────────────────────────────┘
```

---

## 6. Configuration & Settings

### 6.1 Platform Configuration
```
┌─────────────────────────────────────┐
│ [←]  Platform Configuration        │
├─────────────────────────────────────┤
│                                     │
│  ─── General Settings ───            │
│                                     │
│  Platform Name:                     │
│  ┌─────────────────────────────────┐│
│  │  FarmConnect AgriManagement     ││
│  └─────────────────────────────────┘│
│                                     │
│  Support Email:                     │
│  ┌─────────────────────────────────┐│
│  │  support@farmconnect.et        ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Order Settings ───             │
│                                     │
│  Order Timeout (hours):             │
│  ┌─────────────────────────────────┐│
│  │  24  [Auto-cancel unconfirmed]  ││
│  └─────────────────────────────────┘│
│                                     │
│  Escrow Release Days:               │
│  ┌─────────────────────────────────┐│
│  │  3   [After successful delivery]││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Fee Configuration ───          │
│                                     │
│  Platform Fee (%):                  │
│  ┌─────────────────────────────────┐│
│  │  5.0                            ││
│  └─────────────────────────────────┘│
│                                     │
│  Delivery Margin (%):               │
│  ┌─────────────────────────────────┐│
│  │  10.0                           ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Feature Flags ───              │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  AI Diagnostics      [ON]     ││
│  │  Weather Integration  [ON]     ││
│  │  Escrow Payments     [ON]      ││
│  │  QC Workflow         [ON]      ││
│  │  Maintenance Mode    [OFF]     ││
│  └─────────────────────────────────┘│
│                                     │
│       [Save Changes]                │
│                                     │
└─────────────────────────────────────┘
```

### 6.2 Pricing Rules Management
```
┌─────────────────────────────────────┐
│ [←]  Pricing Rules                 │
├─────────────────────────────────────┤
│                                     │
│  [+ Add New Rule]                   │
│                                     │
│  ─── Active Rules ───               │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Base Delivery Fee           ││
│  │  Type: Distance-based           ││
│  │  Base: $5.00 + $0.50/km        ││
│  │  Priority: 1                    ││
│  │  Status: Active                 ││
│  │  [Edit] [Disable]              ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Quality Premium            ││
│  │  Type: Quality-based            ││
│  │  Grade A: +10%                 ││
│  │  Grade B: +0%                  ││
│  │  Grade C: -5%                  ││
│  │  Priority: 2                    ││
│  │  Status: Active                 ││
│  │  [Edit] [Disable]              ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Regional Adjustment         ││
│  │  Type: Region-based             ││
│  │  Addis Ababa: -5%              ││
│  │  Oromia: +0%                    ││
│  │  SNNPR: +5%                    ││
│  │  Priority: 3                    ││
│  │  Status: Active                 ││
│  │  [Edit] [Disable]              ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Inactive Rules ───             │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 Seasonal Promo (Expired)   ││
│  │  Valid: Jan 1-31, 2026         ││
│  │  [Edit] [Enable]              ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## 7. Regional Analytics

### 7.1 Regional Overview Map
```
┌─────────────────────────────────────┐
│ [←]  Regional Analytics    [Map ▼]  │
├─────────────────────────────────────┤
│                                     │
│  Select Region: [All Regions ▼]     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  🗺️  Ethiopia Regional Map   │   │
│  │                             │   │
│  │   ┌──┐ ┌──┐ ┌──┐            │   │
│  │   │  │ │★ │ │  │            │   │
│  │   └──┘ └──┘ └──┘            │   │
│  │   Oromia  AA  SNNPR          │   │
│  │                             │   │
│  │   ┌──┐ ┌──┐                 │   │
│  │   │  │ │  │                 │   │
│  │   └──┘ └──┘                 │   │
│  │   Amhara Tigray              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ─── Regional Statistics ───        │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📍 Oromia Region              ││
│  │  ─────────────────────────────  ││
│  │  Farmers: 523                   ││
│  │  Orders: 1,245                 ││
│  │  Revenue: $125,000             ││
│  │  Top Crop: Maize               ││
│  │  [View Details]                ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📍 Addis Ababa               ││
│  │  ─────────────────────────────  ││
│  │  Farmers: 89                   ││
│  │  Orders: 567                   ││
│  │  Revenue: $85,000              ││
│  │  Top Crop: Vegetables          ││
│  │  [View Details]                ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 7.2 Regional Detail View
```
┌─────────────────────────────────────┐
│ [←]  Oromia Region Details          │
├─────────────────────────────────────┤
│                                     │
│  📍 Oromia Region                   │
│  Population: 35M | Farming: 70%     │
│                                     │
│  ─── Key Metrics ───                │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  523    │ │  1,245   │        │
│  │  Farmers │ │ Orders   │        │
│  │  +15%    │ │ +22%     │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  $125K   │ │  4,500   │        │
│  │  Revenue  │ │ Harvested│        │
│  │  +18%    │ │ kg       │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ─── District Breakdown ───        │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  East Hararghe     156 farmers ││
│  │  ████████████████████          ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  West Hararghe     98 farmers  ││
│  │  █████████████                  ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  Arsi               87 farmers ││
│  │  ████████████                   ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  East Shoa        72 farmers   ││
│  │  ██████████                     ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Top Products ───               │
│                                     │
│  🌽 Maize: 45%                      │
│  🍅 Tomato: 25%                     │
│  🥬 Cabbage: 18%                    │
│  🫑 Pepper: 12%                     │
│                                     │
│       [Export Report]               │
│                                     │
└─────────────────────────────────────┘
```

---

## 8. System Health & Monitoring

### 8.1 System Status Dashboard
```
┌─────────────────────────────────────┐
│ [←]  System Health                  │
├─────────────────────────────────────┤
│                                     │
│  ─── Service Status ───             │
│                                     │
│  ✅ API Gateway          [Healthy]  │
│     Response: 45ms                 │
│                                     │
│  ✅ Database Connection   [Healthy] │
│     Connections: 24/100            │
│                                     │
│  ✅ Authentication      [Healthy]  │
│     Keycloak: Connected            │
│                                     │
│  ✅ Payment Gateway      [Healthy]  │
│     Escrow: Operational            │
│                                     │
│  ✅ Weather Service     [Healthy]  │
│     Last sync: 5 min ago          │
│                                     │
│  ✅ AI Service          [Healthy]   │
│     Model: v2.1.0                  │
│                                     │
│  ─── Server Metrics ───             │
│                                     │
│  CPU: ██████░░░░ 60%                │
│  Memory: ████████░░ 78%             │
│  Disk: ███░░░░░░░ 28%              │
│                                     │
│  ─── Recent Events ───              │
│                                     │
│  ℹ️  Deployment v2.5.1 completed    │
│  ℹ️  Database backup completed       │
│  ⚠️  High API latency detected      │
│      (resolved automatically)      │
│                                     │
│       [View Logs] [System Report]   │
│                                     │
└─────────────────────────────────────┘
```

---

## 9. Audit Logs

### 9.1 Audit Trail View
```
┌─────────────────────────────────────┐
│ [←]  Audit Logs                     │
├─────────────────────────────────────┤
│                                     │
│  Filter by:                         │
│  [All Actions ▼] [User ▼] [Date ▼] │
│                                     │
│  Search:                            │
│  ┌─────────────────────────────────┐│
│  │  🔍  ─────────────────────     ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Recent Activity ───            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 admin@farmconnect.et       ││
│  │  Updated pricing rules         ││
│  │  Mar 6, 2026 10:30 AM         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 system                      ││
│  │  Completed daily backup        ││
│  │  Mar 6, 2026 02:00 AM         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 agent@farmconnect.et       ││
│  │  Resolved dispute DSP-2026-082 ││
│  │  Mar 5, 2026 04:15 PM         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 farmer@farm.com            ││
│  │  Created new farm              ││
│  │  Mar 5, 2026 11:20 AM         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 merchant@abc.com           ││
│  │  Placed order #ORD-2026-201   ││
│  │  Mar 5, 2026 09:45 AM         ││
│  └─────────────────────────────────┘│
│                                     │
│  [Export Logs] [Filter by Date]    │
│                                     │
└─────────────────────────────────────┘
```

---

## 10. Navigation Structure

```
┌─────────────────────────────────────┐
│         ADMIN SIDEBAR               │
├─────────────────────────────────────┤
│ 👑 Admin Panel                      │
│                                     │
│ 🏠 Dashboard                        │
│                                     │
│ 👥 User Management                  │
│   ├─ All Users                      │
│   ├─ Farmers                        │
│   ├─ Merchants                      │
│   └─ Staff                          │
│                                     │
│ 📊 Reports & Analytics              │
│   ├─ Platform Performance           │
│   ├─ Financial Reports              │
│   └─ Regional Analytics             │
│                                     │
│ ⚖️ Disputes                         │
│                                     │
│ ⚙️ Configuration                   │
│   ├─ General Settings               │
│   ├─ Pricing Rules                 │
│   └─ Feature Flags                 │
│                                     │
│ 🔧 System                           │
│   ├─ Health Check                   │
│   └─ Audit Logs                     │
│                                     │
│                                     │
│ ─────────────────────               │
│ [👤 Profile] [🚪 Logout]           │
└─────────────────────────────────────┘
```

---

## 11. Mobile Admin View

For mobile access, the admin panel simplifies to:
```
┌─────────────────────────────────────┐
│ ☰  Dashboard        [🔔] [👤]      │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  1,247   │ │   342    │        │
│  │  Users   │ │ Orders   │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ⚠️ 3 Open Disputes                │
│                                     │
│  ─── Quick Actions ───              │
│                                     │
│  [👥 Users]  [📊 Reports]          │
│                                     │
│  [⚖️ Disputes] [⚙️ Settings]       │
│                                     │
│  ─── Alerts ───                    │
│                                     │
│  ⚠️  New farmer registrations: 5   │
│  ℹ️  System backup completed        │
│                                     │
└─────────────────────────────────────┘
```

---

*Document Version: 1.0*
*Generated for: FarmConnect AgriManagement*
*Target: React + TypeScript Frontend*
