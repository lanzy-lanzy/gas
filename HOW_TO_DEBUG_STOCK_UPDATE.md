# How to Debug Stock Update Issues - Quick Start

## TL;DR (30 seconds)

1. **Open terminal in project directory:**
   ```bash
   python manage.py runserver > debug.log 2>&1
   ```

2. **In browser:**
   - Go to `/dealer/inventory/adjustment/`
   - Select a product
   - Choose "Increase Stock"
   - Enter quantity: 10
   - Submit

3. **In terminal:**
   - Stop server (Ctrl+C)
   - Check log: `cat debug.log | grep "\[DEBUG\]\|\[ERROR\]"`

4. **Look for:**
   - `[DEBUG] adjustment.quantity_change: 10` ✅ (converted)
   - `[DEBUG] Product saved successfully!` ✅ (updated)
   - `[ERROR]` ❌ (failure point)

5. **Check database:**
   ```bash
   python manage.py shell
   ```
   ```python
   from core.models import LPGProduct
   product = LPGProduct.objects.get(id=1)
   print(product.current_stock)  # Should show 60 if started at 50
   ```

---

## Full Process (5 minutes)

### 1. Prepare Debug Environment

**Option A: File Output (Recommended)**
```bash
# Open new terminal
cd /path/to/prycegas
python manage.py runserver > debug.log 2>&1
```

**Option B: Console Output (Quick)**
```bash
python manage.py runserver
# Just watch the console directly
```

**Option C: Real-Time File**
```bash
# Terminal 1
python manage.py runserver > debug.log 2>&1

# Terminal 2
tail -f debug.log | grep "\[DEBUG\]\|\[ERROR\]"
```

### 2. Trigger Adjustment

1. Open browser to: `http://127.0.0.1:8000/dealer/inventory/adjustment/`
2. **Product**: Select any product (note the name)
3. **Adjustment Type**: Select "Increase Stock"
4. **Quantity**: Enter `10`
5. **Reason**: Select any reason
6. **Notes**: Optional
7. Click **"Apply Adjustment"**

### 3. Check Debug Output

#### For File Output:
```bash
# View all debug output
cat debug.log

# View only debug messages
cat debug.log | grep "\[DEBUG\]"

# View only errors
cat debug.log | grep "\[ERROR\]"

# View last 50 lines
tail -50 debug.log
```

#### For Console Output:
Look at the terminal where you ran `runserver`

### 4. Understand the Output

#### Expected Output (Success):
```
[DEBUG] inventory_adjustment() - Method: POST
[DEBUG] POST data: {...}
[DEBUG] Form is_valid(): True
[DEBUG] adjustment.quantity_change: 10
[DEBUG] InventoryAdjustment.save() called
[DEBUG] Product saved successfully!
[DEBUG] Transaction completed successfully
Success message should appear in browser
```

#### What Each Line Means:
- `Form is_valid(): True` → Form data is correct ✅
- `adjustment.quantity_change: 10` → Conversion worked ✅
- `Product saved successfully!` → Stock updated ✅
- `Transaction completed successfully` → All saved ✅

### 5. Check Database

```bash
python manage.py shell
```

```python
# Check product stock
from core.models import LPGProduct
product = LPGProduct.objects.get(id=1)  # Use YOUR product ID
print(f"Stock: {product.current_stock}")

# Check if adjustment was recorded
from core.models import InventoryAdjustment
adj = InventoryAdjustment.objects.latest('created_at')
print(f"Latest adjustment: {adj.quantity_change}")
```

### 6. Refresh Browser

If debug shows success but browser shows old stock:
- Hard refresh: **Ctrl+Shift+R** (or Cmd+Shift+R on Mac)
- Or open new private/incognito window
- Or clear cache and reload

---

## Troubleshooting by Symptom

### Symptom: "Form invalid" Error

**Debug Shows:**
```
[DEBUG] Form is_valid(): False
[DEBUG] Form errors: {'quantity': [...]}
```

