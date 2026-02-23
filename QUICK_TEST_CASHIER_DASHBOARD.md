# Quick Test Guide - Cashier Dashboard Fix

## 5-Minute Test

### Step 1: Login as Customer
- URL: http://127.0.0.1:8000/
- Login as customer user

### Step 2: Create Order
- Go to: `/customer/order/`
- Select Product: Any available
- Quantity: 1
- Click: "Place Order"
- **Check:** Order created with ID (e.g., #10)

### Step 3: Login as Cashier
- Logout current user
- Login as cashier user (e.g., "john doe")
- Verify: Shift shows (08:00 - 17:00)

### Step 4: Mark "Out for Delivery"
- Go to: `/dealer/orders/` (Process Orders)
- Find your order
- Update status to: "out_for_delivery"
- Click: Save/Update

### Step 5: Login Back as Customer
- Logout cashier
- Login as original customer

### Step 6: Mark as Received
- Go to: Order details
- Click: "Mark as Received"
- Verify: Status changes to "delivered"

### Step 7: Check Cashier Dashboard
- Logout customer
- Login as cashier
- Go to: `/cashier/dashboard/` (MY DASHBOARD)
- **EXPECTED RESULTS:**
  - ✅ Today's Total: > 0.00
  - ✅ Today's Transactions: > 0
  - ✅ Total Transactions: > 0
  - ✅ Avg Transaction: > 0.00
  - ✅ Recent Transactions: Order appears in list

---

## Database Check (If Dashboard is Empty)

Open Django shell:
```bash
python manage.py shell
```

Run these commands:
```python
from core.models import Order, CashierTransaction
from django.utils import timezone

# Check order
order = Order.objects.latest('id')
print(f"Order ID: {order.id}")
print(f"Status: {order.status}")
print(f"Processed by: {order.processed_by}")
print(f"Amount: {order.total_amount}")

# Check transaction
trans = CashierTransaction.objects.filter(order=order)
print(f"\nTransaction count for this order: {trans.count()}")
if trans.exists():
    t = trans.first()
    print(f"Cashier: {t.cashier.user.username}")
    print(f"Amount: {t.amount}")
    print("✅ TRANSACTION EXISTS")
else:
    print("❌ NO TRANSACTION - FIX NOT WORKING")

# Check dashboard data
today = timezone.now().date()
if order.processed_by:
    today_trans = CashierTransaction.objects.filter(
        cashier=order.processed_by,
        created_at__date=today
    )
    print(f"\nDashboard Data:")
    print(f"Transactions today: {today_trans.count()}")
    print(f"Total today: {sum(t.amount for t in today_trans)}")
```

---

## Expected Output

### Dashboard Screen
```
MY DASHBOARD
Hello, john doe! Here's your performance overview

Employee ID: csh-001
Shift: 08:00 - 17:00

Today's Total: 500.00
Today's Transactions: 1
Total Transactions: 1
Avg Transaction: 500.00

Recent Transactions:
- Order #10: Customer Name - 500.00 ₦
```

### Database Output
```
Order ID: 10
Status: delivered
Processed by: Cashier: john doe
Amount: 500.00

Transaction count for this order: 1
Cashier: john doe
Amount: 500.00
✅ TRANSACTION EXISTS

Dashboard Data:
Transactions today: 1
Total today: 500.00
```

---

## Troubleshooting

### Issue 1: Transaction Count = 0
**Problem:** No CashierTransaction created

**Solutions:**
1. Verify order.processed_by is NOT NULL (should be set when marked "out_for_delivery")
2. Verify order.status is "delivered" (not "out_for_delivery")
3. Check if fix code is in place (see code verification below)
4. Restart Django server

### Issue 2: processed_by is NULL
**Problem:** Order not associated with cashier

**Solutions:**
1. Verify cashier marked as "out_for_delivery" (not just viewed)
2. Check if cashier is logged in as cashier role
3. Verify order.processed_by = <cashier> in database

### Issue 3: Dashboard Still Shows 0
**Problem:** Transaction exists but dashboard empty

**Solutions:**
1. Refresh page (clear browser cache)
2. Check if logged in as correct cashier
3. Verify transaction creation date is today
4. Verify dashboard query filter (see code below)

---

## Code Verification

### Check 1: processed_by Set Earlier
```bash
# In core/views.py, line ~894 should have:
if new_status in ['out_for_delivery', 'delivered']:
    order.processed_by = request.user.cashier_profile
```

### Check 2: Transaction Created in mark_order_received
```bash
# In core/views.py, lines ~528-537 should have:
CashierTransaction.objects.create(
    cashier=order.processed_by,
    order=order,
    transaction_type='order',
    amount=order.total_amount,
    payment_method='cash',
    customer=order.customer
)
```

### Check 3: Dashboard Filters to Today
```bash
# In core/cashier_views.py, line ~248 should have:
recent_transactions = today_transactions.select_related(...).order_by('-created_at')[:10]
```

---

## Quick Validation

**Success Indicators:**

✅ Order created successfully
✅ Cashier marked "out_for_delivery"
✅ Customer marked "received"
✅ CashierTransaction exists in database
✅ Dashboard shows metrics
✅ Transaction appears in "Recent Transactions"

**If all ✅:** Fix is working correctly!

**If any ❌:** See troubleshooting section above

---

## Notes

- Test takes ~5 minutes
- Use test user credentials for safety
- Check database to verify transaction creation
- Monitor logs for any errors
- Test multiple times with different users

---

**Last Updated:** 2025-11-28
**Status:** Ready for Testing
