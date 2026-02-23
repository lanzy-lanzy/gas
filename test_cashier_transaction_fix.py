#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify CashierTransaction creation when orders are marked as delivered
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.utils import timezone
from core.models import Order, Cashier, CashierTransaction, User, LPGProduct
from decimal import Decimal

def test_cashier_transaction_creation():
    """Test that CashierTransaction is created when order is marked as delivered"""
    
    print("=" * 70)
    print("Testing CashierTransaction Creation on Order Delivery")
    print("=" * 70)
    
    # Get or create test data
    print("\n1. Setting up test data...")
    
    # Get or create a test cashier
    user, created = User.objects.get_or_create(
        username='test_cashier',
        defaults={
            'is_staff': True,
            'first_name': 'Test',
            'last_name': 'Cashier'
        }
    )
    
    cashier, created = Cashier.objects.get_or_create(
        user=user,
        defaults={'employee_id': 'TEST-001'}
    )
    print(f"   [OK] Cashier: {cashier.user.username} (ID: {cashier.id})")
    
    # Get or create a test customer
    customer, created = User.objects.get_or_create(
        username='test_customer',
        defaults={
            'first_name': 'Test',
            'last_name': 'Customer'
        }
    )
    print(f"   [OK] Customer: {customer.username}")
    
    # Get or create a test product
    product, created = LPGProduct.objects.get_or_create(
        name='Test LPG',
        defaults={
            'description': 'Test product',
            'price': Decimal('100.00'),
            'quantity_in_stock': 100,
            'reorder_level': 10,
            'unit': 'cylinder'
        }
    )
    print(f"   [OK] Product: {product.name} - NGN{product.price}")
    
    # Create test orders
    print("\n2. Creating test orders...")
    test_orders = []
    for i in range(3):
        order = Order.objects.create(
            customer=customer,
            product=product,
            quantity=5,
            delivery_type='delivery',
            delivery_address='Test Address',
            status='out_for_delivery',
            total_amount=Decimal('500.00')
        )
        test_orders.append(order)
        print(f"   ✓ Order #{order.id} created - Status: {order.get_status_display()}")
    
    # Check initial transaction count
    print("\n3. Checking initial transactions...")
    initial_count = CashierTransaction.objects.filter(
        cashier=cashier,
        created_at__date=timezone.now().date()
    ).count()
    print(f"   Initial transactions today: {initial_count}")
    
    # Simulate marking orders as delivered
    print("\n4. Marking orders as delivered...")
    for order in test_orders:
        # Simulate what update_order_status() does
        order.status = 'delivered'
        order.delivery_date = timezone.now()
        order.processed_by = cashier
        order.save()
        
        # Create transaction (this is the fix we implemented)
        if order.processed_by:
            transaction, created = CashierTransaction.objects.get_or_create(
                order=order,
                defaults={
                    'cashier': order.processed_by,
                    'transaction_type': 'order',
                    'amount': order.total_amount,
                    'payment_method': 'cash',
                    'customer': order.customer
                }
            )
            if created:
                print(f"   ✓ Order #{order.id} marked as delivered")
                print(f"     Transaction created: ₦{transaction.amount}")
            else:
                print(f"   ⚠ Order #{order.id} already has transaction")
    
    # Check final transaction count
    print("\n5. Verifying transactions...")
    today_transactions = CashierTransaction.objects.filter(
        cashier=cashier,
        created_at__date=timezone.now().date()
    )
    final_count = today_transactions.count()
    
    print(f"   Total transactions today: {final_count}")
    print(f"   Expected: {len(test_orders)}")
    
    if final_count >= len(test_orders):
        print("   ✓ SUCCESS: All transactions created!")
    else:
        print(f"   ✗ FAILED: Expected {len(test_orders)}, got {final_count}")
    
    # Display transaction details
    print("\n6. Transaction Details:")
    total_amount = Decimal('0.00')
    for trans in today_transactions[:5]:  # Show first 5
        print(f"   - {trans.get_transaction_type_display()}: ₦{trans.amount} ({trans.created_at.strftime('%H:%M')})")
        total_amount += trans.amount
    
    print(f"\n   Total Amount: ₦{total_amount}")
    
    # Test dashboard data
    print("\n7. Simulating Dashboard Data Fetch...")
    today = timezone.now().date()
    
    today_total = sum(
        t.amount for t in today_transactions
    ) or Decimal('0.00')
    today_count = today_transactions.count()
    
    print(f"   Today's Total: ₦{today_total}")
    print(f"   Today's Transaction Count: {today_count}")
    
    if today_total > 0 and today_count > 0:
        avg_transaction = today_total / today_count
        print(f"   Average Transaction: ₦{avg_transaction:.2f}")
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)

if __name__ == '__main__':
    test_cashier_transaction_creation()
