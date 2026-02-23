# PDF Export Usage Examples

## Basic Usage

### Example 1: Export All Orders

**URL**: `/customer/history/export-pdf/`

**What you get**: PDF with all orders sorted by newest first

**File saved as**: `order_history_20240115_143022.pdf`

---

## Advanced Usage with Filters

### Example 2: Export Only Pending Orders

**URL**: `/customer/history/export-pdf/?status=pending`

**PDF Contains**:
- Only orders with "Pending" status
- Sorted by newest first (default)
- Summary shows: 5 pending orders, 0 delivered

**Use case**: Customer wants to review orders waiting to be processed

---

### Example 3: Export Only Delivered Orders

**URL**: `/customer/history/export-pdf/?status=delivered`

**PDF Contains**:
- Only successfully delivered orders
- All delivery dates and person names
- Complete history of completed transactions

**Use case**: For customer records/receipts, financial tracking

---

### Example 4: Export Out for Delivery Orders

**URL**: `/customer/history/export-pdf/?status=out_for_delivery`

**PDF Contains**:
- Only orders currently out for delivery
- Expected delivery information
- Delivery contact details

**Use case**: Track orders in transit

---

## Sorting Examples

### Example 5: Highest Amount Orders First

**URL**: `/customer/history/export-pdf/?sort=-total_amount`

**PDF Shows**:
- Most expensive orders first
- Useful for financial analysis
- Shows spending patterns

**Sample Output**:
```
Order #15   | ₦50,000.00  | Delivered
Order #12   | ₦27,500.00  | Delivered
Order #8    | ₦22,000.00  | Pending
Order #3    | ₦11,000.00  | Delivered
```

**Use case**: Budget planning, spending reviews

---

### Example 6: Lowest Amount Orders First

**URL**: `/customer/history/export-pdf/?sort=total_amount`

**PDF Shows**:
- Smallest orders first
- Increasing to largest orders

**Use case**: Small order analysis, bulk purchase planning

---

### Example 7: Oldest Orders First

**URL**: `/customer/history/export-pdf/?sort=order_date`

**PDF Shows**:
- Orders in ascending date order
- Good for historical review
- Chronological record keeping

**Use case**: Historical records, archives

---

## Complex Filtering Examples

### Example 8: Pending Orders by Amount (Highest First)

**URL**: `/customer/history/export-pdf/?status=pending&sort=-total_amount`

**PDF Contains**:
- Only pending orders
- Sorted from highest to lowest amount
- Shows which pending orders cost the most

**Sample Output**:
```
Summary: 3 Pending Orders | Total: ₦66,000.00

Order #20   | ₦33,000.00  | Pending   | Delivery
Order #19   | ₦22,000.00  | Pending   | Pickup
Order #18   | ₦11,000.00  | Pending   | Delivery
```

**Use case**: Prioritizing high-value pending orders

---

### Example 9: All Cancelled Orders

**URL**: `/customer/history/export-pdf/?status=cancelled`

**PDF Contains**:
- Only cancelled orders
- Reasons (if available)
- Can identify patterns

**Use case**: Refund reconciliation, complaint analysis

---

## Using from Web Interface

### Step-by-Step Guide

1. **Navigate to Order History**
   - Click "Order History" in sidebar
   - URL: `/customer/history/`

2. **Apply Filters (Optional)**
   - Click "Filter by Status" dropdown
   - Select: "Pending", "Out for Delivery", "Delivered", or "Cancelled"

3. **Change Sort Order (Optional)**
   - Click "Sort Orders" dropdown
   - Select: "Newest First", "Oldest First", "Highest Amount", "Lowest Amount", or "Status"

4. **Export to PDF**
   - Click "Export PDF" button (top right)
   - Browser downloads PDF automatically

5. **Save/View PDF**
   - PDF is saved to Downloads folder
   - Can open immediately or later
   - Filename includes timestamp

---

## Real-World Scenarios

### Scenario 1: Monthly Review

**Goal**: Get a summary of all orders for the month

**Steps**:
1. Go to Order History
2. Don't apply any filters
3. Click "Export PDF"
4. Save as "March 2024 Orders.pdf"

**Result**: PDF shows:
- 12 total orders
- 8 delivered
- 4 pending
- Total spent: ₦176,500.00

---

### Scenario 2: Budget Reconciliation

**Goal**: Check high-value orders for accounting

**Steps**:
1. Go to Order History
2. Select sort "Highest Amount"
3. Click "Export PDF"

**Result**: PDF shows orders from ₦50,000 down to ₦11,000

---

### Scenario 3: Delivery Tracking

