"""
Create test delivery data for the Delivery Log page
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import LPGProduct, DeliveryLog
from django.utils import timezone

# Get or create a test user
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    print("Error: Admin user does not exist. Please create an admin user first.")
    exit(1)

# Get products
products = LPGProduct.objects.filter(is_active=True)
if not products.exists():
    print("Error: No active products found. Please create products first.")
    exit(1)

# Create test deliveries
suppliers = ['Shell Gas', 'Petron LPG', 'Global Gas Ltd', 'Seaoil Distributors', 'Victory Gasul']
now = timezone.now()

print("Creating test delivery records...")

for i in range(10):
    product = products[i % len(products)]
    supplier = suppliers[i % len(suppliers)]
    delivery_date = now - timedelta(days=i)
    quantity = 50 + (i * 10)
    cost_per_unit = 25.50 + (i * 0.5)
    
    delivery = DeliveryLog.objects.create(
        product=product,
        quantity_received=quantity,
        supplier_name=supplier,
        delivery_date=delivery_date,
        cost_per_unit=cost_per_unit,
        total_cost=quantity * cost_per_unit,
        logged_by=admin_user,
        notes=f'Test delivery {i+1}'
    )
    print(f"Created delivery: {delivery}")

print(f"\nTotal deliveries created: {DeliveryLog.objects.count()}")
