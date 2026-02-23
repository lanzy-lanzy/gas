# Debug Guide - Inventory Adjustment Stock Update Issue

## Overview
Comprehensive debugging has been added to trace exactly where stock updates fail. All major functions now log detailed information.

## How to Use the Debug Output

### 1. Check Django Server Console
When you submit an inventory adjustment, look for debug messages in your server output:

```
[DEBUG] inventory_adjustment() - Method: POST
[DEBUG] POST request received
[DEBUG] POST data: {'product': '1', 'adjustment_type': 'increase', 'quantity': '10', 'reason': 'count_error', ...}
[DEBUG] Form created: <InventoryAdjustmentForm object>
[DEBUG] Form is_valid(): True
[DEBUG] Form is valid! Processing...
[DEBUG] Calling form.save(commit=False)...
[DEBUG] Form saved (commit=False)
[DEBUG] adjustment.quantity_change: 10
[DEBUG] Verifying quantity_change is set...
[DEBUG] quantity_change verified: 10
[DEBUG] Checking for negative stock...
[DEBUG] Product: LPG - 11kg
[DEBUG] Current stock: 50
[DEBUG] Adjustment amount: 10
[DEBUG] Calculated new_stock: 60
[DEBUG] Stock validation passed. Ready to save adjustment.
[DEBUG] Starting database transaction...
[DEBUG] Inside transaction - calling adjustment.save()...

================================================================================
[DEBUG] InventoryAdjustment.save() called
[DEBUG] self.pk = None
[DEBUG] self.quantity_change = 10
[DEBUG] self.product = LPG - 11kg
[DEBUG] self.reason = count_error
================================================================================

[DEBUG] is_new = True
[DEBUG] This is a NEW adjustment (pk is None)
[DEBUG] Checking if quantity_change is set...
[DEBUG] quantity_change is set: 10
[DEBUG] Refreshing product from DB...
[DEBUG] Product refreshed: LPG - 11kg
[DEBUG] previous_stock = 50
[DEBUG] Calculating: 50 + 10 = 60
[DEBUG] Set product.current_stock to 60
[DEBUG] Validating stock won't be negative...
[DEBUG] Validation passed - stock is valid: 60
[DEBUG] Saving product to database...
[DEBUG] Product saved successfully!
[DEBUG] Verified product.current_stock in DB: 60
[DEBUG] Creating StockMovement record...
[DEBUG] StockMovement created successfully: Adjustment: 10 LPG
[DEBUG] Saving InventoryAdjustment record...
[DEBUG] InventoryAdjustment saved successfully with ID: 12345
================================================================================
[DEBUG] InventoryAdjustment.save() COMPLETE
================================================================================

[DEBUG] Adjustment saved! ID: 12345
[DEBUG] Refreshing product from DB...
[DEBUG] Product refreshed. New stock in DB: 60
[DEBUG] Transaction completed successfully
[DEBUG] Success message: Inventory adjustment completed for LPG - 11kg. Stock adjusted by 10
[DEBUG] Transaction completed successfully
```

## What Each Debug Section Means

### View Debug Section
```
[DEBUG] inventory_adjustment() - Method: POST    ← Request received
[DEBUG] POST data: {...}                          ← What form data was sent
[DEBUG] Form is_valid(): True                     ← Form validation passed
[DEBUG] adjustment.quantity_change: 10            ← Conversion worked
[DEBUG] Calculated new_stock: 60                  ← Stock calculation correct
```

**If you see errors here:**
- Form not valid → Check field names in template
- quantity_change missing → Form.save() didn't convert properly
- new_stock negative → Adjustment amount too large

### Model Debug Section
```
[DEBUG] is_new = True                             ← New record (should be True)
[DEBUG] quantity_change is set: 10                ← Value confirmed
[DEBUG] previous_stock = 50                       ← Current stock read from DB
[DEBUG] Calculating: 50 + 10 = 60                 ← Math is correct
[DEBUG] Product saved successfully!               ← Stock updated in DB
[DEBUG] StockMovement created successfully        ← Audit record created
```

**If you see errors here:**
- is_new = False → Update instead of create (wrong)
- "quantity_change must be set" → Form didn't set quantity_change
- Product save fails → Database or field error
- StockMovement fails → User permission issue

## Common Debug Scenarios

### Scenario 1: Form Not Valid
```
[DEBUG] Form is_valid(): False
[DEBUG] Form errors: {'quantity': ['This field is required.']}
```
**Solution:** Check template form field names match form fields
- `name="quantity"` (not `quantity_change`)
- `name="adjustment_type"` (not `type`)

### Scenario 2: quantity_change Not Set
```
[DEBUG] adjustment.quantity_change: None
[ERROR] quantity_change is None!
```
**Solution:** Form.save() not working properly
- Check form.save() method in core/forms.py
- Verify adjustment_type and quantity in cleaned_data

### Scenario 3: Product Not Saving
```
[DEBUG] Saving product to database...
[ERROR] Failed to save product: ...
```
**Solution:** Database issue with product
- Check product.current_stock is integer
- Check product permissions
- Check database integrity

### Scenario 4: Stock Not Updated
```
[DEBUG] Set product.current_stock to 60
[DEBUG] Product saved successfully!
[DEBUG] Product refreshed. New stock in DB: 50    ← Still 50!
```
**Solution:** Stock updated in object but not in database
- Check update_fields=['current_stock', 'updated_at']
- Check model save() method
- Check database transaction

