# Merchant Role - Wireframes & Screen Designs

## FarmConnect AgriManagement

This document outlines the wireframes and screen designs for the **Merchant (Buyer)** role, based on the UI/UX decisions in `ui_ux_decisions_summary.md`.

---

## 1. Authentication & Onboarding

### 1.1 Login Screen
```
┌─────────────────────────────────────┐
│         [FarmConnect Logo]          │
│       "Farm-to-Table Marketplace"   │
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
│  "Don't have an account? Register"  │
│                                     │
│  🌐 English ▼  |  🔊 Audio On       │
└─────────────────────────────────────┘
```

### 1.2 Registration Screen
```
┌─────────────────────────────────────┐
│  [←]  Create Merchant Account       │
│                                     │
│  Select Your Role:                 │
│  ┌───────────┐  ┌───────────┐      │
│  │  👨‍🌾      │  │  🏪      │      │
│  │  Farmer   │  │ Merchant  │      │
│  │    ○      │  │    ●      │      │
│  └───────────┘  └───────────┘      │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🏪 Business Name               ││
│  │  "Fresh Grocery Co."            ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  👤 Contact Person               ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  📧 Email                        ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  📱 Phone Number                 ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  📍 Business Address             ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  🔒 Create Password             ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  🔒 Confirm Password            ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📋 Business License (Optional) ││
│  │  [Upload Document]              ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │        [CREATE ACCOUNT]         ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

---

## 2. Dashboard Overview

### 2.1 Main Dashboard
```
┌─────────────────────────────────────┐
│ 🏪 Fresh Grocery Co.   [🔔] [⚙️]  │
├─────────────────────────────────────┤
│                                     │
│  Welcome back! Today: Mar 6, 2026 │
│                                     │
│  ─── Today's Summary ───             │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  3 Active │ │  12     │        │
│  │  Orders   │ │ Pending │        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ┌──────────┐ ┌──────────┐        │
│  │  $1,250  │ │  4.8    │        │
│  │  Revenue  │ │ ⭐ Rating│        │
│  └──────────┘ └──────────┘        │
│                                     │
│  ─── Orders Requiring Action ───    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🚚 Ready for Pickup (2)       ││
│  │  📦 #ORD-2026-156             ││
│  │  Maize Grade A - 500kg         ││
│  │  Farmer: John Doe              ││
│  │  [View Details]                ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ⏳ Payment Pending (1)         ││
│  │  📦 #ORD-2026-158             ││
│  │  Tomatoes - 200kg              ││
│  │  Farmer: Sarah Ali             ││
│  │  [Complete Payment]            ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Discover Products ───          │
│                                     │
│  [Browse Marketplace]              │
│                                     │
│  ─── Alerts ───                     │
│  ℹ️ Price drop: Maize down 5%      │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. Product Discovery (Marketplace)

### 3.1 Product Discovery Grid
```
┌─────────────────────────────────────┐
│ [←]  Marketplace           [🛒] [🔍]│
├─────────────────────────────────────┤
│                                     │
│  Search products...                  │
│  ┌─────────────────────────────────┐│
│  │  🔍  ───────────────────────    ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Categories ───                 │
│                                     │
│  [All] [🌽 Grains] [🍅 Vegetables] │
│  [🍎 Fruits] [🫘 Legumes] [🌿 Herbs]│
│                                     │
│  ─── Products ───                   │
│                                     │
│  ┌───────────┐ ┌───────────┐        │
│  │  🌽      │ │  🌽       │        │
│  │  Maize   │ │  Maize    │        │
│  │  Grade A │ │  Grade B  │        │
│  │ ─────────│ │ ───────── │        │
│  │ $0.45/kg │ │ $0.35/kg │        │
│  │ 2,000kg  │ │ 1,500kg   │        │
│  │ 📍 Oromia│ │ 📍 SNNPR  │        │
│  │ ─────────│ │ ───────── │        │
│  │ 👨‍🌾 John │ │ 👨‍🌾 Mary │        │
│  │ ⭐ 4.8   │ │ ⭐ 4.5    │        │
│  │[Add to  ]│ │[Add to  ]│        │
│  │[ Cart  ] │ │[ Cart  ] │        │
│  └───────────┘ └───────────┘        │
│                                     │
│  ┌───────────┐ ┌───────────┐        │
│  │  🍅      │ │  🥬      │        │
│  │  Tomato  │ │  Cabbage  │        │
│  │ ─────────│ │ ───────── │        │
│  │ $0.90/kg │ │ $0.40/kg │        │
│  │ 500kg    │ │ 3,000kg   │        │
│  │ 📍 AA    │ │ 📍 Oromia │        │
│  │ ─────────│ │ ───────── │        │
│  │ 👨‍🌾 Ahmed│ │ 👨‍🌾 Tekle│        │
│  │ ⭐ 4.9   │ │ ⭐ 4.7    │        │
│  │[Add to  ]│ │[Add to  ]│        │
│  │[ Cart  ] │ │[ Cart  ] │        │
│  └───────────┘ └───────────┘        │
│                                     │
│  [<] 1 2 3 4 5 [>]                │
│                                     │
└─────────────────────────────────────┘
```

