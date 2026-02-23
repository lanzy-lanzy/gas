# Code Changes - Detailed Before & After

## 1. place_order.html Template

### BEFORE: Single Product Form
```html
<!-- Product Selection -->
<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
    <label for="{{ form.product.id_for_label }}">Select Product</label>
    <div class="mt-2">{{ form.product }}</div>
</div>

<!-- Quantity -->
<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
    <label for="{{ form.quantity.id_for_label }}">Quantity</label>
    <div class="mt-2">{{ form.quantity }}</div>
</div>

<!-- Stock Information -->
<div id="stock-info"><!-- HTMX loaded here --></div>

<!-- Delivery Type -->
<div><!-- Radio buttons --></div>

<!-- Delivery Address -->
<div x-show="deliveryType === 'delivery'"><!-- Address field --></div>

<!-- Notes -->
<div><!-- Notes field --></div>

<!-- Submit -->
<button type="submit">Place Order</button>
```

### AFTER: Multi-Product Cart Form
```html
<!-- Product Selection - Same -->
<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
    <label for="{{ form.product.id_for_label }}">Select Product</label>
    <div class="mt-2">{{ form.product }}</div>
</div>

<!-- Quantity - Same -->
<div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
    <label for="{{ form.quantity.id_for_label }}">Quantity</label>
    <div class="mt-2">{{ form.quantity }}</div>
</div>

<!-- NEW: Add Product Button -->
<div class="flex gap-3">
    <button type="button" 
            onclick="addProductToCart()"
            class="...">
        Add Product to Order
    </button>
</div>

<!-- NEW: Order Items Cart -->
<div id="order-items" class="bg-white rounded-xl border border-gray-200 p-6">
    <div class="flex items-center mb-4">
        <h3 class="text-lg font-semibold">Order Items</h3>
    </div>
    <div id="cart-items" class="space-y-2">
        <p class="text-gray-500 text-center">No items added yet</p>
    </div>
    <div id="cart-total" class="mt-4 pt-4 border-t border-gray-200 hidden">
        <div class="flex justify-between items-center text-lg font-semibold">
            <span>Total Amount:</span>
            <span id="total-amount" class="text-prycegas-orange">₱0.00</span>
        </div>
    </div>
</div>

<!-- Stock Information - Same -->
<div id="stock-info"><!-- HTMX loaded here --></div>

<!-- Delivery Type - Same -->
<div><!-- Radio buttons --></div>

<!-- Delivery Address - Same -->
<div x-show="deliveryType === 'delivery'"><!-- Address field --></div>

<!-- Notes - Same -->
<div><!-- Notes field --></div>

<!-- Submit - Modified to track cart -->
<button type="submit" 
        @click="handleSubmit($event)"
        x-bind:disabled="isSubmitting || orderItems.length === 0"
        ...>
    Place Order
</button>
```

## 2. JavaScript Functions

### NEW: Cart Management Functions

```javascript
// Global cart storage
let orderItems = [];

// Add product to cart
function addProductToCart() {
    const productSelect = document.querySelector('[name="product"]');
    const quantityInput = document.querySelector('[name="quantity"]');
    
    const productId = productSelect.value;
    const quantity = parseInt(quantityInput.value) || 1;
    
    if (!productId) {
        showToast('error', 'Select Product', 'Please select a product first');
        return;
    }
    
    // Fetch product details from API
    fetch('/get-product-details/?product_id=' + productId)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Check if product already in cart
                const existingItem = orderItems.find(
                    item => item.product_id == productId
                );
                
                if (existingItem) {
                    // Merge quantities
                    existingItem.quantity += quantity;
                    existingItem.total = existingItem.price * existingItem.quantity;
                } else {
                    // Add new item
                    orderItems.push({
                        product_id: productId,
                        product_name: data.name,
                        quantity: quantity,
                        price: data.price,
                        total: data.price * quantity
                    });
                }
                
                updateCartDisplay();
                
                // Reset form
                quantityInput.value = 1;
                productSelect.value = '';
            }
        });
}

// Remove item from cart
function removeFromCart(index) {
    const item = orderItems[index];
    orderItems.splice(index, 1);
    showToast('info', 'Removed', `${item.product_name} removed`);
    updateCartDisplay();
}

// Update quantity
function updateQuantity(index, newQuantity) {
    const quantity = parseInt(newQuantity) || 0;
    if (quantity < 1) {
        removeFromCart(index);
        return;
    }
    
    orderItems[index].quantity = quantity;
    orderItems[index].total = orderItems[index].price * quantity;
    updateCartDisplay();
}

// Refresh cart display
function updateCartDisplay() {
    const cartItemsDiv = document.getElementById('cart-items');
    const cartTotalDiv = document.getElementById('cart-total');
    const totalAmountSpan = document.getElementById('total-amount');
    
    if (orderItems.length === 0) {
        cartItemsDiv.innerHTML = 
            '<p class="text-gray-500 text-center py-4">No items added yet</p>';
        cartTotalDiv.classList.add('hidden');
        return;
    }
    
    let cartHTML = '';
    let cartTotal = 0;
    
    orderItems.forEach((item, index) => {
        cartTotal += item.total;
        cartHTML += `
            <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex-1">
                    <h4 class="text-sm font-medium">${item.product_name}</h4>
                    <p class="text-sm text-gray-500 mt-1">
                        Price: ₱${item.price.toFixed(2)}
                    </p>
                </div>
                <div class="flex items-center gap-3">
                    <div class="flex items-center border border-gray-300 rounded-md">
                        <button type="button" 
                                onclick="updateQuantity(${index}, ${item.quantity - 1})"
                                class="px-2 py-1">−</button>
                        <input type="number" value="${item.quantity}" 
                               onchange="updateQuantity(${index}, this.value)"
                               class="w-12 text-center border-l border-r py-1" min="1">
                        <button type="button" 
                                onclick="updateQuantity(${index}, ${item.quantity + 1})"
                                class="px-2 py-1">+</button>
                    </div>
                    <div class="text-right min-w-fit">
                        <p class="text-sm font-semibold text-prycegas-orange">
                            ₱${item.total.toFixed(2)}
                        </p>
                    </div>
                    <button type="button" 
                            onclick="removeFromCart(${index})"
                            class="text-red-500 hover:text-red-700 ml-2">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" 
                                  d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" 
                                  clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    });
    
    cartItemsDiv.innerHTML = cartHTML;
    
    if (cartTotal > 0) {
        totalAmountSpan.textContent = 
            '₱' + cartTotal.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        cartTotalDiv.classList.remove('hidden');
        updateHiddenCartInput();
    }
}

