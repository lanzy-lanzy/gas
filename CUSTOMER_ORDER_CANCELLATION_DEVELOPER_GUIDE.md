# Customer Order Cancellation - Developer Guide

## Overview
This guide provides technical details for developers maintaining or extending the order cancellation feature.

## Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  order_detail.html + order_rows_partial.html                │
│  - Cancel button                                            │
│  - Modal dialog                                             │
│  - Status display                                           │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /customer/order/{id}/cancel/
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      VIEWS LAYER                             │
│  views.py → cancel_order()                                  │
│  - Validation                                               │
│  - Transaction management                                  │
│  - Error handling                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│ ORDER MODEL  │  │ PRODUCT MODEL  │  │NOTIFICATION │
│              │  │                │  │ MODEL        │
│- Update      │  │- Release Stock │  │              │
│  Status      │  │                │  │- Create      │
│- Record      │  │                │  │  Order       │
│  Details     │  │                │  │  Cancelled   │
└──────────────┘  └────────────────┘  └──────────────┘
```

## Code Structure

### View Function: `cancel_order()`

**Location**: `core/views.py` (lines 875-927)

```python
@login_required
@require_http_methods(["POST"])
@csrf_protect
def cancel_order(request, order_id):
    """
    Cancel a customer order if it's still pending
    """
    # 1. Get order with security check
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # 2. Get cancellation reason from form
    cancellation_reason = request.POST.get('cancellation_reason', 'Customer requested cancellation')
    
    # 3. Validate order can be cancelled
    if not order.can_be_cancelled:
        messages.error(request, f'Cannot cancel order. Current status: {order.get_status_display()}')
        return redirect('core:order_detail', order_id=order.id)
    
    # 4. Transaction-safe updates
    try:
        with transaction.atomic():
            # Release stock
            order.product.release_stock(order.quantity)
            
            # Update order
            order.status = 'cancelled'
            order.cancellation_reason = cancellation_reason
            order.cancelled_by = request.user
            order.cancelled_at = timezone.now()
            order.save()
            
            # Create notification
            Notification.objects.create(...)
            
            messages.success(request, 'Order cancelled successfully!')
    except Exception as e:
        messages.error(request, f'Error cancelling order: {str(e)}')
        return redirect('core:order_detail', order_id=order.id)
    
    # 5. Return response
    if request.headers.get('HX-Request'):
        # HTMX response
        ...
    return redirect('core:order_detail', order_id=order.id)
```

### Model Properties

**Order.can_be_cancelled**
```python
@property
def can_be_cancelled(self):
    """Check if order can still be cancelled"""
    return self.status in ['pending']
```

**Product.release_stock()**
```python
def release_stock(self, quantity):
    """Release reserved stock"""
    self.reserved_stock = max(0, self.reserved_stock - quantity)
    self.save()
```

## Data Flow

### Request → Response Flow

```
1. User clicks "Cancel Order" button
   ↓
2. Modal dialog opens
   ↓
3. User fills (optional) reason field
   ↓
4. User clicks "Yes, Cancel Order"
   ↓
5. Form POSTs to /customer/order/{id}/cancel/
   ↓
6. Django processes request:
   a. Validates CSRF token
   b. Checks user is authenticated
   c. Looks up order (with customer check)
   d. Validates status is 'pending'
   e. Starts database transaction
   f. Releases reserved stock
   g. Updates order fields
   h. Creates notification
   g. Commits transaction
   h. Renders response
   ↓
7. Response sent to browser:
   - Success message
   - Updated order status
   - Modal closed
   - Page refreshed
```

## Database Schema

### Order Model Fields Used

```python
class Order(models.Model):
    # Existing fields (not changed)
    status = CharField(
        choices=['pending', 'out_for_delivery', 'delivered', 'cancelled'],
        default='pending'
    )
    
    # Cancellation fields (already existed)
    cancellation_reason = TextField(blank=True)
    cancelled_by = ForeignKey(User, null=True, blank=True, related_name='cancelled_orders')
    cancelled_at = DateTimeField(null=True, blank=True)
