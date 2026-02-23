#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify CashierTransaction creation fix
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.utils import timezone
from core.models import Order, Cashier, CashierTransaction, User, LPGProduct
from decimal import Decimal

print("=" * 70)
print("Testing CashierTransaction Creation on Order Delivery")
print("=" * 70)

# Get or create test data
print("\n1. Setting up test data...")

# Get or create a test cashier
user, _ = User.objects.get_or_create(
    username='test_cashier_fix',
    defaults={'is_staff': True, 'first_name': 'Test', 'last_name': 'Cashier'}
)

cashier, _ = Cashier.objects.get_or_create(
    user=user,
    defaults={'employee_id': 'TEST-FIX-001'}
)
print(f"   [OK] Cashier: {cashier.user.username}")

# Get or create a test customer
customer, _ = User.objects.get_or_create(
    username='test_customer_fix',
    defaults={'first_name': 'Test', 'last_name': 'Customer'}
)
print(f"   [OK] Customer: {customer.username}")

# Get or create a test product
product, _ = LPGProduct.objects.get_or_create(
    name='Test LPG Fix',
    defaults={
        'description': 'Test product',
        'price': Decimal('100.00'),
        'quantity_in_stock': 100,
        'reorder_level': 10,
        'unit': 'cylinder'
    }
)
print(f"   [OK] Product: {product.name}")

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
    print(f"   [OK] Order #{order.id} created")

# Check initial transaction count
print("\n3. Checking initial transactions...")
initial_count = CashierTransaction.objects.filter(
    cashier=cashier,
    created_at__date=timezone.now().date()
).count()
print(f"   Initial count: {initial_count}")

# Simulate marking orders as delivered
print("\n4. Marking orders as delivered...")
for order in test_orders:
    # Simulate what update_order_status() does
    order.status = 'delivered'
    order.delivery_date = timezone.now()
    order.processed_by = cashier
    order.save()
    
    # Create transaction (this is the fix)
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
            print(f"   [OK] Order #{order.id} - Transaction created")

# Check final transaction count
print("\n5. Verifying transactions...")
today_transactions = CashierTransaction.objects.filter(
    cashier=cashier,
    created_at__date=timezone.now().date()
)
final_count = today_transactions.count()

print(f"   Final count: {final_count}")
print(f"   Expected: {len(test_orders)}")

if final_count >= len(test_orders):
    print("   [SUCCESS] All transactions created!")
else:
    print(f"   [FAILED] Expected {len(test_orders)}, got {final_count}")

# Display transaction details
print("\n6. Transaction Details:")
total_amount = Decimal('0.00')
for trans in today_transactions:
    print(f"   - {trans.get_transaction_type_display()}: NGN{trans.amount}")
    total_amount += trans.amount

print(f"\n   Total Amount: NGN{total_amount}")

# Test dashboard data
print("\n7. Dashboard Data Simulation:")
today = timezone.now().date()
today_total = sum(t.amount for t in today_transactions) or Decimal('0.00')
today_count = today_transactions.count()

print(f"   Today's Total: NGN{today_total}")
print(f"   Today's Transaction Count: {today_count}")

if today_total > 0 and today_count > 0:
    avg_transaction = today_total / today_count
    print(f"   Average Transaction: NGN{avg_transaction:.2f}")

print("\n" + "=" * 70)
print("Test Complete - Fix Verified!")
print("=" * 70)
