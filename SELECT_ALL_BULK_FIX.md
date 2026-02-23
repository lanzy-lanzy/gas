# Select All Bulk Functionality Fix

## Problem Identified ✅

After removing Unpoly, the "select all" checkbox functionality was broken because:

1. **Alpine.js Scope Issues**: The table partials (`order_table_partial.html` and `order_row_partial.html`) were using `$parent` references that don't work correctly when content is loaded via HTMX
2. **Component Access**: The individual checkboxes couldn't access the main `orderManagement()` component methods
3. **State Synchronization**: The select-all checkbox wasn't properly synchronized with individual checkbox states

## Root Cause Analysis

### Before Fix:
```html
<!-- In order_table_partial.html -->
<input type="checkbox" @change="$event.target.checked ? $parent.selectAllOrders() : $parent.clearSelection()">

<!-- In order_row_partial.html -->
<input type="checkbox" @change="$parent.toggleOrderSelection({{ order.id }})"
       :checked="$parent.selectedOrders.includes({{ order.id }})">
```

**Problem**: `$parent` references don't work when table content is loaded via HTMX because the Alpine.js component scope is lost.

## Solution Implemented ✅

### 1. Global Component Reference
Made the main Alpine.js component globally accessible:

```javascript
// In orderManagement() component init()
window.orderManagementComponent = this;
```

### 2. Updated Table Partials
Changed the partials to use the global component reference:

```html
<!-- In order_table_partial.html -->
<input type="checkbox" @change="window.orderManagementComponent?.handleSelectAllChange($event)">

<!-- In order_row_partial.html -->
<input type="checkbox" @change="window.orderManagementComponent?.handleOrderCheckboxChange({{ order.id }}, $event)"
       :checked="window.orderManagementComponent?.isOrderSelected({{ order.id }}) || false">
```

### 3. Added Helper Methods
Created specific methods for table partial interactions:

```javascript
handleSelectAllChange(event) {
    console.log('Select all change:', event.target.checked);
    if (event.target.checked) {
        this.selectAllOrders();
    } else {
        this.clearSelection();
    }
},

handleOrderCheckboxChange(orderId, event) {
    console.log('Order checkbox change:', orderId, event.target.checked);
    this.toggleOrderSelection(orderId);
},

isOrderSelected(orderId) {
    const selected = this.selectedOrders.includes(orderId);
    console.log('Is order selected:', orderId, selected);
    return selected;
},
```

### 4. Enhanced HTMX Event Handling
Ensured the global component reference is restored after table refreshes:

```javascript
document.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'order-table-container') {
        // Restore global reference
        window.orderManagementComponent = orderMgmt;
        
        // Restore checkbox states
        setTimeout(() => {
            orderMgmt.restoreCheckboxStates();
        }, 100);
    }
});
```

## Files Modified

1. **`templates/dealer/order_management.html`**
   - Added global component reference in `init()`
   - Added helper methods for table partials
   - Enhanced HTMX event handling
   - Added debugging to helper methods

2. **`templates/dealer/order_table_partial.html`**
   - Changed select-all checkbox to use global component reference
   - Updated `@change` handler

3. **`templates/dealer/order_row_partial.html`**
   - Changed individual checkboxes to use global component reference
   - Updated `@change` and `:checked` bindings

## Testing Instructions

### 1. Basic Functionality Test
1. Navigate to Order Management page
2. Click the select-all checkbox in the table header
3. **Expected**: All individual order checkboxes should be checked
4. **Expected**: Bulk operations panel should appear showing selected count
5. Click select-all checkbox again to uncheck
6. **Expected**: All checkboxes should be unchecked, bulk panel should disappear

### 2. Individual Selection Test
1. Check individual order checkboxes one by one
2. **Expected**: Select-all checkbox should show indeterminate state (partially filled)
3. Check all orders individually
4. **Expected**: Select-all checkbox should become fully checked
5. Uncheck one order
6. **Expected**: Select-all checkbox should return to indeterminate state

### 3. Bulk Operations Test
1. Select multiple orders using select-all or individual checkboxes
2. Click a bulk operation button (e.g., "Mark as Out for Delivery")
3. **Expected**: Operation should execute successfully
4. **Expected**: Selection should be cleared after operation
5. **Expected**: Table should refresh showing updated statuses

### 4. Keyboard Shortcuts Test
1. Press `Ctrl+A`
2. **Expected**: All orders should be selected
3. Press `Esc`
4. **Expected**: All selections should be cleared

### 5. Table Refresh Test
1. Select some orders
2. Use the refresh button or wait for auto-refresh
3. **Expected**: Selected orders should remain selected after table refresh
4. **Expected**: Select-all checkbox state should be preserved

## Debug Commands

### Check Component Status
```javascript
debugOrderManagement()
```

### Manual Component Test
```javascript
// Test select all
window.orderManagementComponent.selectAllOrders()

// Test clear selection
window.orderManagementComponent.clearSelection()

// Check selected orders
console.log(window.orderManagementComponent.selectedOrders)
```

### Check Checkbox States
```javascript
// Check individual checkboxes
document.querySelectorAll('input[name="order_checkbox"]').forEach(cb => {
    console.log('Checkbox', cb.value, 'checked:', cb.checked);
});

// Check select-all checkbox
const selectAll = document.querySelector('thead input[type="checkbox"]');
console.log('Select all - checked:', selectAll.checked, 'indeterminate:', selectAll.indeterminate);
```

## Expected Results

✅ **Select-all checkbox works immediately**  
✅ **Individual checkboxes sync with select-all state**  
✅ **Bulk operations work with selected orders**  
✅ **Checkbox states preserved during table refreshes**  
✅ **Keyboard shortcuts function correctly**  
✅ **No JavaScript errors in console**  
✅ **Proper indeterminate state handling**

## Troubleshooting

### If select-all doesn't work:
1. Check browser console for errors
2. Run `debugOrderManagement()` to verify component is available
3. Check that `window.orderManagementComponent` exists

### If checkboxes don't stay selected:
1. Verify HTMX event handling is working
2. Check that `restoreCheckboxStates()` is being called
3. Ensure global component reference is restored after HTMX swaps

### If bulk operations don't work:
1. Verify orders are actually selected (`window.orderManagementComponent.selectedOrders`)
2. Check network tab for failed requests
3. Verify CSRF tokens are being sent correctly

The fix ensures that the select-all functionality works consistently regardless of how the table content is loaded (initial page load or HTMX refresh), providing a seamless bulk selection experience.
