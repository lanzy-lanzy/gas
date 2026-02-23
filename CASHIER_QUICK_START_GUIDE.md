# 🚀 Cashier Order Processing - Quick Start Guide

## What's New

Cashiers can now **process customer orders** with action buttons in the order list.

---

## 3 Simple Steps for Cashiers

### Step 1: Login & Go to Orders
```
1. Login as Cashier
2. Click "Process Orders" in sidebar
3. See list of all customer orders
```

### Step 2: View Order (Eye Icon 👁️)
```
1. Click EYE icon on any order
2. Popup shows full order details:
   - Customer info
   - Product & quantity
   - Delivery address
   - Payment amount
   - Order timeline
```

### Step 3: Update Status (Ellipsis ⋮ Icon)
```
1. Click ELLIPSIS (⋮) on order
2. Select status:
   - Pending → "Mark as Out for Delivery"
   - Out4Delivery → "Mark as Delivered"
   - Any → "Cancel Order"
3. See green success message
4. Page auto-refreshes
```

---

## Action Buttons Explained

### 👁️ View Details Button
- **When to use:** Need to see full order information
- **What happens:** Order details open in popup
- **Can use on:** Any order status
- **Result:** Read-only view of order

### ⋮ Update Status Button
- **When to use:** Need to move order to next stage
- **What happens:** Dropdown menu appears
- **Can use on:** Pending and Out for Delivery orders only
- **Result:** Order status changes + page refreshes

---

## Order Status Workflow

```
Customer Places Order
        ↓
[PENDING] ← Awaiting processing
    ↓
    Options:
    → Mark as Out for Delivery ✅
    → Cancel ❌
        ↓
[OUT FOR DELIVERY] ← In transit
    ↓
    Options:
    → Mark as Delivered ✅
    → Cancel ❌
        ↓
[DELIVERED] ← Complete
    ↓
    Options:
    ❌ None (read-only)

Alternative Path:
[PENDING/OUT FOR DELIVERY]
    ↓
[CANCELLED] ← Stopped
    ↓
Options:
❌ None (read-only)
```

---

## Filter & Search Features

**Find orders by:**
- Customer name (first/last)
- Order ID
- Product name
- Order status (pending, out for delivery, delivered, cancelled)
- Delivery type (pickup, delivery)

**Usage:**
```
1. Type in search box → Hit Filter
2. Select status dropdown → Hit Filter
3. Select delivery type → Hit Filter
4. Combine multiple filters
5. Click "Clear" to reset
```

---

## Getting Feedback

After any action, you'll see a notification:

**✓ Green (Success)**
- Order status updated successfully
- Change has been saved

**✗ Red (Error)**
- Something went wrong
- Check order details and try again

**ℹ Blue (Info)**
- General information messages

---

## Common Tasks

### Task 1: Process a Pending Order
```
1. Find pending order in list
2. Click ⋮ (ellipsis)
3. Click "Mark as Out for Delivery"
4. ✓ Order status changes to "Out for Delivery"
5. Notify customer of shipment
```

### Task 2: Complete a Delivery
```
1. Find "Out for Delivery" order
2. Click ⋮ (ellipsis)
3. Click "Mark as Delivered"
4. ✓ Order status changes to "Delivered"
5. Update delivery logs
```

### Task 3: Cancel an Order
```
1. Find order to cancel (Pending or Out4Delivery)
2. Click ⋮ (ellipsis)
3. Click "Cancel Order"
4. ✓ Order status changes to "Cancelled"
5. Notify customer of cancellation
```

### Task 4: View Order Details
```
1. Find any order
2. Click 👁️ (eye icon)
3. Popup opens with:
   - Customer details
   - Product & quantity
   - Delivery address
   - Amount paid/due
   - Order history
4. Click X or outside to close
```

---

## Statistics Cards (Top of Page)

These show at a glance:
- **Total Orders:** All customer orders
- **Pending Orders:** Awaiting processing
- **Out for Delivery:** In transit
- **Delivered Orders:** Completed