**Goal**: Track orders currently being delivered

**Steps**:
1. Go to Order History
2. Filter by "Out for Delivery"
3. Click "Export PDF"

**Result**: PDF shows:
- Current delivery person
- Expected delivery date
- Contact information

---

### Scenario 4: Customer Service Dispute

**Goal**: Provide proof of order history to resolve dispute

**Steps**:
1. Go to Order History
2. Filter by "Delivered"
3. Sort "Oldest First"
4. Click "Export PDF"
5. Send PDF to customer service

**Result**: Professional document showing:
- Complete delivery history
- Dates and amounts
- All delivered orders

---

## PDF Examples Output

### Example PDF Header
```
Prycegas Station
Order History Report
Generated: January 15, 2024 at 14:30

Customer Information
Name: Adekunle Okafor | Phone: 08012345678 | Address: 123 Main Street, Lagos...
```

### Example PDF Table
```
┌─────────┬──────────┬──────────────┬──────┬────────────┬──────────────┬─────────────┬────────┐
│ Order # │ Date     │ Product      │ Qty  │ Price/Unit │ Total        │ Status      │ Type   │
├─────────┼──────────┼──────────────┼──────┼────────────┼──────────────┼─────────────┼────────┤
│ #25     │ Jan 15   │ LPG Gas 11kg │ 2    │ ₦5,500.00  │ ₦11,000.00   │ Pending     │ Pickup │
│ #24     │ Jan 10   │ LPG Gas 22kg │ 1    │ ₦10,000.00 │ ₦10,000.00   │ Delivered   │ Deliv. │
│ #23     │ Jan 05   │ LPG Gas 11kg │ 3    │ ₦5,500.00  │ ₦16,500.00   │ Delivered   │ Deliv. │
└─────────┴──────────┴──────────────┴──────┴────────────┴──────────────┴─────────────┴────────┘

Summary: Total Orders: 3 | Pending: 1 | Delivered: 2 | Total Amount: ₦37,500.00
```

---

## Automation Tips

### Using Browser Console

Open browser developer tools (F12) and run:

```javascript
// Export all orders
window.location.href = '/customer/history/export-pdf/';

// Export pending orders, sorted by amount
window.location.href = '/customer/history/export-pdf/?status=pending&sort=-total_amount';
```

---

### Creating Bookmarks

Save these as browser bookmarks for quick access:

1. **All Orders**: 
   - `javascript:window.location='/customer/history/export-pdf/';`

2. **Pending Orders**:
   - `javascript:window.location='/customer/history/export-pdf/?status=pending';`

3. **Delivered Orders**:
   - `javascript:window.location='/customer/history/export-pdf/?status=delivered';`

---

## Troubleshooting Examples

### Problem: PDF is Blank

**Possible Causes**:
1. No orders in filtered category
   - Solution: Check "Filter by Status" dropdown

2. Orders exist but PDF looks empty
   - Solution: Try exporting all orders first

3. Browser blocked the download
   - Solution: Check browser notifications/popup blocker

---

### Problem: Wrong Data in PDF

**Possible Causes**:
1. Filter didn't apply properly
   - Solution: Click "Refresh Orders" then "Export PDF"

2. Sort didn't work
   - Solution: Reset to "Newest First" and re-export

3. Using old page data
   - Solution: Reload page (Ctrl+R) then export

---

### Problem: PDF Takes Too Long

**Possible Causes**:
1. Exporting too many orders (100+)
   - Solution: Apply a filter first

2. Slow internet connection
   - Solution: Try again or use 4G/WiFi

3. Server overload
   - Solution: Try again in a few minutes

---

## Performance Notes

### File Sizes

- **10 orders**: ~45 KB
- **25 orders**: ~65 KB
- **50 orders**: ~95 KB
- **100 orders**: ~150 KB

### Generation Times

- **10 orders**: <0.5 seconds
- **50 orders**: <1 second
- **100 orders**: <2 seconds

*Times vary based on server load*

---

## Format Details

### Timestamps
- Format: `YYYYMMDD_HHMMSS`
- Example: `order_history_20240115_143022.pdf`

### Currency
- Format: Nigerian Naira (₦)
- Decimals: 2 places
- Example: ₦11,000.00

### Dates
- Format: Mon DD, YYYY
- Example: Jan 15, 2024
- Timezone: Server timezone

---

## Support

If you have questions:
1. Check the full documentation: `PDF_EXPORT_DOCUMENTATION.md`
2. Review troubleshooting section above
3. Contact customer support with your PDF error

---

**Last Updated**: 2024
**Version**: 1.0.0
