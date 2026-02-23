from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
import re
from .models import (
    CustomerProfile, Order, LPGProduct, DeliveryLog,
    ProductCategory, Supplier, InventoryAdjustment, Staff, Payroll,
    Cashier, CashierTransaction, PendingRegistration
)


class PendingRegistrationForm(forms.ModelForm):
    """
    Form for capturing new user registration with ID verification
    Requirements: Registration with ID document upload and admin approval
    """
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Create a password (min. 8 characters)',
            'autocomplete': 'new-password'
        }),
        validators=[
            MinLengthValidator(8, 'Password must be at least 8 characters long.')
        ]
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = PendingRegistration
        fields = [
            'username', 'email', 'phone_number', 'address', 
            'delivery_instructions', 'id_type', 'id_number', 'id_document'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Choose a username (3-30 characters)',
                'minlength': '3',
                'maxlength': '30'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your email address',
                'autocomplete': 'email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'e.g., 09123456789 or +639123456789',
                'autocomplete': 'tel'
            }),
            'address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your complete delivery address with landmarks',
                'rows': 3,
                'autocomplete': 'street-address'
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Any special delivery instructions (optional)',
                'rows': 2,
                'maxlength': '200'
            }),
            'id_type': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your ID number'
            }),
            'id_document': forms.FileInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'accept': 'image/*',
                'required': 'required'
            })
        }
    
    def clean_password2(self):
        """Validate password match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Passwords do not match.')
        return password2
    
    def clean_email(self):
        """Validate email is unique"""
        email = self.cleaned_data.get('email')
        if PendingRegistration.objects.filter(email=email).exists():
            raise ValidationError('This email is already pending approval or has been registered.')
        return email
    
    def clean_username(self):
        """Validate username is unique and meets requirements"""
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
            raise ValidationError('Username must be 3-30 characters with only letters, numbers, and underscores.')
        if PendingRegistration.objects.filter(username=username).exists():
            raise ValidationError('This username is already pending approval or has been registered.')
        return username
    
    def clean_id_document(self):
        """Validate ID document file"""
        id_document = self.cleaned_data.get('id_document')
        if id_document:
            # Check file size (max 5MB)
            if id_document.size > 5 * 1024 * 1024:
                raise ValidationError('ID document file size must not exceed 5MB.')
            # Check file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf']
            file_ext = id_document.name.split('.')[-1].lower()
            if file_ext not in valid_extensions:
                raise ValidationError('Please upload a valid image or PDF file.')
        return id_document


class CustomerRegistrationForm(UserCreationForm):
    """
    Customer registration form with additional profile fields and enhanced validation
    Requirements: 1.1, 1.2, 10.1, 10.2, 10.3 - Customer registration with validation and security
    """
    email = forms.EmailField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Please enter a valid email address.'
            )
        ],
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter your email address',
            'x-model': 'email',
            '@input.debounce.500ms': 'validateEmail()',
            'autocomplete': 'email'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^(\+63|0)[0-9]{10}$',
                message='Please enter a valid Philippine phone number (e.g., +639123456789 or 09123456789).'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter your phone number (e.g., 09123456789)',
            'x-model': 'phoneNumber',
            '@input': 'validatePhoneNumber()',
            'autocomplete': 'tel'
        })
    )
    address = forms.CharField(
        min_length=10,
        max_length=500,
        validators=[
            MinLengthValidator(10, 'Address must be at least 10 characters long.')
        ],
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter your complete delivery address with landmarks',
            'rows': 3,
            'x-model': 'address',
            '@input': 'validateAddress()',
            'autocomplete': 'street-address'
        })
    )
    delivery_instructions = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Any special delivery instructions (optional)',
            'rows': 2,
            'maxlength': '200'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes and validation attributes to default fields
        self.fields['username'].widget.attrs.update({
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Choose a username (3-30 characters)',
            'x-model': 'username',
            '@input.debounce.500ms': 'validateUsername()',
            'autocomplete': 'username',
            'minlength': '3',
            'maxlength': '30'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter your password (min. 8 characters)',
            'x-model': 'password1',
            '@input': 'validatePassword()',
            'autocomplete': 'new-password',
            'minlength': '8'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Confirm your password',
            'x-model': 'password2',
            '@input': 'validatePasswordMatch()',
            'autocomplete': 'new-password'
        })
        
        # Add enhanced validation to username field
        self.fields['username'].validators.append(
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.'
            )
        )
        self.fields['username'].validators.append(
            MinLengthValidator(3, 'Username must be at least 3 characters long.')
        )

    def clean_username(self):
        """Enhanced username validation with sanitization"""
        username = self.cleaned_data.get('username')
        if username:
            # Sanitize input
            username = strip_tags(username).strip()
            
            # Check length
            if len(username) < 3:
                raise ValidationError('Username must be at least 3 characters long.')
            if len(username) > 30:
                raise ValidationError('Username cannot exceed 30 characters.')
            
            # Check for valid characters
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise ValidationError('Username can only contain letters, numbers, and underscores.')
            
            # Check uniqueness
            if User.objects.filter(username__iexact=username).exists():
                raise ValidationError('This username is already taken.')
        
        return username

    def clean_email(self):
        """Enhanced email validation with sanitization"""
        email = self.cleaned_data.get('email')
        if email:
            # Sanitize input
            email = strip_tags(email).strip().lower()
            
            # Additional email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('Please enter a valid email address.')
            
            # Check uniqueness
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('A user with this email already exists.')
        
        return email

    def clean_phone_number(self):
        """Enhanced phone number validation with sanitization"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Sanitize input - remove all non-digit characters except +
            phone = re.sub(r'[^\d+]', '', phone)
            
            # Normalize Philippine phone numbers
            if phone.startswith('0'):
                phone = '+63' + phone[1:]
            elif phone.startswith('63'):
                phone = '+' + phone
            elif not phone.startswith('+63'):
                raise ValidationError('Please enter a valid Philippine phone number.')
            
            # Validate format
            if not re.match(r'^\+63[0-9]{10}$', phone):
                raise ValidationError('Please enter a valid Philippine phone number (e.g., +639123456789).')
        
        return phone

    def clean_address(self):
        """Enhanced address validation with sanitization"""
        address = self.cleaned_data.get('address')
        if address:
            # Sanitize input
            address = strip_tags(address).strip()
            
            # Check minimum length
            if len(address) < 10:
                raise ValidationError('Address must be at least 10 characters long.')
            
            # Check maximum length
            if len(address) > 500:
                raise ValidationError('Address cannot exceed 500 characters.')
        
        return address

    def clean_delivery_instructions(self):
        """Sanitize delivery instructions"""
        instructions = self.cleaned_data.get('delivery_instructions')
        if instructions:
            # Sanitize input
            instructions = strip_tags(instructions).strip()
            
            # Check maximum length
            if len(instructions) > 200:
                raise ValidationError('Delivery instructions cannot exceed 200 characters.')
        
        return instructions

    def save(self, commit=True):
        """Save user and create customer profile"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create customer profile
            CustomerProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
                delivery_instructions=self.cleaned_data['delivery_instructions']
            )
        return user


class CustomerLoginForm(AuthenticationForm):
    """
    Custom login form with styling
    Requirements: 1.4 - Customer login functionality
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter your password'
        })


