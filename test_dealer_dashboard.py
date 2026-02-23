#!/usr/bin/env python
"""
Test script for dealer dashboard functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_dealer_dashboard():
    print("Testing dealer dashboard functionality...")
    
    # Create a test client
    client = Client()
    
    # Get the dealer user
    try:
        dealer = User.objects.get(username='dealer')
        print(f"Found dealer user: {dealer.username}")
    except User.DoesNotExist:
        print("Error: Dealer user not found. Run setup_dealer_test_data.py first.")
        return False
    
    # Test dealer authentication
    login_success = client.login(username='dealer', password='dealer123')
    if not login_success:
        print("Error: Could not log in as dealer")
        return False
    print("✓ Dealer authentication successful")
    
    # Test main dashboard view
    dashboard_url = reverse('core:dealer_dashboard')
    response = client.get(dashboard_url)
    if response.status_code == 200:
        print("✓ Main dashboard loads successfully")
        print(f"  - Response contains dashboard stats: {'dashboard_stats' in str(response.content)}")
        print(f"  - Response contains recent orders: {'recent_orders' in str(response.content)}")
    else:
        print(f"Error: Dashboard returned status {response.status_code}")
        return False
    
    # Test dashboard stats refresh endpoint
    stats_url = reverse('core:refresh_dashboard_stats')
    response = client.get(stats_url, HTTP_HX_REQUEST='true')
    if response.status_code == 200:
        print("✓ Dashboard stats refresh endpoint works")
    else:
        print(f"Error: Stats refresh returned status {response.status_code}")
        return False
    
    # Test recent activity refresh endpoint
    activity_url = reverse('core:refresh_recent_activity')
    response = client.get(activity_url, HTTP_HX_REQUEST='true')
    if response.status_code == 200:
        print("✓ Recent activity refresh endpoint works")
    else:
        print(f"Error: Activity refresh returned status {response.status_code}")
        return False
    
    # Test non-staff user access (should be redirected)
    client.logout()
    customer = User.objects.filter(is_staff=False).first()
    if customer:
        client.login(username=customer.username, password='customer123')
        response = client.get(dashboard_url)
        if response.status_code == 302:  # Redirect to login
            print("✓ Non-staff users are properly redirected")
        else:
            print(f"Warning: Non-staff user got status {response.status_code} instead of redirect")
    
    print("\n✅ All dealer dashboard tests passed!")
    return True

if __name__ == '__main__':
    success = test_dealer_dashboard()
    sys.exit(0 if success else 1)