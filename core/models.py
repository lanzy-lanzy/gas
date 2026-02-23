from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid
import os


class PendingRegistration(models.Model):
    """
    Model for storing pending user registrations awaiting admin approval
    Requirements: Admin approval workflow with ID document verification
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    ID_TYPE_CHOICES = [
        ('national_id', 'National ID'),
        ('drivers_license', "Driver's License"),
        ('passport', 'Passport'),
        ('barangay_id', 'Barangay ID'),
        ('sss_id', 'SSS ID'),
        ('tin_id', 'TIN ID'),
        ('company_id', 'Company ID'),
        ('other', 'Other'),
    ]
    
    # User registration data
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed password
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    
    # ID verification
    id_type = models.CharField(max_length=50, choices=ID_TYPE_CHOICES)
    id_number = models.CharField(max_length=100)
    id_document = models.ImageField(
        upload_to='pending_registrations/id_documents/%Y/%m/%d/',
        help_text="Upload a clear image of the ID document"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")
    
    # Admin actions
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_registrations',
        help_text="Admin user who reviewed this registration"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pending Registration"
        verbose_name_plural = "Pending Registrations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_status_display()})"
    
    @property
    def days_pending(self):
        """Calculate how many days the registration has been pending"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
    
    def approve(self, user):
        """Mark registration as approved"""
        self.status = 'approved'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()
    
    def reject(self, user, reason):
        """Mark registration as rejected"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()


def customer_profile_picture_path(instance, filename):
    """Generate upload path for customer profile pictures"""
    import os
    import uuid
    ext = filename.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        ext = 'jpg'
    filename = f'profile_{instance.user.id}_{uuid.uuid4().hex[:8]}.{ext}'
    return os.path.join('profile_pictures', filename)


class CustomerProfile(models.Model):
    """
    Extended profile for customers with delivery information
    Requirements: 1.2 - Customer registration with contact information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=15, help_text="Customer contact number")
    address = models.TextField(help_text="Customer delivery address")
    delivery_instructions = models.TextField(
        blank=True, 
        help_text="Special delivery instructions (optional)"
    )
    profile_picture = models.ImageField(
        upload_to=customer_profile_picture_path,
        blank=True,
        null=True,
        help_text="Customer profile picture"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"
    
    def get_profile_picture_url(self):
        """Return profile picture URL or default placeholder"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return None


class LPGProduct(models.Model):
    """
    LPG products with enhanced inventory tracking and management
    Requirements: 2.3, 6.2 - Product management with comprehensive inventory tracking
    """
    name = models.CharField(max_length=100, help_text="Product name (e.g., LPG Gas)")
    size = models.CharField(max_length=50, help_text="Product size (e.g., 11kg, 22kg)")
    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Stock Keeping Unit (SKU) for inventory tracking"
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        help_text="Product barcode for scanning"
    )
    category = models.ForeignKey(
        'ProductCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="Product category"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price per unit"
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=Decimal('0.00'),
        help_text="Cost price per unit"
    )
    current_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current available stock"
    )
    reserved_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Stock reserved for pending orders"
    )
    minimum_stock = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Minimum stock level for low stock alerts"
    )
    maximum_stock = models.IntegerField(
        default=1000,
        validators=[MinValueValidator(0)],
        help_text="Maximum stock level for reorder management"
    )
    reorder_point = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0)],
        help_text="Stock level at which to reorder"
    )
    reorder_quantity = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Quantity to order when restocking"
    )
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Product weight in kg"
    )
    description = models.TextField(blank=True, help_text="Product description")
    is_active = models.BooleanField(default=True, help_text="Product availability status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "LPG Product"
        verbose_name_plural = "LPG Products"
        ordering = ['name', 'size']

    def __str__(self):
        return f"{self.name} - {self.size}"

    def save(self, *args, **kwargs):
        """Auto-generate SKU if not provided"""
        if not self.sku:
            # Generate SKU based on name and size
            base_sku = f"{self.name[:3].upper()}-{self.size.replace('kg', '')}"
            counter = 1
            while LPGProduct.objects.filter(sku=f"{base_sku}-{counter:03d}").exists():
                counter += 1
            self.sku = f"{base_sku}-{counter:03d}"
        super().save(*args, **kwargs)

    @property
    def is_low_stock(self):
        """Check if product is below minimum stock level"""
        return self.current_stock <= self.minimum_stock

    @property
    def is_reorder_needed(self):
        """Check if product needs to be reordered"""
        return self.current_stock <= self.reorder_point

    @property
    def available_stock(self):
        """Get available stock (current - reserved)"""
        return max(0, self.current_stock - self.reserved_stock)

    @property
    def stock_value(self):
        """Calculate total stock value at cost price"""
        return self.current_stock * self.cost_price

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0

    def can_fulfill_order(self, quantity):
        """Check if there's enough available stock for an order"""
        return self.available_stock >= quantity and self.is_active

    def reserve_stock(self, quantity):
        """Reserve stock for an order"""
        if self.can_fulfill_order(quantity):
            self.reserved_stock += quantity
            self.save()
            return True
        return False

    def release_stock(self, quantity):
        """Release reserved stock"""
        self.reserved_stock = max(0, self.reserved_stock - quantity)
        self.save()

    def get_stock_movements(self, days=30):
        """Get stock movements for the last N days"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.stock_movements.filter(created_at__gte=cutoff_date)


class Order(models.Model):
    """
    Customer orders with status workflow and delivery options
    Requirements: 2.3, 5.5 - Order management with status tracking
    Multiple products in a single order share the same batch_id
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    DELIVERY_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]
    
    batch_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="Groups multiple products in a single order together"
    )
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        related_name='orders',
        help_text="Customer who placed the order (null for walk-in customers)"
    )
    product = models.ForeignKey(
        LPGProduct, 
        on_delete=models.CASCADE, 
        related_name='orders',
        help_text="Ordered product"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of units ordered"
    )
    delivery_type = models.CharField(
        max_length=20, 
        choices=DELIVERY_CHOICES,
        help_text="Pickup or delivery option"
    )
    delivery_address = models.TextField(help_text="Address for delivery orders")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current order status"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total order amount"
    )
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date when order was delivered"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional order notes or instructions"
    )
    processed_by = models.ForeignKey(
        'Cashier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_orders',
        help_text="Cashier who processed/delivered this order"
    )
    delivery_person_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the delivery person who delivered the order"
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Reason for order cancellation (if cancelled)"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the order was cancelled"
    )
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_orders',
        help_text="User who cancelled the order"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-order_date']

    def __str__(self):
        customer_name = self.customer.username if self.customer else "Walk-in Customer"
        return f"Order #{self.id} - {customer_name} - {self.product.name}"

    def save(self, *args, **kwargs):
        """Calculate total amount on save"""
        if not self.total_amount:
            self.total_amount = self.product.price * self.quantity
        super().save(*args, **kwargs)

    @property
    def is_delivered(self):
        """Check if order has been delivered"""
        return self.status == 'delivered'

    @property
    def can_be_cancelled(self):
        """Check if order can still be cancelled"""
        return self.status in ['pending']
    
    @property
    def processed_by_name(self):
        """Get the name of who processed this order"""
        if self.processed_by:
            return self.processed_by.user.get_full_name() or self.processed_by.user.username
        return None
    
    @property
    def get_delivery_person(self):
        """Get delivery person info"""
        if self.delivery_person_name:
            return self.delivery_person_name
        if self.processed_by:
            return self.processed_by.user.get_full_name() or self.processed_by.user.username
        return None
    
    @property
    def batch_items(self):
        """Get all orders in the same batch"""
        return Order.objects.filter(batch_id=self.batch_id).order_by('id')
    
    @property
    def batch_total(self):
        """Get total amount for all items in the batch"""
        return sum(item.total_amount for item in self.batch_items)
    
    @property
    def batch_item_count(self):
        """Get number of items in the batch"""
        return self.batch_items.count()
    
    @property
    def is_batch_order(self):
        """Check if this order has multiple items"""
        return self.batch_items.count() > 1
    
    @property
    def is_first_in_batch(self):
        """Check if this is the first item in the batch (for display purposes)"""
        first_item = self.batch_items.first()
        return first_item and first_item.id == self.id