**Check These:**
- [ ] Entered a number for Quantity?
- [ ] Selected a Product?
- [ ] Selected a Reason?
- [ ] Browser autocomplete not interfering?

**Fix:** Fill in all required fields and try again

---

### Symptom: "Quantity change is None" Error

**Debug Shows:**
```
[DEBUG] adjustment.quantity_change: None
[ERROR] quantity_change is None!
```

**This means:** Form didn't convert `adjustment_type` + `quantity` to `quantity_change`

**Check template has correct field names:**
```html
<!-- Check these are in the form -->
<input name="adjustment_type" type="radio" value="increase">
<input name="quantity" type="number" min="1">
```

**Not these:**
```html
<!-- WRONG -->
<input name="quantity_change">
<input name="type">
```

**Fix:** Update template field names and try again

---

### Symptom: "New stock would be negative" Error

**Debug Shows:**
```
[DEBUG] Current stock: 10
[DEBUG] Adjustment amount: 20
[DEBUG] Calculated new_stock: -10
[ERROR] New stock would be negative
```

**This means:** You're trying to decrease more than available

**Fix:** 
1. Check current stock first
2. Use a smaller adjustment amount
3. Or select "Increase Stock" instead

---

### Symptom: "Failed to save product" Error

**Debug Shows:**
```
[DEBUG] Saving product to database...
[ERROR] Failed to save product: [error message]
```

**This means:** Database error, not logic error

**Check:**
1. Is database running?
2. Any migration issues?
3. Are permissions correct?

**Test:**
```bash
python manage.py migrate
python manage.py check
```

---

### Symptom: Form Succeeds But Stock Unchanged

**Debug Shows:**
```
[DEBUG] Transaction completed successfully
```
**But:** Stock in database is still old value

**Check:**
1. Hard refresh browser (Ctrl+Shift+R)
2. Check database directly:
   ```bash
   python manage.py shell
   ```
   ```python
   from core.models import LPGProduct
   product = LPGProduct.objects.get(id=1)
   product.refresh_from_db()
   print(product.current_stock)  # Fresh from DB
   ```

3. If database shows updated stock:
   - Issue is browser cache - clear cache
   - Or view has stale data - refresh page

4. If database shows old stock:
   - Issue is in save logic - check for errors
   - Check if transaction actually committed

---

## Debug Output Markers

```
[DEBUG]   = Normal information (green)
[ERROR]   = Problem occurred (red)
[WARNING] = Non-critical issue (yellow)
```

## Key Values to Watch

When you submit:
- `adjustment_type` → Should be `increase` or `decrease`
- `quantity` → Should be the number you entered
- `quantity_change` → Should be `+quantity` or `-quantity`
- Current stock → Should match database
- New stock → Should be current + adjustment

## Step-by-Step Checklist

- [ ] Server running with debug output
- [ ] Adjustment submitted successfully
- [ ] Debug output shows: `Form is_valid(): True`
- [ ] Debug output shows: `adjustment.quantity_change: [some number]`
- [ ] Debug output shows: `Product saved successfully!`
- [ ] Browser shows success message
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Check database manually
- [ ] Stock matches expected value

## Still Having Issues?

1. **Collect all information:**
   ```bash
   # Get full debug output
   python manage.py runserver > debug_full.log 2>&1
   # Submit adjustment
   # Ctrl+C to stop
   ```

2. **Get database state:**
   ```bash
   python manage.py shell
   # Run verification queries above
   # Copy output
   ```

3. **Create report with:**
   - Steps taken (exactly)
   - What you expected
   - What happened
   - Full debug_full.log file
   - Database query results

## Read More

- **Quick Checklist**: `QUICK_DEBUG_CHECKLIST.md`
- **Detailed Guide**: `DEBUG_INVENTORY_ADJUSTMENT.md`  
- **Common Issues**: `INVENTORY_ADJUSTMENT_TROUBLESHOOTING.md`

---

**You're now ready to debug! Start with step 1 above.** 🚀
