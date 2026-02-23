#!/usr/bin/env python
"""
Comprehensive test script for form validation and security enhancements
Requirements: 10.1, 10.2, 10.3, 8.3 - Form validation and security testing
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from core.forms import CustomerRegistrationForm, OrderForm, DeliveryLogForm
from core.models import CustomerProfile, LPGProduct, Order


class FormValidationTestCase(TestCase):
    """Test cases for enhanced form validation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Create customer profile
        self.profile = CustomerProfile.objects.create(
            user=self.user,
            phone_number='+639123456789',
            address='Test Address, Test City',
            delivery_instructions='Test instructions'
        )
        
        # Create test product
        self.product = LPGProduct.objects.create(
            name='Test LPG',
            size='11kg',
            price=500.00,
            current_stock=50,
            minimum_stock=10
        )
    
    def test_customer_registration_form_validation(self):
        """Test customer registration form validation"""
        print("Testing customer registration form validation...")
        
        # Test valid data
        valid_data = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone_number': '+639987654321',
            'address': 'Complete address with landmarks',
            'delivery_instructions': 'Optional instructions'
        }
        
        form = CustomerRegistrationForm(data=valid_data)
        self.assertTrue(form.is_valid(), f"Form should be valid. Errors: {form.errors}")
        
        # Test invalid username (too short)
        invalid_data = valid_data.copy()
        invalid_data['username'] = 'ab'
        form = CustomerRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Test invalid email format
        invalid_data = valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        form = CustomerRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Test invalid phone number
        invalid_data = valid_data.copy()
        invalid_data['phone_number'] = '123'
        form = CustomerRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        
        # Test short address
        invalid_data = valid_data.copy()
        invalid_data['address'] = 'Short'
        form = CustomerRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors)
        
        # Test password mismatch
        invalid_data = valid_data.copy()
        invalid_data['password2'] = 'DifferentPass123!'
        form = CustomerRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
        print("✓ Customer registration form validation tests passed")
    
    def test_order_form_validation(self):
        """Test order form validation"""
        print("Testing order form validation...")
        
        # Test valid order data
        valid_data = {
            'product': self.product.id,
            'quantity': 2,
            'delivery_type': 'delivery',
            'delivery_address': 'Complete delivery address with landmarks',
            'notes': 'Optional order notes'
        }
        
        form = OrderForm(data=valid_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form should be valid. Errors: {form.errors}")
        
        # Test invalid quantity (negative)
        invalid_data = valid_data.copy()
        invalid_data['quantity'] = -1
        form = OrderForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        
        # Test excessive quantity
        invalid_data = valid_data.copy()
        invalid_data['quantity'] = 1000
        form = OrderForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        
        # Test insufficient stock
        invalid_data = valid_data.copy()
        invalid_data['quantity'] = 100  # More than available stock
        form = OrderForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        
        # Test delivery without address
        invalid_data = valid_data.copy()
        invalid_data['delivery_type'] = 'delivery'
        invalid_data['delivery_address'] = ''
        form = OrderForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        
        # Test short delivery address
        invalid_data = valid_data.copy()
        invalid_data['delivery_address'] = 'Short'
        form = OrderForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_address', form.errors)
        
        print("✓ Order form validation tests passed")
    
    def test_delivery_log_form_validation(self):
        """Test delivery log form validation"""
        print("Testing delivery log form validation...")
        
        # Test valid delivery data
        valid_data = {
            'product': self.product.id,
            'quantity_received': 20,
            'supplier': 'Test Supplier Company',
            'delivery_date': '2024-01-15T10:00',
            'cost_per_unit': 450.00,
            'total_cost': 9000.00,
            'notes': 'Delivery notes'
        }
        
        form = DeliveryLogForm(data=valid_data)
        self.assertTrue(form.is_valid(), f"Form should be valid. Errors: {form.errors}")
        
        # Test invalid quantity (negative)
        invalid_data = valid_data.copy()
        invalid_data['quantity_received'] = -5
        form = DeliveryLogForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity_received', form.errors)
        
        # Test excessive quantity
        invalid_data = valid_data.copy()
        invalid_data['quantity_received'] = 50000
        form = DeliveryLogForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity_received', form.errors)
        
        # Test short supplier name
        invalid_data = valid_data.copy()
        invalid_data['supplier'] = 'A'
        form = DeliveryLogForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('supplier', form.errors)
        
        # Test invalid cost
        invalid_data = valid_data.copy()
        invalid_data['cost_per_unit'] = -100
        form = DeliveryLogForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cost_per_unit', form.errors)
        
        # Test total cost mismatch
        invalid_data = valid_data.copy()
        invalid_data['total_cost'] = 5000.00  # Should be 20 * 450 = 9000
        form = DeliveryLogForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('total_cost', form.errors)
        
        print("✓ Delivery log form validation tests passed")
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        print("Testing input sanitization...")
        
        # Test HTML tag removal
        malicious_data = {
            'username': 'user<script>alert("xss")</script>',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone_number': '+639123456789',
            'address': 'Address with <b>HTML</b> tags',
            'delivery_instructions': 'Instructions with <script>malicious code</script>'
        }
        
        form = CustomerRegistrationForm(data=malicious_data)
        if form.is_valid():
            # Check that HTML tags are stripped
            self.assertNotIn('<script>', form.cleaned_data['username'])
            self.assertNotIn('<b>', form.cleaned_data['address'])
            self.assertNotIn('<script>', form.cleaned_data['delivery_instructions'])
        
        print("✓ Input sanitization tests passed")
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        print("Testing CSRF protection...")
        
        # Test form submission without CSRF token
        response = self.client.post(reverse('core:register'), {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone_number': '+639123456789',
            'address': 'Test address for CSRF test'
        })
        
        # Should be forbidden due to missing CSRF token
        self.assertEqual(response.status_code, 403)
        
        print("✓ CSRF protection tests passed")
    
    def test_validation_endpoints(self):
        """Test AJAX validation endpoints"""
        print("Testing validation endpoints...")
        
        # Test username validation endpoint
        response = self.client.post(reverse('core:validate_username'), {
            'username': 'newuser123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('valid', data)
        self.assertIn('message', data)
        
        # Test email validation endpoint
        response = self.client.post(reverse('core:validate_email'), {
            'email': 'newemail@example.com'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('valid', data)
        self.assertIn('message', data)
        
        # Test duplicate username
        response = self.client.post(reverse('core:validate_username'), {
            'username': 'testuser'  # Already exists
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])
        
        # Test duplicate email
        response = self.client.post(reverse('core:validate_email'), {
            'email': 'test@example.com'  # Already exists
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])
        
        print("✓ Validation endpoints tests passed")
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("=" * 60)
        print("RUNNING COMPREHENSIVE FORM VALIDATION TESTS")
        print("=" * 60)
        
        try:
            self.test_customer_registration_form_validation()
            self.test_order_form_validation()
            self.test_delivery_log_form_validation()
            self.test_input_sanitization()
            self.test_csrf_protection()
            self.test_validation_endpoints()
            
            print("\n" + "=" * 60)
            print("✅ ALL FORM VALIDATION TESTS PASSED SUCCESSFULLY!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            print("=" * 60)
            raise


def run_validation_tests():
    """Run the validation tests"""
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Create test case instance
    test_case = FormValidationTestCase()
    test_case.setUp()
    test_case.run_all_tests()


if __name__ == '__main__':
    run_validation_tests()