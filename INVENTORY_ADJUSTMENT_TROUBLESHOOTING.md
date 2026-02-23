# Inventory Adjustment Troubleshooting Guide

## Quick Verification Steps

### Step 1: Verify Form Submission
1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Make an inventory adjustment
4. Look for POST request to `/dealer/inventory/adjustment/`
5. Check the Form Data includes:
   - `product`: (product ID)
   - `adjustment_type`: `increase` or `decrease`
   - `quantity`: (a number)
   - `reason`: (from dropdown)
   - `notes`: (optional)

### Step 2: Check Form Validation
If form shows errors:
1. Ensure all required fields are filled:
   - ✓ Product selected
   - ✓ Adjustment type selected
   - ✓ Quantity entered (must be > 0)
   - ✓ Reason selected
2. Quantity must be a positive integer
3. Message should show under each field if invalid

### Step 3: Verify Model Save is Called
1. Check Django server logs for any exceptions
2. Look for console messages like:
   - "quantity_change must be set before saving"
   - "Adjustment would result in negative stock"
   - "Could not create stock movement"

### Step 4: Database Verification
Run these commands in Django shell:

```python
# Check if adjustment was created
from core.models import InventoryAdjustment, LPGProduct
adj = InventoryAdjustment.objects.latest('created_at')
print(f"Latest adjustment: {adj}")
print(f"  Product: {adj.product}")
print(f"  Quantity Change: {adj.quantity_change}")
print(f"  Adjusted By: {adj.adjusted_by}")

# Check if product stock was updated
product = adj.product
print(f"Current product stock: {product.current_stock}")

# Check stock movements
from core.models import StockMovement
movements = StockMovement.objects.filter(reference_id=str(adj.id))
print(f"Stock movements for this adjustment: {movements.count()}")
for m in movements:
    print(f"  {m.movement_type}: {m.quantity} (previous: {m.previous_stock}, new: {m.new_stock})")
```

## Common Problems and Solutions

### Problem 1: Form Shows "Quantity change not properly set" Error

**Possible Causes:**
1. Form field name mismatch
2. quantity_change not being set by form.save()

**Solution:**
1. Check template form fields match what form expects:
   ```html
   <input type="radio" name="adjustment_type" value="increase">
   <input type="number" name="quantity" min="1">
   <select name="product">
   <select name="reason">
   <textarea name="notes">
   ```

2. Verify form.save() is being called:
   ```python
   # In Python shell
   from core.forms import InventoryAdjustmentForm
   from django.contrib.auth.models import User
   from core.models import LPGProduct
   
   user = User.objects.first()
   product = LPGProduct.objects.filter(is_active=True).first()
   
   data = {
       'product': product.id,
       'adjustment_type': 'increase',
       'quantity': 5,
       'reason': 'count_error',
       'notes': 'test'
   }
   
   form = InventoryAdjustmentForm(data)
   if form.is_valid():
       adj = form.save(commit=False)
       print(f"quantity_change set: {adj.quantity_change}")
       adj.adjusted_by = user
       adj.save()
       print(f"Saved! Product stock now: {adj.product.current_stock}")
   else:
       print(f"Form errors: {form.errors}")
   ```

### Problem 2: Stock Not Updating

**Check List:**
- [ ] Product is active (`is_active=True`)
- [ ] Adjustment saved without errors
- [ ] No concurrent adjustments happening
- [ ] Database transaction completed
- [ ] Page was refreshed to see updated value

**Debug Commands:**
```python
from core.models import LPGProduct, InventoryAdjustment

# Get the product
product = LPGProduct.objects.get(id=1)  # Change to your product ID
print(f"Current stock in DB: {product.current_stock}")

# Get latest adjustment
adj = InventoryAdjustment.objects.filter(product=product).latest('created_at')
print(f"Latest adjustment quantity_change: {adj.quantity_change}")
print(f"Saved at: {adj.created_at}")

# Recalculate what stock should be
from core.models import StockMovement
movements = StockMovement.objects.filter(product=product).order_by('created_at')
calculated_stock = 0
for m in movements:
    calculated_stock += m.quantity
    print(f"{m.movement_type}: {m.quantity} (running total: {calculated_stock})")
```

