# Comprehensive Debugging Added - Summary

## What Was Added

Complete debugging has been added to trace inventory adjustment stock updates through the entire system.

## Debug Points Across 3 Files

### 1. **Form Debug** (`core/forms.py` - InventoryAdjustmentForm.save())

Traces:
- Form.save() method called with commit parameter
- Instance creation from super().save(commit=False)
- adjustment_type extraction from cleaned_data
- quantity extraction from cleaned_data
- quantity_change calculation (positive for increase, negative for decrease)
- Final instance state before/after save

**Output Example:**
```
[DEBUG] InventoryAdjustmentForm.save() called with commit=False
[DEBUG] Instance created from super().save(commit=False): <InventoryAdjustment object>
[DEBUG] adjustment_type: increase
[DEBUG] quantity: 10
[DEBUG] Setting quantity_change to POSITIVE: 10
[DEBUG] Final quantity_change: 10
[DEBUG] Instance product: LPG - 11kg
[DEBUG] Instance reason: count_error
[DEBUG] Instance notes: Test notes
```

### 2. **View Debug** (`core/views.py` - inventory_adjustment())

Traces:
- Request method (GET/POST)
- POST data received
- Form creation and validation
- Form errors if any
- adjustment object state after form.save(commit=False)
- quantity_change verification
- Stock calculation (current + adjustment = new)
- Negative stock validation
- Transaction start/completion
- Success/failure with detailed messages

**Output Example:**
```
[DEBUG] inventory_adjustment() - Method: POST
[DEBUG] POST request received
[DEBUG] POST data: {'product': '1', 'adjustment_type': 'increase', 'quantity': '10', ...}
[DEBUG] Form is_valid(): True
[DEBUG] Form is valid! Processing...
[DEBUG] Calling form.save(commit=False)...
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
[DEBUG] Transaction completed successfully
```

### 3. **Model Debug** (`core/models.py` - InventoryAdjustment.save())

Most detailed debugging. Traces:
- Save method entry/exit
- is_new flag (new vs update)
- quantity_change verification
- Product refresh from database
- Previous stock before adjustment
- Stock calculation (previous + change = new)
- Negative stock validation
- Product save operation
- StockMovement record creation
- InventoryAdjustment record save

**Output Example:**
```
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
```

## Total Lines Added

- **Form**: ~30 debug lines added
- **View**: ~50 debug lines added
- **Model**: ~70 debug lines added
- **Total**: ~150 debug print statements

## Running With Debug Output

### Method 1: Console Output
```bash
python manage.py runserver
# Submit adjustment
# Watch console for [DEBUG] messages
```

### Method 2: Save to File
```bash
python manage.py runserver > debug.log 2>&1
# Submit adjustment
# Check debug.log
```

### Method 3: Django Shell
```bash
python manage.py shell
# Run manual test (see QUICK_DEBUG_CHECKLIST.md)
# Watch for [DEBUG] output
```

## Reading the Debug Output

### Flow Order (Should see in this sequence):
1. **View starts** → `inventory_adjustment() - Method: POST`
2. **Form validation** → `Form is_valid(): True`
3. **Form conversion** → `adjustment_type`, `quantity` → `quantity_change`
4. **Validation** → `Calculated new_stock: X`
5. **Transaction starts** → `Starting database transaction...`
6. **Model save starts** → `InventoryAdjustment.save() called`
7. **Product updates** → `Product saved successfully!`
8. **Audit trail** → `StockMovement created successfully`
9. **Adjustment saves** → `InventoryAdjustment saved successfully`
10. **Transaction ends** → `Transaction completed successfully`

### If Output Stops at Step X

The issue is at step X or between X and X+1:
- Stops at 2 → Form not valid
- Stops at 3 → Conversion failed
- Stops at 5 → Validation failed
- Stops at 7 → Database error
- Stops at 10 → Transaction rolled back

## Key Debug Values to Watch For

| Value | What to Look For |
|-------|-----------------|
| `adjustment_type` | Should be `increase` or `decrease` |
| `quantity` | Should be positive integer |
| `quantity_change` | Should match ±quantity |
| `current_stock` | Original product stock |
| `new_stock` | current_stock + quantity_change |
| `is_new` | Should be `True` for new adjustments |
| `[DEBUG]` | Normal operation |
| `[ERROR]` | Something went wrong |
| `[WARNING]` | Non-critical issue |

## Debug Output Examples

### ✅ SUCCESS: Increase stock 50 → 60
```
[DEBUG] adjustment_type: increase
[DEBUG] quantity: 10
[DEBUG] Setting quantity_change to POSITIVE: 10
[DEBUG] Calculated new_stock: 60
[DEBUG] Product saved successfully!
[DEBUG] Transaction completed successfully
```

### ✅ SUCCESS: Decrease stock 60 → 55
```
[DEBUG] adjustment_type: decrease
[DEBUG] quantity: 5
[DEBUG] Setting quantity_change to NEGATIVE: -5
[DEBUG] Calculated new_stock: 55
[DEBUG] Product saved successfully!
[DEBUG] Transaction completed successfully
```

### ❌ FAILURE: Form error
```
[DEBUG] Form is_valid(): False
[DEBUG] Form errors: {'quantity': ['This field is required.']}
```

### ❌ FAILURE: Negative stock
```
[DEBUG] Current stock: 10
[DEBUG] Adjustment amount: 20
[DEBUG] Calculated new_stock: -10
[ERROR] New stock would be negative: -10
```

### ❌ FAILURE: Database error
```
[DEBUG] Saving product to database...
[ERROR] Failed to save product: [database error details]
```

## Finding Errors

When debugging:
1. Look for `[ERROR]` markers first
2. Look for `[WARNING]` markers second
3. Look for where output stops (failure point)
4. Check the values at each step

## Performance Note

Debug prints slow down execution slightly but help identify issues:
- Development: Leave enabled
- Production: Should disable (remove or use logging level)

To disable:
```python
# Comment out print statements or use logging filter
import logging
logging.disable(logging.CRITICAL)  # Disable all logging/prints
```

## Next Steps

Once you have debug output:

1. **If successful in debug but stock not in UI:**
   - Hard refresh browser (Ctrl+Shift+R)
   - Check database directly (Django shell)
   - See if it's a caching issue

2. **If debug shows error:**
   - Identify the step where it failed
   - Check QUICK_DEBUG_CHECKLIST.md for that failure
   - Make the fix suggested
   - Test again

3. **If unclear:**
   - Save full debug output
   - Check `DEBUG_INVENTORY_ADJUSTMENT.md` for detailed analysis
   - Create report with output and steps

## Documentation

- **Quick Start**: `QUICK_DEBUG_CHECKLIST.md`
- **Detailed Guide**: `DEBUG_INVENTORY_ADJUSTMENT.md`
- **Troubleshooting**: `INVENTORY_ADJUSTMENT_TROUBLESHOOTING.md`
- **Complete Fix**: `INVENTORY_ADJUSTMENT_COMPLETE_FIX.md`

---

**Status**: Debugging fully implemented and ready to use.

Submit an adjustment and check the server console for detailed debug output!
