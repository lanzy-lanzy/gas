# Cashier Dashboard Testing Guide

## Quick Test Steps

### Step 1: Create a Test Order
1. Login as a customer
2. Go to "Place Order" or similar
3. Select product (LPG Gas)
4. Enter quantity and delivery details
5. Submit order
6. **Expected Result**: Order created with status: "pending"

### Step 2: Process Order (Dealer/Admin View)
1. Login as dealer/admin
2. Go to "Order Management"
3. Find the newly created order
4. Mark as "Out for Delivery"
5. **Expected Result**: Order status changes to "out_for_delivery"

### Step 3: Mark as Delivered (Individual Update)
1. In Order Management, find the order
2. Click "Mark as Delivered" or update status to "delivered"
3. **Expected Result**: 
   - Order status changes to "delivered"
   - Delivery date is set to now
   - CashierTransaction record is created in database

### Step 4: Verify in Cashier Dashboard
1. Login as a cashier (the one who delivered the order)
2. Go to "Cashier Dashboard" or "My Dashboard"
3. **Expected Results**:
   - ✓ "Today's Total" shows the order amount
   - ✓ "Today's Transactions" shows count of 1+
   - ✓ "Total Transactions" shows cumulative count
   - ✓ "Avg Transaction" shows calculated average
   - ✓ "Recent Transactions" section shows list of deliveries

### Step 5: Bulk Test (Optional)
1. Create 3+ orders
2. Mark multiple as "out for delivery"
3. Select multiple orders
4. Click "Bulk Mark Delivered"
5. **Expected Result**: All selected orders get CashierTransaction records

### Step 6: Database Verification (Technical)
```python
# Run in Django shell: python manage.py shell
from core.models import CashierTransaction, Cashier
from django.utils import timezone

today = timezone.now().date()

# Check transactions for specific cashier
cashier = Cashier.objects.first()
today_trans = CashierTransaction.objects.filter(
    cashier=cashier,
    created_at__date=today
)

print(f"Transactions today: {today_trans.count()}")
for trans in today_trans:
    print(f"  {trans.transaction_type}: {trans.amount} (Order #{trans.order.id})")
```

## Troubleshooting

### Issue: Dashboard Still Shows "No transactions yet"
**Checks:**
1. Verify order was marked as "delivered" (not just "out_for_delivery")
2. Verify cashier is logged in as the user who delivered the order
3. Check database: `CashierTransaction.objects.filter(created_at__date=<today>).count()`
4. Verify `processed_by` is set on the Order model

### Issue: Transactions Showing Old Data
**Solution:**
- Recent transactions should only show today's activity
- Refresh page or check browser cache
- Verify query filter in dashboard view

### Issue: Metrics Show Incorrect Amounts
**Check:**
1. Order's `total_amount` is correct
2. CashierTransaction `amount` matches order amount
3. No duplicate transactions (check by order ID)

## Expected Dashboard Display

After successful delivery of a 500 NGN order:

```
Today's Total
500.00 ₦

Today's Transactions
1

Total Transactions
1

Avg Transaction
500.00 ₦

Recent Transactions
[Order details showing Order #X for 500.00 NGN]
```

## Debugging Commands

### Check all transactions for today
```python
from core.models import CashierTransaction
from django.utils import timezone

today = timezone.now().date()
trans = CashierTransaction.objects.filter(created_at__date=today)
print(f"Total today: {trans.count()}")
```

### Check specific cashier's transactions
```python
from core.models import Cashier, CashierTransaction

cashier = Cashier.objects.get(user__username='test_cashier')
trans = CashierTransaction.objects.filter(cashier=cashier)
print(f"Total transactions: {trans.count()}")
print(f"Total amount: {sum(t.amount for t in trans)}")
```

### Check order-to-transaction mapping
```python
from core.models import Order

order = Order.objects.get(id=1)
print(f"Order ID: {order.id}")
print(f"Status: {order.status}")
print(f"Processed by: {order.processed_by}")
print(f"Transactions: {order.cashier_transactions.count()}")
```

## Success Criteria

✓ Dashboard displays non-zero metrics
✓ Recent transactions list is populated
✓ Dashboard shows only today's transactions
✓ Metrics update immediately after marking delivery
✓ Both single and bulk operations create transactions
✓ Proper cashier-to-order tracking