```

### No Migrations Required
- All fields already exist in model
- Database schema unchanged
- Backward compatible

## Transaction Management

### Atomic Block Usage
```python
with transaction.atomic():
    # All operations here are atomic
    # If ANY operation fails, ALL are rolled back
    order.product.release_stock(order.quantity)
    order.status = 'cancelled'
    order.save()
    Notification.objects.create(...)
```

**Why?** Prevents scenarios where:
- Stock released but order not updated
- Notification sent but order still pending
- Partial data corruption

## Error Handling

### Validation Chain
```
1. Order exists → 404 if not found
2. User owns order → 404 if not owner
3. Status is 'pending' → Error message if not
4. Stock release → Fails gracefully
5. Database save → Transaction rollback if fails
6. Notification create → Warning logged but doesn't block
```

### Exception Handling
```python
try:
    with transaction.atomic():
        # All operations
except Exception as e:
    # Log error
    messages.error(request, f'Error cancelling order: {str(e)}')
    # Redirect without changes
    return redirect('core:order_detail', order_id=order.id)
```

## HTMX Integration

### Supporting Partial Page Updates
```python
# Check if request is from HTMX
if request.headers.get('HX-Request'):
    # Return partial HTML for client-side swap
    context = {'order': order, 'progress_percentage': 0}
    return render(request, 'customer/order_detail_section.html', context)

