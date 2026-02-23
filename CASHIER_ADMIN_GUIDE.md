# Cashier Admin Guide - Daily Monitoring

## Overview
This guide shows admins how to monitor daily income and inventory impact caused by cashier processing of customer orders.

## Two New Admin Reports

### 1. Daily Income Report
**Location:** Admin Dashboard → Cashier Management → Daily Income Report
**URL:** `/dealer/cashiers/reports/daily-income/`

#### What You See:
- **Summary Cards:**
  - Total Income (all cashiers combined)
  - Total Orders Delivered
  - Average Order Value

- **Detailed Table:**
  - Cashier Name & Employee ID
  - Status (Active/Inactive)
  - Number of Orders
  - Total Amount Generated
  - Average Order Value

#### How to Use:
1. Select "From Date" - Starting date for the report
2. Select "To Date" - Ending date for the report
3. Check "Show All Cashiers" to include inactive cashiers (optional)
4. Click "Filter" to generate report

#### Example Use Cases:
- Track daily sales by cashier
- Identify top performers
- Monitor revenue trends
- Compare cashier productivity

---

### 2. Inventory Impact Report
**Location:** Admin Dashboard → Cashier Management → Inventory Impact Report
**URL:** `/dealer/cashiers/reports/inventory-impact/`

#### What You See:
- **Summary Cards:**
  - Total Units Delivered
  - Total Revenue
  - Average Price per Unit

- **Two View Modes:**

**A. Detailed View (Table)**
- Product Name & Size
- Cashier Name & Employee ID
- Quantity delivered by this cashier
- Number of orders
- Total revenue
- Price per unit

**B. Product Summary (Cards)**
- Each product card shows totals across all cashiers
- Total units sold
- Total revenue
- Quick overview of popular products

#### How to Use:
1. Select date range (From Date → To Date)
2. Click "Filter"
3. Click "Detailed View" tab to see breakdown by cashier
4. Click "Product Summary" tab to see product totals
5. Use pagination for detailed view if there are many records

#### Example Use Cases:
- Track which products are moving
- Identify inventory demand patterns
- Monitor stock depletion
- Plan reordering based on delivery history
- See which cashiers handle which products

---

## Quick Access Menu

### Cashier Management Areas:
- **Cashier List** - View/edit all cashiers
- **Cashier Dashboard** - Transaction overview
- **Daily Income Report** - Income by cashier ⭐
- **Inventory Impact Report** - Products by cashier ⭐
- **Cashier Performance** - Historical performance metrics

---

## Understanding the Data

### Daily Income Report Fields:

| Field | Meaning |
|-------|---------|
| Cashier | Name of the cashier |
| Employee ID | Staff ID for identification |
| Orders | Count of orders delivered by this cashier |
| Total Amount | Total revenue from delivered orders |
| Avg Order Value | Average sale amount per order |
| Status | Whether cashier is Active or Inactive |

### Inventory Impact Report Fields:

| Field | Meaning |
|-------|---------|
| Product | Product name and size |
| Cashier | Who delivered these units |
| Quantity | Total units of this product delivered |
| Orders | How many separate orders |
| Total Amount | Revenue from these deliveries |
| Avg Price/Unit | Average unit price |

---

## Common Questions

**Q: Why do some reports show no data?**
A: Make sure:
- Orders have been delivered (status = "Delivered")
- The date range includes those deliveries
- You're checking the correct date format

**Q: How do I compare two cashiers?**
A: Use the Daily Income Report:
1. Set date range
2. Look at the "Total Amount" column
3. Orders with higher amounts are better performers

**Q: How do I see what products are popular?**
A: Use the Inventory Impact Report:
1. Click "Product Summary" tab
2. Look at "Total Units" for each product
3. Higher numbers = more popular

**Q: Can I export these reports?**
A: Currently print-friendly. Future versions may include CSV export.

**Q: What if a cashier is inactive?**
A: Check "Show All Cashiers" option to include them in the report.

---

## Key Metrics Explained

### Total Amount
- Sum of all order totals processed by cashier
- Represents revenue generated
- Key metric for cashier evaluation

### Order Count
- Number of orders delivered
- Shows productivity/activity level
- Higher = more busy

### Average Order Value
- Total Amount ÷ Order Count
- Shows consistency and order size
- Helps identify patterns

### Inventory Quantity
- Units of products delivered
- Shows product movement
- Key for stock management

---

## Data Interpretation Tips

### For Revenue (Daily Income Report):
```
High Total Amount + Low Orders = Large sales/bulk orders
High Total Amount + High Orders = Consistent high performer
Low Total Amount = Either new cashier or slow day
```

### For Inventory (Inventory Impact Report):
```
High Quantity + High Revenue = Product is popular & selling well
Low Quantity + High Revenue = Product has high unit price
High Quantity + Low Orders = Many units in few orders (bulk sales)
```

---

## Integration with Order Processing

### Automatic Tracking:
When a cashier marks an order as "Delivered", the system automatically:
1. Records the delivery timestamp
2. Records which cashier processed it
3. Updates these reports immediately

### No Manual Entry Required:
- Everything is automatic
- Data is accurate in real-time
- No additional steps for cashiers

---

## Report Navigation

### From Cashier Dashboard:
1. Click "Cashier Management" (left sidebar)
2. Click "Daily Income Report" OR "Inventory Impact Report"

### Direct URLs:
- Daily Income: `/dealer/cashiers/reports/daily-income/`
- Inventory Impact: `/dealer/cashiers/reports/inventory-impact/`

---

## Best Practices

1. **Daily Check:** Review daily income each morning
2. **Weekly Analysis:** Compare trends across the week
3. **Inventory Planning:** Use impact report for reordering
4. **Performance Review:** Base cashier evaluations on metrics
5. **Spot Checking:** Cross-reference with physical inventory counts

---

## Troubleshooting

**Issue:** Report shows no cashier data
- **Solution:** Check if cashiers have processed any deliveries

**Issue:** Dates look wrong
- **Solution:** Clear browser cache, date format is YYYY-MM-DD

**Issue:** Numbers don't match expectations
- **Solution:** Verify only "Delivered" orders are counted (not pending)

---

## Support

For technical issues:
- Check database migration was applied
- Verify cashier records exist
- Clear Django cache if needed
- Check server logs for errors

