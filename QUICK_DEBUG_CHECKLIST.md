# Quick Debug Checklist - Stock Not Updating

Follow these steps to find where stock update is failing.

## Step 1: Run Server with Debug Output
```bash
python manage.py runserver > debug.log 2>&1
```

## Step 2: Submit Adjustment
1. Navigate to `/dealer/inventory/adjustment/`
2. Select a product (note the ID)
3. Choose "Increase Stock"
4. Enter quantity: 10
5. Select reason
6. Click "Apply Adjustment"

## Step 3: Check Server Output
Look for this in `debug.log` or server console:

### ✅ If you see this - Everything worked:
```
[DEBUG] inventory_adjustment() - Method: POST
[DEBUG] Form is_valid(): True
[DEBUG] adjustment.quantity_change: 10
[DEBUG] Product saved successfully!
[DEBUG] Transaction completed successfully
[DEBUG] Success message: ...Stock adjusted by 10
```
**But stock didn't update in UI?**
- Hard refresh browser (Ctrl+Shift+R)
- Check database directly (see Step 4)

### ❌ If you see this - Form problem:
```
[DEBUG] Form is_valid(): False
[DEBUG] Form errors: {'field': ['error message']}
```
**Fix:** Check template field names match form definition

### ❌ If you see this - Conversion problem:
```
[DEBUG] adjustment.quantity_change: None
```
**Fix:** Form.save() method not setting quantity_change properly

### ❌ If you see this - Database problem:
```
[ERROR] Failed to save product: [error]
```
**Fix:** Check database permissions and fields

### ❌ If you see this - Never reached save:
```
[DEBUG] Checking for negative stock...
[DEBUG] new_stock < 0
```
**Fix:** Current stock too low, or adjustment backwards

## Step 4: Verify in Database

### Option A: Using Django Shell
```bash
python manage.py shell
```

```python
from core.models import LPGProduct, InventoryAdjustment, StockMovement

# Check product
product = LPGProduct.objects.get(id=1)  # Use your product ID
print(f"Current stock: {product.current_stock}")
print(f"Last updated: {product.updated_at}")

# Check latest adjustment
adj = InventoryAdjustment.objects.latest('created_at')
print(f"Latest adjustment: {adj.quantity_change} ({adj.reason})")
print(f"Created: {adj.created_at}")

# Check movement
movement = StockMovement.objects.filter(reference_id=str(adj.id)).first()
if movement:
    print(f"Movement: {movement.quantity} (prev: {movement.previous_stock} → new: {movement.new_stock})")
else:
    print("No movement record!")
```

### Option B: Using Database Query
```sql
-- SQLite
SELECT id, name, current_stock FROM core_lpgproduct WHERE id = 1;

SELECT id, quantity_change, reason FROM core_inventoryadjustment ORDER BY created_at DESC LIMIT 1;

SELECT id, quantity, previous_stock, new_stock FROM core_stockmovement ORDER BY created_at DESC LIMIT 1;
```

## Step 5: Analyze Results

### Test Case 1: Stock SHOULD increase from 50 to 60
- [ ] Submitted: INCREASE + 10
- [ ] Debug output: "adjustment.quantity_change: 10"
- [ ] Database product.current_stock: 60 ✓ or 50 ❌
- [ ] Database adjustment.quantity_change: 10
- [ ] Database movement exists: Yes ✓ or No ❌

### Test Case 2: Stock SHOULD decrease from 60 to 55
- [ ] Submitted: DECREASE + 5
- [ ] Debug output: "adjustment.quantity_change: -5"
- [ ] Database product.current_stock: 55 ✓ or 60 ❌
- [ ] Database adjustment.quantity_change: -5
- [ ] Database movement exists: Yes ✓ or No ❌

## Common Issues & Fixes

### Issue 1: Form Valid But Stock Not Updating
```
Debug shows: [DEBUG] Product saved successfully!
But: Database still shows old stock
```
**Most likely cause:** Browser cache or concurrent adjustment