class CustomerProfileForm(forms.ModelForm):
    """
    Form for updating customer profile information
    Requirements: 1.2 - Customer profile management
    """
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address', 'delivery_instructions', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your delivery address',
                'rows': 3
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Any special delivery instructions (optional)',
                'rows': 2
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ajax_mode = False
    
    def set_ajax_mode(self):
        self._ajax_mode = True
        self.fields['phone_number'].required = False
        self.fields['address'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        if self._ajax_mode:
            cleaned_data['phone_number'] = cleaned_data.get('phone_number') or self.instance.phone_number
            cleaned_data['address'] = cleaned_data.get('address') or self.instance.address
        return cleaned_data
    
    def clean_profile_picture(self):
        """Validate profile picture"""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValidationError('Profile picture size must not exceed 5MB.')
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            file_ext = profile_picture.name.split('.')[-1].lower()
            if file_ext not in valid_extensions:
                raise ValidationError('Please upload a valid image file (JPG, PNG, GIF, or WEBP).')
        return profile_picture


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information
    Requirements: 1.2 - Customer profile management
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
                'placeholder': 'Enter your email address'
            })
        }

    def clean_email(self):
        """Validate that email is unique (excluding current user)"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class OrderForm(forms.ModelForm):
    """
    Form for placing LPG orders with product selection and delivery options
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5 - Order placement with validation
    """
    product = forms.ModelChoiceField(
        queryset=LPGProduct.objects.filter(is_active=True, current_stock__gt=0),
        empty_label="Select a product",
        required=False,  # Not required for submission, only for adding to cart
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'hx-get': '/check-stock/',
            'hx-target': '#stock-info',
            'hx-trigger': 'change',
            'hx-include': '[name="quantity"]'
        })
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        required=False,  # Not required for submission, only for adding to cart
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter quantity',
            'hx-get': '/check-stock/',
            'hx-target': '#stock-info',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-include': '[name="product"]'
        })
    )
    
    delivery_type = forms.ChoiceField(
        choices=Order.DELIVERY_CHOICES,
        initial='delivery',
        widget=forms.RadioSelect(attrs={
            'class': 'focus:ring-prycegas-orange h-4 w-4 text-prycegas-orange border-gray-300'
        })
    )
    
    delivery_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter delivery address (required for delivery orders)',
            'rows': 3
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Any special instructions or notes (optional)',
            'rows': 2
        })
    )

    class Meta:
        model = Order
        fields = ['delivery_type', 'delivery_address', 'notes']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set delivery address from user profile if available
        if self.user and hasattr(self.user, 'customer_profile'):
            self.fields['delivery_address'].initial = self.user.customer_profile.address

    def clean_quantity(self):
        """Enhanced quantity validation"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None:
            if quantity < 1:
                raise ValidationError('Quantity must be at least 1.')
            if quantity > 100:  # Reasonable maximum
                raise ValidationError('Quantity cannot exceed 100 units per order.')
        return quantity

    def clean_delivery_address(self):
        """Enhanced delivery address validation with sanitization"""
        address = self.cleaned_data.get('delivery_address')
        if address:
            # Sanitize input
            address = strip_tags(address).strip()
            
            # Check minimum length for delivery addresses
            if len(address) < 10:
                raise ValidationError('Delivery address must be at least 10 characters long.')
            
            # Check maximum length
            if len(address) > 500:
                raise ValidationError('Delivery address cannot exceed 500 characters.')
        
        return address

    def clean_notes(self):
        """Sanitize order notes"""
        notes = self.cleaned_data.get('notes')
        if notes:
            # Sanitize input
            notes = strip_tags(notes).strip()
            
            # Check maximum length
            if len(notes) > 500:
                raise ValidationError('Notes cannot exceed 500 characters.')
        
        return notes

    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        delivery_address = cleaned_data.get('delivery_address')

        # Validate delivery address for delivery orders
        if delivery_type == 'delivery':
            if not delivery_address or len(delivery_address.strip()) < 10:
                raise ValidationError({
                    'delivery_address': 'A complete delivery address is required for delivery orders.'
                })

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        if self.user:
            order.customer = self.user
        
        # Calculate total amount
        if order.product and order.quantity:
            order.total_amount = order.product.price * order.quantity
        
        # Set delivery address from form or user profile
        if order.delivery_type == 'pickup':
            order.delivery_address = "Pickup at station"
        elif not order.delivery_address and self.user and hasattr(self.user, 'customer_profile'):
            order.delivery_address = self.user.customer_profile.address

        if commit:
            order.save()
            # Reduce product stock
            product = order.product
            product.current_stock -= order.quantity
            product.save()

        return order


