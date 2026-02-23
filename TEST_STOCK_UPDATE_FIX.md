# Test Stock Update Fix

## What Was Fixed

The bug: Stock was not being updated because the UUID primary key was generated BEFORE save(), making `self.pk is None` check return False.

**Solution:** Changed to use `self._state.adding` which properly detects new instances regardless of pk generation timing.

## How to Test

### Step 1: Get Current Stock
```bash
python manage.py shell
```

```python
from core.models import LPGProduct
product = LPGProduct.objects.get(name='LPG PRYCEGAS', size='11kg')
print(f"Current stock BEFORE: {product.current_stock}")
```

Note the number (e.g., 860)

### Step 2: Make Adjustment
1. Go to `/dealer/inventory/adjustment/`
2. Select: "LPG PRYCEGAS - 11kg"
3. Choose: "Decrease Stock"
4. Enter: 60
5. Reason: "damage"
6. Click: "Apply Adjustment"

### Step 3: Check in Database

**In browser:**
- Check product stock (should be 800 now, not 860)

**In Django shell:**
```python
from core.models import LPGProduct
product = LPGProduct.objects.get(name='LPG PRYCEGAS', size='11kg')
product.refresh_from_db()
print(f"Current stock AFTER: {product.current_stock}")
```

**Expected:** 800 (not 860!)

### Step 4: Check Debug Output

Look for:
```
[DEBUG] is_new (using _state.adding) = True
[DEBUG] Product saved successfully!
[DEBUG] StockMovement created successfully
```

## Verification

✅ Stock changes from 860 to 800
✅ Debug shows `is_new = True`
✅ Product saved message appears
✅ StockMovement created message appears
✅ Adjustment record saved

## If Still Not Working

Check if you did a hard browser refresh:
- **Ctrl+Shift+R** (Windows/Linux)
- **Cmd+Shift+R** (Mac)

Or clear the page cache and try again.
