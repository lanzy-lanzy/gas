#!/usr/bin/env python
"""
Script to verify model relationships and functionality
"""
import os
import sys
import django
from datetime import datetime
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CustomerProfile, LPGProduct, Order, DeliveryLog

def test_models():
    print("Testing Django Models...")
    
    # Test 1: Create a test user and customer profile
    print("\n1. Testing CustomerProfile model...")
    try:
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='testcustomer',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Customer'
            }
        )
        
        # Create or get customer profile
        profile, created = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': '09123456789',
                'address': 'Test Address, Tambulig',
                'delivery_instructions': 'Call before delivery'
            }
        )
        
        print(f"✓ CustomerProfile created/retrieved: {profile}")
        print(f"  - User: {profile.user.username}")
        print(f"  - Phone: {profile.phone_number}")
        print(f"  - Address: {profile.address}")
        
    except Exception as e:
        print(f"✗ CustomerProfile test failed: {e}")
        return False
    
    # Test 2: Create LPG Product
    print("\n2. Testing LPGProduct model...")
    try:
        product, created = LPGProduct.objects.get_or_create(
            name='LPG Gas',
            size='11kg',
            defaults={
                'price': Decimal('500.00'),
                'current_stock': 50,
                'minimum_stock': 10,
                'is_active': True
            }
        )
        
        print(f"✓ LPGProduct created/retrieved: {product}")
        print(f"  - Name: {product.name} - {product.size}")
        print(f"  - Price: ₱{product.price}")
        print(f"  - Stock: {product.current_stock}")
        print(f"  - Low stock: {product.is_low_stock}")
        print(f"  - Can fulfill 5 units: {product.can_fulfill_order(5)}")
        
    except Exception as e:
        print(f"✗ LPGProduct test failed: {e}")
        return False
    
    # Test 3: Create Order
    print("\n3. Testing Order model...")
    try:
        order, created = Order.objects.get_or_create(
            customer=user,
            product=product,
            quantity=2,
            defaults={
                'delivery_type': 'delivery',
                'delivery_address': profile.address,
                'status': 'pending',
                'notes': 'Test order'
            }
        )
        
        print(f"✓ Order created/retrieved: {order}")
        print(f"  - Customer: {order.customer.username}")
        print(f"  - Product: {order.product}")
        print(f"  - Quantity: {order.quantity}")
        print(f"  - Total: ₱{order.total_amount}")
        print(f"  - Status: {order.status}")
        print(f"  - Can be cancelled: {order.can_be_cancelled}")
        
    except Exception as e:
        print(f"✗ Order test failed: {e}")
        return False
    
    # Test 4: Create DeliveryLog
    print("\n4. Testing DeliveryLog model...")
    try:
        # Create admin user for logging
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        initial_stock = product.current_stock
        
        delivery_log, created = DeliveryLog.objects.get_or_create(
            product=product,
            supplier='Test Supplier',
            delivery_date=datetime.now(),
            defaults={
                'quantity_received': 20,
                'cost_per_unit': Decimal('400.00'),
                'logged_by': admin_user,
                'notes': 'Test delivery'
            }
        )
        
        # Refresh product to see updated stock
        product.refresh_from_db()
        
        print(f"✓ DeliveryLog created/retrieved: {delivery_log}")
        print(f"  - Product: {delivery_log.product}")
        print(f"  - Quantity received: {delivery_log.quantity_received}")
        print(f"  - Supplier: {delivery_log.supplier}")
        print(f"  - Total cost: ₱{delivery_log.total_cost}")
        print(f"  - Logged by: {delivery_log.logged_by.username}")
        
        if created:
            print(f"  - Stock updated: {initial_stock} → {product.current_stock}")
        
    except Exception as e:
        print(f"✗ DeliveryLog test failed: {e}")
        return False
    
    # Test 5: Verify relationships
    print("\n5. Testing model relationships...")
    try:
        # Test reverse relationships
        customer_orders = user.orders.all()
        product_orders = product.orders.all()
        product_deliveries = product.delivery_logs.all()
        admin_deliveries = admin_user.delivery_logs.all()
        
        print(f"✓ Relationships verified:")
        print(f"  - Customer orders: {customer_orders.count()}")
        print(f"  - Product orders: {product_orders.count()}")
        print(f"  - Product deliveries: {product_deliveries.count()}")
        print(f"  - Admin logged deliveries: {admin_deliveries.count()}")
        
        # Test customer profile relationship
        customer_profile = user.customer_profile
        print(f"  - Customer profile access: {customer_profile.phone_number}")
        
    except Exception as e:
        print(f"✗ Relationship test failed: {e}")
        return False
    
    print("\n✅ All model tests passed successfully!")
    print("\nModel Summary:")
    print(f"- CustomerProfile records: {CustomerProfile.objects.count()}")
    print(f"- LPGProduct records: {LPGProduct.objects.count()}")
    print(f"- Order records: {Order.objects.count()}")
    print(f"- DeliveryLog records: {DeliveryLog.objects.count()}")
    
    return True

if __name__ == '__main__':
    success = test_models()
    sys.exit(0 if success else 1)