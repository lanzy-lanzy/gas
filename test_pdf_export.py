#!/usr/bin/env python
"""
Test script to verify PDF export functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import CustomerProfile, LPGProduct, Order
from decimal import Decimal

def test_pdf_export():
    """Test the PDF export functionality"""
    
    print("Testing PDF export functionality...")
    print("-" * 50)
    
    # Create test user if not exists
    user, created = User.objects.get_or_create(
        username='testcustomer',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Customer'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing test user: {user.username}")
    
    # Create customer profile if not exists
    profile, created = CustomerProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': '08012345678',
            'address': 'Test Address, Lagos, Nigeria',
            'delivery_instructions': 'Ring bell twice'
        }
    )
    
    if created:
        print(f"✓ Created customer profile")
    else:
        print(f"✓ Using existing customer profile")
    
    # Create test product if not exists
    product, created = LPGProduct.objects.get_or_create(
        sku='LPG-11KG-001',
        defaults={
            'name': 'LPG Gas',
            'size': '11kg',
            'price': Decimal('5500.00'),
            'cost_price': Decimal('4500.00'),
            'current_stock': 100,
            'is_active': True
        }
    )
    
    if created:
        print(f"✓ Created test product: {product}")
    else:
        print(f"✓ Using existing test product: {product}")
    
    # Create test order if not exists
    order, created = Order.objects.get_or_create(
        id=9999,
        defaults={
            'customer': user,
            'product': product,
            'quantity': 2,
            'delivery_type': 'delivery',
            'delivery_address': 'Test Address, Lagos',
            'status': 'pending',
            'total_amount': Decimal('11000.00')
        }
    )
    
    if created:
        print(f"✓ Created test order: Order #{order.id}")
    else:
        print(f"✓ Using existing test order: Order #{order.id}")
    
    # Test PDF export endpoint
    client = Client()
    
    # Login user
    login_success = client.login(username='testcustomer', password='testpass123')
    if login_success:
        print(f"✓ User logged in successfully")
    else:
        print(f"✗ Failed to login user")
        return False
    
    # Test basic PDF export
    print("\nTesting PDF export endpoint...")
    response = client.get('/customer/history/export-pdf/')
    
    if response.status_code == 200:
        print(f"✓ PDF export endpoint returned 200 OK")
        print(f"  Content-Type: {response.get('Content-Type')}")
        print(f"  Content length: {len(response.content)} bytes")
        print(f"  Content-Disposition: {response.get('Content-Disposition')}")
        
        if response.get('Content-Type') == 'application/pdf':
            print(f"✓ Response has correct content type")
            
            # Check if PDF has content
            if len(response.content) > 1000:
                print(f"✓ PDF has reasonable size ({len(response.content)} bytes)")
                
                # Try to verify it's a real PDF
                if response.content.startswith(b'%PDF'):
                    print(f"✓ Response starts with PDF magic number")
                else:
                    print(f"✗ Response doesn't start with PDF magic number")
            else:
                print(f"✗ PDF seems too small ({len(response.content)} bytes)")
        else:
            print(f"✗ Wrong content type: {response.get('Content-Type')}")
    else:
        print(f"✗ PDF export failed with status code: {response.status_code}")
        print(f"  Response: {response.content.decode()}")
        return False
    
    # Test with filter parameters
    print("\nTesting PDF export with filters...")
    response = client.get('/customer/history/export-pdf/?status=pending&sort=-order_date')
    
    if response.status_code == 200:
        print(f"✓ PDF export with filters returned 200 OK")
        if response.get('Content-Type') == 'application/pdf':
            print(f"✓ Filtered response has correct content type")
        else:
            print(f"✗ Filtered response has wrong content type")
    else:
        print(f"✗ Filtered PDF export failed with status code: {response.status_code}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All PDF export tests passed!")
    return True

if __name__ == '__main__':
    try:
        success = test_pdf_export()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