**Fix:**
1. Hard refresh: Ctrl+Shift+R or Cmd+Shift+R
2. Close and reopen browser
3. Check if another process is modifying stock

### Issue 2: quantity_change is None
```
Debug shows: [DEBUG] adjustment.quantity_change: None
```
**Cause:** Form.save() method not executing or form fields wrong

**Check:**
1. Template has correct field names:
   - `name="adjustment_type"` (not `type`)
   - `name="quantity"` (not `quantity_change`)
   - `name="product"`
   - `name="reason"`

2. Form is receiving data:
   ```python
   # In Django shell
   from core.forms import InventoryAdjustmentForm
   data = {'adjustment_type': 'increase', 'quantity': 10, 'product': 1, 'reason': 'count_error', 'notes': ''}
   form = InventoryAdjustmentForm(data)
   print(form.is_valid())  # Should be True
   ```

### Issue 3: Form Invalid
```
Debug shows: [DEBUG] Form is_valid(): False
[DEBUG] Form errors: {'product': ['required']}
```
**Fix:** Check which field is failing and why

**Common field issues:**
- `product`: Product ID not submitted or invalid
- `adjustment_type`: Value not 'increase' or 'decrease'
- `quantity`: Not a number or less than 1
- `reason`: Not in the choices list

### Issue 4: Negative Stock Error
```
Debug shows: [ERROR] New stock would be negative: -5
```
**Cause:** Trying to decrease more than available

**Current: 50, Trying to decrease by 60 → -10 (blocked)**

**Fix:** Use correct quantity or check current stock first

### Issue 5: Product Doesn't Update, But No Errors
This means:
1. Form submitted ✓
2. Validation passed ✓
3. Database saved ✓
4. But stock didn't change ❌

**Check if:**
- [ ] Wrong product selected?
- [ ] Browser showing cached page?
- [ ] Multiple database replicas (lag)?
- [ ] Transaction rolled back silently?

**Test:**
```python
# Get fresh from DB
from django.core.cache import cache
cache.clear()  # Clear cache
product.refresh_from_db()
print(product.current_stock)  # Should show updated value
```

## Quick Debug Print Locations

The code now has debug prints in:

**1. Form** (`core/forms.py` - line 905):
```python
print(f"[DEBUG] adjustment_type: {adjustment_type}")
print(f"[DEBUG] quantity_change: {instance.quantity_change}")
```

**2. Model** (`core/models.py` - line 632):
```python
print(f"[DEBUG] Product saved successfully!")
print(f"[DEBUG] InventoryAdjustment saved successfully")
```

**3. View** (`core/views.py` - line 2941):
```python
print(f"[DEBUG] adjustment.quantity_change: {adjustment.quantity_change}")
print(f"[DEBUG] Transaction completed successfully")
```

## Before Reporting Issues

Make sure you've checked:
- [ ] Server console shows debug output
- [ ] You hard refreshed the browser (Ctrl+Shift+R)
- [ ] You checked database directly (Django shell)
- [ ] The form actually submitted (check POST data in debug)
- [ ] Quantity_change was calculated correctly (check value in debug)
- [ ] No error messages in server output

## Collecting Debug Information

To report the issue effectively:

1. **Save console output:**
   ```bash
   # Stop server
   # Run with output to file
   python manage.py runserver > debug.log 2>&1
   # Submit adjustment
   # Stop server (Ctrl+C)
   # Share debug.log
   ```

2. **Check database:**
   ```bash
   python manage.py shell
   # Run the verification queries above
   # Copy output
   ```

3. **Create report with:**
   - What you did (step by step)
   - What you expected
   - What actually happened
   - Full debug.log output
   - Database query results

---

**Still having issues?** Check `DEBUG_INVENTORY_ADJUSTMENT.md` for detailed analysis guide.
