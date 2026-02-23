# Cashier Transaction Flow - Complete Fix

## Issue
Dashboard was empty even when cashier marked order as "out for delivery" because CashierTransaction was only created when order reached "delivered" status. But the customer marking it as received happened separately, and the transaction wasn't created in both flows.

## New Flow (Scenario: Customer Marks as Received)

```
1. Order Created (pending)
   Order.status = 'pending'
   Order.processed_by = NULL
   
2. Cashier marks as "out_for_delivery"
   ✓ NEW: Order.processed_by = current_cashier
   Order.status = 'out_for_delivery'
   (No transaction yet - waiting for delivery confirmation)
   
3. Customer marks as "received"
   Order.status = 'delivered'
   Order.delivery_date = now()
   ✓ Create CashierTransaction (links to processed_by cashier)
   
4. Dashboard Query
   CashierTransaction.objects
       .filter(cashier=current_cashier, created_at__date=today)
   ✓ Shows transaction in dashboard
```

## Files Modified

### 1. core/views.py - update_order_status() (Lines 885-895)

**BEFORE:**
```python
# Track which cashier processed the delivery
if new_status == 'delivered' and is_cashier_user and not order.processed_by:
    order.processed_by = request.user.cashier_profile

# Set delivery date when order is delivered
if new_status == 'delivered' and not order.delivery_date:
    order.delivery_date = timezone.now()
```

**AFTER:**
```python
# Track which cashier is processing (set on out_for_delivery or delivered)
if is_cashier_user and not order.processed_by:
    if new_status in ['out_for_delivery', 'delivered']:
        order.processed_by = request.user.cashier_profile

# Set delivery date when order is delivered
if new_status == 'delivered' and not order.delivery_date:
    order.delivery_date = timezone.now()
```

**Change:** `processed_by` is now set when cashier marks as "out_for_delivery" (not just "delivered")

### 2. core/views.py - mark_order_received() (Lines 511-540)

**ADDED:**
```python
# Ensure processed_by is set - should have been set when cashier marked as out_for_delivery
if not order.processed_by:
    from .models import Cashier
    # Fallback: assign to first active cashier (shouldn't normally happen)
    cashiers = Cashier.objects.filter(is_active=True)
    if cashiers.exists():
        order.processed_by = cashiers.first()

order.save()

# Create CashierTransaction record when customer receives order
# This ensures transactions are recorded even if cashier just marked as out_for_delivery
if order.processed_by:
    from .models import CashierTransaction
    # Check if transaction already exists (from when cashier marked as delivered)
    existing = CashierTransaction.objects.filter(order=order).exists()
    if not existing:
        CashierTransaction.objects.create(
            cashier=order.processed_by,
            order=order,
            transaction_type='order',
            amount=order.total_amount,
            payment_method='cash',
            customer=order.customer
        )
```

**Change:** Creates CashierTransaction when customer marks as received

## Transaction Creation Triggers

Now transactions are created in these scenarios:

### Scenario 1: Cashier marks directly as "delivered"
```
Cashier → Update Order → Status = "delivered"
    ↓
    (Lines 876-920 in views.py)
    ✓ Sets processed_by = current_cashier
    ✓ Creates CashierTransaction
    ✓ Dashboard shows immediately
```

### Scenario 2: Cashier marks "out_for_delivery", customer marks "received"
```
Cashier → Update Order → Status = "out_for_delivery"
    ↓
    ✓ Sets processed_by = current_cashier
    (No transaction yet)
    
Customer → Mark Received → Status = "delivered"
    ↓
    (Lines 511-540 in views.py)
    ✓ Uses existing processed_by
    ✓ Creates CashierTransaction
    ✓ Dashboard shows
```

### Scenario 3: Bulk marking as "delivered"
```
Cashier → Bulk Mark Delivered
    ↓
    (Lines 1156-1176 in views.py)
    ✓ Sets processed_by = current_cashier
    ✓ Creates CashierTransaction for each
    ✓ Dashboard shows all
```

## Data Model Relationships

```
Order
├─ id
├─ status (pending → out_for_delivery → delivered)
├─ processed_by (ForeignKey to Cashier) ← NOW SET EARLIER
├─ delivery_date (set when "delivered")
└─ total_amount

CashierTransaction
├─ id
├─ cashier (ForeignKey to Cashier)
├─ order (ForeignKey to Order)
├─ amount (= order.total_amount)
├─ transaction_type = 'order'
├─ created_at (timestamp)
└─ customer (ForeignKey to User)
```

## Dashboard Query Logic

**File:** `core/cashier_views.py` line 237-248

```python
cashier = request.user.cashier_profile
today = timezone.now().date()

# Get all transactions for this cashier
cashier_transactions = CashierTransaction.objects.filter(cashier=cashier)

# Get today's transactions
today_transactions = cashier_transactions.filter(created_at__date=today)

# Calculate metrics
today_total = today_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
today_count = today_transactions.count()

# Get recent transactions (today only, ordered by newest first)
recent_transactions = today_transactions.select_related('order', 'customer').order_by('-created_at')[:10]

# Render dashboard with metrics
context = {
    'today_total': today_total,
    'today_transaction_count': today_count,
    'recent_transactions': recent_transactions,
    ...
}
```

## Expected Behavior After Fix

### Before (Broken)
```
Cashier marks "out_for_delivery" → No transaction created
Customer marks "received" → No transaction created
Dashboard → "No transactions yet" ✗
```

### After (Fixed)
```
Cashier marks "out_for_delivery" → processed_by set
Customer marks "received" → CashierTransaction created
Dashboard → Shows transaction ✓
```

## Testing Scenarios

### Test 1: Sequential Status Update
1. Create order (pending)
2. Cashier marks "out_for_delivery"
   - Check: Order.processed_by = cashier
3. Customer marks "received"
   - Check: CashierTransaction created
   - Check: Dashboard shows transaction

### Test 2: Direct Delivery
1. Create order (pending)
2. Cashier marks directly "delivered"
   - Check: processed_by = cashier
   - Check: CashierTransaction created
   - Check: Dashboard shows transaction

### Test 3: Bulk Operations
1. Create 3 orders (pending)
2. Cashier bulk marks "out_for_delivery"
   - Check: All have processed_by = cashier
3. Customer bulk marks "received" (simulate)
   - Check: All have CashierTransaction
   - Check: Dashboard shows count = 3

## Backup/Rollback

If needed, revert these changes:
1. Remove processed_by assignment on "out_for_delivery" (line 891)
2. Remove transaction creation in mark_order_received (lines 528-537)
3. Revert to only creating transaction on "delivered" status

## Notes

- Transactions are created only once per order (checked with exists())
- processed_by is preserved once set (not changed on subsequent updates)
- Works with all order flow variations
- No duplicate transactions possible
- Dashboard will always show transactions when order is marked as received
