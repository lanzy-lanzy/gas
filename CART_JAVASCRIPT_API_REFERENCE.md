# Cart JavaScript API Reference

## Global Variables

### `orderItems`
Array of cart items currently in the shopping cart.

**Type:** `Array<CartItem>`

**Example:**
```javascript
orderItems = [
  {
    product_id: 1,
    product_name: "LPG 50kg",
    quantity: 3,
    price: 1500.00,
    total: 4500.00
  }
]
```

## Data Structures

### CartItem Object
```typescript
interface CartItem {
  product_id: number,           // Product database ID
  product_name: string,         // Display name of product
  quantity: number,             // Number of units
  price: number,               // Price per unit
  total: number                // quantity * price
}
```

### Product Details Response
```typescript
interface ProductDetails {
  success: boolean,
  id: number,
  name: string,
  price: number,
  current_stock: number,
  can_fulfill: boolean
}
```

## Functions

### addProductToCart()

Adds a product to the cart or updates its quantity if already present.

**Signature:**
```javascript
function addProductToCart(): void
```

**Process:**
1. Gets product ID and quantity from form
2. Validates inputs
3. Fetches product details from `/get-product-details/`
4. Adds or updates in `orderItems`
5. Updates cart display
6. Resets form inputs

**Throws:**
- Toast error if no product selected
- Toast error if quantity invalid
- Toast error if product not found

**Example:**
```javascript
// User selects "LPG 50kg" and enters quantity "3"
addProductToCart()
// Result: Item added to cart, display updated, form reset
```

### removeFromCart(index)

Removes a product from the cart by index.

**Signature:**
```javascript
function removeFromCart(index: number): void
```

**Parameters:**
- `index` - Position in orderItems array (0-based)

**Throws:**
- Shows info toast when item is removed

**Example:**
```javascript
// Remove item at position 1
removeFromCart(1)
// Result: Item removed, display updated
```

### updateQuantity(index, newQuantity)

Updates the quantity of a cart item.

**Signature:**
```javascript
function updateQuantity(index: number, newQuantity: number | string): void
```

**Parameters:**
- `index` - Position in orderItems array
- `newQuantity` - New quantity (will be parsed to int)

**Behavior:**
- If quantity < 1: removes item
- Updates total: `price * newQuantity`
- Refreshes display

**Example:**
```javascript
// Change item 0 from 3 to 5 units
updateQuantity(0, 5)

// Change item 1 from 2 to 0 (removes item)
updateQuantity(1, 0)
```

### updateCartDisplay()

Refreshes the cart UI based on current orderItems.

**Signature:**
```javascript
function updateCartDisplay(): void
```

**Updates:**
- Cart items HTML
- Total amount display
- Hidden input for form submission
- Shows/hides total section

**When Called:**
- After adding/removing items
- After updating quantities
- After successful submission

**Example:**
```javascript
// Manually refresh display
updateCartDisplay()
```

### updateHiddenCartInput()

Serializes cart items to JSON and stores in hidden form input.

**Signature:**
```javascript
function updateHiddenCartInput(): void
```

**Creates/Updates:**
- Hidden input: `#cart-items-input`
- Name: `cart_items`
- Value: JSON serialized array

**Example:**
```javascript
// This is called automatically by updateCartDisplay()
// But can be called manually:
updateHiddenCartInput()

// Result: 
// <input type="hidden" id="cart-items-input" name="cart_items" 
//        value='[{"product_id":1,...}]'>
```

### orderForm()

Alpine.js data component managing form state.

**Signature:**
```javascript
function orderForm(): Object
```

**Returns Object with:**
- `deliveryType` - Current delivery selection
- `isSubmitting` - Form submission state
- `orderItems` - Reference to cart items
- `init()` - Initialization method
- `handleSubmit()` - Form submit handler

**Methods:**

#### init()
Initializes form watchers on first load.

```javascript
init() {
  // Watches delivery type changes
  // Shows/hides address field
  // Sets required attribute
}
```

#### handleSubmit(event)
Validates and submits the form.

```javascript
handleSubmit(event: Event): void
```

**Validation:**
- Checks cart has items
- Checks rate limiting
- Validates delivery address if needed
- Sets isSubmitting flag

**Example:**
```javascript
// Called when form submitted
// Validates cart, checks rate limit, submits form
```

## API Endpoints

### GET /get-product-details/

Fetches product information for the cart system.

**Query Parameters:**
```
product_id: number (required)
```

**Response (Success):**
```json
{
  "success": true,
  "id": 1,
  "name": "LPG 50kg",
  "price": 1500.00,
  "current_stock": 100,
  "can_fulfill": true
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Product not found"
}
```

**Example Call:**
```javascript
fetch('/get-product-details/?product_id=1')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`Price: ${data.price}`)
    }
  })
```