_These update when you refresh the page._

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Clear filters | Clear button |
| Next page | "Next" button |
| Previous page | "Previous" button |
| Search | Type in search box |

---

## Troubleshooting

### Problem: Can't see action buttons
**Solution:** Make sure you're logged in as a cashier

### Problem: Button is grayed out
**Solution:** That status doesn't have available transitions

### Problem: Action failed (red error)
**Solution:** 
1. Check order details
2. Refresh page
3. Try again

### Problem: Changes not showing
**Solution:** Page should auto-refresh. If not, refresh manually (F5)

---

## Tips & Best Practices

1. **View details first** - Know order details before marking as delivered
2. **Update promptly** - Update status as soon as order stage changes
3. **Use filters** - Filter by status to find orders to process
4. **Check address** - Before marking delivered, confirm delivery address
5. **Notify customers** - Keep customers informed of status changes

---

## What Changed in UI

**New Column in Table:**
- "Actions" column with two buttons per order
- Eye icon (view details)
- Ellipsis icon (update status)

**New Notifications:**
- Toast messages appear top-right
- Show success/error feedback
- Auto-dismiss after 3 seconds

**Same Features:**
- Search & filters still work
- Pagination still works
- All order information visible
- Professional table layout

---

## Permissions & Limits

✅ You CAN:
- View all customer orders
- View order details
- Update order status (if allowed by workflow)
- Search and filter orders
- See order statistics

❌ You CANNOT:
- Place orders (that's customers)
- Edit order amount
- Delete orders
- Access admin panel
- Modify customer info

---

## Getting Help

If you need help:
1. Check "View Order Details" - might have answer
2. Hover over buttons - shows tooltip
3. Contact admin for blocked actions
4. Check status options - limits shown in menu

---

## Workflow Summary

```
1. LOGIN
   ↓
2. GO TO PROCESS ORDERS
   ↓
3. SEARCH/FILTER ORDERS
   ↓
4. CLICK EYE TO VIEW DETAILS
   ↓
5. CLICK ELLIPSIS TO UPDATE STATUS
   ↓
6. CONFIRM CHANGE (GREEN SUCCESS)
   ↓
7. REPEAT FOR NEXT ORDER
```

---

## Dashboard Stats

Numbers at top of page show:
- **Total**: All orders ever
- **Pending**: Need processing
- **Out4Delivery**: Currently shipping
- **Delivered**: Already received

_These are helpful for daily planning._

---

## Page Layout

```
┌─ HEADER ──────────────────────────────┐
│  Process Customer Orders              │
│  View and process all customer orders │
└─────────────────────────────────────────┘

┌─ STATS ───────────────────────────────┐
│ Total: 10 │ Pending: 3 │ Out: 2 │ Done: 5 │
└─────────────────────────────────────────┘

┌─ FILTERS ─────────────────────────────┐
│ [Search]    [Status ▼]  [Type ▼] [Filter] │
└─────────────────────────────────────────┘

┌─ ORDERS TABLE ────────────────────────┐
│ ID │ Customer │ Product │ ... │ ACTIONS │
├───┼──────────┼─────────┼─────┼─────────┤
│ #2│ John D.  │ LPG 11kg│ ... │ 👁️ ⋮   │
│ #1│ Jane S.  │ LPG 11kg│ ... │ 👁️ ⋮   │
└─────────────────────────────────────────┘

┌─ PAGINATION ──────────────────────────┐
│ First Previous [Page 1 of 3] Next Last │
└─────────────────────────────────────────┘
```

---

## Key Differences: Old vs New

| Feature | Old | New |
|---------|-----|-----|
| See orders | ✅ | ✅ |
| View details | ❌ | ✅ Eye icon |
| Update status | ❌ | ✅ Ellipsis menu |
| Notifications | ❌ | ✅ Toast alerts |
| Filter delivery | ❌ | ✅ New filter |
| Clear feedback | ❌ | ✅ Auto-refresh |

---

**Ready to process orders? Go to `/cashier/orders/` and get started!**

For questions, contact your admin.
