# Customer Order Cancellation - Quick Start Guide

## What's New
Customers can now cancel their pending orders before they are processed or shipped.

## How It Works for Customers

### 1. Navigate to Order Details
- Click on an order in "Order History"
- Or go to Dashboard → View Recent Orders → Click order

### 2. Cancel Pending Order
**If order status is "Pending":**
- A red "Cancel Order" button appears
- Click it to open confirmation modal

### 3. Confirm Cancellation
In the modal dialog:
1. Review the warning message
2. See order summary (amount, product, quantity)
3. *(Optional)* Type cancellation reason
4. Click "Yes, Cancel Order" to confirm

### 4. See Result
- Page updates immediately
- Status changes to "Cancelled"
- Cancellation reason displays (if provided)
- Success message shown

## What Happens When Order is Cancelled

✅ **Order Status** → "Cancelled"  
✅ **Stock** → Released back to inventory  
✅ **Notification** → Customer receives notification  
✅ **Record** → Cancellation logged with timestamp  

## When CAN'T Orders Be Cancelled

❌ Order is "Out for Delivery" → Too late, already dispatched  
❌ Order is "Delivered" → Already completed  
❌ Order is "Cancelled" → Already cancelled  

## User Interface

### Order Detail Page
```
Order #123 - Pending
[Cancel Order] button (red, visible only for pending)
```

### Cancellation Modal
```
┌─────────────────────────────────┐
│ Cancel Order            [✕]     │
├─────────────────────────────────┤
│ ⚠️ Warning: Sure to cancel?     │
│                                  │
│ Order Summary:                   │
│ • Order #: 123                   │
│ • Product: LPG 11kg             │
│ • Quantity: 2                    │
│ • Amount: ₱500.00                │
│                                  │
│ Reason (optional):               │
│ [textarea...]                    │
│                                  │
│ [Keep Order] [Yes, Cancel]      │
└─────────────────────────────────┘
```

### After Cancellation
```
Order #123 - Cancelled
⚠️ Order Cancelled
   Cancelled on Feb 15, 2024 10:30 AM
   
Cancellation Reason:
"Changed my mind about the order"
```

## Order History View
- Cancelled orders show red badge: "Cancelled"
- Shows cancellation timestamp
- Still viewable and filterable

## Technical Details

### API Endpoint
```
POST /customer/order/<order_id>/cancel/
```

### Required Parameters
- `order_id`: Order to cancel (in URL)
- `cancellation_reason`: Optional (in form body)

### Response
- Success: Order status updated, redirect or HTMX update
- Error: Error message displayed, no changes made

## Features & Safety

### Data Safety
✅ Transaction-based - All or nothing  
✅ Atomic operations - No partial updates  
✅ Stock validation - Prevents inventory errors  
✅ Ownership check - Can't cancel others' orders  

### User Experience
✅ Confirmation modal - Prevents accidental cancellation  
✅ Order summary - Review before confirming  
✅ Optional reason - Feedback for improvements  
✅ Real-time update - Immediate visual feedback  

### Security
✅ Login required - Must be authenticated  
✅ CSRF protected - Safe form submission  
✅ Permission verified - Customer ownership validated  
✅ Input sanitized - Reason text cleaned  

## Common Scenarios

### Scenario 1: Changed Mind
Customer realizes they don't need the order immediately
- Cancel before it ships
- Stock released for other customers
- System updated in real-time

### Scenario 2: Made Duplicate Order
Customer accidentally placed order twice
- Cancel one of the duplicate orders
- No penalty or fees
- Stock becomes available again

### Scenario 3: Better Offer Found
Customer found better price elsewhere
- Cancel pending order
- Try new supplier
- Order history shows cancellation record

## If Something Goes Wrong

### Common Issues

**Q: I can't see the Cancel button**
- A: Order might already be out for delivery or delivered
- Check the order status at the top

**Q: Cancellation modal won't submit**
- A: Refresh the page and try again
- Check browser console for errors

**Q: Stock wasn't released**
- A: Contact admin - rare edge case
- System should have released stock automatically

## Integration with Other Features

### Notifications
- Cancellation creates automatic notification
- Appears in notification bell
- Customers can mark as read

### Order History
- Cancelled orders remain in history
- Can filter by status: "Cancelled"
- Shows cancellation details

### Inventory System
- Releases reserved stock immediately
- Updates stock movements log
- Maintains audit trail

## Admin/Dealer View

Dealers can see:
- Customer cancelled orders
- Cancellation timestamps
- Customer-provided reasons
- Stock impact

## Future Enhancements

🔄 **Planned Features:**
- Automatic refund processing
- Email confirmation of cancellation
- Bulk cancellation dashboard
- Cancellation analytics
- Reorder recommendations

## Questions?

For more detailed information, see:
- `CUSTOMER_ORDER_CANCELLATION_IMPLEMENTATION.md` - Technical details
- `core/models.py` - Order model structure
- `core/views.py` - Cancellation logic
- `templates/customer/order_detail.html` - UI implementation
