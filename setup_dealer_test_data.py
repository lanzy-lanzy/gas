#!/usr/bin/env python
"""
Script to set up test data for dealer dashboard
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import LPGProduct, Order, DeliveryLog, CustomerProfile
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

def setup_test_data():
    print("Setting up test data for dealer dashboard...")
    
    # Create a staff user (dealer) if it doesn't exist
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
        print(f"Dealer user already exists: {dealer.username}")
    
    # Create test customers if they don't exist
    customers = []
    for i in range(3):
        customer, created = User.objects.get_or_create(
            username=f'customer{i+1}',
            defaults={
                'email': f'customer{i+1}@example.com',
                'first_name': f'Customer',
                'last_name': f'{i+1}',
                'is_active': True
            }
        )
        if created:
            customer.set_password('customer123')
            customer.save()
            # Create customer profile
            CustomerProfile.objects.get_or_create(
                user=customer,
                defaults={
                    'phone_number': f'09123456{i+1:03d}',
                    'address': f'Test Address {i+1}, Tambulig',
                    'delivery_instructions': f'Test delivery instructions {i+1}'
                }
            )
            print(f"Created customer: {customer.username}")
        customers.append(customer)
    
    # Create test products if they don't exist
    products_data = [
        {'name': 'LPG Gas', 'size': '11kg', 'price': Decimal('500.00'), 'current_stock': 25, 'minimum_stock': 10},
        {'name': 'LPG Gas', 'size': '22kg', 'price': Decimal('950.00'), 'current_stock': 5, 'minimum_stock': 8},  # Low stock
        {'name': 'LPG Gas', 'size': '50kg', 'price': Decimal('2100.00'), 'current_stock': 0, 'minimum_stock': 3},  # Out of stock
    ]
    
    products = []
    for product_data in products_data:
        product, created = LPGProduct.objects.get_or_create(
            name=product_data['name'],
            size=product_data['size'],
            defaults=product_data
        )
        if created:
            print(f"Created product: {product.name} - {product.size}")
        products.append(product)
    
    # Create test orders if they don't exist
    if Order.objects.count() < 10:
        statuses = ['pending', 'out_for_delivery', 'delivered']
        delivery_types = ['pickup', 'delivery']
        
        for i in range(15):
            customer = customers[i % len(customers)]
            product = products[i % len(products)]
            
            # Skip if product is out of stock for new orders
            if product.current_stock == 0:
                continue
                
            quantity = min(2, product.current_stock)  # Don't exceed stock
            status = statuses[i % len(statuses)]
            delivery_type = delivery_types[i % len(delivery_types)]
            
            order_date = timezone.now() - timedelta(days=i % 7)
            delivery_date = order_date + timedelta(days=1) if status == 'delivered' else None
            
            order, created = Order.objects.get_or_create(
                customer=customer,
                product=product,
                quantity=quantity,
                defaults={
                    'delivery_type': delivery_type,
                    'delivery_address': customer.customer_profile.address if delivery_type == 'delivery' else 'Pickup at station',
                    'status': status,
                    'total_amount': product.price * quantity,
                    'order_date': order_date,
                    'delivery_date': delivery_date,
                    'notes': f'Test order {i+1}'
                }
            )
            if created:
                print(f"Created order: #{order.id} - {customer.username} - {product.name}")
    
    # Create test delivery logs if they don't exist
    if DeliveryLog.objects.count() < 5:
        suppliers = ['Main Distributor', 'Secondary Supplier', 'Emergency Supplier']
        
        for i, product in enumerate(products):
            if i < 3:  # Create logs for first 3 products
                delivery_date = timezone.now() - timedelta(days=i+1)
                quantity = 20 + (i * 10)
                cost_per_unit = product.price * Decimal('0.7')  # 70% of selling price
                
                delivery_log, created = DeliveryLog.objects.get_or_create(
                    product=product,
                    delivery_date=delivery_date,
                    defaults={
                        'quantity_received': quantity,
                        'supplier': suppliers[i % len(suppliers)],
                        'cost_per_unit': cost_per_unit,
                        'total_cost': cost_per_unit * quantity,
                        'logged_by': dealer,
                        'notes': f'Test delivery log {i+1}'
                    }
                )
                if created:
                    print(f"Created delivery log: {quantity}x {product.name} from {delivery_log.supplier}")
    
    print("Test data setup completed!")
    print(f"Total users: {User.objects.count()}")
    print(f"Total products: {LPGProduct.objects.count()}")
    print(f"Total orders: {Order.objects.count()}")
    print(f"Total delivery logs: {DeliveryLog.objects.count()}")

if __name__ == '__main__':
    setup_test_data()