### Problem 3: Can't Select Product

**Possible Causes:**
1. No active products in database
2. Product queryset not loading

**Solution:**
```python
from core.models import LPGProduct

# Check if active products exist
active = LPGProduct.objects.filter(is_active=True)
print(f"Active products: {active.count()}")

if active.count() == 0:
    print("No active products! Creating test product...")
    p = LPGProduct.objects.create(
        name="Test Product",
        size="11kg",
        price=500,
        cost_price=400,
        current_stock=100,
        is_active=True
    )
    print(f"Created: {p}")
```

### Problem 4: Error "Adjustment would result in negative stock"

**This is by design** - the system prevents invalid adjustments.

**Check:**
1. Is current stock sufficient?
   ```python
   product.current_stock  # Should show current amount
   ```

2. Are you trying to decrease more than available?
   ```python
   # Current: 10, Trying to decrease by 20?
   # This will fail, which is correct
   ```

3. Need to correct the stock? Create a new adjustment:
   ```python
   # If stock shows 10 but should be 30
   # Create adjustment: INCREASE by 20
   ```

## Manual Testing Steps

1. **Create Test Product** (if needed):
   - Go to Stock Management
   - Create product with initial stock
   - Verify product appears in adjustment dropdown

2. **Test Increase Adjustment**:
   - Product: Select your test product
   - Type: "Increase Stock"
   - Quantity: 10
   - Reason: Select any reason
   - Notes: "Test increase"
   - Click Apply
   - Should see: "Inventory adjustment completed... Stock adjusted by 10"
   - Verify stock increased by 10

3. **Test Decrease Adjustment**:
   - Same but: Type: "Decrease Stock", Quantity: 5
   - Should see: "Stock adjusted by -5"
   - Verify stock decreased by 5

4. **Test Negative Stock Prevention**:
   - Current stock: 10
   - Try: Decrease by 20
   - Should see: "would result in negative stock"
   - Button should be disabled

## Log Checking

Check Django logs for adjustment errors:
```bash
# Windows
type server.log | findstr "Inventory adjustment error"

# Linux/Mac
tail -f server.log | grep "Inventory adjustment"
```

## Testing with Python Shell

```bash
python manage.py shell
```

```python
from core.models import LPGProduct, InventoryAdjustment, StockMovement
from core.forms import InventoryAdjustmentForm
from django.contrib.auth.models import User

# Create test user if needed
user, _ = User.objects.get_or_create(username='testuser', is_staff=True)

# Get or create test product
product, _ = LPGProduct.objects.get_or_create(
    name='Test LPG',
    defaults={'size': '11kg', 'price': 500, 'cost_price': 400, 'current_stock': 50, 'is_active': True}
)

print(f"Test product: {product} (Stock: {product.current_stock})")

# Test form
form_data = {
    'product': product.id,
    'adjustment_type': 'increase',
    'quantity': 10,
    'reason': 'count_error',
    'notes': 'Manual test'
}

form = InventoryAdjustmentForm(form_data)
print(f"Form valid: {form.is_valid()}")

if form.is_valid():
    adj = form.save(commit=False)
    adj.adjusted_by = user
    
    print(f"Before save - quantity_change: {adj.quantity_change}")
    adj.save()
    print(f"After save - adjustment created: {adj.id}")
    
    product.refresh_from_db()
    print(f"Product stock now: {product.current_stock}")
    
    # Check movement
    movement = StockMovement.objects.filter(reference_id=str(adj.id)).first()
    print(f"Movement created: {movement}")
else:
    print(f"Form errors: {form.errors}")
```

## File Locations for Reference

- **Form**: `core/forms.py` - lines 844-920
- **Model**: `core/models.py` - lines 632-674
- **View**: `core/views.py` - lines 2941-2988
- **Template**: `templates/dealer/inventory_adjustment.html`
- **Tests**: `test_inventory_adjustment_fix.py`

## Need More Help?

If you're still having issues:
1. Check server logs for actual error messages
2. Run the test script to identify where the process breaks
3. Use Python shell to manually test the form and model
4. Verify database records are being created
