# Customer Order Cancellation - Testing Checklist

## Pre-Testing Setup
- [ ] Start Django development server
- [ ] Log in as test customer
- [ ] Have at least one pending order (create if needed)
- [ ] Have orders with other statuses for negative testing

## Core Functionality Tests

### Test 1: Cancel Button Visibility
**Objective**: Verify cancel button only shows for pending orders
- [ ] Navigate to pending order detail
- [ ] **PASS**: Red "Cancel Order" button is visible
- [ ] Navigate to out_for_delivery order
- [ ] **PASS**: Cancel button is NOT visible
- [ ] Navigate to delivered order
- [ ] **PASS**: Cancel button is NOT visible
- [ ] Navigate to cancelled order
- [ ] **PASS**: Cancel button is NOT visible

### Test 2: Modal Opens Correctly
**Objective**: Test cancellation modal dialog
- [ ] Click "Cancel Order" button on pending order
- [ ] **PASS**: Modal dialog opens smoothly
- [ ] **PASS**: Modal shows all required elements:
  - [ ] Title: "Cancel Order"
  - [ ] Warning message
  - [ ] Order summary (ID, product, qty, amount)
  - [ ] Cancellation reason textarea
  - [ ] "Keep Order" button
  - [ ] "Yes, Cancel Order" button
  - [ ] Close button (X)

### Test 3: Modal Close Functions
**Objective**: Test modal can be closed without action
- [ ] Open cancellation modal
- [ ] Click "Keep Order" button
- [ ] **PASS**: Modal closes without changes
- [ ] Open modal again
- [ ] Click X (close button)
- [ ] **PASS**: Modal closes without changes
- [ ] Check order status unchanged

### Test 4: Successful Cancellation with Reason
**Objective**: Cancel order with cancellation reason provided
- [ ] Open pending order detail
- [ ] Click "Cancel Order"
- [ ] Type in reason: "Changed my mind about this order"
- [ ] Click "Yes, Cancel Order"
- [ ] **PASS**: Page reloads/updates
- [ ] **PASS**: Order status changed to "Cancelled"
- [ ] **PASS**: Status badge shows "Order Cancelled" (red)
- [ ] **PASS**: Cancellation reason displays in box
- [ ] **PASS**: Cancellation timestamp shows
- [ ] **PASS**: Success message appears

### Test 5: Successful Cancellation without Reason
**Objective**: Cancel order without providing reason
- [ ] Open another pending order
- [ ] Click "Cancel Order"
- [ ] Leave reason blank (no text)
- [ ] Click "Yes, Cancel Order"
- [ ] **PASS**: Order cancels successfully
- [ ] **PASS**: Default reason saved (or empty)
- [ ] **PASS**: All status updates show

### Test 6: Stock Release After Cancellation
**Objective**: Verify reserved stock is released
- [ ] Before cancellation: Check product stock levels
- [ ] Note reserved stock amount
- [ ] Cancel an order with quantity 2
- [ ] After cancellation: Check product stock
- [ ] **PASS**: Reserved stock decreased by 2
- [ ] **PASS**: Available stock increased

### Test 7: Order History Shows Cancellation
**Objective**: Verify cancelled order appears in history correctly
- [ ] Go to Order History
- [ ] Find the cancelled order you just created
- [ ] **PASS**: Status badge shows "Cancelled" (red)
- [ ] **PASS**: Cancellation notice box visible
- [ ] **PASS**: "This order has been cancelled" message shows

### Test 8: Notification Created
**Objective**: Verify customer notification is created
- [ ] After cancellation, go to Notifications
- [ ] **PASS**: New notification appears
- [ ] **PASS**: Type is "Order Cancelled"
- [ ] **PASS**: Title includes order ID
- [ ] **PASS**: Message mentions the product

### Test 9: Order Detail Shows Cancellation Info
**Objective**: Verify full order detail displays cancellation
- [ ] From order history, click cancelled order
- [ ] Go to Order Detail page
- [ ] **PASS**: Status shows "Cancelled"
- [ ] **PASS**: Cancellation reason displays
- [ ] **PASS**: Cancellation timestamp shows
- [ ] **PASS**: "Order Cancelled" badge visible
- [ ] **PASS**: Cancel button is gone

### Test 10: Cannot Cancel Non-Pending Orders
**Objective**: Verify system prevents invalid cancellations
- [ ] Try to manually POST to cancel API for out_for_delivery order
- [ ] **PASS**: Error message appears
- [ ] **PASS**: Order status unchanged
- [ ] Repeat for delivered order
- [ ] **PASS**: Same protection works