### 3.2 Product Detail View (Farm-to-Table Visual)
```
┌─────────────────────────────────────┐
│ [←]  Product Details               │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │      📷 Product Image       │   │
│  │                             │   │
│  │  [View All 4 Photos]        │   │
│  └─────────────────────────────┘   │
│                                     │
│  🌽 Premium Maize - Grade A         │
│                                     │
│  ─── Farmer Information ───         │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤  John Doe                   ││
│  │  ⭐ 4.8 (156 orders)           ││
│  │  📍 Oromia, Ethiopia           ││
│  │  [View Farm Profile]          ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Product Details ───            │
│                                     │
│  Available: 2,000 kg               │
│  Quality: Grade A (Premium)        │
│  Harvest Date: Feb 20, 2026       │
│  Expected Expiry: Mar 30, 2026   │
│                                     │
│  ─── Pricing ───                    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │        $0.45 / kg              ││
│  │                                 ││
│  │  Quantity: [  500  ] kg       ││
│  │        -100   +100            ││
│  └─────────────────────────────────┘│
│                                     │
│  Subtotal: $225.00                 │
│  Delivery: Calculated at checkout  │
│  Platform Fee: $11.25 (5%)        │
│                                     │
│  ─── Delivery ───                  │
│                                     │
│  Delivery Address:                 │
│  ┌─────────────────────────────────┐│
│  │  📍 Bole, Addis Ababa         ││
│  │  [Change]                      ││
│  └─────────────────────────────────┘│
│                                     │
│  Estimated Delivery:                │
│  2-3 business days                 │
│                                     │
│  ┌─────────────────────────────────┐│
│  │      [ADD TO CART]             ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 3.3 Search & Filter
```
┌─────────────────────────────────────┐
│ [←]  Search Results     [Filters ▼] │
├─────────────────────────────────────┤
│                                     │
│  "Maize" - 45 results              │
│                                     │
│  ─── Active Filters ───            │
│                                     │
│  [x] Price: $0.30-$0.50 [Clear]    │
│  [x] Location: Oromia [Clear]      │
│                                     │
│  ─── Sort By ───                   │
│                                     │
│  [Price: Low to High ▼]            │
│                                     │
│  ─── Results ───                    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize Grade A              ││
│  │  $0.45/kg | 2,000kg           ││
│  │  Farmer: John Doe | ⭐4.8      ││
│  │  📍 Oromia                     ││
│  │  [View] [Add to Cart]         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize Grade A              ││
│  │  $0.42/kg | 3,500kg           ││
│  │  Farmer: Bekele Farm | ⭐4.6   ││
│  │  📍 SNNPR                      ││
│  │  [View] [Add to Cart]         ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## 4. Shopping Cart & Checkout