class DeliveryLogForm(forms.ModelForm):
    """
    Form for logging distributor deliveries with automatic inventory adjustment
    Requirements: 6.2, 6.4 - Delivery logging with form validation
    """
    product = forms.ModelChoiceField(
        queryset=LPGProduct.objects.filter(is_active=True),
        empty_label="Select a product",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'x-model': 'selectedProduct',
            '@change': 'calculateTotal()'
        })
    )
    
    quantity_received = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter quantity received',
            'x-model': 'quantity',
            '@input': 'calculateTotal()'
        })
    )
    
    supplier_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter supplier/distributor name'
        })
    )
    
    delivery_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'type': 'datetime-local'
        })
    )
    
    cost_per_unit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Enter cost per unit',
            'step': '0.01',
            'x-model': 'costPerUnit',
            '@input': 'calculateTotal()'
        })
    )
    
    total_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50 placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Auto-calculated',
            'step': '0.01',
            'readonly': True,
            'x-model': 'totalCost'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-prycegas-orange focus:border-prycegas-orange',
            'placeholder': 'Any additional notes about the delivery (optional)',
            'rows': 3
        })
    )

    class Meta:
        model = DeliveryLog
        fields = ['product', 'quantity_received', 'supplier_name', 'delivery_date', 'cost_per_unit', 'total_cost', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default delivery date to current time
        if not self.initial.get('delivery_date'):
            from django.utils import timezone
            self.fields['delivery_date'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def clean_quantity_received(self):
        """Enhanced quantity validation"""
        quantity = self.cleaned_data.get('quantity_received')
        if quantity is not None:
            if quantity < 1:
                raise ValidationError('Quantity received must be at least 1.')
            if quantity > 10000:  # Reasonable maximum for deliveries
                raise ValidationError('Quantity received cannot exceed 10,000 units.')
        return quantity

    def clean_supplier_name(self):
        """Sanitize supplier name"""
        supplier_name = self.cleaned_data.get('supplier_name')
        if supplier_name:
            # Sanitize input
            supplier_name = strip_tags(supplier_name).strip()

            # Check minimum length
            if len(supplier_name) < 2:
                raise ValidationError('Supplier name must be at least 2 characters long.')

            # Check maximum length
            if len(supplier_name) > 100:
                raise ValidationError('Supplier name cannot exceed 100 characters.')

        return supplier_name

    def clean_cost_per_unit(self):
        """Enhanced cost validation"""
        cost = self.cleaned_data.get('cost_per_unit')
        if cost is not None:
            if cost < 0:
                raise ValidationError('Cost per unit cannot be negative.')
            if cost > 10000:  # Reasonable maximum
                raise ValidationError('Cost per unit cannot exceed ₱10,000.')
        return cost

    def clean_notes(self):
        """Sanitize delivery notes"""
        notes = self.cleaned_data.get('notes')
        if notes:
            # Sanitize input
            notes = strip_tags(notes).strip()
            
            # Check maximum length
            if len(notes) > 500:
                raise ValidationError('Notes cannot exceed 500 characters.')
        
        return notes

    def clean(self):
        cleaned_data = super().clean()
        quantity_received = cleaned_data.get('quantity_received')
        cost_per_unit = cleaned_data.get('cost_per_unit')
        total_cost = cleaned_data.get('total_cost')

        # Calculate total cost if not provided
        if quantity_received and cost_per_unit and not total_cost:
            cleaned_data['total_cost'] = quantity_received * cost_per_unit

        # Validate that total cost matches calculation
        if quantity_received and cost_per_unit and total_cost:
            expected_total = quantity_received * cost_per_unit
            if abs(total_cost - expected_total) > 0.01:  # Allow for small rounding differences
                raise ValidationError({
                    'total_cost': f'Total cost should be ₱{expected_total:.2f} (quantity × cost per unit).'
                })

        return cleaned_data


class ProductForm(forms.ModelForm):
    """
    Form for adding/editing LPG products with enhanced inventory fields
    """
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True),
        required=False,
        empty_label="-- Select or create a category --",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
            'id': 'id_category_select'
        })
    )

    class Meta:
        model = LPGProduct
        fields = [
            'name', 'size', 'sku', 'barcode', 'category', 'description',
            'price', 'cost_price', 'current_stock', 'minimum_stock',
            'maximum_stock', 'reorder_point', 'reorder_quantity', 'weight', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Product name (e.g., LPG Gas)'
            }),
            'size': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Product size (e.g., 11kg, 22kg)'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'SKU (leave blank to auto-generate)'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Product barcode'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 3,
                'placeholder': 'Product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'step': '0.01',
                'min': '0.01'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'step': '0.01',
                'min': '0.01'
            }),
            'current_stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'min': '0'
            }),
            'minimum_stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'min': '0'
            }),
            'maximum_stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'min': '1'
            }),
            'reorder_point': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'min': '0'
            }),
            'reorder_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'min': '1'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'step': '0.01',
                'min': '0'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        minimum_stock = cleaned_data.get('minimum_stock')
        maximum_stock = cleaned_data.get('maximum_stock')
        reorder_point = cleaned_data.get('reorder_point')
        current_stock = cleaned_data.get('current_stock')

        if minimum_stock and maximum_stock and minimum_stock >= maximum_stock:
            raise ValidationError('Maximum stock must be greater than minimum stock.')

        if reorder_point and minimum_stock and reorder_point < minimum_stock:
            raise ValidationError('Reorder point should be at least equal to minimum stock.')

        if current_stock and maximum_stock and current_stock > maximum_stock:
            raise ValidationError('Current stock cannot exceed maximum stock.')

        return cleaned_data