class DeliveryLog(models.Model):
    """
    Log of distributor deliveries for inventory management
    Requirements: 6.2 - Inventory management with delivery tracking
    """
    product = models.ForeignKey(
        LPGProduct, 
        on_delete=models.CASCADE, 
        related_name='delivery_logs',
        help_text="Product that was delivered"
    )
    quantity_received = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of units received"
    )
    supplier_name = models.CharField(
        max_length=100,
        help_text="Name of the supplier/distributor"
    )
    delivery_date = models.DateTimeField(help_text="Date when delivery was received")
    cost_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cost per unit from supplier"
    )
    total_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total cost of the delivery"
    )
    logged_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='delivery_logs',
        help_text="Staff member who logged this delivery"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the delivery"
    )

    class Meta:
        verbose_name = "Delivery Log"
        verbose_name_plural = "Delivery Logs"
        ordering = ['-delivery_date']

    def __str__(self):
        return f"Delivery: {self.quantity_received}x {self.product.name} from {self.supplier_name}"

    def save(self, *args, **kwargs):
        """Calculate total cost, update product stock, and create stock movement on save"""
        if not self.total_cost:
            self.total_cost = self.cost_per_unit * self.quantity_received

        is_new = self.pk is None

        # Update product stock when delivery is logged
        if is_new:
            previous_stock = self.product.current_stock
            self.product.current_stock += self.quantity_received
            self.product.save()

            # Save the delivery log first
            super().save(*args, **kwargs)

            # Create stock movement record
            try:
                StockMovement.objects.create(
                    product=self.product,
                    movement_type='delivery',
                    quantity=self.quantity_received,
                    previous_stock=previous_stock,
                    new_stock=self.product.current_stock,
                    reference_id=str(self.id),
                    notes=f"Delivery from {self.supplier_name}",
                    created_by=self.logged_by
                )
            except Exception as e:
                # Log the error but don't fail the delivery logging
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to create stock movement for delivery {self.id}: {str(e)}")
                # Continue without failing - the delivery log is more important than the stock movement
        else:
            super().save(*args, **kwargs)