## Security & Validation Tests

### Test 11: CSRF Protection
**Objective**: Verify CSRF token requirement
- [ ] Open Network Developer Tools
- [ ] Monitor POST request when cancelling
- [ ] **PASS**: CSRF token in request body
- [ ] **PASS**: Form has {% csrf_token %} tag

### Test 12: Authentication Required
**Objective**: Verify cancellation requires login
- [ ] Log out
- [ ] Try to access cancel endpoint manually
- [ ] **PASS**: Redirected to login page

### Test 13: Customer Ownership Check
**Objective**: Verify customer can only cancel own orders
- [ ] Log in as customer A
- [ ] Get customer B's order ID
- [ ] Try to cancel customer B's order
- [ ] **PASS**: 404 error or permission denied

### Test 14: Input Sanitization
**Objective**: Test reason textarea input validation
- [ ] Try to input very long text (>500 chars)
- [ ] **PASS**: Text limited to 500 characters
- [ ] Try to input special characters: `<script>alert('xss')</script>`
- [ ] **PASS**: Text accepted but cleaned on display
- [ ] Try to input SQL: `'; DROP TABLE Orders; --`
- [ ] **PASS**: Treated as literal text

### Test 15: Transaction Atomicity
**Objective**: Verify all-or-nothing cancellation
- [ ] Monitor database during cancellation
- [ ] **PASS**: Either all changes applied or none
- [ ] No partial updates should occur

## User Experience Tests

### Test 16: Mobile Responsiveness
**Objective**: Test on mobile device/viewport
- [ ] Resize browser to mobile width (375px)
- [ ] Open order detail page
- [ ] Click cancel button
- [ ] **PASS**: Modal displays properly on mobile
- [ ] **PASS**: Modal text readable
- [ ] **PASS**: Buttons clickable on touch

### Test 17: Loading States
**Objective**: Verify UI feedback during submission
- [ ] Open modal and submit
- [ ] **PASS**: Form shows loading state (if implemented)
- [ ] **PASS**: Buttons disabled during submission
- [ ] **PASS**: No duplicate submissions possible

### Test 18: Error Messages
**Objective**: Test error handling and messages
- [ ] Artificially cause an error (e.g., DB down)
- [ ] Try to cancel order
- [ ] **PASS**: Clear error message displayed
- [ ] **PASS**: Order status unchanged
- [ ] **PASS**: User informed of issue

### Test 19: Success Messages
**Objective**: Verify user feedback on success
- [ ] Cancel an order successfully
- [ ] **PASS**: "Order cancelled successfully!" message appears
- [ ] **PASS**: Message auto-dismisses (if using dismissible alerts)
- [ ] **PASS**: No error messages visible

## Browser Compatibility Tests

### Test 20: Chrome/Chromium
- [ ] Open order detail page in Chrome
- [ ] Test all functionality
- [ ] **PASS**: Modal works
- [ ] **PASS**: Cancellation works
- [ ] **PASS**: No console errors

### Test 21: Firefox
- [ ] Open order detail page in Firefox
- [ ] Test all functionality
- [ ] **PASS**: Modal works
- [ ] **PASS**: Cancellation works
- [ ] **PASS**: No console errors

### Test 22: Safari
- [ ] Open order detail page in Safari
- [ ] Test all functionality
- [ ] **PASS**: Modal works (HTML5 dialog)
- [ ] **PASS**: Cancellation works
- [ ] **PASS**: No console errors

### Test 23: Edge
- [ ] Open order detail page in Edge
- [ ] Test all functionality
- [ ] **PASS**: All features work

## Performance Tests

### Test 24: Page Load Time
**Objective**: Verify cancellation feature doesn't slow page load
- [ ] Load order detail page
- [ ] Check Network tab
- [ ] **PASS**: Page loads in < 2 seconds
- [ ] **PASS**: No additional slow requests

### Test 25: Modal Response Time
**Objective**: Verify modal opens quickly
- [ ] Click "Cancel Order" button
- [ ] **PASS**: Modal appears instantly (< 200ms)

### Test 26: Cancellation Processing Time
**Objective**: Verify cancellation completes quickly
- [ ] Submit cancellation
- [ ] **PASS**: Page updates within 1-2 seconds

## Edge Cases & Stress Tests

### Test 27: Double Submission
**Objective**: Prevent accidental double cancellation
- [ ] Open modal
- [ ] Rapidly click "Yes, Cancel" twice
- [ ] **PASS**: Only one cancellation processed
- [ ] **PASS**: Second attempt fails gracefully

