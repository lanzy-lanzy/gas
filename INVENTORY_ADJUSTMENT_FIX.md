# Inventory Adjustment Product Dropdown Fix

## Issue
The Inventory Adjustment form's product dropdown was empty (showing only "—") and users couldn't select products to adjust.

## Root Cause
The `InventoryAdjustmentForm` class in `core/forms.py` was missing an `__init__` method to populate the product field's queryset. Without explicit queryset configuration, the form wasn't loading products from the database.

## Solution
Added an `__init__` method to `InventoryAdjustmentForm` that:
1. Populates the product dropdown with all active (`is_active=True`) LPG products
2. Orders products by name for better usability
3. Sets a friendly empty label: "-- Select a product --"

## Changes Made

### File: `core/forms.py` (Lines 869-873)
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Populate product dropdown with all active products
    self.fields['product'].queryset = LPGProduct.objects.filter(is_active=True).order_by('name')
    self.fields['product'].empty_label = "-- Select a product --"
```

## How It Works
1. When the form is instantiated, the `__init__` method runs
2. It queries all active LPG products from the database
3. Sets them as the available options in the product dropdown
4. Users can now select from the list of available products

## Features Enabled
- Product selection in inventory adjustment form
- Real-time stock information display (via existing JavaScript)
- Projected stock calculation when quantity is changed
- Negative stock prevention

## Testing
To test the fix:
1. Navigate to Inventory → Inventory Adjustment
2. The Product dropdown should now show all active products
3. Select a product to see current stock information
4. Enter a quantity change (positive or negative)
5. Select a reason from the dropdown
6. Click "Apply Adjustment" to save

## Related Code
- View: `core/views.py` - `inventory_adjustment()` function
- Template: `templates/dealer/inventory_adjustment.html` - Form rendering and JavaScript
- Model: `core/models.py` - `InventoryAdjustment` and `LPGProduct` models
