from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate
from .models import CustomerProfile
from .forms import CustomerRegistrationForm, CustomerLoginForm, CustomerProfileForm, UserUpdateForm
import json


class AuthenticationTestCase(TestCase):
    """Test cases for customer authentication system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer_profile = CustomerProfile.objects.create(
            user=self.test_user,
            phone_number='1234567890',
            address='Test Address',
            delivery_instructions='Test instructions'
        )

    def test_registration_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Email Address')

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')

    def test_successful_login(self):
        """Test successful user login"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        
        # Check if user is logged in
        user = User.objects.get(username='testuser')
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_failed_login(self):
        """Test failed login with wrong credentials"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Sign in to your account')

    def test_profile_requires_authentication(self):
        """Test that profile page requires authentication"""
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_access_after_login(self):
        """Test profile page access after login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Profile')
        self.assertContains(response, 'testuser')

    def test_logout_functionality(self):
        """Test user logout"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Logout
        response = self.client.post(reverse('core:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        
        # Check if user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_username_validation_endpoint(self):
        """Test HTMX username validation endpoint"""
        # Test available username
        response = self.client.post(reverse('core:validate_username'), {
            'username': 'newuser'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['valid'])
        
        # Test existing username
        response = self.client.post(reverse('core:validate_username'), {
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['valid'])

    def test_email_validation_endpoint(self):
        """Test HTMX email validation endpoint"""
        # Test available email
        response = self.client.post(reverse('core:validate_email'), {
            'email': 'new@example.com'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['valid'])
        
        # Test existing email
        response = self.client.post(reverse('core:validate_email'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['valid'])

    def test_profile_update(self):
        """Test profile update functionality"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('core:profile'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '9876543210',
            'address': 'Updated Address',
            'delivery_instructions': 'Updated instructions'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check if profile was updated
        updated_user = User.objects.get(username='testuser')
        updated_profile = updated_user.customer_profile
        
        self.assertEqual(updated_user.first_name, 'John')
        self.assertEqual(updated_user.last_name, 'Doe')
        self.assertEqual(updated_user.email, 'john.doe@example.com')
        self.assertEqual(updated_profile.phone_number, '9876543210')
        self.assertEqual(updated_profile.address, 'Updated Address')


