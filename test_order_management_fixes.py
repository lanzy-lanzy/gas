#!/usr/bin/env python
"""
Test script to verify the order management fixes
Tests the routing, template rendering, and HTMX functionality
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from decimal import Decimal
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from core.models import CustomerProfile, LPGProduct, Order


class OrderManagementFixesTestCase(TestCase):
    """Test cases for the order management fixes"""
    
    def setUp(self):
        """Set up test data"""
        # Create dealer user (superuser for dealer permissions)
        self.dealer = User.objects.create_superuser(
            username='dealer',
            email='dealer@example.com',
            password='dealerpass123'
        )
        
        # Create customer user
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpass123'
        )
        
        # Create customer profile
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer,
            phone_number='+63912345678',
            address='123 Test Street, Test City',
            delivery_instructions='Test instructions'
        )
        
        # Create test product
        self.product = LPGProduct.objects.create(
            name='LPG Gas',
            size='11kg',
            price=Decimal('500.00'),
            current_stock=50,
            minimum_stock=10,
            is_active=True
        )
        
        # Create test orders
        self.order1 = Order.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=2,
            delivery_type='delivery',
            delivery_address='123 Test Street',
            status='pending',
            total_amount=Decimal('1000.00')
        )
        
        self.order2 = Order.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=1,
            delivery_type='pickup',
            delivery_address='Pickup at station',
            status='out_for_delivery',
            total_amount=Decimal('500.00')
        )
        
        self.client = Client()
    
    def test_order_management_page_loads(self):
        """Test that order management page loads correctly for dealers"""
        self.client.login(username='dealer', password='dealerpass123')
        response = self.client.get(reverse('core:order_management'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order Management')
        self.assertContains(response, 'Orders')
        
    def test_order_management_pagination(self):
        """Test that pagination works correctly"""
        self.client.login(username='dealer', password='dealerpass123')
        response = self.client.get(reverse('core:order_management'))
        
        # Check that pagination context is provided
        self.assertIn('page_obj', response.context)
        self.assertIn('is_paginated', response.context)
        
    def test_refresh_order_table_htmx(self):
        """Test HTMX refresh order table endpoint"""
        self.client.login(username='dealer', password='dealerpass123')
        
        # Make HTMX request
        response = self.client.get(
            reverse('core:refresh_order_table'),
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order #')
        
    def test_refresh_order_table_pagination_consistency(self):
        """Test that refresh endpoint maintains pagination consistency"""
        self.client.login(username='dealer', password='dealerpass123')
        
        # Test with page parameter
        response = self.client.get(
            reverse('core:refresh_order_table') + '?page=1',
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        # Should contain pagination elements
        self.assertContains(response, 'Showing')
        
    def test_order_detail_modal_htmx(self):
        """Test order detail modal HTMX endpoint"""
        self.client.login(username='dealer', password='dealerpass123')
        
        response = self.client.get(
            reverse('core:order_detail_modal', args=[self.order1.id]),
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Order #{self.order1.id}')
        self.assertContains(response, self.customer.username)
        
    def test_update_order_status_htmx(self):
        """Test order status update with HTMX"""
        self.client.login(username='dealer', password='dealerpass123')
        
        response = self.client.post(
            reverse('core:update_order_status', args=[self.order1.id]),
            {'status': 'out_for_delivery'},
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that order status was updated
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'out_for_delivery')
        
    def test_update_order_status_error_handling(self):
        """Test error handling in order status update"""
        self.client.login(username='dealer', password='dealerpass123')
        
        # Try invalid status
        response = self.client.post(
            reverse('core:update_order_status', args=[self.order1.id]),
            {'status': 'invalid_status'},
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Invalid status', data['message'])
        
    def test_bulk_order_operations_htmx(self):
        """Test bulk order operations with HTMX"""
        self.client.login(username='dealer', password='dealerpass123')
        
        response = self.client.post(
            reverse('core:bulk_order_operations'),
            {
                'operation': 'mark_out_for_delivery',
                'order_ids': [self.order1.id]
            },
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
    def test_bulk_order_operations_error_handling(self):
        """Test error handling in bulk operations"""
        self.client.login(username='dealer', password='dealerpass123')
        
        # Test with no orders selected
        response = self.client.post(
            reverse('core:bulk_order_operations'),
            {'operation': 'mark_delivered'},
            HTTP_HX_REQUEST='true'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('No orders selected', data['message'])
        
    def test_order_management_filters(self):
        """Test that filtering works correctly"""
        self.client.login(username='dealer', password='dealerpass123')
        
        # Test status filter
        response = self.client.get(
            reverse('core:order_management') + '?status=pending'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order Management')
        
    def test_non_htmx_fallback(self):
        """Test that non-HTMX requests are handled properly"""
        self.client.login(username='dealer', password='dealerpass123')
        
        # Test refresh endpoint without HTMX header
        response = self.client.get(reverse('core:refresh_order_table'))
        
        # Should redirect to main order management page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:order_management'))


def run_tests():
    """Run the test cases"""
    import unittest
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(OrderManagementFixesTestCase)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