class InventoryAdjustmentForm(forms.ModelForm):
    """
    Form for making inventory adjustments with increase/decrease toggle
    """
    ADJUSTMENT_TYPE_CHOICES = [
        ('increase', 'Increase Stock'),
        ('decrease', 'Decrease Stock'),
    ]
    
    adjustment_type = forms.ChoiceField(
        choices=ADJUSTMENT_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'h-4 w-4 text-prycegas-orange'
        }),
        label='Adjustment Type',
        initial='increase'
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
            'placeholder': 'Enter quantity',
            'min': '1'
        }),
        label='Quantity'
    )
    
    class Meta:
        model = InventoryAdjustment
        fields = ['product', 'reason', 'notes']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'reason': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 3,
                'placeholder': 'Additional notes about the adjustment'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate product dropdown with all active products
        self.fields['product'].queryset = LPGProduct.objects.filter(is_active=True).order_by('name')
        self.fields['product'].empty_label = "-- Select a product --"

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        adjustment_type = cleaned_data.get('adjustment_type')
        
        if quantity and quantity == 0:
            raise ValidationError('Quantity must be greater than zero.')
        
        return cleaned_data

    def save(self, commit=True):
        """Convert adjustment_type and quantity to quantity_change"""
        print(f"[DEBUG] InventoryAdjustmentForm.save() called with commit={commit}")
        
        instance = super().save(commit=False)
        print(f"[DEBUG] Instance created from super().save(commit=False): {instance}")
        
        adjustment_type = self.cleaned_data.get('adjustment_type')
        quantity = self.cleaned_data.get('quantity')
        
        print(f"[DEBUG] adjustment_type: {adjustment_type}")
        print(f"[DEBUG] quantity: {quantity}")
        
        # Convert to signed quantity_change
        if adjustment_type == 'increase':
            instance.quantity_change = quantity
            print(f"[DEBUG] Setting quantity_change to POSITIVE: {quantity}")
        else:  # decrease
            instance.quantity_change = -quantity
            print(f"[DEBUG] Setting quantity_change to NEGATIVE: {-quantity}")
        
        print(f"[DEBUG] Final quantity_change: {instance.quantity_change}")
        print(f"[DEBUG] Instance product: {instance.product}")
        print(f"[DEBUG] Instance reason: {instance.reason}")
        print(f"[DEBUG] Instance notes: {instance.notes}")
        
        if commit:
            print(f"[DEBUG] Calling instance.save() with commit=True")
            instance.save()
            print(f"[DEBUG] Instance saved successfully. ID: {instance.id}")
        else:
            print(f"[DEBUG] Not calling save() - commit=False")
        
        return instance


