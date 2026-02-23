# Cashier Reports - Visual Guide

## Navigation Flow

```
Login
  └── Dashboard
       └── Left Sidebar
            └── Reports
                 ├── Reports Dashboard
                 ├── Sales Reports
                 ├── Stock Reports
                 └── ⭐ Cashier Reports ← NEW
                      ├── Daily Report
                      ├── Monthly Report
                      └── Yearly Report
```

---

## Report Layout

### All Reports Share This Structure

```
┌─────────────────────────────────────────────────────────────┐
│  REPORT TITLE + TYPE TABS (Daily | Monthly | Yearly)       │
├─────────────────────────────────────────────────────────────┤
│  DATE/PERIOD SELECTOR (Calendar or Year/Month Dropdowns)    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  Total      │  Total       │  Total Units │             │
│  │  Income     │  Orders      │  Delivered   │             │
│  │  ₱XXX.XX    │  XX          │  XXX         │             │
│  └──────────────┴──────────────┴──────────────┘             │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────┐  ┌───────────────────────┐      │
│  │ Income by Cashier     │  │ Inventory by Product  │      │
│  ├───────────────────────┤  ├───────────────────────┤      │
│  │ Name | Orders | Total │  │ Product | Qty | Rev   │      │
│  ├───────────────────────┤  ├───────────────────────┤      │
│  │ John | 5 | ₱2500      │  │ LPG 11kg| 50 | ₱10K   │      │
│  │ Jane | 3 | ₱1800      │  │ LPG 22kg| 30 | ₱9K    │      │
│  │ Mike | 2 | ₱1200      │  │ Cartridge|20| ₱4K     │      │
│  └───────────────────────┘  └───────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Daily Report Example

```
Cashier Reports
├─ [Daily] | [Monthly] | [Yearly]
├─ 📅 Select Date: [Nov 27, 2025] [Apply Button]
├─ Summary Cards:
│  ├─ Total Income: ₱5,500.00
│  ├─ Total Orders: 10
│  └─ Total Units: 100
└─ Two-Column Tables:
   ├─ Income by Cashier:
   │  ├─ John Smith (Emp#001): 5 orders, ₱2,500, avg ₱500
   │  ├─ Jane Doe (Emp#002): 3 orders, ₱1,800, avg ₱600
   │  └─ Mike Jones (Emp#003): 2 orders, ₱1,200, avg ₱600
   └─ Inventory by Product:
      ├─ LPG Gas (11kg): 60 units, ₱3,000, ₱50/unit
      ├─ LPG Gas (22kg): 30 units, ₱2,100, ₱70/unit
      └─ Cartridge: 10 units, ₱400, ₱40/unit
```

---

## Monthly Report Example

```
Cashier Reports
├─ [Daily] | [Monthly] | [Yearly]
├─ 📆 Year: [2025] Month: [November ▼] [Apply Button]
├─ Summary Cards:
│  ├─ Total Income: ₱45,000.00
│  ├─ Total Orders: 87
│  └─ Total Units: 890
└─ Two-Column Tables:
   ├─ Income by Cashier (November 2025):
   │  ├─ John Smith: 35 orders, ₱19,000, avg ₱543
   │  ├─ Jane Doe: 28 orders, ₱15,200, avg ₱543
   │  └─ Mike Jones: 24 orders, ₱10,800, avg ₱450
   └─ Inventory by Product (November 2025):
      ├─ LPG Gas (11kg): 520 units, ₱26,000, ₱50/unit
      ├─ LPG Gas (22kg): 280 units, ₱19,600, ₱70/unit
      └─ Cartridge: 90 units, ₱3,600, ₱40/unit
```

---

## Yearly Report Example

```
Cashier Reports
├─ [Daily] | [Monthly] | [Yearly]
├─ 📊 Year: [2025] [Apply Button]
├─ Summary Cards:
│  ├─ Total Income: ₱520,000.00
│  ├─ Total Orders: 1,050
│  └─ Total Units: 10,500
├─ Two-Column Tables:
│  ├─ Income by Cashier (2025):
│  │  ├─ John Smith: 425 orders, ₱230,000, avg ₱541
│  │  ├─ Jane Doe: 360 orders, ₱195,000, avg ₱542
│  │  └─ Mike Jones: 265 orders, ₱95,000, avg ₱358
│  └─ Inventory by Product (2025):
│     ├─ LPG Gas (11kg): 6,200 units, ₱310,000, ₱50/unit
│     ├─ LPG Gas (22kg): 3,100 units, ₱217,000, ₱70/unit
│     └─ Cartridge: 1,200 units, ₱48,000, ₱40/unit
└─ Monthly Breakdown (4 columns per row):
   ├─ [January]     [February]     [March]      [April]
   │  Income:₱42K   Income:₱45K    Income:₱43K  Income:₱50K
   │  Units: 850    Units: 920     Units: 880   Units: 950
   │  Orders: 87    Orders: 95     Orders: 91   Orders: 98
   ├─ [May]         [June]         [July]       [August]
   │  Income:₱48K   Income:₱52K    Income:₱49K  Income:₱51K
   │  Units: 920    Units: 1000    Units: 950   Units: 980
   │  Orders: 93    Orders: 102    Orders: 96   Orders: 100
   └─ [September]   [October]      [November]   [December]
      Income:₱44K   Income:₱46K    Income:₱50K  Income:₱52K
      Units: 890    Units: 920     Units: 1000  Units: 1050
      Orders: 89    Orders: 94     Orders: 102  Orders: 107
```

---

## Cashier Performance Ranking

### How to Interpret Income Rankings

**High Performer:**
- High Total Amount (₱)
- High Order Count
- Reasonable Average (not too high/low)
```
Name: John Smith
Orders: 35
Total: ₱19,000
Average: ₱543
= Consistent high performer
```

**Efficient Seller:**
- Good Total Amount
- Fewer Orders
- Higher Average
```
Name: Jane Doe
Orders: 28
Total: ₱15,200
Average: ₱543
= Sells higher value items
```

**New Cashier:**
- Low Total Amount
- Few Orders
- Variable Average
```
Name: Mike Jones
Orders: 24
Total: ₱10,800
Average: ₱450
= Still building up
```

---

## Product Performance Ranking

### How to Interpret Inventory Rankings

**Best Seller by Volume:**
- Highest Quantity
```
Product: LPG Gas (11kg)
Quantity: 520 units
= Most customers want this size
```

**Best Seller by Revenue:**
- Highest Total Revenue
```
Product: LPG Gas (22kg)
Quantity: 280 units
Revenue: ₱19,600
= More expensive, good sales
```

**Premium Product:**
- High Price/Unit
- Moderate to High Quantity
```
Product: Premium Cartridge
Price/Unit: ₱50
Quantity: 250 units
= High margin product
```

---

## Color Legend

### Summary Cards
```
┌─────────────────┐
│ Total Income    │  🟠 Orange = Revenue/Money
│ ₱5,500.00       │
└─────────────────┘

┌─────────────────┐
│ Total Orders    │  🔵 Blue = Counts/Orders
│ 10              │
└─────────────────┘

┌─────────────────┐
│ Total Units     │  🟢 Green = Inventory/Stock
│ 100             │
└─────────────────┘
```

### Table Headers
```
Income Table          Inventory Table
🟠 Orange header      🔵 Blue header
= Financial metrics   = Product metrics
```

---

## Interactive Elements

### Date/Period Selection

**Daily Report:**
```
📅 Select Date
  [Calendar icon] [Date input field] [Apply Button]
```

**Monthly Report:**
```
Year: [2025 text input]
Month: [November dropdown ▼] [Apply Button]
```

**Yearly Report:**
```
Year: [2025 text input] [Apply Button]
```

---

## Table Interactions

### Hovering Over Rows
```
Normal Row:
John Smith | 35 | ₱19,000 | ₱543

Hover Effect:
→ Row background lightens
→ Text becomes more visible
→ Shows better readability
```

---

## Mobile View

### Responsive Behavior
```
DESKTOP (Wide Screen):
┌──────────────────┬──────────────────┐
│  Income Table    │  Inventory Table │
├──────────────────┼──────────────────┤
│                  │                  │
└──────────────────┴──────────────────┘

TABLET (Medium Screen):
┌──────────────────────────────┐
│  Income Table                │
├──────────────────────────────┤
│  Inventory Table             │
└──────────────────────────────┘

MOBILE (Small Screen):
┌──────────────────┐
│  Income Table    │
│  (scrollable)    │
├──────────────────┤
│  Inventory Table │
│  (scrollable)    │
└──────────────────┘
```

---

## Decision Flow

### What Report Should I Use?

```
What do you want to know?

├─ "Sales today?" 
│  └─→ Daily Report (today's date)
│
├─ "Performance last month?"
│  └─→ Monthly Report (select month/year)
│
├─ "How did we do this year?"
│  └─→ Yearly Report (see month-by-month breakdown)
│
├─ "Best performer this month?"
│  └─→ Monthly Report (check Income table, sort by Total)
│
├─ "Most popular product?"
│  └─→ Any Report (check Inventory table, sort by Qty)
│
├─ "Seasonal trends?"
│  └─→ Yearly Report (review Monthly Breakdown cards)
│
└─ "Daily operations?"
   └─→ Daily Report (open each day)
```

---

## Example Insights

### Scenario 1: Morning Manager Check
```
Action: Open Daily Report for today
Look at: 
  - Total Income: How much money received?
  - Top Cashier: Who's performing best?
  - Product Mix: What's selling today?
Result: "Today we're on track for ₱5500, John is leading"
```

### Scenario 2: Month-End Review
```
Action: Open Monthly Report for November 2025
Look at:
  - Total Orders: Did we meet target?
  - Cashier Rankings: Who performed best?
  - Product Movement: Seasonal trends?
Result: "November is strong, LPG 11kg is most popular"
```

### Scenario 3: Annual Planning
```
Action: Open Yearly Report for 2025
Look at:
  - Monthly Breakdown Cards: Best and worst months?
  - Top Products: What to focus on in 2026?
  - Cashier Performance: Plan staffing for next year?
Result: "Summer months (May-Aug) were strongest, plan staffing accordingly"
```

---

## Quick Reference

| Need | Report | Look At | Column |
|------|--------|---------|--------|
| Today's income | Daily | Summary | Total Income |
| Best cashier | Monthly | Income Table | Total Amount |
| Popular product | Any | Inventory Table | Quantity |
| Revenue leader | Any | Inventory Table | Total Revenue |
| Seasonal trends | Yearly | Monthly Cards | Income/Qty |
| Cash collected | Daily | Summary | Total Income |

---

## Tips for Better Insights

1. **Compare Periods:** Run reports for same period last year/month
2. **Look for Patterns:** Check which products sell together
3. **Monitor Trends:** Track cashier performance over time
4. **Identify Peak Days:** Check daily reports for busiest days
5. **Plan Inventory:** Use product metrics to stock better
6. **Staff Planning:** Use cashier metrics to plan shifts
7. **Set Goals:** Use metrics to set performance targets

