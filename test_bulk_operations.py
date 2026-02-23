#!/usr/bin/env python
"""
Test script for bulk operations functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from core.models import Order, LPGProduct
import json

def test_bulk_operations():
    print("Testing bulk operations functionality...")
    
    # Create a test client
    client = Client()
    
    # Get or create dealer user
    dealer, created = User.objects.get_or_create(
        username='dealer',
        defaults={
            'email': 'dealer@prycegas.com',
            'first_name': 'John',
            'last_name': 'Dealer',
            'is_staff': True,
            'is_active': True
        }
    )
    if created:
        dealer.set_password('dealer123')
        dealer.save()
        print(f"Created dealer user: {dealer.username}")
    else:
        print(f"Found dealer user: {dealer.username}, is_staff: {dealer.is_staff}")
    
    # Login as dealer
    login_success = client.login(username='dealer', password='dealer123')
    if not login_success:
        print("Error: Could not log in as dealer")
        return False
    print("✓ Dealer authentication successful")
    
    # Check if there are orders
    orders = Order.objects.all()
    print(f"Total orders in database: {orders.count()}")

    # Show order statuses
    if orders.exists():
        status_counts = {}
        for order in orders:
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1
        print(f"Order statuses: {status_counts}")

    if orders.count() == 0:
        print("No orders found. Creating test orders...")
        # Create test customer and product
        customer, _ = User.objects.get_or_create(
            username='testcustomer',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Customer',
                'is_active': True
            }
        )
        
        product, _ = LPGProduct.objects.get_or_create(
            name='LPG Gas',
            defaults={
                'size': '11kg',
                'price': 500.00,
                'stock_quantity': 100,
                'is_active': True
            }
        )
        
        # Create test orders
        for i in range(3):
            Order.objects.create(
                customer=customer,
                product=product,
                quantity=1,
                delivery_type='pickup',
                delivery_address='Test Address',
                status='pending',
                total_amount=500.00
            )
        
        orders = Order.objects.all()
        print(f"Created {orders.count()} test orders")
    
    # Get some pending orders for testing
    pending_orders = orders.filter(status='pending')[:2]
    if not pending_orders.exists():
        print("No pending orders found. Creating some pending orders for testing...")

        # Get first customer and product
        customer = User.objects.filter(is_staff=False).first()
        product = LPGProduct.objects.first()

        if customer and product:
            # Create 2 pending orders
            for i in range(2):
                Order.objects.create(
                    customer=customer,
                    product=product,
                    quantity=1,
                    delivery_type='pickup',
                    delivery_address='Test Address',
                    status='pending',
                    total_amount=product.price
                )

            pending_orders = Order.objects.filter(status='pending')[:2]
            print(f"Created {pending_orders.count()} pending orders")
        else:
            print("Could not create test orders - missing customer or product")
            return False
    
    order_ids = [str(order.id) for order in pending_orders]
    print(f"Testing with order IDs: {order_ids}")
    
    # Test bulk operation
    bulk_url = reverse('core:bulk_order_operations')
    print(f"Bulk operations URL: {bulk_url}")
    
    # Prepare POST data
    post_data = {
        'operation': 'mark_out_for_delivery',
        'order_ids': order_ids
    }
    
    print(f"Sending POST data: {post_data}")
    
    # Make the request
    response = client.post(
        bulk_url,
        data=post_data,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        HTTP_HX_REQUEST='true'
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.items())}")
    
    if response.status_code == 200:
        try:
            response_data = json.loads(response.content)
            print(f"Response JSON: {response_data}")
            
            if response_data.get('success'):
                print("✓ Bulk operation successful!")
                
                # Verify orders were updated
                updated_orders = Order.objects.filter(id__in=[int(id) for id in order_ids])
                for order in updated_orders:
                    print(f"Order #{order.id} status: {order.status}")
                
                return True
            else:
                print(f"✗ Bulk operation failed: {response_data.get('message')}")
                return False
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON response: {response.content}")
            return False
    else:
        print(f"✗ HTTP error {response.status_code}: {response.content}")
        return False

if __name__ == '__main__':
    success = test_bulk_operations()
    sys.exit(0 if success else 1)
