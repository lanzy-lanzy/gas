"""
Test script to verify inventory adjustment functionality
Run with: python manage.py shell < test_inventory_adjustment_fix.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import LPGProduct, InventoryAdjustment, StockMovement
from core.forms import InventoryAdjustmentForm
from django.test import RequestFactory
from django.utils import timezone

print("=" * 80)
print("INVENTORY ADJUSTMENT FUNCTIONALITY TEST")
print("=" * 80)

# 1. Check if products exist
print("\n1. Checking for active products...")
products = LPGProduct.objects.filter(is_active=True)
print(f"   Found {products.count()} active products")

if not products.exists():
    print("   ERROR: No active products found. Creating test product...")
    test_product = LPGProduct.objects.create(
        name="Test LPG",
        size="11kg",
        price=500.00,
        cost_price=400.00,
        current_stock=50
    )
    print(f"   Created: {test_product}")
    product = test_product
else:
    product = products.first()
    print(f"   Using product: {product} (Stock: {product.current_stock})")

# 2. Check if users exist
print("\n2. Checking for admin user...")
admin_users = User.objects.filter(is_superuser=True)
if not admin_users.exists():
    print("   ERROR: No admin users found. Creating admin user...")
    admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print(f"   Created: {admin}")
    user = admin
else:
    user = admin_users.first()
    print(f"   Using user: {user}")

# 3. Test form with increase
print("\n3. Testing form submission (INCREASE)...")
form_data = {
    'product': product.id,
    'adjustment_type': 'increase',
    'quantity': 10,
    'reason': 'count_error',
    'notes': 'Test increase adjustment'
}

form = InventoryAdjustmentForm(form_data)
if form.is_valid():
    print("   ✓ Form is valid")
    
    # Get the adjustment before saving
    adjustment = form.save(commit=False)
    print(f"   - quantity_change before set: {getattr(adjustment, 'quantity_change', 'NOT SET')}")
    
    # Save form (which sets quantity_change)
    adjustment = form.save(commit=False)
    adjustment.adjusted_by = user
    print(f"   - quantity_change after form.save(): {adjustment.quantity_change}")
    print(f"   - adjustment_type from form: {form.cleaned_data.get('adjustment_type')}")
    print(f"   - quantity from form: {form.cleaned_data.get('quantity')}")
    
    # Check stock before
    initial_stock = product.current_stock
    print(f"   - Product stock before adjustment: {initial_stock}")
    
    # Save the adjustment (this should trigger model save)
    try:
        adjustment.save()
        print("   ✓ Adjustment saved successfully")
        
        # Refresh product to check updated stock
        product.refresh_from_db()
        print(f"   - Product stock after adjustment: {product.current_stock}")
        print(f"   - Expected stock: {initial_stock + 10}")
        
        if product.current_stock == initial_stock + 10:
            print("   ✓ INCREASE test PASSED")
        else:
            print(f"   ✗ INCREASE test FAILED - Stock not updated correctly")
        
        # Check stock movement
        movement = StockMovement.objects.filter(reference_id=str(adjustment.id)).first()
        if movement:
            print(f"   ✓ Stock movement created: {movement}")
        else:
            print("   ✗ Stock movement not created")
            
    except Exception as e:
        print(f"   ✗ Error saving adjustment: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("   ✗ Form is invalid")
    for field, errors in form.errors.items():
        print(f"     - {field}: {errors}")

# 4. Test form with decrease
print("\n4. Testing form submission (DECREASE)...")
initial_stock = product.current_stock
form_data_decrease = {
    'product': product.id,
    'adjustment_type': 'decrease',
    'quantity': 5,
    'reason': 'damage',
    'notes': 'Test decrease adjustment'
}

form_dec = InventoryAdjustmentForm(form_data_decrease)
if form_dec.is_valid():
    print("   ✓ Form is valid")
    
    adjustment_dec = form_dec.save(commit=False)
    adjustment_dec.adjusted_by = user
    print(f"   - quantity_change: {adjustment_dec.quantity_change}")
    
    print(f"   - Product stock before adjustment: {initial_stock}")
    
    try:
        adjustment_dec.save()
        print("   ✓ Adjustment saved successfully")
        
        product.refresh_from_db()
        print(f"   - Product stock after adjustment: {product.current_stock}")
        print(f"   - Expected stock: {initial_stock - 5}")
        
        if product.current_stock == initial_stock - 5:
            print("   ✓ DECREASE test PASSED")
        else:
            print(f"   ✗ DECREASE test FAILED - Stock not updated correctly")
            
    except Exception as e:
        print(f"   ✗ Error saving adjustment: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("   ✗ Form is invalid")
    for field, errors in form_dec.errors.items():
        print(f"     - {field}: {errors}")

# 5. Summary
print("\n5. Adjustment History for product:")
adjustments = InventoryAdjustment.objects.filter(product=product).order_by('-created_at')
for adj in adjustments[:5]:
    print(f"   - {adj.created_at}: {adj.quantity_change} ({adj.reason}) by {adj.adjusted_by.username}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
