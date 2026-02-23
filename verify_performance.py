#!/usr/bin/env python
"""
Simple verification script for performance optimizations
"""

import requests
import time
import sys

def test_page_performance(url, expected_max_time=2.0):
    """Test page load performance"""
    print(f"Testing {url}...")
    
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        duration = end_time - start_time
        
        print(f"  Status: {response.status_code}")
        print(f"  Load time: {duration:.2f}s")
        
        # Check for performance headers
        if 'X-Response-Time' in response.headers:
            print(f"  Server time: {response.headers['X-Response-Time']}")
        
        if 'X-Query-Count' in response.headers:
            print(f"  DB queries: {response.headers['X-Query-Count']}")
        
        if 'Cache-Control' in response.headers:
            print(f"  Cache: {response.headers['Cache-Control']}")
        
        # Check performance
        if duration > expected_max_time:
            print(f"  ⚠️  SLOW: Expected < {expected_max_time}s")
            return False
        else:
            print(f"  ✅ GOOD: Within {expected_max_time}s limit")
            return True
            
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        return False

def main():
    """Run performance verification tests"""
    print("Performance Optimization Verification")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test pages
    test_urls = [
        f"{base_url}/",
        f"{base_url}/login/",
        f"{base_url}/register/",
    ]
    
    results = []
    
    for url in test_urls:
        result = test_page_performance(url, 2.0)
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All performance tests passed!")
        return 0
    else:
        print("⚠️  Some performance issues detected")
        return 1

if __name__ == '__main__':
    print("Note: Make sure Django development server is running on http://127.0.0.1:8000")
    print("Run: python manage.py runserver")
    print()
    
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)