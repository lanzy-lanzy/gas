# Developer Integration Guide - Multiple Products Order Feature

## Quick Start for Developers

### Prerequisites
- Django 3.0+
- Python 3.6+
- Modern browser with Fetch API

### Installation
No special installation needed. The feature is built into the existing codebase.

1. Ensure all files are deployed:
   - `templates/customer/place_order.html`
   - `core/views.py` (updated)
   - `core/urls.py` (updated)

2. No database migrations required

3. Test the feature at `/customer/order/`

## Code Structure

### Frontend Code Organization

```
place_order.html
├── Form section (unchanged)
├── Product selection
├── Add button
├── Cart display
├── Delivery options
└── JavaScript
    ├── Cart management
    ├── API calls
    ├── UI updates
    └── Form handling
```

### Backend Code Organization

```
views.py
├── place_order() - Main order handler
│   ├── Validation
│   ├── JSON parsing
│   ├── Cart processing
│   └── Order creation
│
└── get_product_details() - Product API
    ├── Product lookup
    ├── Stock check
    └── JSON response

urls.py
├── Existing routes
└── /get-product-details/ - New route
```

## Integration Points

### 1. View Integration

**File:** `core/views.py`

**Key Function - place_order():**
```python
@csrf_protect
@login_required
def place_order(request):
    # POST handler parses JSON cart items
    # Creates multiple Order records
    # Uses atomic transactions
    # Returns JSON response
```

**Key Function - get_product_details():**
```python
@login_required
def get_product_details(request):
    # GET handler for product info
    # Returns JSON with price, stock
    # Used by JavaScript to build cart
```

### 2. URL Integration

**File:** `core/urls.py`

```python
path('get-product-details/', get_product_details, name='get_product_details'),
```

### 3. Template Integration

**File:** `templates/customer/place_order.html`

```html
<!-- Cart display section -->
<div id="order-items">
    <div id="cart-items"><!-- Items rendered here --></div>
    <div id="cart-total"><!-- Total amount --></div>
</div>

<!-- Hidden input for cart data -->
<input type="hidden" id="cart-items-input" name="cart_items">

<!-- JavaScript functions -->
<script>
  function addProductToCart() { ... }
  function removeFromCart(index) { ... }
  function updateQuantity(index, qty) { ... }
  // ... more functions
</script>
```

## Data Flow Diagram

```
┌─────────────┐
│  Browser    │
└─────────────┘
      │
      │ 1. Click "Add Product"
      ├─→ addProductToCart()
      │
      │ 2. Fetch product details
      ├─→ GET /get-product-details/?product_id=1
      │
      ├─→ Server returns JSON
      │
      │ 3. Add to orderItems array
      │
      │ 4. Update UI
      ├─→ updateCartDisplay()
      │
      │ 5. User clicks "Place Order"
      │
      │ 6. Serialize cart to JSON
      ├─→ updateHiddenCartInput()
      │
      │ 7. Submit form
      ├─→ POST /customer/order/
      │       cart_items: [...JSON...]
      │       delivery_type: "delivery"
      │       delivery_address: "..."
      │       notes: "..."
      │
      └─→ Server processes atomically
          ├─ Parse JSON
          ├─ Validate stock
          ├─ Create orders
          ├─ Deduct inventory
          └─ Return JSON response
```

## Extending the Feature

### Add Cart Persistence

```python
# In place_order view
def place_order(request):
    # ... existing code ...
    
    # Save cart to session
    request.session['cart_items'] = json_cart_items
    
    # Later, retrieve from session
    if 'cart_items' in request.session:
        cart_items = request.session['cart_items']
```

### Add Bulk Discount

```python
# In place_order view
total_amount = Decimal('0.00')
for item in cart_items:
    total_amount += product.price * quantity

# Apply discount
if total_amount > 50000:
    total_amount *= Decimal('0.95')  # 5% discount
```

### Add Order Bundle

```python
# Create order bundle instead of individual orders
with transaction.atomic():
    bundle = OrderBundle.objects.create(
        customer=request.user,
        total_amount=total_amount,
        delivery_type=delivery_type
    )
    
    for item in cart_items:
        order = Order.objects.create(
            customer=request.user,
            bundle=bundle,
            ...
        )
```

## Testing Strategies

### Unit Tests

```python
# test_views.py
from django.test import TestCase, Client
from core.models import LPGProduct, Order

class PlaceOrderTests(TestCase):
    def setUp(self):
        self.product = LPGProduct.objects.create(
            name="LPG 50kg",
            price=1500,
            current_stock=100
        )
    
    def test_get_product_details(self):
        response = self.client.get(
            '/get-product-details/',
            {'product_id': self.product.id}
        )
        data = response.json()
        self.assertEqual(data['price'], 1500)
    
    def test_multiple_order_creation(self):
        cart_items = json.dumps([
            {'product_id': 1, 'quantity': 5},
            {'product_id': 2, 'quantity': 3}
        ])
        
        response = self.client.post(
            '/customer/order/',
            {
                'cart_items': cart_items,
                'delivery_type': 'delivery',
                'delivery_address': '123 Main St'
            }
        )
        
        # Verify 2 orders created
        self.assertEqual(Order.objects.count(), 2)
```

### Integration Tests

