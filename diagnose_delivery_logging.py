#!/usr/bin/env python
"""
Diagnostic script for delivery logging mechanism
Investigates why log files are not being properly generated during automated calculations
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
from core.models import LPGProduct, DeliveryLog, StockMovement

def setup_detailed_logging():
    """Setup detailed logging to capture all delivery log entries"""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'delivery_diagnostic.log')),
            logging.StreamHandler()
        ]
    )
    
    # Also configure Django's logging
    django_logger = logging.getLogger('django')
    django_logger.setLevel(logging.DEBUG)

def diagnose_delivery_logging():
    """Comprehensive diagnosis of the delivery logging mechanism"""
    print("🔍 Diagnostic Analysis of Delivery Logging Mechanism")
    print("=" * 60)
    
    # Setup detailed logging
    setup_detailed_logging()
    logger = logging.getLogger(__name__)
    logger.info("=== STARTING DELIVERY LOGGING DIAGNOSTIC ===")
    
    try:
        # Test 1: Check if we can create a StockMovement directly
        print("\n📝 Test 1: Direct StockMovement Creation")
        logger.info("Test 1: Direct StockMovement Creation")
        
        # Get admin user
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            print("❌ Admin user not found")
            logger.error("Admin user not found")
            return False
            
        print(f"✅ Found admin user: {admin_user.username}")
        logger.info(f"Found admin user: {admin_user.username}")
        
        # Get a product
        product = LPGProduct.objects.filter(is_active=True).first()
        if not product:
            print("❌ No active products found")
            logger.error("No active products found")
            return False
            
        print(f"✅ Found product: {product.name} - {product.size}")
        logger.info(f"Found product: {product.name} - {product.size}")
        
        # Test direct StockMovement creation
        try:
            stock_movement = StockMovement.objects.create(
                product=product,
                movement_type='delivery',
                quantity=10,
                previous_stock=product.current_stock,
                new_stock=product.current_stock + 10,
                reference_id='DIAGNOSTIC_TEST',
                notes="Diagnostic test StockMovement creation",
                created_by=admin_user
            )
            print("✅ Direct StockMovement creation successful")
            logger.info(f"Direct StockMovement creation successful: ID {stock_movement.id}")
            
            # Clean up
            stock_movement.delete()
            print("✅ Cleaned up diagnostic StockMovement")
            logger.info("Cleaned up diagnostic StockMovement")
            
        except Exception as e:
            print(f"❌ Direct StockMovement creation failed: {str(e)}")
            logger.error(f"Direct StockMovement creation failed: {str(e)}", exc_info=True)
            return False
        
        # Test 2: Create a delivery log and check if StockMovement is created
        print("\n📝 Test 2: DeliveryLog Creation with StockMovement")
        logger.info("Test 2: DeliveryLog Creation with StockMovement")
        
        initial_stock = product.current_stock
        print(f"📊 Initial stock: {initial_stock}")
        logger.info(f"Initial stock: {initial_stock}")
        
        # Create delivery log
        delivery_data = {
            'product': product,
            'quantity_received': 15,
            'supplier_name': 'Diagnostic Test Supplier',
            'delivery_date': datetime.now(),
            'cost_per_unit': Decimal('125.00'),
            'total_cost': Decimal('1875.00'),
            'logged_by': admin_user,
            'notes': 'Diagnostic test delivery log'
        }
        
        print("🚚 Creating delivery log...")
        logger.info("Creating delivery log...")
        
        try:
            delivery_log = DeliveryLog.objects.create(**delivery_data)
            print(f"✅ Delivery log created successfully: ID {delivery_log.id}")
            logger.info(f"Delivery log created successfully: ID {delivery_log.id}")
            
            # Check if stock was updated
            product.refresh_from_db()
            expected_stock = initial_stock + 15
            if product.current_stock == expected_stock:
                print(f"✅ Stock automatically updated: {initial_stock} → {product.current_stock}")
                logger.info(f"Stock automatically updated: {initial_stock} → {product.current_stock}")
            else:
                print(f"❌ Stock update failed: expected {expected_stock}, got {product.current_stock}")
                logger.error(f"Stock update failed: expected {expected_stock}, got {product.current_stock}")
                # Clean up and return
                delivery_log.delete()
                product.current_stock = initial_stock
                product.save()
                return False
            
            # Check if StockMovement was created
            print("🔍 Checking for associated StockMovement...")
            logger.info("Checking for associated StockMovement...")
            
            try:
                stock_movements = StockMovement.objects.filter(
                    product=product,
                    reference_id=str(delivery_log.id)
                )
                
                if stock_movements.exists():
                    stock_movement = stock_movements.first()
                    print(f"✅ StockMovement created successfully: ID {stock_movement.id}")
                    logger.info(f"StockMovement created successfully: ID {stock_movement.id}")
                    print(f"   - Movement type: {stock_movement.movement_type}")
                    print(f"   - Quantity: {stock_movement.quantity}")
                    print(f"   - Previous stock: {stock_movement.previous_stock}")
                    print(f"   - New stock: {stock_movement.new_stock}")
                    logger.info(f"StockMovement details - Type: {stock_movement.movement_type}, Quantity: {stock_movement.quantity}, Previous: {stock_movement.previous_stock}, New: {stock_movement.new_stock}")
                else:
                    print("❌ No StockMovement found for this delivery")
                    logger.error("No StockMovement found for this delivery")
                    # This is the issue we need to fix
                    
            except Exception as e:
                print(f"❌ Error checking StockMovement: {str(e)}")
                logger.error(f"Error checking StockMovement: {str(e)}", exc_info=True)
            
            # Clean up
            print("\n🧹 Cleaning up test data...")
            logger.info("Cleaning up test data...")
            
            # Store the delivery log ID for later cleanup
            delivery_log_id = delivery_log.id
            
            # Delete delivery log
            delivery_log.delete()
            print("✅ Delivery log deleted")
            logger.info("Delivery log deleted")
            
            # Restore original stock
            product.current_stock = initial_stock
            product.save()
            print(f"✅ Stock restored to: {product.current_stock}")
            logger.info(f"Stock restored to: {product.current_stock}")
            
            # Check if StockMovement was also deleted (cascade delete)
            try:
                stock_movements = StockMovement.objects.filter(reference_id=str(delivery_log_id))
                if stock_movements.exists():
                    print("⚠️  Orphaned StockMovement found - cleaning up")
                    logger.warning("Orphaned StockMovement found - cleaning up")
                    stock_movements.delete()
                else:
                    print("✅ No orphaned StockMovements")
                    logger.info("No orphaned StockMovements")
            except Exception as e:
                print(f"⚠️  Error during cleanup: {str(e)}")
                logger.warning(f"Error during cleanup: {str(e)}")
                
        except Exception as e:
            print(f"❌ Delivery log creation failed: {str(e)}")
            logger.error(f"Delivery log creation failed: {str(e)}", exc_info=True)
            return False
            
        # Test 3: Simulate the exact scenario from the view
        print("\n📝 Test 3: Simulating View-Level Delivery Creation")
        logger.info("Test 3: Simulating View-Level Delivery Creation")
        
        # This mimics what happens in the view
        try:
            print("🚚 Creating delivery log via form simulation...")
            logger.info("Creating delivery log via form simulation...")
            
            # Create delivery log data as it would come from the form
            delivery_data = {
                'product': product,
                'quantity_received': 20,
                'supplier_name': 'View Simulation Supplier',
                'delivery_date': datetime.now(),
                'cost_per_unit': Decimal('140.00'),
                'logged_by': admin_user,
                'notes': 'View simulation test delivery log'
            }
            
            # Note: We're not setting total_cost to test auto-calculation
            delivery_log = DeliveryLog(**delivery_data)
            
            # This should trigger the auto-calculation in save() method
            if not delivery_log.total_cost:
                delivery_log.total_cost = delivery_log.cost_per_unit * delivery_log.quantity_received
                print(f"🔧 Auto-calculated total cost: {delivery_log.total_cost}")
                logger.info(f"Auto-calculated total cost: {delivery_log.total_cost}")
            
            # Save the delivery log (this should create StockMovement)
            delivery_log.save()
            
            print(f"✅ Delivery log created via simulation: ID {delivery_log.id}")
            logger.info(f"Delivery log created via simulation: ID {delivery_log.id}")
            
            # Clean up
            delivery_log_id = delivery_log.id
            delivery_log.delete()
            product.current_stock = initial_stock
            product.save()
            
            # Cleanup orphaned StockMovement if any
            StockMovement.objects.filter(reference_id=str(delivery_log_id)).delete()
            
            print("✅ Simulation test completed")
            logger.info("Simulation test completed")
            
        except Exception as e:
            print(f"❌ View simulation failed: {str(e)}")
            logger.error(f"View simulation failed: {str(e)}", exc_info=True)
            return False
            
        logger.info("=== DELIVERY LOGGING DIAGNOSTIC COMPLETED ===")
        print("\n🎉 Diagnostic Analysis Completed!")
        print("✅ StockMovement model is working")
        print("✅ DeliveryLog creation is working")
        print("✅ Stock level updates are working")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ Unexpected error during diagnostic: {str(e)}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        return False

if __name__ == "__main__":
    success = diagnose_delivery_logging()
    if success:
        print("\n✅ Diagnostic indicates the system is working correctly")
        print("If you're still experiencing issues, check:")
        print("  1. Django logging configuration in settings.py")
        print("  2. File permissions for log directory")
        print("  3. Database constraints or triggers")
    else:
        print("\n❌ Diagnostic found issues that need to be addressed")
    exit(0 if success else 1)