class ProductCategoryForm(forms.ModelForm):
    """
    Form for managing product categories
    """
    class Meta:
        model = ProductCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 3,
                'placeholder': 'Category description'
            }),
        }


class SupplierForm(forms.ModelForm):
    """
    Form for managing suppliers
    """
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Supplier name'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Contact person name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Email address'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 3,
                'placeholder': 'Supplier address'
            }),
        }

class StaffForm(forms.ModelForm):
    """
    Form for creating and updating staff members.
    """
    class Meta:
        model = Staff
        fields = ['user', 'position', 'salary', 'hire_date']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'position': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Staff position'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'step': '0.01',
                'min': '0.01'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'type': 'date'
            }),
        }

class StaffCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'}), required=True)

    class Meta:
        model = Staff
        fields = ['position', 'salary', 'hire_date']
        widgets = {
            'position': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Staff position'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'step': '0.01',
                'min': '0.01'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'type': 'date'
            }),
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            is_staff=True
        )
        staff = super().save(commit=False)
        staff.user = user
        if commit:
            staff.save()
        return staff

class PayrollForm(forms.ModelForm):
    """
    Form for creating new payroll records.
    """
    class Meta:
        model = Payroll
        fields = ['staff', 'payment_date', 'amount', 'notes']
        widgets = {
            'staff': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'step': '0.01',
                'min': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 3,
                'placeholder': 'Additional notes about the payment'
            }),
        }


