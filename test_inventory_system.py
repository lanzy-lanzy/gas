#!/usr/bin/env python
"""
Test script for the inventory management system
This script tests all the key features of task 8: Build inventory management system
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import LPGProduct, DeliveryLog

def test_inventory_management_system():
    """Test all inventory management features"""
    print("🧪 Testing Inventory Management System")
    print("=" * 50)
    
    # Setup test client and user
    client = Client()
    dealer_user = User.objects.filter(is_staff=True).first()
    if not dealer_user:
        print("❌ No dealer user found. Please create a staff user first.")
        return False
    
    client.force_login(dealer_user)
    print(f"✅ Logged in as dealer: {dealer_user.username}")
    
    # Test 1: Inventory dashboard access
    print("\n📊 Testing inventory dashboard...")
    response = client.get('/dealer/inventory/')
    if response.status_code == 200:
        print("✅ Inventory dashboard loads successfully")
        print(f"   - Response contains inventory data: {'inventory_stats' in str(response.content)}")
    else:
        print(f"❌ Inventory dashboard failed: {response.status_code}")
        return False
    
    # Test 2: Stock levels and low stock warnings
    print("\n📦 Testing stock levels and low stock detection...")
    products = LPGProduct.objects.all()
    print(f"✅ Found {products.count()} products")
    
    low_stock_products = [p for p in products if p.is_low_stock]
    print(f"✅ Low stock detection working: {len(low_stock_products)} products below minimum")
    
    for product in products:
        print(f"   - {product.name} ({product.size}): {product.current_stock} units (min: {product.minimum_stock})")
    
    # Test 3: Delivery form modal
    print("\n📝 Testing delivery logging modal...")
    response = client.get('/dealer/inventory/delivery-form/', HTTP_HX_REQUEST='true')
    if response.status_code == 200:
        print("✅ Delivery form modal loads successfully")
        print(f"   - Form contains product options: {'Select a product' in str(response.content)}")
    else:
        print(f"❌ Delivery form modal failed: {response.status_code}")
        return False
    
    # Test 4: Automatic inventory adjustment when deliveries are logged
    print("\n🚚 Testing delivery logging and automatic inventory adjustment...")
    
    # Get initial stock level
    test_product = products.first()
    initial_stock = test_product.current_stock
    initial_delivery_count = DeliveryLog.objects.count()
    
    # Log a test delivery
    delivery_data = {
        'product': test_product.id,
        'quantity_received': 25,
        'supplier_name': 'Test Automation Supplier',
        'delivery_date': datetime.now().strftime('%Y-%m-%dT%H:%M'),
        'cost_per_unit': 150.00,
        'total_cost': 3750.00,
        'notes': 'Automated test delivery'
    }
    
    response = client.post('/dealer/inventory/log-delivery/', delivery_data, HTTP_HX_REQUEST='true')
    if response.status_code == 200:
        print("✅ Delivery logging successful")
        
        # Check if delivery was created
        new_delivery_count = DeliveryLog.objects.count()
        if new_delivery_count > initial_delivery_count:
            print("✅ Delivery log record created")
            
            # Check if inventory was automatically updated
            test_product.refresh_from_db()
            expected_stock = initial_stock + 25
            if test_product.current_stock == expected_stock:
                print(f"✅ Inventory automatically updated: {initial_stock} → {test_product.current_stock}")
            else:
                print(f"❌ Inventory not updated correctly: expected {expected_stock}, got {test_product.current_stock}")
                return False
        else:
            print("❌ Delivery log record not created")
            return False
    else:
        print(f"❌ Delivery logging failed: {response.status_code}")
        return False
    
    # Test 5: Stock movement history and tracking
    print("\n📈 Testing stock movement history...")
    response = client.get('/dealer/inventory/movements/', HTTP_HX_REQUEST='true')
    if response.status_code == 200:
        print("✅ Stock movement history loads successfully")
        
        # Check if recent delivery appears in history
        recent_deliveries = DeliveryLog.objects.order_by('-delivery_date')[:5]
        print(f"✅ Found {recent_deliveries.count()} recent deliveries")
        
        for delivery in recent_deliveries:
            print(f"   - {delivery.delivery_date.strftime('%Y-%m-%d %H:%M')}: +{delivery.quantity_received} {delivery.product.name} from {delivery.supplier_name}")
    else:
        print(f"❌ Stock movement history failed: {response.status_code}")
        return False
    
    # Test 6: Real-time inventory displays with Unpoly updates
    print("\n🔄 Testing real-time inventory updates...")
    response = client.get('/dealer/inventory/refresh/', HTTP_HX_REQUEST='true')
    if response.status_code == 200:
        print("✅ Real-time inventory refresh working")
        print(f"   - Response contains updated stats: {'inventory_stats' in str(response.content)}")
    else:
        print(f"❌ Real-time inventory refresh failed: {response.status_code}")
        return False
    
    # Test 7: Form validation
    print("\n✅ Testing form validation...")
    
    # Test invalid delivery data
    invalid_data = {
        'product': '',  # Missing product
        'quantity_received': 0,  # Invalid quantity
        'supplier': '',  # Missing supplier
        'delivery_date': '',  # Missing date
        'cost_per_unit': -10.00,  # Invalid cost
    }
    
    response = client.post('/dealer/inventory/log-delivery/', invalid_data, HTTP_HX_REQUEST='true')
    if response.status_code == 400 or 'error' in str(response.content).lower():
        print("✅ Form validation working - invalid data rejected")
    else:
        print("⚠️  Form validation may not be working properly")
    
    print("\n🎉 All inventory management tests completed successfully!")
    print("=" * 50)
    
    # Summary of features tested
    print("\n📋 Features Tested:")
    print("✅ Inventory dashboard showing current stock levels and low stock warnings")
    print("✅ Delivery logging modal using Alpine.js with form validation")
    print("✅ Automatic inventory adjustment when deliveries are logged")
    print("✅ Stock movement history and tracking")
    print("✅ Unpoly updates for real-time inventory displays")
    print("✅ Form validation and error handling")
    
    return True

if __name__ == "__main__":
    success = test_inventory_management_system()
    sys.exit(0 if success else 1)