```python
# test_integration.py
from selenium import webdriver

class OrderFlowTest:
    def test_complete_order_flow(self):
        # 1. Navigate to order page
        driver.get('http://localhost:8000/customer/order/')
        
        # 2. Select product
        select = driver.find_element_by_name('product')
        select.send_keys('LPG 50kg')
        
        # 3. Enter quantity
        qty = driver.find_element_by_name('quantity')
        qty.clear()
        qty.send_keys('5')
        
        # 4. Click add button
        driver.find_element_by_xpath(
            "//button[contains(text(), 'Add Product')]"
        ).click()
        
        # 5. Verify item in cart
        cart_items = driver.find_element_by_id('cart-items')
        self.assertIn('LPG 50kg', cart_items.text)
        
        # 6. Submit form
        driver.find_element_by_xpath(
            "//button[contains(text(), 'Place Order')]"
        ).click()
        
        # 7. Verify success
        self.assertIn('Order placed', driver.page_source)
```

## Performance Optimization

### Caching Product Details

```python
# In views.py
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
@login_required
def get_product_details(request):
    # Cached response for frequently accessed products
    ...
```

### Batch Stock Check

```python
# Check all products at once
from django.db.models import Q

product_ids = [item['product_id'] for item in cart_items]
products = LPGProduct.objects.filter(id__in=product_ids)

for product in products:
    item = next(i for i in cart_items if i['product_id'] == product.id)
    if not product.can_fulfill_order(item['quantity']):
        raise ValueError(f"Insufficient stock: {product.name}")
```

### Asynchronous Order Creation

```python
# Using Celery for async processing
from celery import shared_task

@shared_task
def process_orders(cart_items, customer_id, delivery_type, address):
    customer = User.objects.get(id=customer_id)
    
    with transaction.atomic():
        for item in cart_items:
            Order.objects.create(
                customer=customer,
                product_id=item['product_id'],
                quantity=item['quantity'],
                delivery_type=delivery_type,
                delivery_address=address
            )
    
    # Send confirmation email
    send_order_confirmation.delay(customer_id)

# In view
process_orders.delay(cart_items, request.user.id, ...)
```

## Debugging Tools

### JavaScript Debugging

```javascript
// Add to console to debug cart
console.table(orderItems)
console.log('Total:', orderItems.reduce((sum, i) => sum + i.total, 0))

// Monitor form submission
document.addEventListener('htmx:beforeRequest', e => {
  console.log('Form data:', e.detail)
})
```

### Server Debugging

```python
# In views.py
import logging

logger = logging.getLogger(__name__)

def place_order(request):
    logger.debug(f"Cart items: {cart_items}")
    logger.debug(f"Total amount: {total_amount}")
    logger.debug(f"Orders created: {[o.id for o in orders]}")
```

### Database Debugging

```python
# Check orders created
from core.models import Order

orders = Order.objects.filter(customer=user).order_by('-id')[:5]
for order in orders:
    print(f"Order {order.id}: {order.product.name} x{order.quantity}")
```

## Common Pitfalls

### 1. Missing CSRF Token
**Problem:** POST requests failing with 403
**Solution:** Ensure `{% csrf_token %}` in form

### 2. JSON Parsing Error
**Problem:** "Invalid JSON format"
**Solution:** Check JavaScript serialization: `JSON.stringify(orderItems)`

### 3. Stock Validation Fails
**Problem:** "Insufficient stock" even when stock available
**Solution:** Check if `can_fulfill_order()` is working correctly

### 4. Cart Cleared on Refresh
**Problem:** User refreshes page and loses cart
**Solution:** Use localStorage or session to persist cart

### 5. Duplicate Orders
**Problem:** Same items created multiple times
**Solution:** Check form submission isn't being triggered twice

## API Contract

### Request Format

```http
POST /customer/order/ HTTP/1.1
Content-Type: application/x-www-form-urlencoded

cart_items=[{"product_id":1,"quantity":5},...]&
delivery_type=delivery&
delivery_address=123 Main St&
notes=Handle with care
```

### Response Format - Success

```json
{
  "success": true,
  "message": "3 order(s) placed successfully!",
  "order_ids": [101, 102, 103],
  "total_amount": 14900.00,
  "redirect": "/customer/dashboard/"
}
```

### Response Format - Error

```json
{
  "success": false,
  "message": "Insufficient stock for LPG 50kg. Only 25 available."
}
```

## Monitoring & Alerts

### Key Metrics to Monitor

```python
# Track order creation rate
Order.objects.filter(
    order_date__gte=timezone.now() - timedelta(hours=1)
).count()

# Track cart abandonment
# (Could be added: abandoned_carts table)

# Track error rates
# (Check logs for JSON parsing errors)
```

### Alert Triggers

- Order creation failures
- Stock validation errors
- Database transaction rollbacks
- API timeouts

## Maintenance

### Regular Tasks

- Monitor API response times
- Check database transaction logs
- Review error logs weekly
- Update documentation with edge cases
- Performance test with large carts

### Backup Procedures

- Backup database before major changes
- Test rollback procedures
- Document all customizations
- Keep version history

## Support Resources

- See `MULTIPLE_PRODUCTS_ORDER_FEATURE.md` for feature details
- See `CART_JAVASCRIPT_API_REFERENCE.md` for API documentation
- Check Django transaction documentation
- Review HTMX documentation for async behavior
