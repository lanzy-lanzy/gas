# Test Guide - Order Submission Fix

## Quick Test (5 minutes)

### Step 1: Open Developer Console
Press `F12` to open browser developer tools
Go to **Console** tab

### Step 2: Navigate to Order Page
Visit: `http://localhost:8000/customer/order/`

### Step 3: Add Items to Cart
1. Select a product from the dropdown
2. Enter quantity (e.g., 5)
3. Click **"Add Product to Order"** button
4. You should see:
   - Success toast notification: "Added: [Product Name]"
   - Item appears in "Order Items" section below
   - "Place Order" button becomes enabled (orange)
   - Total amount displays at bottom

### Step 4: Add Second Item
1. Select a different product
2. Enter different quantity
3. Click **"Add Product to Order"** again
4. Second item should appear in cart
5. Total should update

### Step 5: Place Order
1. Select delivery type (Pickup or Delivery)
2. If Delivery: enter address
3. Click **"Place Order"** button
4. You should see:
   - Button shows "Placing Order..." with spinner
   - Toast shows success message
   - Page redirects to dashboard after 1.5 seconds
   - New orders appear in order history

## Detailed Troubleshooting

### Issue: "Add Product" button doesn't work

**Check:**
1. Is a product selected? (Dropdown should show product name)
2. Is quantity > 0?
3. Check console for errors: `addProductToCart()` errors?

**Fix:**
- Make sure to select product first
- Ensure quantity is valid (1-100)
- Clear cache (Ctrl+Shift+Delete) and reload

### Issue: "Place Order" button is disabled/grayed out

**Check:**
1. Is cart empty? (Check "Order Items" section)
2. No items should show "No items added yet"

**Fix:**
- Add at least one item to cart
- Click "Add Product to Order" button
- Verify item appears in cart

### Issue: "Place Order" button doesn't respond

**Check:**
1. Open browser console (F12)
2. Click "Place Order" 
3. Look for error messages

**Common errors and fixes:**

```
"Cannot read property 'classList' of undefined"
→ Page needs reload, refresh (F5) and try again

"Delivery address required"
→ Select "Delivery" option and enter address

"Empty Cart" error
→ Cart items cleared, add items again

"Failed to add product"
→ Product may be out of stock, try different product
```

### Issue: Order submitted but redirects don't work

**Check:**
1. Does success toast appear?
2. Does page redirect after 1.5 seconds?
3. Can you see order in dashboard?

**If yes:**
- Order succeeded, redirect may be blocked by browser
- Manually navigate to dashboard: `/customer/dashboard/`

**If no:**
- Check browser console for errors
- Check network tab for response status
- Order may not have been created

## Browser Testing

### Test in Multiple Browsers

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Should work | Modern browser, full support |
| Firefox | ✅ Should work | Modern browser, full support |
| Safari | ✅ Should work | Modern browser, full support |
| Edge | ✅ Should work | Chromium-based, full support |
| IE 11 | ❌ Won't work | Not supported, Fetch API missing |

## Network Inspection

### Watch the Request/Response

1. Open DevTools (F12)
2. Go to **Network** tab
3. Add items to cart and click "Place Order"
4. Look for POST request to `/customer/order/`

**Request should include:**
```
Headers:
- Content-Type: multipart/form-data
- X-Requested-With: XMLHttpRequest

Body:
- cart_items: [{"product_id":1,"quantity":5,...}]
- delivery_type: "delivery"
- delivery_address: "123 Main St"
- notes: "..."
- csrfmiddlewaretoken: "..."
```

**Response should be:**
```json
{
  "success": true,
  "message": "3 order(s) placed successfully!",
  "order_ids": [101, 102, 103],
  "total_amount": 14900.00,
  "redirect": "/customer/dashboard/"
}
```

If response shows error:
```json
{
  "success": false,
  "message": "Insufficient stock for LPG 50kg"
}
```

→ Check stock levels, modify quantity

## JavaScript Console Commands

You can test functionality directly in console:

```javascript
// Check current cart
console.log(orderItems)

// Check total
console.log(orderItems.reduce((sum, i) => sum + i.total, 0))

// Manually add item (for testing)
orderItems.push({
  product_id: 1,
  product_name: "Test",
  quantity: 5,
  price: 100,
  total: 500
})
updateCartDisplay()

// Clear cart
orderItems = []
updateCartDisplay()

// Test API endpoint
fetch('/get-product-details/?product_id=1')
  .then(r => r.json())
  .then(d => console.log(d))
```

## Database Verification

After successful order, check database:

```python
# Django shell
python manage.py shell

from core.models import Order
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')
orders = Order.objects.filter(customer=user).order_by('-id')[:5]

for order in orders:
    print(f"Order {order.id}: {order.product.name} x{order.quantity}")
    print(f"  Status: {order.status}")
    print(f"  Total: {order.total_amount}")
    print(f"  Delivery: {order.delivery_type}")
```

Expected output:
```
Order 101: LPG 50kg x5
  Status: pending
  Total: 7500.00
  Delivery: delivery
Order 102: Propane Gas x2
  Status: pending
  Total: 1600.00
  Delivery: delivery
Order 103: LPG 100kg x1
  Status: pending
  Total: 2500.00
  Delivery: delivery
```

## Performance Check

### Load Time
- Page should load in < 2 seconds
- Adding item should be instant (< 100ms)
- Submission should complete in < 2 seconds

### Check with DevTools:
1. Open Network tab
2. Reload page
3. Click "Add Product"
4. Look at network request time in "Time" column

Expected times:
- GET /customer/order/: < 500ms
- GET /get-product-details/: < 100ms
- POST /customer/order/: < 1000ms

## Success Checklist

✅ Items add to cart  
✅ Cart displays correctly  
✅ Quantities update  
✅ Total calculates correctly  
✅ "Place Order" button enables/disables appropriately  
✅ Form submission doesn't show errors  
✅ Success toast appears  
✅ Page redirects to dashboard  
✅ Orders created in database  
✅ Stock updated correctly  

## Report Issues

If you encounter any issues:

1. **Screenshot** the error message
2. **Note** the exact steps to reproduce
3. **Check** browser console for errors (F12 → Console)
4. **Check** network requests (F12 → Network)
5. **Copy** error message from console
6. Report with these details

Error example format:
```
Issue: "Place Order" button doesn't work
Steps: 
1. Added LPG 50kg x5 to cart
2. Clicked "Place Order"
3. Button shows spinner but nothing happens

Console Error:
[Error] TypeError: Cannot read property 'action' of undefined

Expected: Order should be created and page should redirect
```