# Otherwise full redirect
return redirect('core:order_detail', order_id=order.id)
```

### HTMX Headers Detected
- `HX-Request`: true when HTMX made request
- Used to optimize response (partial vs full page)

## URL Routing

### Route Definition
```python
# core/urls.py
path('customer/order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
```

### Named URL Usage in Template
```html
<form action="{% url 'core:cancel_order' order.id %}" method="POST">
```

### Reverse URL in Tests
```python
url = reverse('core:cancel_order', args=[order.id])
```

## Template Integration

### Form Implementation
```html
<form action="{% url 'core:cancel_order' order.id %}" method="POST" class="w-full">
    {% csrf_token %}
    <input type="hidden" name="order_id" value="{{ order.id }}">
    <textarea name="cancellation_reason" maxlength="500"></textarea>
    <button type="submit">Yes, Cancel Order</button>
</form>
```

### Key Elements
1. `{% csrf_token %}` - Security
2. `method="POST"` - Required for @require_http_methods
3. `name="cancellation_reason"` - Matches view.POST.get()
4. Modal `<dialog>` element - Native HTML5

## Security Implementation

### Decorator Stack
```python
@login_required  # Redirects to login if not authenticated
@require_http_methods(["POST"])  # Only accepts POST
@csrf_protect  # Validates CSRF token
def cancel_order(request, order_id):
    # Customer ownership check
    order = get_object_or_404(Order, id=order_id, customer=request.user)
```

### Authorization
```python
# Only customer who placed order can cancel it
get_object_or_404(Order, id=order_id, customer=request.user)
# Returns 404 to anyone else (including admins)
```

### Input Sanitization
```html
<!-- Textarea limited to 500 chars -->
<textarea maxlength="500"></textarea>

<!-- JavaScript backup -->
<script>
if (this.value.length > 500) {
    this.value = this.value.substring(0, 500);
}
</script>
```

## Testing Strategy

### Unit Tests (Example)
```python
def test_cancel_pending_order():
    order = Order.objects.create(..., status='pending')
    response = client.post(reverse('core:cancel_order', args=[order.id]))
    order.refresh_from_db()
    assert order.status == 'cancelled'

def test_cannot_cancel_delivered_order():
    order = Order.objects.create(..., status='delivered')
    response = client.post(reverse('core:cancel_order', args=[order.id]))
    order.refresh_from_db()
    assert order.status == 'delivered'  # Unchanged

def test_requires_authentication():
    response = client.post(reverse('core:cancel_order', args=[1]))
    assert response.status_code == 302  # Redirect to login
```

### Integration Tests
```python
def test_stock_released_on_cancellation():
    product = LPGProduct.objects.create(...)
    order = Order.objects.create(
        product=product,
        quantity=5,
        status='pending'
    )
    product.reserved_stock = 5
    product.save()
    
    client.post(reverse('core:cancel_order', args=[order.id]))
    
    product.refresh_from_db()
    assert product.reserved_stock == 0
```

## Performance Considerations

### Database Queries
```python
# Single query with select_related for customer
order = get_object_or_404(Order, id=order_id, customer=request.user)

# Single save (UPDATE)
order.save()

# Single create
Notification.objects.create(...)

# Total: ~3 database hits (optimal)
```

### Query Optimization
- No N+1 queries
- Minimal joins
- Uses primary key lookup (fast)
- Transaction ensures consistency

### Response Time
- Expected: < 500ms
- Processing: < 100ms
- Database: < 300ms
- Template rendering: < 100ms

## Common Extensions

### Adding Email Notification
```python
# In cancel_order() after status update:
from django.core.mail import send_mail

send_mail(
    subject=f'Order #{order.id} Cancelled',
    message=f'Your order has been cancelled...',
    from_email='noreply@prycegas.com',
    recipient_list=[order.customer.email],
)
```

### Adding Refund Processing
```python
# In cancel_order() after stock release:
if order.paid_via_card:
    refund_payment(order)  # Integration with payment gateway
```

### Adding Admin Approval
```python
# Change status to 'cancellation_requested'
order.status = 'cancellation_requested'
order.save()

# Create admin notification
# Wait for approval before completing cancellation
```

### Adding Time-Based Rules
```python
# Only allow cancellation within 1 hour of order
if timezone.now() - order.order_date > timedelta(hours=1):
    messages.error(request, 'Can only cancel within 1 hour')
    return redirect(...)
```

## Debugging Tips

### Enable Debug Logging
```python
import logging
logger = logging.getLogger(__name__)

# In cancel_order():
logger.info(f'Cancelling order {order.id} for user {request.user.id}')
logger.debug(f'Releasing stock: {order.quantity}')
```

### Check Database State
```python
# In Django shell
from core.models import Order
order = Order.objects.get(id=123)
print(f"Status: {order.status}")
print(f"Cancelled by: {order.cancelled_by}")
print(f"Cancelled at: {order.cancelled_at}")
print(f"Reason: {order.cancellation_reason}")
```

### Monitor Transactions
```python
# Enable query logging
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

## Troubleshooting

### Issue: Stock not released
```python
# Check reserved_stock field
product.refresh_from_db()
print(product.reserved_stock)

# Check release_stock() method logic
# Ensure max(0, ...) prevents negative
```

### Issue: Notification not created
```python
# Check if notification_type='order_cancelled' exists
Notification.objects.filter(order=order)

# Check if customer field is set
# Ensure order.customer is not None
```

### Issue: Status not updating
```python
# Check transaction committed
# Check status value is in STATUS_CHOICES
# Check .save() was called

order.refresh_from_db()  # Get from DB
print(order.status)  # Verify persisted
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2024 | Initial implementation |

## Maintenance Checklist

### Regular Tasks
- [ ] Monitor error logs weekly
- [ ] Check cancellation success rate monthly
- [ ] Review cancellation reasons quarterly
- [ ] Verify stock integrity monthly
- [ ] Update documentation as needed

### On Update
- [ ] Run full test suite
- [ ] Test in staging environment
- [ ] Verify no performance degradation
- [ ] Update version number
- [ ] Document changes

## Related Documentation
- `CUSTOMER_ORDER_CANCELLATION_IMPLEMENTATION.md` - Full technical details
- `CUSTOMER_ORDER_CANCELLATION_QUICK_START.md` - User guide
- `CUSTOMER_ORDER_CANCELLATION_TESTING_CHECKLIST.md` - QA procedures
- `CUSTOMER_ORDER_CANCELLATION_SUMMARY.md` - Implementation overview

## Questions?

For detailed information on specific components, refer to:
1. View implementation: `core/views.py`
2. Model properties: `core/models.py`
3. Template code: `templates/customer/`
4. URL routing: `core/urls.py`
5. Form handling: Django built-in CSRF and form processing
