# Inventory Adjustment Logic Fix

## Problem
The inventory adjustment form was not actually updating product stock when submitted, even though the form appeared to work.

## Root Causes Identified and Fixed

### 1. **Form Save Method Not Setting quantity_change**
**Issue**: The form's `save()` method converts `adjustment_type` + `quantity` into `quantity_change`, but if not properly called, the model wouldn't have this value.

**Fix**: Enhanced the form's `save()` method to explicitly set quantity_change:
```python
def save(self, commit=True):
    instance = super().save(commit=False)
    adjustment_type = self.cleaned_data.get('adjustment_type')
    quantity = self.cleaned_data.get('quantity')
    
    # Convert to signed quantity_change
    if adjustment_type == 'increase':
        instance.quantity_change = quantity
    else:  # decrease
        instance.quantity_change = -quantity
    
    if commit:
        instance.save()
    return instance
```

### 2. **Model Save Method Not Validating/Updating Properly**
**Issue**: The model's `save()` method needed better error handling and validation.

**Fixes Applied**:
- ✓ Added validation that `quantity_change` is set before processing
- ✓ Refresh product from DB before calculating to get latest stock
- ✓ Validate that adjustment won't result in negative stock
- ✓ Use `update_fields` when saving product for efficiency
- ✓ Wrap StockMovement creation in try/except to prevent total failure
- ✓ Better error messages for debugging

**Code**:
```python
def save(self, *args, **kwargs):
    is_new = self.pk is None
    
    if is_new:
        # Verify quantity_change is set
        if not self.quantity_change:
            raise ValueError("quantity_change must be set before saving")
        
        # Refresh product from DB to get latest stock
        self.product.refresh_from_db()
        
        # Store previous stock
        previous_stock = self.product.current_stock
        
        # Update product stock
        self.product.current_stock += self.quantity_change
        
        # Validate stock won't go negative
        if self.product.current_stock < 0:
            raise ValueError(f"Adjustment would result in negative stock...")
        
        # Save the product with updated stock
        self.product.save(update_fields=['current_stock', 'updated_at'])
        
        # Create stock movement record
        try:
            StockMovement.objects.create(...)
        except Exception as e:
            print(f"Warning: Could not create stock movement: {str(e)}")
    
    super().save(*args, **kwargs)
```

### 3. **View Not Validating quantity_change Was Set**
**Issue**: The view wasn't checking if `quantity_change` was properly set before attempting the adjustment.

**Fixes Applied**:
- ✓ Added validation that `quantity_change` attribute exists and is not None
- ✓ Better error messages showing actual values
- ✓ Added try/except with proper traceback logging
- ✓ Included adjustment amount in success message for verification

**Code**:
```python
# Verify quantity_change is set
if not hasattr(adjustment, 'quantity_change') or adjustment.quantity_change is None:
    messages.error(request, 'Error: Quantity change not properly set.')
    return render(request, 'dealer/inventory_adjustment.html', {'form': form})

# Show details in error messages
messages.error(request, 
    f'Current stock: {product.current_stock}, Adjustment: {adjustment.quantity_change}')

# Include amount in success
messages.success(request, 
    f'Stock adjusted by {adjustment.quantity_change}')
```

## Data Flow

```
User submits form
    ↓
InventoryAdjustmentForm.is_valid() → checks all fields
    ↓
form.save(commit=False)
    ↓ (converts adjustment_type + quantity → quantity_change)
adjustment object (quantity_change now set)
    ↓
view sets: adjustment.adjusted_by = request.user
    ↓
view validates: quantity_change exists and stock won't go negative
    ↓
adjustment.save() → triggers model save method
    ↓ (is_new = True, so:)
    ├─ Refresh product from DB
    ├─ Calculate: new_stock = current_stock + quantity_change
    ├─ Validate new_stock >= 0
    ├─ Update: product.current_stock = new_stock
    ├─ Save product
    └─ Create StockMovement record
    ↓
Redirect to inventory management
```

## Testing

Run the test script:
```bash
python manage.py shell < test_inventory_adjustment_fix.py
```

This will:
1. Create test data if needed
2. Test INCREASE adjustment
3. Test DECREASE adjustment
4. Verify stock was actually updated
5. Verify StockMovement records were created

## Verification Checklist

- [ ] Form displays product dropdown with active products
- [ ] Form displays "Increase Stock" and "Decrease Stock" options
- [ ] Form accepts positive quantity only
- [ ] Form displays projected stock calculation
- [ ] Clicking "Apply Adjustment" saves the change
- [ ] Product stock is actually updated in database
- [ ] Success message shows the adjustment amount
- [ ] Negative stock prevention works
- [ ] StockMovement records are created
- [ ] Can view adjustment history

## Common Issues and Solutions

### Issue: "Quantity change not properly set"
**Solution**: Check that form fields are named correctly in template:
- `adjustment_type` (radio buttons)
- `quantity` (number input)
- `product` (select dropdown)
- `reason` (select dropdown)
- `notes` (textarea)

### Issue: Stock not updating
**Solution**: Check:
1. Product is active (`is_active=True`)
2. Database transaction completes successfully
3. No validation errors in browser console
4. Check Django error logs for exceptions

### Issue: Negative stock error when there should be enough
**Solution**: 
1. Verify current stock in database
2. Check for decimal vs integer mismatch
3. Ensure no concurrent adjustments happening

## Files Modified

1. **core/forms.py** - `InventoryAdjustmentForm`
   - Added `adjustment_type` field
   - Added `quantity` field
   - Enhanced `save()` method

2. **core/models.py** - `InventoryAdjustment.save()`
   - Added validation
   - Better error handling
   - Refresh product before updating

3. **core/views.py** - `inventory_adjustment()`
   - Added validation checks
   - Better error messages
   - Improved logging

4. **templates/dealer/inventory_adjustment.html**
   - Updated form layout
   - Added adjustment type radio buttons
   - Updated JavaScript for new fields