class ProductCategory(models.Model):
    """
    Product categories for better inventory organization
    Requirements: Enhanced inventory management with categorization
    """
    name = models.CharField(max_length=100, unique=True, help_text="Category name")
    description = models.TextField(blank=True, help_text="Category description")
    is_active = models.BooleanField(default=True, help_text="Category status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """
    Supplier management for inventory tracking
    Requirements: Enhanced inventory management with supplier tracking
    """
    name = models.CharField(max_length=200, unique=True, help_text="Supplier name")
    contact_person = models.CharField(max_length=100, blank=True, help_text="Contact person name")
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number")
    email = models.EmailField(blank=True, help_text="Email address")
    address = models.TextField(blank=True, help_text="Supplier address")
    is_active = models.BooleanField(default=True, help_text="Supplier status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    """
    Detailed stock movement tracking for comprehensive inventory management
    Requirements: Enhanced inventory management with detailed movement tracking
    """
    MOVEMENT_TYPES = [
        ('delivery', 'Delivery'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('return', 'Return'),
        ('damage', 'Damage/Loss'),
        ('audit', 'Audit Adjustment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'LPGProduct',
        on_delete=models.CASCADE,
        related_name='stock_movements',
        help_text="Product involved in the movement"
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        help_text="Type of stock movement"
    )
    quantity = models.IntegerField(help_text="Quantity moved (positive for in, negative for out)")
    previous_stock = models.IntegerField(help_text="Stock level before movement")
    new_stock = models.IntegerField(help_text="Stock level after movement")
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference ID (order ID, delivery ID, etc.)"
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        help_text="User who created this movement"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['movement_type', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.movement_type.title()}: {self.quantity} {self.product.name}"


class InventoryAdjustment(models.Model):
    """
    Inventory adjustments for stock corrections
    Requirements: Enhanced inventory management with adjustment tracking
    """
    ADJUSTMENT_REASONS = [
        ('damage', 'Damage'),
        ('theft', 'Theft'),
        ('expired', 'Expired'),
        ('count_error', 'Count Error'),
        ('system_error', 'System Error'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'LPGProduct',
        on_delete=models.CASCADE,
        related_name='adjustments',
        help_text="Product being adjusted"
    )
    quantity_change = models.IntegerField(help_text="Quantity change (positive or negative)")
    reason = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_REASONS,
        help_text="Reason for adjustment"
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    adjusted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inventory_adjustments',
        help_text="User who made the adjustment"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inventory Adjustment"
        verbose_name_plural = "Inventory Adjustments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Adjustment: {self.quantity_change} {self.product.name} ({self.reason})"

    def save(self, *args, **kwargs):
        """Update product stock and create stock movement on save"""
        print(f"\n{'='*80}")
        print(f"[DEBUG] InventoryAdjustment.save() called")
        print(f"[DEBUG] self.pk = {self.pk}")
        print(f"[DEBUG] self.quantity_change = {self.quantity_change}")
        print(f"[DEBUG] self.product = {self.product}")
        print(f"[DEBUG] self.reason = {self.reason}")
        print(f"{'='*80}\n")
        
        # Use _state.adding to properly detect new instances (UUID fields generate pk before save)
        is_new = self._state.adding
        print(f"[DEBUG] is_new (using _state.adding) = {is_new}")
        print(f"[DEBUG] self.pk is None = {self.pk is None}")
        print(f"[DEBUG] self._state.adding = {self._state.adding}")

        if is_new:
            print(f"[DEBUG] This is a NEW adjustment (pk is None)")
            
            # Verify quantity_change is set
            print(f"[DEBUG] Checking if quantity_change is set...")
            if not self.quantity_change and self.quantity_change != 0:
                error_msg = "quantity_change must be set before saving"
                print(f"[ERROR] {error_msg}")
                raise ValueError(error_msg)
            print(f"[DEBUG] quantity_change is set: {self.quantity_change}")
            
            # Refresh product from DB to get latest stock
            print(f"[DEBUG] Refreshing product from DB...")
            self.product.refresh_from_db()
            print(f"[DEBUG] Product refreshed: {self.product}")
            
            # Store previous stock
            previous_stock = self.product.current_stock
            print(f"[DEBUG] previous_stock = {previous_stock}")
            
            # Update product stock
            new_calculated_stock = previous_stock + self.quantity_change
            print(f"[DEBUG] Calculating: {previous_stock} + {self.quantity_change} = {new_calculated_stock}")
            self.product.current_stock = new_calculated_stock
            print(f"[DEBUG] Set product.current_stock to {self.product.current_stock}")
            
            # Validate stock won't go negative
            print(f"[DEBUG] Validating stock won't be negative...")
            if self.product.current_stock < 0:
                error_msg = f"Adjustment would result in negative stock. Current: {previous_stock}, Change: {self.quantity_change}, Result: {self.product.current_stock}"
                print(f"[ERROR] {error_msg}")
                raise ValueError(error_msg)
            print(f"[DEBUG] Validation passed - stock is valid: {self.product.current_stock}")
            
            # Save the product with updated stock
            print(f"[DEBUG] Saving product to database...")
            try:
                self.product.save(update_fields=['current_stock', 'updated_at'])
                print(f"[DEBUG] Product saved successfully!")
                print(f"[DEBUG] Verified product.current_stock in DB: {self.product.current_stock}")
            except Exception as e:
                print(f"[ERROR] Failed to save product: {str(e)}")
                import traceback
                traceback.print_exc()
                raise

            # Create stock movement record for audit trail
            print(f"[DEBUG] Creating StockMovement record...")
            try:
                movement = StockMovement.objects.create(
                    product=self.product,
                    movement_type='adjustment',
                    quantity=self.quantity_change,
                    previous_stock=previous_stock,
                    new_stock=self.product.current_stock,
                    reference_id=str(self.id),
                    notes=f"Adjustment: {self.reason} - {self.notes}",
                    created_by=self.adjusted_by
                )
                print(f"[DEBUG] StockMovement created successfully: {movement}")
            except Exception as e:
                print(f"[WARNING] Could not create stock movement: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[DEBUG] This is an UPDATE (pk exists: {self.pk})")

        # Save the adjustment record itself
        print(f"[DEBUG] Saving InventoryAdjustment record...")
        try:
            super().save(*args, **kwargs)
            print(f"[DEBUG] InventoryAdjustment saved successfully with ID: {self.id}")
        except Exception as e:
            print(f"[ERROR] Failed to save InventoryAdjustment: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        print(f"\n{'='*80}")
        print(f"[DEBUG] InventoryAdjustment.save() COMPLETE")
        print(f"{'='*80}\n")


class Staff(models.Model):
    """
    Staff model for managing employees
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.CharField(max_length=100, help_text="Staff member's position")
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Staff member's salary"
    )
    hire_date = models.DateField(help_text="Date when the staff member was hired")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        ordering = ['user__username']

    def __str__(self):
        return self.user.username