## Debug Log Locations

### Django Development Server
- **Output**: Console/Terminal where you run `python manage.py runserver`
- **Capture**: Copy all output when submitting adjustment

### Production Server (gunicorn/uwsgi)
- **Output**: Usually in log files (check your deployment)
- **Location**: Often in `/var/log/` or application directory
- **Command**: `tail -f /path/to/logfile.log`

### Django Logging Configuration
The debug output uses Python's `print()` which outputs to stdout:

```python
# View logs with:
python manage.py runserver 2>&1 | tee debug.log

# Or save to file:
python manage.py runserver > debug.log 2>&1
```

## Step-by-Step Debug Process

### Step 1: Submit Adjustment with Debugging
1. Open two terminal windows
2. In first window, run: `python manage.py runserver`
3. In second window, run: `tail -f debug.log` (if using file)
4. Submit an inventory adjustment
5. Watch the debug output

### Step 2: Trace the Flow
Follow these markers in the output:
1. `[DEBUG] inventory_adjustment() - Method: POST` ← Started
2. `[DEBUG] Form is_valid(): True` ← Form OK?
3. `[DEBUG] adjustment.quantity_change: 10` ← Converted?
4. `[DEBUG] InventoryAdjustment.save() called` ← Save called?
5. `[DEBUG] Product saved successfully!` ← Stock updated?
6. `[DEBUG] Transaction completed successfully` ← Finished?

### Step 3: Identify Failure Point
- If fails at step 2 → Form issue
- If fails at step 3 → Conversion issue
- If fails at step 4 → Not reaching save
- If fails at step 5 → Database issue
- If fails at step 6 → Transaction issue

## Extracting Debug Output to File

### Option 1: Redirect Server Output
```bash
python manage.py runserver > debug.log 2>&1
```
Then check: `debug.log`

### Option 2: Use Logging Module
```python
# Add to settings.py for persistent logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
}
```

### Option 3: Save Console Output
Just copy-paste the console output into a text file for analysis.

## Testing Without the Web Interface

Run this in Python shell:

```python
python manage.py shell
```

```python
from django.contrib.auth.models import User
from core.models import LPGProduct, InventoryAdjustment
from core.forms import InventoryAdjustmentForm

# Setup
user = User.objects.first()
product = LPGProduct.objects.filter(is_active=True).first()

print(f"Before: {product.name} stock = {product.current_stock}")

# Submit form
data = {
    'product': product.id,
    'adjustment_type': 'increase',
    'quantity': 10,
    'reason': 'count_error',
    'notes': 'Test'
}

form = InventoryAdjustmentForm(data)
print(f"Form valid: {form.is_valid()}")
print(f"Form errors: {form.errors}")

if form.is_valid():
    adj = form.save(commit=False)
    adj.adjusted_by = user
    print(f"Before save - quantity_change: {adj.quantity_change}")
    
    # This will trigger all debug output
    adj.save()
    
    product.refresh_from_db()
    print(f"After: {product.name} stock = {product.current_stock}")
```

Look for debug output like:
```
[DEBUG] InventoryAdjustment.save() called
[DEBUG] quantity_change is set: 10
[DEBUG] Product saved successfully!
[DEBUG] InventoryAdjustment.save() COMPLETE
```

## Understanding Debug Markers

| Marker | Meaning | Status |
|--------|---------|--------|
| `[DEBUG]` | Normal information | ℹ️ |
| `[ERROR]` | Error occurred | ❌ |
| `[WARNING]` | Non-critical issue | ⚠️ |
| `==...==` | Section boundary | 📍 |

## If Debug Output Shows Success But Stock Didn't Update

This indicates:
1. Django says stock updated ✅
2. But you don't see the change in the UI ❌

**Possible causes:**
- Browser cached the page (hard refresh: Ctrl+Shift+R)
- Multiple database connections (check for replica lag)
- View not refreshing product correctly
- Inventory management view has different query

**Solution:**
```python
# In Django shell
from core.models import LPGProduct
product = LPGProduct.objects.get(id=1)  # Replace with your product ID
product.refresh_from_db()
print(product.current_stock)
```

If this shows the updated value but UI doesn't, the issue is in the UI layer, not the adjustment logic.

## Disabling Debug Output

When debug output is working and you're done:

**Option 1:** Comment out debug lines (not recommended - lose visibility)

**Option 2:** Use logging level (better):
```python
import logging
logging.getLogger('django.db').setLevel(logging.WARNING)
```

**Option 3:** Use environment variable:
```bash
DEBUG=0 python manage.py runserver
```

## Creating a Debug Report

When reporting issues, include:
1. **Full debug output** (from form submission to completion)
2. **Product ID and current stock** (before and after)
3. **Adjustment amount and type** (increase/decrease)
4. **Any error messages** (from form or console)
5. **Database query results** (from manual check)

Example:
```
Product: LPG 11kg (ID: 1)
Current Stock Before: 50
Adjustment: INCREASE by 10
Expected After: 60
Actual After: 50 (NOT UPDATED)

[Complete debug output here...]
```

---

**Note:** This debug version is for development. For production, remove or disable debug output to reduce log file size and improve performance.
