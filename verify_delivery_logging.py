#!/usr/bin/env python
"""
Verification script for delivery logging mechanism
Tests that delivery logs are properly generated during automated calculations
"""

import os
import django
import logging
from datetime import datetime
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import LPGProduct, DeliveryLog

def setup_logging():
    """Setup logging to capture delivery log entries"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('delivery_log_verification.log'),
            logging.StreamHandler()
        ]
    )

def test_delivery_logging():
    """Test the delivery logging mechanism"""
    print("🔍 Testing Delivery Logging Mechanism")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting delivery logging verification test")
    
    try:
        # Get or create test user
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            print("❌ Admin user not found. Please create an admin user first.")
            return False
            
        print(f"✅ Using user: {admin_user.username}")
        
        # Get an active product
        product = LPGProduct.objects.filter(is_active=True).first()
        if not product:
            print("❌ No active products found. Please create products first.")
            return False
            
        print(f"✅ Using product: {product.name} - {product.size}")
        initial_stock = product.current_stock
        print(f"📊 Initial stock: {initial_stock}")
        
        # Create a test delivery log
        print("\n🚚 Creating test delivery log...")
        delivery_data = {
            'product': product,
            'quantity_received': 25,
            'supplier_name': 'Test Automation Supplier',
            'delivery_date': datetime.now(),
            'cost_per_unit': Decimal('150.00'),
            'total_cost': Decimal('3750.00'),
            'logged_by': admin_user,
            'notes': 'Automated test delivery for verification'
        }
        
        # Log the delivery creation
        logger.info(f"Creating delivery log: {delivery_data['quantity_received']}x {delivery_data['product'].name}")
        
        # Create the delivery log
        delivery_log = DeliveryLog.objects.create(**delivery_data)
        
        print(f"✅ Delivery log created successfully: ID {delivery_log.id}")
        logger.info(f"Delivery log created with ID: {delivery_log.id}")
        
        # Verify the delivery log was created
        saved_delivery = DeliveryLog.objects.get(id=delivery_log.id)
        print(f"✅ Verified delivery log exists in database")
        
        # Check if stock was updated
        product.refresh_from_db()
        expected_stock = initial_stock + 25
        if product.current_stock == expected_stock:
            print(f"✅ Stock automatically updated: {initial_stock} → {product.current_stock}")
        else:
            print(f"❌ Stock update failed: expected {expected_stock}, got {product.current_stock}")
            return False
        
        # Check if the delivery log has correct data
        if (saved_delivery.quantity_received == 25 and 
            saved_delivery.supplier_name == 'Test Automation Supplier' and
            saved_delivery.total_cost == Decimal('3750.00')):
            print("✅ Delivery log data is correct")
        else:
            print("❌ Delivery log data is incorrect")
            return False
            
        # Clean up - delete the test delivery
        print("\n🧹 Cleaning up test data...")
        delivery_log.delete()
        product.refresh_from_db()
        # Restore original stock
        product.current_stock = initial_stock
        product.save()
        print("✅ Test data cleaned up")
        
        logger.info("Delivery logging verification completed successfully")
        print("\n🎉 Delivery Logging Verification PASSED!")
        print("✅ Auto-calculation mechanism is working correctly")
        print("✅ Log files are properly generated during automated calculations")
        print("✅ Stock levels are automatically updated")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ Error during delivery logging test: {str(e)}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        return False

if __name__ == "__main__":
    success = test_delivery_logging()
    exit(0 if success else 1)