## Event Handling

### Form Submission

**Trigger:** Click "Place Order" button

**Flow:**
1. `@click="handleSubmit($event")`
2. Validates cart not empty
3. Validates delivery address if needed
4. Submits form via HTMX
5. `hx-post="/customer/order/"`

### HTMX Response Handling

**Event:** `htmx:afterRequest`

**Handles:**
- Success response: Shows success toast, clears cart, redirects
- Error response: Shows error toast, keeps form

### Product Selection Change

**Trigger:** Select product from dropdown

**Action:** Updates form value, no cart action

### Quantity Change

**Trigger:** Change quantity input

**Action:** Updates form value, no cart action

## Usage Examples

### Example 1: Simple Single Item

```javascript
// HTML
<select name="product"><option value="1">LPG 50kg</option></select>
<input name="quantity" value="5">
<button onclick="addProductToCart()">Add</button>

// Result
orderItems = [
  {product_id: 1, product_name: "LPG 50kg", quantity: 5, price: 1500, total: 7500}
]
```

### Example 2: Multiple Items Same Product

```javascript
// First add
orderItems = [{product_id: 1, quantity: 3, ...}]

// Select same product, quantity 2, add again
addProductToCart()

// Result (quantity merged)
orderItems = [{product_id: 1, quantity: 5, ...}]
```

### Example 3: Complex Cart

```javascript
// Add LPG 50kg x5
orderItems = [{product_id: 1, quantity: 5, total: 7500, ...}]

// Add Propane x2
orderItems = [
  {product_id: 1, quantity: 5, total: 7500, ...},
  {product_id: 2, quantity: 2, total: 1600, ...}
]

// Add LPG 100kg x1
orderItems = [
  {product_id: 1, quantity: 5, total: 7500, ...},
  {product_id: 2, quantity: 2, total: 1600, ...},
  {product_id: 3, quantity: 1, total: 2500, ...}
]

// Remove item 1 (Propane)
removeFromCart(1)

// Result
orderItems = [
  {product_id: 1, quantity: 5, total: 7500, ...},
  {product_id: 3, quantity: 1, total: 2500, ...}
]

// Change item 0 quantity to 10
updateQuantity(0, 10)

// Result
orderItems = [
  {product_id: 1, quantity: 10, total: 15000, ...},
  {product_id: 3, quantity: 1, total: 2500, ...}
]
```

## Error Handling

### Try-Catch in addProductToCart

```javascript
try {
  const response = await fetch(...)
  const data = await response.json()
  
  if (!data.success) {
    showToast('error', 'Error', data.message)
    return
  }
  
  // Process...
} catch (error) {
  console.error('Error:', error)
  showToast('error', 'Error', 'Failed to add product')
}
```

### Error Messages Shown to User

```
"Please select a product first"
"Quantity must be at least 1"
"Could not fetch product details"
"Failed to add product to order"
"Please add at least one product to your order"
"Insufficient stock for LPG 50kg. Only 25 available."
```

## Form Data Submission

### Cart Items in Form

```javascript
// Before submission, hidden input contains:
<input type="hidden" id="cart-items-input" name="cart_items"
       value='[
         {"product_id":1,"product_name":"LPG 50kg","quantity":5,"price":1500,"total":7500},
         {"product_id":2,"product_name":"Propane","quantity":2,"price":800,"total":1600}
       ]'>

// Submitted as POST data:
POST /customer/order/
cart_items=[...]
delivery_type=delivery
delivery_address=123 Main St
notes=Handle carefully
```

## Debugging

### Log Current Cart
```javascript
console.log('Cart:', orderItems)
console.log('Total:', orderItems.reduce((sum, item) => sum + item.total, 0))
```

### Log Element State
```javascript
console.log('Cart div:', document.getElementById('cart-items'))
console.log('Hidden input:', document.getElementById('cart-items-input'))
console.log('Total display:', document.getElementById('total-amount'))
```

### Monitor HTMX Events
```javascript
document.addEventListener('htmx:beforeRequest', (e) => {
  console.log('Request:', e.detail)
})

document.addEventListener('htmx:afterRequest', (e) => {
  console.log('Response:', e.detail.xhr.status)
})
```

## Performance Notes

- Cart operations are instant (client-side only)
- API call only made once per product add
- Cart display update is optimized with innerHTML
- No database queries until submission
- Form serialization happens once before submit

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Fetch API | ✅ | ✅ | ✅ | ✅ |
| JSON | ✅ | ✅ | ✅ | ✅ |
| Array methods | ✅ | ✅ | ✅ | ✅ |
| DOM manipulation | ✅ | ✅ | ✅ | ✅ |
| Template literals | ✅ | ✅ | ✅ | ✅ |

Minimum: Chrome 42+, Firefox 39+, Safari 10+, Edge 12+