### Test 28: Network Interruption
**Objective**: Handle network errors
- [ ] Start cancellation
- [ ] Disconnect network during submission
- [ ] **PASS**: Error message shown
- [ ] **PASS**: Order not partially updated
- [ ] Reconnect and retry
- [ ] **PASS**: Cancellation works

### Test 29: Concurrent Cancellations
**Objective**: Handle race conditions
- [ ] Open same order in two tabs
- [ ] Cancel in both simultaneously
- [ ] **PASS**: First succeeds, second fails gracefully
- [ ] **PASS**: Database stays consistent

### Test 30: Very Long Reason Text
**Objective**: Handle maximum input
- [ ] Paste 500 character reason (at limit)
- [ ] Try to add one more character
- [ ] **PASS**: Text limited to exactly 500 chars
- [ ] **PASS**: No error, gracefully handled

## Integration Tests

### Test 31: Inventory Management Integration
**Objective**: Verify stock system works correctly
- [ ] Check product page before cancellation
- [ ] Cancel order (qty: 5)
- [ ] Check product page after
- [ ] **PASS**: Stock numbers updated correctly
- [ ] **PASS**: Available stock reflects release

### Test 32: Notification System Integration
**Objective**: Verify notification creation
- [ ] Clear all notifications
- [ ] Cancel an order
- [ ] **PASS**: New notification appears in bell
- [ ] **PASS**: Notification content is correct
- [ ] **PASS**: Can mark as read

### Test 33: Order History Integration
**Objective**: Verify history page works with cancellations
- [ ] Apply "Cancelled" filter
- [ ] **PASS**: Only cancelled orders show
- [ ] Apply "Pending" filter
- [ ] **PASS**: Cancelled order not in list
- [ ] Remove filters
- [ ] **PASS**: Both show together

### Test 34: Dashboard Integration
**Objective**: Verify dashboard updates
- [ ] Go to customer dashboard
- [ ] See recent orders with cancelled status
- [ ] **PASS**: Displays correctly
- [ ] **PASS**: Shows cancellation timestamp

## Data Integrity Tests

### Test 35: Database Consistency
**Objective**: Verify database records are correct
- [ ] Query cancelled order in admin
- [ ] **PASS**: status = 'cancelled'
- [ ] **PASS**: cancelled_by = current user
- [ ] **PASS**: cancelled_at has timestamp
- [ ] **PASS**: cancellation_reason populated

### Test 36: Audit Trail
**Objective**: Verify cancellation is logged
- [ ] Check order record
- [ ] **PASS**: Cancellation timestamp accurate
- [ ] **PASS**: Cancelled_by field correct
- [ ] **PASS**: Can trace action to specific user

### Test 37: Stock Movement Log
**Objective**: Verify inventory audit trail
- [ ] Go to Stock Movements
- [ ] Filter for cancelled order
- [ ] **PASS**: Cancellation stock release logged
- [ ] **PASS**: Correct quantity released

## Admin Tests (Optional)

### Test 38: Admin Can View Cancellation
**Objective**: Verify admin can see cancellation info
- [ ] Log in as admin/dealer
- [ ] View cancelled order
- [ ] **PASS**: Cancellation info displays
- [ ] **PASS**: Can see cancellation reason

### Test 39: Admin Cannot Cancel Delivered Orders
**Objective**: Verify same rules apply to staff
- [ ] Log in as dealer
- [ ] Try to cancel delivered order
- [ ] **PASS**: Not allowed (if rules apply to staff too)

## Final Checklist

### Before Going Live
- [ ] All 39 tests passed
- [ ] No console errors in browser
- [ ] No server errors in logs
- [ ] Database integrity verified
- [ ] Performance acceptable
- [ ] Mobile works properly
- [ ] All browsers tested
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Security verified

### Post-Deployment
- [ ] Monitor error logs
- [ ] Check cancellation success rate
- [ ] Verify stock integrity
- [ ] Monitor notification delivery
- [ ] Gather user feedback
- [ ] Check performance metrics

## Test Data Requirements

For comprehensive testing, ensure you have:
- [ ] 1 pending order
- [ ] 1 out_for_delivery order  
- [ ] 1 delivered order
- [ ] 1 cancelled order
- [ ] Orders from multiple products
- [ ] Orders with different quantities
- [ ] Orders with and without notes

## Notes

**Date Tested**: _______________  
**Tested By**: _______________  
**Browser/Device**: _______________  
**Issues Found**: _______________  
**Resolution**: _______________  