// Store cart as JSON for form submission
function updateHiddenCartInput() {
    let cartInput = document.getElementById('cart-items-input');
    if (!cartInput) {
        cartInput = document.createElement('input');
        cartInput.type = 'hidden';
        cartInput.id = 'cart-items-input';
        cartInput.name = 'cart_items';
        document.querySelector('form').appendChild(cartInput);
    }
    cartInput.value = JSON.stringify(orderItems);
}
```

## 3. Alpine.js orderForm() Component

### BEFORE: Simple Form Handling
```javascript
function orderForm() {
    return {
        deliveryType: '{{ form.delivery_type.value|default:"delivery" }}',
        isSubmitting: false,
        
        init() {
            this.$watch('deliveryType', (value) => {
                const addressField = document.querySelector('[name="delivery_address"]');
                if (addressField) {
                    if (value === 'delivery') {
                        addressField.setAttribute('required', 'required');
                    } else {
                        addressField.removeAttribute('required');
                    }
                }
            });
        },

        handleSubmit(event) {
            if (!formSubmissionLimiter.canMakeRequest()) {
                event.preventDefault();
                showToast('error', 'Rate Limit Exceeded', 'Please wait...');
                return;
            }
            this.isSubmitting = true;
        }
    }
}
```

### AFTER: Cart-Aware Form Handling
```javascript
function orderForm() {
    return {
        deliveryType: '{{ form.delivery_type.value|default:"delivery" }}',
        isSubmitting: false,
        orderItems: orderItems,  // NEW: reference to cart
        
        init() {
            this.$watch('deliveryType', (value) => {
                const addressField = document.querySelector('[name="delivery_address"]');
                if (addressField) {
                    if (value === 'delivery') {
                        addressField.setAttribute('required', 'required');
                    } else {
                        addressField.removeAttribute('required');
                    }
                }
            });
        },

        handleSubmit(event) {
            // NEW: Check cart not empty
            if (orderItems.length === 0) {
                event.preventDefault();
                showToast('error', 'Empty Cart', 
                    'Please add at least one product');
                return;
            }
            
            if (!formSubmissionLimiter.canMakeRequest()) {
                event.preventDefault();
                showToast('error', 'Rate Limit Exceeded', 'Please wait...');
                return;
            }
            this.isSubmitting = true;
        }
    }
}
```

## 4. place_order View Function

### BEFORE: Single Product Order
```python
@csrf_protect
def place_order(request):
    # ... validation ...
    
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create single order
                    order = form.save()
                    messages.success(request, 
                        f'Order #{order.id} placed successfully!')
                    
                    if request.headers.get('HX-Request'):
                        return JsonResponse({
                            'success': True,
                            'message': f'Order #{order.id} placed!',
                            'order_id': order.id,
                            'total_amount': float(order.total_amount),
                            'redirect': '/customer/dashboard/'
                        })
                    
                    return redirect('core:customer_dashboard')
            except Exception as e:
                # Error handling...
                pass
        else:
            # Form error handling...
            pass
    else:
        form = OrderForm(user=request.user)
    
    context = {'form': form, 'products': products}
    return render(request, 'customer/place_order.html', context)
```

### AFTER: Multiple Product Order
```python
import json
from decimal import Decimal