### 4.1 Shopping Cart
```
┌─────────────────────────────────────┐
│ [←]  Shopping Cart        [🛒 (2)] │
├─────────────────────────────────────┤
│                                     │
│  ─── Cart Items ───                 │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize Grade A              ││
│  │  ───────────────────────────   ││
│  │  Farmer: John Doe              ││
│  │  Quantity: 500 kg             ││
│  │  Price: $0.45/kg              ││
│  │                                ││
│  │  Subtotal: $225.00            ││
│  │                                ││
│  │  [−] 500 [+] | [🗑️ Remove]   ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🍅 Tomatoes (Premium)         ││
│  │  ───────────────────────────   ││
│  │  Farmer: Sarah Ali             ││
│  │  Quantity: 200 kg             ││
│  │  Price: $0.90/kg              ││
│  │                                ││
│  │  Subtotal: $180.00            ││
│  │                                ││
│  │  [−] 200 [+] | [🗑️ Remove]   ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Price Summary ───              │
│                                     │
│  Products: $405.00                 │
│  Platform Fee (5%): $20.25         │
│  Delivery: $35.00                  │
│  ──────────────────────────────    │
│  Total: $460.25                    │
│                                     │
│  ─── Delivery Address ───           │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📍 Bole, Addis Ababa         ││
│  │  [Change]                      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │     [PROCEED TO CHECKOUT]      ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 4.2 Checkout Flow
```
┌─────────────────────────────────────┐
│ [←]  Checkout - Step 2 of 3        │
├─────────────────────────────────────┤
│                                     │
│  Progress: [✓] Cart [●] Payment [ ]│
│                                     │
│  ─── Order Review ───               │
│                                     │
│  Items (2):                         │
│  • Maize Grade A - 500kg ($225.00) │
│  • Tomatoes - 200kg ($180.00)      │
│                                     │
│  ─── Delivery ───                   │
│                                     │
│  Address:                          │
│  ┌─────────────────────────────────┐│
│  │  Fresh Grocery Co.              ││
│  │  Bole, Addis Ababa             ││
│  │  Attn: Ahmed Mohammed           ││
│  └─────────────────────────────────┘│
│                                     │
│  Preferred Time:                     │
│  ┌─────────────────────────────────┐│
│  │  [Any Time ▼]                  ││
│  │  Morning (8am-12pm)            ││
│  │  Afternoon (12pm-5pm)          ││
│  │  Evening (5pm-8pm)             ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Payment Method ───             │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ● Bank Transfer               ││
│  │  ○ Mobile Money                ││
│  │  ○ Wallet Balance ($500.00)   ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Order Summary ───              │
│                                     │
│  Subtotal: $405.00                 │
│  Platform Fee: $20.25               │
│  Delivery: $35.00                  │
│  ──────────────────────────────    │
│  Total: $460.25                    │
│                                     │
│       [Back]    [Proceed to Pay]    │
│                                     │
└─────────────────────────────────────┘
```

### 4.3 Payment (Optimistic Checkout)
```
┌─────────────────────────────────────┐
│  ⚠️  Payment Processing              │
├─────────────────────────────────────┤
│                                     │
│  ⏳ Processing your payment...       │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Order: #ORD-2026-159         ││
│  │  Amount: $460.25              ││
│  │  Method: Bank Transfer        ││
│  └─────────────────────────────────┘│
│                                     │
│  Please wait while we confirm        │
│  your payment with the bank...      │
│                                     │
│         [⏳ Processing]              │
│                                     │
└─────────────────────────────────────┘
```

### 4.4 Payment Error (Stock Conflict)
```
┌─────────────────────────────────────┐
│  ⚠️  Payment Failed                  │
├─────────────────────────────────────┤
│                                     │
│  😔 We're sorry!                    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  One of the items you          ││
│  │  selected is no longer         ││
│  │  available in the requested     ││
│  │  quantity.                     ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Affected Items ───            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize Grade A              ││
│  │  Requested: 500kg              ││
│  │  Available: 200kg              ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Options ───                    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [Reduce Quantity to 200kg]    ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [Remove Item & Continue]      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [Return to Cart]              ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 4.5 Payment Success
```
┌─────────────────────────────────────┐
│  ✅ Order Confirmed!                 │
├─────────────────────────────────────┤
│                                     │
│  🎉 Thank you for your order!       │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Order: #ORD-2026-159         ││
│  │  ───────────────────────────   ││
│  │  Amount: $460.25              ││
│  │  Status: Paid & Escrow Funded ││
│  │                                ││
│  │  📦 2 items from 2 farmers    ││
│  │  🚚 Expected: 2-3 days       ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Next Steps ───                 │
│                                     │
│  1. Farmer has been notified         │
│  2. They will schedule pickup       │
│  3. You'll receive tracking updates │
│                                     │
│  ┌─────────────────────────────────┐│
│  │      [VIEW ORDER DETAILS]      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │      [CONTINUE SHOPPING]       ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Order Management

### 5.1 Orders List
```
┌─────────────────────────────────────┐
│ [←]  My Orders            [All ▼]   │
├─────────────────────────────────────┤
│                                     │
│  Filter:                            │
│  [All] [Active] [Completed] [Refund]│
│                                     │
│  ─── Active Orders (5) ───         │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 #ORD-2026-159             ││
│  │  ───────────────────────────   ││
│  │  🌽 Maize 500kg + 🍅 200kg   ││
│  │  Total: $460.25               ││
│  │  Status: ⏳ Awaiting Pickup   ││
│  │  Farmer: John D., Sarah A.    ││
│  │  [Track Order →]              ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  📦 #ORD-2026-156             ││
│  │  ───────────────────────────   ││
│  │  🌽 Maize Grade A - 500kg     ││
│  │  Total: $225.00               ││
│  │  Status: 🚚 In Transit        ││
│  │  Farmer: John Doe              ││
│  │  ETA: Today, 2-4 PM          ││
│  │  [Track Order →]              ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Completed (12) ───            │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ✓ #ORD-2026-145              ││
│  │  Delivered: Feb 28, 2026      ││
│  │  [View Details] [Reorder]    ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ✓ #ORD-2026-132              ││
│  │  Delivered: Feb 22, 2026      ││
│  │  [View Details] [Reorder]    ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 5.2 Order Detail & Tracking
```
┌─────────────────────────────────────┐
│ [←]  Order #ORD-2026-159            │
├─────────────────────────────────────┤
│                                     │
│  Status: 🚚 In Transit              │
│                                     │
│  ─── Order Timeline ───             │
│                                     │
│  ✓ Paid - Mar 5, 10:30 AM         │
│    Payment confirmed, escrow funded │
│                                     │
│  ✓ Processing - Mar 5, 02:00 PM   │
│    Farmers preparing order          │
│                                     │
│  ● In Transit - Mar 6, 09:15 AM    │
│    Package in transit               │
│    Last: Awaday, Oromia            │
│                                     │
│  ○ Expected Delivery                │
│    Today, 2-4 PM                   │
│                                     │
│  ─── Items (2) ───                 │
│                                     │
│  1. 🌽 Maize Grade A - 500kg      │
│     Farmer: John Doe               │
│     $225.00                        │
│                                     │
│  2. 🍅 Tomatoes - 200kg           │
│     Farmer: Sarah Ali              │
│     $180.00                        │
│                                     │
│  ─── Delivery Details ───           │
│                                     │
│  To: Bole, Addis Ababa             │
│  Driver: Tadesse K.               │
│  Vehicle: ABC-1234                 │
│                                     │
│  ─── Payment Summary ───            │
│                                     │
│  Products: $405.00                 │
│  Platform Fee: $20.25              │
│  Delivery: $35.00                  │
│  ──────────────────────────────    │
│  Total: $460.25                     │
│  Escrow: $460.25 (Secured)         │
│                                     │
│  ─── Actions ───                    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [📞 Contact Driver]           ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  [💬 Report Issue]              ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  [✓ Confirm Delivery]          ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 5.3 Delivery Confirmation (QR Handover)
```
┌─────────────────────────────────────┐
│  ✓ Ready for Confirmation           │
├─────────────────────────────────────┤
│                                     │
│  ─── Delivery Arrived ───           │
│                                     │
│  Driver: Tadesse K.                │
│  Vehicle: ABC-1234                  │
│                                     │
│  ┌─────────────────────────────────┐│
│  │                                 ││
│  │       ████████████████         ││
│  │       █            ██          ││
│  │       █  QR CODE    ██         ││
│  │       █            ██          ││
│  │       ████████████████         ││
│  │                                 ││
│  │    Show this QR code to        ││
│  │       the driver               ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Or Enter Confirmation Code ─── │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [  A B 1 2 3 4  ]            ││
│  └─────────────────────────────────┘│
│                                     │
│  Scanning transfers custody of:     │
│  • Maize Grade A - 500kg           │
│  • Tomatoes - 200kg                │
│                                     │
│  Once confirmed, funds will be      │
│  released to farmers.              │
│                                     │
└─────────────────────────────────────┘
```

---

## 6. Order Issues & Disputes

### 6.1 Report Issue
```
┌─────────────────────────────────────┐
│ [←]  Report Issue - #ORD-2026-156   │
├─────────────────────────────────────┤
│                                     │
│  ─── Select Issue Type ───          │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ○ Item not received           ││
│  │  ○ Wrong items delivered       ││
│  │  ● Quality not as described    ││
│  │  ○ Damaged products            ││
│  │  ○ Quantity discrepancy        ││
│  └─────────────────────────────────┘│
│                                     │
│  Description:                       │
│  ┌─────────────────────────────────┐│
│  │  The maize delivered is        ││
│  │  lower quality than Grade A.   ││
│  │  About 20% appears to be       ││
│  │  Grade B or lower.            ││
│  │                                 ││
│  │  I have attached photos of     ││
│  │  the delivered product.        ││
│  └─────────────────────────────────┘│
│                                     │
│  Evidence Photos:                    │
│  ┌────┐ ┌────┐ ┌────┐            │
│  │ 📷 │ │ 📷 │ │ 📷 │  [+ Add]   │
│  └────┘ └────┘ └────┘            │
│                                     │
│  ─── Preferred Resolution ───      │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  ○ Request refund               ││
│  │  ○ Request replacement          ││
│  │  ● Partial refund + keep item   ││
│  └─────────────────────────────────┘│
│                                     │
│  Requested Refund Amount:           │
│  ┌─────────────────────────────────┐│
│  │  $ 45.00                       ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │      [SUBMIT REPORT]           ││
│  └─────────────────────────────────┘│
│                                     │
│  "An agent will review your case   │
│   and contact you within 24 hours" │
│                                     │
└─────────────────────────────────────┘
```

### 6.2 Agent Mediation
```
┌─────────────────────────────────────┐
│  💬 Mediation in Progress            │
├─────────────────────────────────────┤
│                                     │
│  Issue: Quality Dispute #DSP-089   │
│                                     │
│  ─── Case Summary ───               │
│                                     │
│  Your claim: Partial refund for     │
│  quality discrepancy               │
│                                     │
│  Farmer response: "I stand by      │
│  my product quality. It was        │
│  properly graded at harvest."       │
│                                     │
│  ─── Agent: Bekele M. ───          │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Bekele M. (Agent):            ││
│  │  I've reviewed the photos      ││
│  │  from both parties. I can     ││
│  │  see the issue. I'm working  ││
│  │  on a fair resolution.        ││
│  │                                ││
│  │  10:30 AM                     ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  You:                          ││
│  │  I understand. Please see      ││
│  │  the additional photo I       ││
│  │  just uploaded showing...     ││
│  │                                ││
│  │  10:15 AM                     ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Type your message...          ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  [📎 Add Photo]  [SEND]       ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Resolution Options ───        │
│                                     │
│  Awaiting agent's proposal...       │
│                                     │
└─────────────────────────────────────┘
```

---

## 7. Inventory Management (as a Seller)

### 7.1 Seller Dashboard (Dual Role)
```
┌─────────────────────────────────────┐
│ 🏪 Fresh Grocery Co.   [🛒] [📦]   │
├─────────────────────────────────────┤
│                                     │
│  Toggle View: [🛒 Buy] [📦 Sell]   │
│                                     │
│  ─── My Listed Products ───         │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize (Reselling)         ││
│  │  ───────────────────────────   ││
│  │  In Stock: 1,200 kg            ││
│  │  Sold: 800 kg                  ││
│  │  Price: $0.50/kg              ││
│  │  Revenue: $400.00              ││
│  │  Status: Active                ││
│  │  [Edit] [Deactivate]          ││
│  └─────────────────────────────────┘│
│                                     │
│  [+ List Product from Harvest]     │
│                                     │
└─────────────────────────────────────┘
```

---

## 8. Farmer Discovery & Sourcing

### 8.1 Farmer Directory
```
┌─────────────────────────────────────┐
│ [←]  Find Farmers        [Map ▼]    │
├─────────────────────────────────────┤
│                                     │
│  Search by location, crop, rating   │
│  ┌─────────────────────────────────┐│
│  │  🔍  ───────────────────────    ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Featured Farmers ───           │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 John Doe                    ││
│  │  ⭐ 4.8 (156 orders)           ││
│  │  📍 Oromia Region               ││
│  │  Crops: Maize, Wheat            ││
│  │  ───────────────────────────    ││
│  │  2 Farms | 45 ha total         ││
│  │  [View Profile] [Order]       ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 Sarah Ali                   ││
│  │  ⭐ 4.9 (89 orders)            ││
│  │  📍 SNNPR Region                ││
│  │  Crops: Tomato, Pepper          ││
│  │  ───────────────────────────    ││
│  │  1 Farm | 12 ha total          ││
│  │  [View Profile] [Order]       ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │  👤 Bekele Farm                 ││
│  │  ⭐ 4.6 (203 orders)           ││
│  │  📍 Amhara Region               ││
│  │  Crops: Teff, Barley            ││
│  │  ───────────────────────────    ││
│  │  3 Farms | 78 ha total         ││
│  │  [View Profile] [Order]       ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### 8.2 Farmer Profile
```
┌─────────────────────────────────────┐
│ [←]  Farmer Profile: John Doe       │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │         👤                      ││
│  │    John Doe                     ││
│  │    ⭐ 4.8 (156 orders)          ││
│  │    📍 Oromia, Ethiopia         ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Farm Information ───           │
│                                     │
│  Farms: 2                            │
│  Total Area: 45 hectares            │
│                                     │
│  ─── Current Products ───           │
│                                     │
│  ┌─────────────────────────────────┐│
│  │  🌽 Maize Grade A              ││
│  │  2,000 kg @ $0.45/kg          ││
│  │  [Add to Cart]                 ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Past Orders ───                │
│                                     │
│  Total Orders: 156                   │
│  Completed: 152 (97%)              │
│  Cancelled: 4 (3%)                  │
│                                     │
│  ─── Actions ───                    │
│                                     │
│  ┌─────────────────────────────────┐│
│  │      [ORDER PRODUCTS]           ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │  [📞 Contact Farmer]           ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

---

## 9. Settings & Profile

### 9.1 Merchant Settings
```
┌─────────────────────────────────────┐
│ [←]  Account Settings               │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │         🏪                      ││
│  │  Fresh Grocery Co.              ││
│  │  🏪 Merchant                   ││
│  │  [Change Logo]                 ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Business Information ───       │
│                                     │
│  Business Name:                      │
│  ┌─────────────────────────────────┐│
│  │  Fresh Grocery Co.              ││
│  └─────────────────────────────────┘│
│                                     │
│  Contact Person:                     │
│  ┌─────────────────────────────────┐│
│  │  Ahmed Mohammed                  ││
│  └─────────────────────────────────┘│
│                                     │
│  Email:                             │
│  ┌─────────────────────────────────┐│
│  │  buyer@freshgrocery.com         ││
│  └─────────────────────────────────┘│
│                                     │
│  Phone:                             │
│  ┌─────────────────────────────────┐│
│  │  +251 911 234 567              ││
│  └─────────────────────────────────┘│
│                                     │
│  Business Address:                   │
│  ┌─────────────────────────────────┐│
│  │  Bole, Addis Ababa             ││
│  └─────────────────────────────────┘│
│                                     │
│  ─── Preferences ───                │
│                                     │
│  Default Delivery Address:          │
│  ┌─────────────────────────────────┐│
│  │  📍 Bole, Addis Ababa         ││
│  │  [Change]                      ││
│  └─────────────────────────────────┘│
│                                     │
│  Notifications:                     │
│  ┌─────────────────────────────────┐│
│  │  Order Updates       [ON]      ││
│  │  Price Alerts        [ON]      ││
│  │  Promotions         [OFF]      ││
│  └─────────────────────────────────┘│
│                                     │
│       [Save Changes]                │
│                                     │
└─────────────────────────────────────┘
```

---

## 10. Navigation Summary

```
┌─────────────────────────────────────┐
│         BOTTOM NAVIGATION           │
├──────┬──────┬──────┬──────┬────────┤
│ 🏠   │ 🛒   │ 📦   │ 👤   │        │
│Home  │Buy   │Orders│Profile│        │
│      │      │      │       │        │
│Dash- │Prod- │Order │Settings│       │
│board │ucts  │Track │        │        │
│      │Cart  │Issue │        │        │
│      │      │      │        │        │
└──────┴──────┴──────┴──────┴────────┘
```

### Screen Flow
```
Login → Dashboard
          ↓
    ┌─────┴─────┐
    ↓           ↓
Products    Orders
  ↓           ↓
  Cart      Tracking
  ↓           ↓
Checkout   Issues
  ↓           ↓
Payment    Dispute
```

---

*Document Version: 1.0*
*Generated for: FarmConnect AgriManagement*
*Target: React + TypeScript Frontend*
