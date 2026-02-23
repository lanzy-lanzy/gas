# Bulk Operations Debug Guide

## Problem Status ✅ BACKEND WORKING

The backend bulk operations are **working perfectly**! Our test script confirmed:
- ✅ Authentication works (dealer user is staff)
- ✅ Orders are processed successfully  
- ✅ Status updates correctly (pending → out_for_delivery)
- ✅ JSON response is returned properly

**The issue is in the frontend JavaScript.**

## Debug Steps

### 1. Open Browser Console
1. Navigate to Order Management page
2. Open Developer Tools (F12)
3. Go to Console tab
4. Clear any existing logs

### 2. Test Component Access
Run these commands in the browser console:

```javascript
// Check if component is available
console.log('Component available:', !!window.orderManagementComponent);

// Check component state
if (window.orderManagementComponent) {
    window.orderManagementComponent.testBulkOperation();
}
```

### 3. Test Select All Functionality
1. Click the select-all checkbox in the table header
2. Check console for any errors
3. Verify that orders are selected:

```javascript
// Check selected orders
console.log('Selected orders:', window.orderManagementComponent?.selectedOrders);

// Check checkboxes
document.querySelectorAll('input[name="order_checkbox"]').forEach(cb => {
    console.log('Checkbox', cb.value, 'checked:', cb.checked);
});
```

### 4. Test Bulk Operation Manually
```javascript
// Manually trigger bulk operation
if (window.orderManagementComponent) {
    // First select some orders
    window.orderManagementComponent.selectedOrders = [14, 15]; // Use actual order IDs
    
    // Then test bulk operation
    window.orderManagementComponent.bulkOperation('mark_out_for_delivery');
}
```

### 5. Check Network Tab
1. Open Network tab in Developer Tools
2. Try to perform a bulk operation
3. Look for the POST request to `/dealer/orders/bulk/`
4. Check if the request is being sent
5. Check the response

## Common Issues to Check

### Issue 1: Component Not Initialized
**Symptoms**: `window.orderManagementComponent` is undefined
**Solution**: Check if Alpine.js is loaded and component is initialized

### Issue 2: CSRF Token Missing
**Symptoms**: 403 Forbidden error
**Check**: 
```javascript
console.log('CSRF token:', document.querySelector('[name=csrfmiddlewaretoken]')?.value);
```

### Issue 3: No Orders Selected
**Symptoms**: "No orders selected" toast message
**Check**: 
```javascript
console.log('Selected orders count:', window.orderManagementComponent?.selectedOrders?.length);
```

### Issue 4: Fetch Request Fails
**Symptoms**: Network error or HTTP error
**Check**: Look in Network tab for failed requests

## Expected Console Output

When working correctly, you should see:
```
Sending bulk operation: mark_out_for_delivery for orders: [14, 15]
CSRF token: [some-token-value]
Response received: 200 OK
Success response: {success: true, message: "Successfully processed 2 order(s).", ...}
```

## Quick Fixes

### Fix 1: Reinitialize Component
```javascript
// If component is missing, try to reinitialize
if (!window.orderManagementComponent && typeof orderManagement === 'function') {
    window.orderManagementComponent = orderManagement();
}
```

### Fix 2: Manual CSRF Token
```javascript
// If CSRF token is missing
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                  document.querySelector('meta[name=csrf-token]')?.content;
console.log('CSRF token found:', !!csrfToken);
```

### Fix 3: Force Select Orders
```javascript
// Manually select orders for testing
const checkboxes = document.querySelectorAll('input[name="order_checkbox"]');
checkboxes.forEach(cb => {
    cb.checked = true;
    const orderId = parseInt(cb.value);
    if (!window.orderManagementComponent.selectedOrders.includes(orderId)) {
        window.orderManagementComponent.selectedOrders.push(orderId);
    }
});
```

## Test Sequence

1. **Load Page**: Navigate to Order Management
2. **Check Component**: Run `window.orderManagementComponent.testBulkOperation()`
3. **Select Orders**: Click select-all checkbox or individual checkboxes
4. **Verify Selection**: Check that `selectedOrders` array is populated
5. **Test Operation**: Click a bulk operation button
6. **Check Console**: Look for success/error messages
7. **Check Network**: Verify POST request was sent
8. **Check Result**: Verify orders were updated

## Next Steps Based on Results

### If Component is Missing:
- Check if Alpine.js is loaded
- Check if `orderManagement()` function exists
- Check for JavaScript errors preventing initialization

### If CSRF Token is Missing:
- Check if Django's CSRF middleware is enabled
- Check if template includes `{% csrf_token %}`
- Check if meta tag with CSRF token exists

### If Request Fails:
- Check user authentication (must be staff/dealer)
- Check URL routing
- Check Django logs for backend errors

### If Orders Not Selected:
- Check if checkboxes are properly bound to Alpine.js
- Check if `handleSelectAllChange` and `handleOrderCheckboxChange` are called
- Check if global component reference is working

Run through these debug steps and let me know what you find in the console!