@csrf_protect
def place_order(request):
    # ... validation ...
    
    if request.method == 'POST':
        try:
            # NEW: Parse JSON cart items
            cart_items_json = request.POST.get('cart_items', '[]')
            cart_items = json.loads(cart_items_json)
            
            if not cart_items:
                raise ValueError('No items in cart')
            
            # Get delivery details
            delivery_type = request.POST.get('delivery_type')
            delivery_address = request.POST.get('delivery_address', '')
            notes = request.POST.get('notes', '')
            
            # Validate delivery
            if delivery_type == 'delivery' and not delivery_address.strip():
                raise ValueError('Delivery address required')
            
            with transaction.atomic():
                orders = []
                total_amount = Decimal('0.00')
                
                # NEW: Create order for each item
                for item in cart_items:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity', 1)
                    
                    # Get product
                    try:
                        product = LPGProduct.objects.get(
                            id=product_id, is_active=True
                        )
                    except LPGProduct.DoesNotExist:
                        raise ValueError(f'Product ID {product_id} not found')
                    
                    # Validate stock
                    if not product.can_fulfill_order(quantity):
                        raise ValueError(
                            f'Insufficient stock for {product.name}. '
                            f'Only {product.current_stock} available.'
                        )
                    
                    # Calculate total
                    order_total = product.price * quantity
                    total_amount += order_total
                    
                    # Create order
                    order = Order(
                        customer=request.user,
                        product=product,
                        quantity=quantity,
                        delivery_type=delivery_type,
                        delivery_address=delivery_address if delivery_type == 'delivery' else '',
                        notes=notes if len(orders) == 0 else '',
                        total_amount=order_total
                    )
                    order.save()
                    
                    # Deduct stock
                    product.current_stock -= quantity
                    product.save()
                    
                    orders.append(order)
                
                # Success message
                if len(orders) == 1:
                    messages.success(request,
                        f'Order #{orders[0].id} placed! Total: ₱{total_amount:.2f}')
                else:
                    order_ids = ', '.join([f'#{o.id}' for o in orders])
                    messages.success(request,
                        f'{len(orders)} orders placed ({order_ids})! '
                        f'Total: ₱{total_amount:.2f}')
                
                # JSON response
                if request.headers.get('HX-Request'):
                    return JsonResponse({
                        'success': True,
                        'message': f'{len(orders)} order(s) placed!',
                        'order_ids': [o.id for o in orders],
                        'total_amount': float(total_amount),
                        'redirect': '/customer/dashboard/'
                    })
                
                return redirect('core:customer_dashboard')
        
        except json.JSONDecodeError:
            error_msg = 'Invalid request format'
            if request.headers.get('HX-Request'):
                return JsonResponse(
                    {'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        except ValueError as e:
            error_msg = str(e)
            if request.headers.get('HX-Request'):
                return JsonResponse(
                    {'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        except Exception as e:
            error_msg = f'Error placing order: {str(e)}'
            if request.headers.get('HX-Request'):
                return JsonResponse(
                    {'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
    else:
        form = OrderForm(user=request.user)
    
    context = {'form': form, 'products': products}
    return render(request, 'customer/place_order.html', context)
```

## 5. New API Endpoint

### NEW: get_product_details() Function
```python
@login_required
def get_product_details(request):
    """
    API endpoint for getting product details (price, stock) 
    for the cart system
    """
    product_id = request.GET.get('product_id')
    
    if not product_id:
        return JsonResponse({
            'success': False,
            'message': 'Product ID is required'
        })
    
    try:
        product = LPGProduct.objects.get(id=product_id, is_active=True)
        
        return JsonResponse({
            'success': True,
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'current_stock': product.current_stock,
            'can_fulfill': product.can_fulfill_order(1)
        })
    except LPGProduct.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
```

## 6. URL Configuration

### BEFORE: urls.py
```python
urlpatterns = [
    # ... other URLs ...
    path('check-stock/', check_stock, name='check_stock'),
    path('refresh-orders/', refresh_order_status, name='refresh_order_status'),
    # ... more URLs ...
]
```

### AFTER: urls.py
```python
# ADDED to imports
from .views import (
    # ... existing imports ...
    get_product_details,  # NEW
    # ... rest of imports ...
)

urlpatterns = [
    # ... other URLs ...
    path('check-stock/', check_stock, name='check_stock'),
    path('get-product-details/', get_product_details, name='get_product_details'),  # NEW
    path('refresh-orders/', refresh_order_status, name='refresh_order_status'),
    # ... more URLs ...
]
```

## 7. Imports

### BEFORE: views.py
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Sum, Q, F, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
```

### AFTER: views.py
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Sum, Q, F, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal  # NEW
```

## Summary of Changes

| Component | Type | Changes |
|-----------|------|---------|
| `place_order.html` | Template | Added cart UI, JavaScript functions, hidden input |
| `views.py` | Backend | Added new endpoint, modified place_order logic |
| `urls.py` | Routing | Added new URL pattern |
| Database | Schema | No changes |
| Forms | Django | No changes to OrderForm |
| Models | Schema | No changes to Order model |

## Backward Compatibility

- ✅ Existing URLs unchanged
- ✅ Existing API endpoints unchanged
- ✅ Database schema compatible
- ✅ Old orders still work
- ✅ No migrations needed
