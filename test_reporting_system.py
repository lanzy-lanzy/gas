#!/usr/bin/env python
"""
Test script to verify the reporting system functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CustomerProfile, LPGProduct, Order, DeliveryLog
from django.utils import timezone

def create_test_data():
    """Create test data for reporting system"""
    print("Creating test data for reporting system...")
    
    # Create admin user if not exists
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@prycegas.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Created admin user")
    
    # Create test customer
    customer_user, created = User.objects.get_or_create(
        username='testcustomer',
        defaults={
            'email': 'customer@test.com',
            'first_name': 'Test',
            'last_name': 'Customer',
        }
    )
    if created:
        customer_user.set_password('test123')
        customer_user.save()
        print("✓ Created test customer")
    
    # Create customer profile
    customer_profile, created = CustomerProfile.objects.get_or_create(
        user=customer_user,
        defaults={
            'phone_number': '09123456789',
            'address': 'Test Address, Tambulig',
            'delivery_instructions': 'Test delivery instructions'
        }
    )
    if created:
        print("✓ Created customer profile")
    
    # Create test products
    products_data = [
        {'name': 'LPG Gas', 'size': '11kg', 'price': Decimal('500.00'), 'current_stock': 50, 'minimum_stock': 10},
        {'name': 'LPG Gas', 'size': '22kg', 'price': Decimal('950.00'), 'current_stock': 30, 'minimum_stock': 5},
        {'name': 'LPG Gas', 'size': '50kg', 'price': Decimal('2100.00'), 'current_stock': 15, 'minimum_stock': 3},
    ]
    
    products = []
    for product_data in products_data:
        product, created = LPGProduct.objects.get_or_create(
            name=product_data['name'],
            size=product_data['size'],
            defaults=product_data
        )
        products.append(product)
        if created:
            print(f"✓ Created product: {product.name} - {product.size}")
    
    # Create test delivery logs (stock replenishment)
    today = timezone.now()
    for i, product in enumerate(products):
        delivery_date = today - timedelta(days=i*5)  # Spread deliveries over time
        delivery_log, created = DeliveryLog.objects.get_or_create(
            product=product,
            delivery_date=delivery_date,
            defaults={
                'quantity_received': 20 + (i * 10),
                'supplier': f'Supplier {i+1}',
                'cost_per_unit': product.price * Decimal('0.8'),  # 80% of selling price
                'total_cost': (20 + (i * 10)) * product.price * Decimal('0.8'),
                'logged_by': admin_user,
                'notes': f'Test delivery for {product.name} - {product.size}'
            }
        )
        if created:
            print(f"✓ Created delivery log for {product.name} - {product.size}")
    
    # Create test orders
    order_data = [
        {'product': products[0], 'quantity': 2, 'delivery_type': 'delivery', 'days_ago': 1},
        {'product': products[1], 'quantity': 1, 'delivery_type': 'pickup', 'days_ago': 3},
        {'product': products[0], 'quantity': 3, 'delivery_type': 'delivery', 'days_ago': 5},
        {'product': products[2], 'quantity': 1, 'delivery_type': 'delivery', 'days_ago': 7},
        {'product': products[1], 'quantity': 2, 'delivery_type': 'pickup', 'days_ago': 10},
    ]
    
    for i, order_info in enumerate(order_data):
        order_date = today - timedelta(days=order_info['days_ago'])
        delivery_date = order_date + timedelta(hours=2)  # Delivered 2 hours after order
        
        order, created = Order.objects.get_or_create(
            customer=customer_user,
            product=order_info['product'],
            order_date=order_date,
            defaults={
                'quantity': order_info['quantity'],
                'delivery_type': order_info['delivery_type'],
                'delivery_address': customer_profile.address,
                'status': 'delivered',
                'total_amount': order_info['product'].price * order_info['quantity'],
                'delivery_date': delivery_date,
                'notes': f'Test order {i+1}'
            }
        )
        if created:
            print(f"✓ Created test order: {order.quantity}x {order.product.name} - {order.product.size}")
    
    print("\n✅ Test data creation completed!")
    print(f"📊 Products: {LPGProduct.objects.count()}")
    print(f"📦 Orders: {Order.objects.count()}")
    print(f"🚚 Deliveries: {DeliveryLog.objects.count()}")
    print(f"👥 Users: {User.objects.count()}")

def test_reporting_views():
    """Test that reporting views work correctly"""
    print("\nTesting reporting system views...")
    
    from django.test import Client
    from django.urls import reverse
    
    client = Client()
    
    # Login as admin
    admin_user = User.objects.get(username='admin')
    client.force_login(admin_user)
    
    # Test reports dashboard
    try:
        response = client.get(reverse('core:reports_dashboard'))
        if response.status_code == 200:
            print("✓ Reports dashboard loads successfully")
        else:
            print(f"✗ Reports dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Reports dashboard error: {e}")
    
    # Test sales report
    try:
        response = client.get(reverse('core:sales_report'))
        if response.status_code == 200:
            print("✓ Sales report loads successfully")
        else:
            print(f"✗ Sales report failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Sales report error: {e}")
    
    # Test stock report
    try:
        response = client.get(reverse('core:stock_report'))
        if response.status_code == 200:
            print("✓ Stock report loads successfully")
        else:
            print(f"✗ Stock report failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Stock report error: {e}")
    
    print("\n✅ Reporting system tests completed!")

if __name__ == '__main__':
    create_test_data()
    test_reporting_views()