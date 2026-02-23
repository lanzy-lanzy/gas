from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import CustomerProfile, LPGProduct, Order
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with test data for LPG dealer system'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create LPG Products
        products_data = [
            {'name': 'LPG Gas', 'size': '11kg', 'price': Decimal('500.00'), 'current_stock': 50, 'minimum_stock': 10},
            {'name': 'LPG Gas', 'size': '22kg', 'price': Decimal('950.00'), 'current_stock': 30, 'minimum_stock': 5},
            {'name': 'LPG Gas', 'size': '50kg', 'price': Decimal('2100.00'), 'current_stock': 15, 'minimum_stock': 3},
        ]
        
        for product_data in products_data:
            product, created = LPGProduct.objects.get_or_create(
                name=product_data['name'],
                size=product_data['size'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Created product: {product}')
            else:
                self.stdout.write(f'Product already exists: {product}')
        
        # Create test customer
        customer_user, created = User.objects.get_or_create(
            username=' ',
            defaults={
                'email': 'customer@test.com',
                'first_name': 'Test',
                'last_name': 'Customer'
            }
        )
        if created:
            customer_user.set_password('testpass123')
            customer_user.save()
            self.stdout.write('Created test customer user')
        
        # Create customer profile
        customer_profile, created = CustomerProfile.objects.get_or_create(
            user=customer_user,
            defaults={
                'phone_number': '+63912345678',
                'address': '123 Test Street, Tambulig, Zamboanga del Sur',
                'delivery_instructions': 'Please call when arriving'
            }
        )
        if created:
            self.stdout.write('Created customer profile')
        
        # Create admin/dealer user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@prycegas.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
        self.stdout.write('Login credentials:')
        self.stdout.write('Customer: testcustomer / testpass123')
        self.stdout.write('Admin: admin / admin123')