class Payroll(models.Model):
    """
    Payroll model for managing staff salaries
    """
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='payrolls')
    payment_date = models.DateField(help_text="Date when the salary was paid")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount paid"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about the payment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payroll"
        verbose_name_plural = "Payrolls"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payroll for {self.staff.user.username} on {self.payment_date}"


class Cashier(models.Model):
    """
    Cashier model for managing cashier staff with role-based access
    A cashier is a staff member with permission to manage customer orders
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cashier_profile')
    employee_id = models.CharField(max_length=50, unique=True, help_text="Unique employee ID")
    is_active = models.BooleanField(default=True, help_text="Cashier status")
    shift_start = models.TimeField(null=True, blank=True, help_text="Cashier shift start time")
    shift_end = models.TimeField(null=True, blank=True, help_text="Cashier shift end time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cashier"
        verbose_name_plural = "Cashiers"
        ordering = ['user__username']

    def __str__(self):
        return f"Cashier: {self.user.first_name or self.user.username}"

    def can_manage_order(self):
        """Check if cashier is active and can manage orders"""
        return self.is_active


class CashierTransaction(models.Model):
    """
    Track all transactions processed by cashiers
    Includes customer orders, payments, and refunds
    """
    TRANSACTION_TYPES = [
        ('order', 'Customer Order'),
        ('payment', 'Payment Received'),
        ('refund', 'Refund'),
        ('adjustment', 'Transaction Adjustment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cashier = models.ForeignKey(Cashier, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='cashier_transactions')
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Transaction amount"
    )
    payment_method = models.CharField(
        max_length=50,
        default='cash',
        help_text="Payment method (cash, card, check, etc.)"
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cashier_transactions',
        help_text="Customer involved in the transaction"
    )
    notes = models.TextField(blank=True, help_text="Additional transaction notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cashier Transaction"
        verbose_name_plural = "Cashier Transactions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cashier', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} by {self.cashier.user.username}"


class Notification(models.Model):
    """
    Customer notifications for order updates, cancellations, and other events
    """
    NOTIFICATION_TYPES = [
        ('order_cancelled', 'Order Cancelled'),
        ('order_updated', 'Order Updated'),
        ('order_delivered', 'Order Delivered'),
        ('order_out_for_delivery', 'Order Out for Delivery'),
        ('system_message', 'System Message'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="Customer receiving the notification"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        help_text="Type of notification"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="Related order (if applicable)"
    )
    title = models.CharField(
        max_length=255,
        help_text="Notification title"
    )
    message = models.TextField(
        help_text="Notification message content"
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for cancellation (if order cancelled)"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the customer has read this notification"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was read")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['customer', 'is_read']),
        ]

    def __str__(self):
        return f"Notification for {self.customer.username} - {self.get_notification_type_display()}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()