class CashierCreationForm(forms.ModelForm):
    """
    Form for creating a cashier account with user details
    Requires admin permission only
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
            'placeholder': 'Enter username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
            'placeholder': 'Enter email address'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
            'placeholder': 'Enter last name'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
            'placeholder': 'Enter password'
        }),
        required=True
    )

    class Meta:
        model = Cashier
        fields = ['employee_id', 'shift_start', 'shift_end', 'is_active']
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Enter unique employee ID'
            }),
            'shift_start': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'type': 'time'
            }),
            'shift_end': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'type': 'time'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Cashier.objects.filter(employee_id=employee_id).exists():
            raise ValidationError('This employee ID is already registered.')
        return employee_id

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            is_staff=True
        )
        cashier = super().save(commit=False)
        cashier.user = user
        if commit:
            cashier.save()
        return cashier


class CashierUpdateForm(forms.ModelForm):
    """
    Form for updating cashier details
    Admin only
    """
    class Meta:
        model = Cashier
        fields = ['employee_id', 'shift_start', 'shift_end', 'is_active']
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'Employee ID'
            }),
            'shift_start': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'type': 'time'
            }),
            'shift_end': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'type': 'time'
            }),
        }


class CashierOrderForm(forms.ModelForm):
    """
    Form for cashier to manage customer orders
    Limited to order creation and status updates
    """
    class Meta:
        model = Order
        fields = ['customer', 'product', 'quantity', 'delivery_type', 'delivery_address', 'notes']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'min': '1',
                'placeholder': 'Enter quantity'
            }),
            'delivery_type': forms.RadioSelect(attrs={
                'class': 'h-4 w-4'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 3,
                'placeholder': 'Enter delivery address'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 2,
                'placeholder': 'Additional notes (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active products with stock
        self.fields['product'].queryset = LPGProduct.objects.filter(is_active=True, current_stock__gt=0)
        # Only show customers
        self.fields['customer'].queryset = User.objects.filter(customer_profile__isnull=False)

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        delivery_type = cleaned_data.get('delivery_type')
        delivery_address = cleaned_data.get('delivery_address')

        if product and quantity:
            if not product.can_fulfill_order(quantity):
                raise ValidationError({
                    'quantity': f'Insufficient stock. Only {product.available_stock} units available.'
                })

        if delivery_type == 'delivery':
            if not delivery_address or len(delivery_address.strip()) < 10:
                raise ValidationError({
                    'delivery_address': 'A complete delivery address is required for delivery orders.'
                })

        return cleaned_data


class CashierTransactionForm(forms.ModelForm):
    """
    Form for recording cashier transactions
    Admin only
    """
    class Meta:
        model = CashierTransaction
        fields = ['transaction_type', 'amount', 'payment_method', 'customer', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter amount'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'placeholder': 'e.g., cash, card, check'
            }),
            'customer': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-prycegas-orange focus:border-transparent',
                'rows': 3,
                'placeholder': 'Additional transaction notes (optional)'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError('Amount must be greater than zero.')
        return amount