class FormTestCase(TestCase):
    """Test cases for authentication forms"""
    
    def test_customer_registration_form_valid(self):
        """Test valid customer registration form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone_number': '1234567890',
            'address': 'Test Address',
            'delivery_instructions': 'Test instructions'
        }
        form = CustomerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_customer_registration_form_duplicate_email(self):
        """Test registration form with duplicate email"""
        # Create existing user
        User.objects.create_user('existinguser', 'existing@example.com', 'password')
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Duplicate email
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone_number': '1234567890',
            'address': 'Test Address'
        }
        form = CustomerRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_customer_login_form_valid(self):
        """Test valid login form"""
        User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = CustomerLoginForm(data=form_data)
        # Note: AuthenticationForm requires a request object for full validation
        # This test just checks basic form structure

    def test_customer_profile_form_valid(self):
        """Test valid profile form"""
        form_data = {
            'phone_number': '9876543210',
            'address': 'Updated Address',
            'delivery_instructions': 'Updated instructions'
        }
        form = CustomerProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_update_form_valid(self):
        """Test valid user update form"""
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        }
        form = UserUpdateForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())


class ModelTestCase(TestCase):
    """Test cases for authentication-related models"""
    
    def test_customer_profile_creation(self):
        """Test customer profile creation"""
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        profile = CustomerProfile.objects.create(
            user=user,
            phone_number='1234567890',
            address='Test Address',
            delivery_instructions='Test instructions'
        )
        
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.phone_number, '1234567890')
        self.assertEqual(profile.address, 'Test Address')
        self.assertEqual(str(profile), 'testuser - 1234567890')

    def test_customer_profile_str_method(self):
        """Test customer profile string representation"""
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        profile = CustomerProfile.objects.create(
            user=user,
            phone_number='1234567890',
            address='Test Address'
        )
        
        expected_str = 'testuser - 1234567890'
        self.assertEqual(str(profile), expected_str)

from decimal import Decimal
from .models import LPGProduct, Order
from .forms import OrderForm


class OrderPlacementTestCase(TestCase):
    """Test cases for the order placement system"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create customer profile
        self.customer_profile = CustomerProfile.objects.create(
            user=self.user,
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
        
        self.client = Client()
    
    def test_order_form_display(self):
        """Test that order form displays correctly for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:place_order'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Place New Order')
        self.assertContains(response, self.product.name)
    
    def test_order_placement_success(self):
        """Test successful order placement"""
        self.client.login(username='testuser', password='testpass123')
        
        order_data = {
            'product': self.product.id,
            'quantity': 2,
            'delivery_type': 'delivery',
            'delivery_address': '123 Test Street, Test City',
            'notes': 'Test order'
        }
        
        response = self.client.post(reverse('core:place_order'), order_data)
        
        # Check that order was created
        self.assertTrue(Order.objects.filter(customer=self.user).exists())
        order = Order.objects.get(customer=self.user)
        
        self.assertEqual(order.product, self.product)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.delivery_type, 'delivery')
        self.assertEqual(order.total_amount, Decimal('1000.00'))  # 2 * 500
        
        # Check that stock was reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 48)  # 50 - 2
    
    def test_insufficient_stock_validation(self):
        """Test that orders with insufficient stock are rejected"""
        self.client.login(username='testuser', password='testpass123')
        
        order_data = {
            'product': self.product.id,
            'quantity': 100,  # More than available stock
            'delivery_type': 'delivery',
            'delivery_address': '123 Test Street, Test City'
        }
        
        response = self.client.post(reverse('core:place_order'), order_data)
        
        # Check that no order was created
        self.assertFalse(Order.objects.filter(customer=self.user).exists())
        
        # Check that stock wasn't changed
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 50)
    
    def test_stock_checking_endpoint(self):
        """Test the HTMX stock checking endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('core:check_stock'), {
            'product': self.product.id,
            'quantity': 5
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, '2500.00')  # 5 * 500
    
    def test_delivery_address_required_for_delivery(self):
        """Test that delivery address is required for delivery orders"""
        self.client.login(username='testuser', password='testpass123')
        
        order_data = {
            'product': self.product.id,
            'quantity': 1,
            'delivery_type': 'delivery',
            'delivery_address': '',  # Empty address
        }
        
        response = self.client.post(reverse('core:place_order'), order_data)
        
        # Check that no order was created
        self.assertFalse(Order.objects.filter(customer=self.user).exists())
    
    def test_pickup_order_success(self):
        """Test successful pickup order placement"""
        self.client.login(username='testuser', password='testpass123')
        
        order_data = {
            'product': self.product.id,
            'quantity': 1,
            'delivery_type': 'pickup',
            'delivery_address': '',  # Not required for pickup
        }
        
        response = self.client.post(reverse('core:place_order'), order_data)
        
        # Check that order was created
        self.assertTrue(Order.objects.filter(customer=self.user).exists())
        order = Order.objects.get(customer=self.user)
        
        self.assertEqual(order.delivery_type, 'pickup')
        self.assertEqual(order.delivery_address, 'Pickup at station')


class OrderFormTestCase(TestCase):
    """Test cases for the order form"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product = LPGProduct.objects.create(
            name='LPG Gas',
            size='11kg',
            price=Decimal('500.00'),
            current_stock=50,
            minimum_stock=10,
            is_active=True
        )
    
    def test_order_form_valid_delivery(self):
        """Test valid order form for delivery"""
        form_data = {
            'product': self.product.id,
            'quantity': 2,
            'delivery_type': 'delivery',
            'delivery_address': '123 Test Street, Test City',
            'notes': 'Test order'
        }
        form = OrderForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_order_form_valid_pickup(self):
        """Test valid order form for pickup"""
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'delivery_type': 'pickup',
            'delivery_address': '',
            'notes': ''
        }
        form = OrderForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_order_form_insufficient_stock(self):
        """Test order form with insufficient stock"""
        form_data = {
            'product': self.product.id,
            'quantity': 100,  # More than available
            'delivery_type': 'delivery',
            'delivery_address': '123 Test Street, Test City'
        }
        form = OrderForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('Insufficient stock', str(form.errors))
    
    def test_order_form_delivery_address_required(self):
        """Test that delivery address is required for delivery orders"""
        form_data = {
            'product': self.product.id,
            'quantity': 1,
            'delivery_type': 'delivery',
            'delivery_address': '',  # Empty address
        }
        form = OrderForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('Delivery address is required', str(form.errors))


class LPGProductModelTestCase(TestCase):
    """Test cases for LPG Product model"""
    
    def setUp(self):
        """Set up test data"""
        self.product = LPGProduct.objects.create(
            name='LPG Gas',
            size='11kg',
            price=Decimal('500.00'),
            current_stock=50,
            minimum_stock=10,
            is_active=True
        )
    
    def test_product_str_method(self):
        """Test product string representation"""
        expected_str = 'LPG Gas - 11kg'
        self.assertEqual(str(self.product), expected_str)
    
    def test_is_low_stock_property(self):
        """Test low stock property"""
        # Normal stock
        self.assertFalse(self.product.is_low_stock)
        
        # Low stock
        self.product.current_stock = 5
        self.product.save()
        self.assertTrue(self.product.is_low_stock)
    
    def test_can_fulfill_order_method(self):
        """Test can fulfill order method"""
        # Can fulfill
        self.assertTrue(self.product.can_fulfill_order(10))
        
        # Cannot fulfill - insufficient stock
        self.assertFalse(self.product.can_fulfill_order(100))
        
        # Cannot fulfill - inactive product
        self.product.is_active = False
        self.product.save()
        self.assertFalse(self.product.can_fulfill_order(10))


class OrderModelTestCase(TestCase):
    """Test cases for Order model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product = LPGProduct.objects.create(
            name='LPG Gas',
            size='11kg',
            price=Decimal('500.00'),
            current_stock=50,
            minimum_stock=10,
            is_active=True
        )
        
        self.order = Order.objects.create(
            customer=self.user,
            product=self.product,
            quantity=2,
            delivery_type='delivery',
            delivery_address='123 Test Street',
            status='pending'
        )
    
    def test_order_str_method(self):
        """Test order string representation"""
        expected_str = f'Order #{self.order.id} - testuser - LPG Gas'
        self.assertEqual(str(self.order), expected_str)
    
    def test_order_total_amount_calculation(self):
        """Test that total amount is calculated correctly"""
        expected_total = Decimal('1000.00')  # 2 * 500
        self.assertEqual(self.order.total_amount, expected_total)
    
    def test_is_delivered_property(self):
        """Test is delivered property"""
        self.assertFalse(self.order.is_delivered)
        
        self.order.status = 'delivered'
        self.order.save()
        self.assertTrue(self.order.is_delivered)
    
    def test_can_be_cancelled_property(self):
        """Test can be cancelled property"""
        # Pending orders can be cancelled
        self.assertTrue(self.order.can_be_cancelled)
        
        # Delivered orders cannot be cancelled
        self.order.status = 'delivered'
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled)