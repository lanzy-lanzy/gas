# Inventory Adjustment Enhancement - Increase/Decrease Toggle

## Overview
Enhanced the Inventory Adjustment form with an intuitive Increase/Decrease toggle and quantity input, making it more user-friendly and operational.

## Changes Made

### 1. Form Updates (core/forms.py)

#### Added new fields:
- **adjustment_type**: Radio button field with "Increase Stock" and "Decrease Stock" options
- **quantity**: Positive integer input field (min value: 1)

#### Removed:
- `quantity_change` field from form (now computed internally)

#### Key Features:
- Custom `__init__` method populates active products
- `save()` method converts adjustment_type + quantity into signed quantity_change
  - If "increase": `quantity_change = quantity`
  - If "decrease": `quantity_change = -quantity`
- Form validation ensures quantity is positive and non-zero

### 2. Template Updates (templates/dealer/inventory_adjustment.html)

#### Visual Changes:
- **Adjustment Type**: Two radio button options with hover effects
  - "Increase Stock" (default selected)
  - "Decrease Stock"
- **Quantity**: Single input field with "units" label
- Real-time projected stock calculation based on selected type

#### Form Elements:
```
Product Selection
↓
Adjustment Type (Increase/Decrease radio buttons)
↓
Quantity (positive integer only)
↓
Reason (dropdown)
↓
Notes (optional textarea)
```

### 3. JavaScript Enhancements

#### Real-time Validation:
- Monitors product selection, adjustment type, quantity, and reason
- Calculates projected stock based on:
  - Current stock from database
  - Selected adjustment type (increase/decrease)
  - Entered quantity
- Shows warning if adjustment would result in negative stock
- Disables Apply button if:
  - No product selected
  - Quantity is empty, zero, or negative
  - No reason selected
  - Projected stock would be negative

#### Functions:
- `getAdjustmentType()`: Returns currently selected adjustment type
- `computeProjected()`: Calculates and displays projected stock
- `fetchProductInfo()`: Loads current stock from API

## User Experience Improvements

✓ Clear, intuitive increase/decrease selection
✓ Prevents accidental negative stock adjustments
✓ Real-time feedback on projected stock
✓ Visual warnings for invalid adjustments
✓ Cannot submit form with incomplete data
✓ Quantity field only accepts positive numbers

## How to Use

1. Navigate to Inventory → Inventory Adjustment
2. Select a product from dropdown
3. Choose "Increase Stock" or "Decrease Stock"
4. Enter quantity to adjust
5. Select reason for adjustment (Damage, Theft, Expired, etc.)
6. (Optional) Add notes
7. Click "Apply Adjustment"

## Technical Details

### Form Conversion Logic
The form handles the conversion transparently:
```python
# User selects: Increase, Quantity = 10
# Result: quantity_change = 10

# User selects: Decrease, Quantity = 5
# Result: quantity_change = -5
```

### Database Impact
The `InventoryAdjustment.save()` model method:
- Updates product.current_stock by quantity_change amount
- Creates a StockMovement record for audit trail
- Triggers only when adjustment is first saved

## Validation Rules

1. **Product**: Must be selected and active
2. **Adjustment Type**: Must choose increase or decrease
3. **Quantity**: Must be positive integer (>0)
4. **Reason**: Must select from predefined options
5. **Negative Stock**: Cannot result in negative stock

## Benefits

- More intuitive than entering positive/negative numbers
- Clear visual indication of whether adding or removing stock
- Prevents common mistakes (negative stock)
- Maintains full audit trail
- Real-time feedback improves user confidence
