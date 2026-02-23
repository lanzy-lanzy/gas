# Multiple Products Order - Quick Start Guide

## What Changed?

The **Place Order** page now allows customers to add multiple LPG products to their order before checkout, instead of being limited to one product per order.

## How to Use

### As a Customer:

1. **Go to Place Order**
   - Click "Place Order" from dashboard

2. **Add Products**
   - Select a product from the dropdown
   - Enter quantity
   - Click "Add Product to Order"
   - Repeat for each additional product

3. **Manage Cart**
   - See all items in the "Order Items" section
   - Adjust quantity with +/- buttons
   - Remove unwanted items with the trash icon
   - View total amount automatically calculated

4. **Complete Order**
   - Select delivery type (Pickup/Delivery)
   - Enter delivery address if needed
   - Add special instructions (optional)
   - Click "Place Order" when ready

## Features

| Feature | Status |
|---------|--------|
| Add multiple products | ✅ |
| Adjust quantities | ✅ |
| Remove items | ✅ |
| Real-time total | ✅ |
| Stock validation | ✅ |
| Same delivery for all items | ✅ |
| Multiple orders created | ✅ |

## Example Workflow

```
Customer adds items:
├─ 5 x LPG 50kg @ ₱1,500 = ₱7,500
├─ 3 x Propane Gas @ ₱800 = ₱2,400
└─ 2 x LPG 100kg @ ₱2,500 = ₱5,000
                    TOTAL = ₱14,900

Selects delivery address
Clicks "Place Order"

Result: 3 orders created
├─ Order #101: 5 x 50kg
├─ Order #102: 3 x Propane
└─ Order #103: 2 x 100kg

All with same delivery address & instructions
```

## Important Notes

⚠️ **Cart is not saved** - Refreshing the page will clear your cart  
⚠️ **Submit when ready** - Cart exists only until you place the order  
⚠️ **Stock checked at submit** - Final validation happens when placing order  
✅ **Multiple orders created** - Each product becomes a separate order  
✅ **Shared delivery** - All items get same delivery address  

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Add Product to Order" button disabled | Select a product and quantity first |
| "Place Order" button disabled | Add at least one item to cart |
| Error: "Product not found" | Product may have been deactivated, refresh page |
| Error: "Insufficient stock" | Reduce quantity, less stock available than needed |
| Cart disappeared | Page refreshed, re-add items |
| Wrong total | Refresh page and re-add items |

## File Changes

- `templates/customer/place_order.html` - Frontend UI & JavaScript
- `core/views.py` - Backend order processing
- `core/urls.py` - New API endpoint

## Technical Details

- **API Endpoint:** `/get-product-details/` (GET)
- **Form Data:** `cart_items` (JSON array)
- **Database:** Uses existing Order model
- **Transaction:** Atomic (all or nothing)
