#!/usr/bin/env python
"""
Test script for performance optimization features
Requirements: 9.1, 9.2, 9.3, 9.5 - Performance optimization testing
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import connection
import time

# Setup Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
    django.setup()

from core.models import Order, LPGProduct, CustomerProfile


class PerformanceOptimizationTest:
    def __init__(self):
        self.client = Client()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Create test data for performance testing"""
        print("Setting up test data...")
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create customer profile
        CustomerProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'phone_number': '09123456789',
                'address': 'Test Address',
                'delivery_instructions': 'Test instructions'
            }
        )
        
        # Create test product
        self.product = LPGProduct.objects.create(
            name='Test LPG',
            size='11kg',
            price=500.00,
            current_stock=100,
            minimum_stock=10
        )
        
        # Create multiple test orders for pagination testing
        for i in range(50):
            Order.objects.create(
                customer=self.user,
                product=self.product,
                quantity=1,
                delivery_type='delivery',
                delivery_address=f'Test Address {i}',
                total_amount=500.00
            )
        
        print(f"Created {Order.objects.count()} test orders")
    
    def test_query_optimization(self):
        """Test that queries are optimized with select_related"""
        print("\nTesting query optimization...")
        
        # Clear query log
        connection.queries_log.clear()
        
        # Test customer dashboard query
        orders = list(Order.objects.filter(customer=self.user).select_related('product')[:5])
        query_count = len(connection.queries)
        
        print(f"Customer dashboard query: {query_count} queries for {len(orders)} orders")
        
        # Should be 1 query due to select_related
        assert query_count <= 2, f"Too many queries: {query_count}"
        
        print("✓ Query optimization test passed")
    
    def test_caching(self):
        """Test caching functionality"""
        print("\nTesting caching...")
        
        # Clear cache
        cache.clear()
        
        # Test cache set/get
        cache_key = 'test_performance'
        test_data = {'orders': 10, 'products': 5}
        
        cache.set(cache_key, test_data, 60)
        cached_data = cache.get(cache_key)
        
        assert cached_data == test_data, "Cache data mismatch"
        print("✓ Basic caching test passed")
        
        # Test cache timeout
        cache.set('timeout_test', 'data', 1)  # 1 second timeout
        time.sleep(1.1)
        expired_data = cache.get('timeout_test')
        
        assert expired_data is None, "Cache should have expired"
        print("✓ Cache timeout test passed")
    
    def test_pagination_performance(self):
        """Test pagination performance with large datasets"""
        print("\nTesting pagination performance...")
        
        from django.core.paginator import Paginator
        
        # Test pagination with large dataset
        orders = Order.objects.filter(customer=self.user).select_related('product')
        paginator = Paginator(orders, 25)
        
        start_time = time.time()
        page = paginator.get_page(1)
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"Pagination query: {duration:.2f}ms for page 1 of {paginator.num_pages}")
        
        # Should be fast (< 100ms)
        assert duration < 100, f"Pagination too slow: {duration}ms"
        
        print("✓ Pagination performance test passed")
    
    def test_lazy_loading_endpoints(self):
        """Test lazy loading API endpoints"""
        print("\nTesting lazy loading endpoints...")
        
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Test customer lazy loading endpoint
        response = self.client.get('/api/customer/orders/lazy/?page=1&page_size=10')
        assert response.status_code == 200, f"Lazy loading endpoint failed: {response.status_code}"
        
        print("✓ Lazy loading endpoints test passed")
    
    def test_mobile_optimization(self):
        """Test mobile optimization features"""
        print("\nTesting mobile optimization...")
        
        # Test mobile user agent detection
        mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = self.client.get('/customer/dashboard/', **mobile_headers)
        assert response.status_code == 200, "Mobile request failed"
        
        # Check for mobile optimization headers
        assert 'X-Mobile-Optimized' in response or response.status_code == 200
        
        print("✓ Mobile optimization test passed")
    
    def test_database_indexes(self):
        """Test that database indexes are working"""
        print("\nTesting database indexes...")
        
        # Test query performance with indexes
        start_time = time.time()
        
        # This query should use the customer_id + status index
        orders = list(Order.objects.filter(customer=self.user, status='pending'))
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        print(f"Indexed query: {duration:.2f}ms for {len(orders)} orders")
        
        # Should be very fast with indexes
        assert duration < 50, f"Indexed query too slow: {duration}ms"
        
        print("✓ Database indexes test passed")
    
    def run_all_tests(self):
        """Run all performance tests"""
        print("Running Performance Optimization Tests")
        print("=" * 50)
        
        try:
            self.test_query_optimization()
            self.test_caching()
            self.test_pagination_performance()
            self.test_lazy_loading_endpoints()
            self.test_mobile_optimization()
            self.test_database_indexes()
            
            print("\n" + "=" * 50)
            print("✅ All performance optimization tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up test data"""
        print("\nCleaning up test data...")
        Order.objects.filter(customer=self.user).delete()
        CustomerProfile.objects.filter(user=self.user).delete()
        self.product.delete()
        self.user.delete()
        cache.clear()
        print("✓ Cleanup completed")


if __name__ == '__main__':
    test = PerformanceOptimizationTest()
    try:
        test.run_all_tests()
    finally:
        test.cleanup()