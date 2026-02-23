from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import (
    CustomerProfile, LPGProduct, Order, DeliveryLog,
    ProductCategory, Supplier, StockMovement, InventoryAdjustment,
    Cashier, CashierTransaction, PendingRegistration, Notification
)


# Customize default admin site
admin.site.site_header = "Prycegas Station Administration"
admin.site.site_title = "Prycegas Admin"
admin.site.index_title = "Welcome to Prycegas Admin Panel"


# Store original index method
_original_index = admin.site.index


def custom_index(self, request, extra_context=None):
    """
    Enhanced admin index with user management stats
    """
    # Get pending registrations count
    pending_count = PendingRegistration.objects.filter(status='pending').count()
    approved_count = PendingRegistration.objects.filter(status='approved').count()
    rejected_count = PendingRegistration.objects.filter(status='rejected').count()
    total_count = PendingRegistration.objects.count()
    
    # Get user stats
    customers = CustomerProfile.objects.count()
    cashiers = Cashier.objects.count()
    
    extra_context = extra_context or {}
    extra_context.update({
        'pending_registrations_count': pending_count,
        'approved_registrations_count': approved_count,
        'rejected_registrations_count': rejected_count,
        'total_registrations_count': total_count,
        'total_customers': customers,
        'total_cashiers': cashiers,
    })
    
    return _original_index(request, extra_context)


# Replace the index method
admin.site.index = custom_index


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LPGProduct)
class LPGProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'sku', 'price', 'current_stock', 'reserved_stock', 'minimum_stock', 'is_low_stock', 'is_active')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'size', 'sku', 'barcode')
    readonly_fields = ('created_at', 'updated_at', 'available_stock', 'stock_value', 'profit_margin')
    list_editable = ('price', 'current_stock', 'minimum_stock', 'is_active')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'size', 'sku', 'barcode', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'cost_price', 'profit_margin')
        }),
        ('Inventory', {
            'fields': ('current_stock', 'reserved_stock', 'available_stock', 'minimum_stock', 'maximum_stock', 'reorder_point', 'reorder_quantity')
        }),
        ('Physical Properties', {
            'fields': ('weight',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'delivery_type', 'status', 'total_amount', 'order_date')
    list_filter = ('status', 'delivery_type', 'order_date')
    search_fields = ('customer__username', 'product__name')
    readonly_fields = ('total_amount', 'order_date', 'created_at', 'updated_at', 'cancelled_at')
    list_editable = ('status',)
    date_hierarchy = 'order_date'
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'product', 'quantity', 'delivery_type', 'delivery_address')
        }),
        ('Status & Dates', {
            'fields': ('status', 'order_date', 'delivery_date')
        }),
        ('Cancellation Details', {
            'fields': ('cancelled_by', 'cancelled_at', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Payment & Processing', {
            'fields': ('total_amount', 'processed_by', 'delivery_person_name', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_received', 'supplier_name', 'delivery_date', 'total_cost', 'logged_by')
    list_filter = ('delivery_date', 'supplier_name')
    search_fields = ('product__name', 'supplier_name')
    readonly_fields = ('total_cost', 'created_at')
    date_hierarchy = 'delivery_date'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'contact_person', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'created_by', 'created_at')
    list_filter = ('movement_type', 'created_at', 'product')
    search_fields = ('product__name', 'reference_id', 'notes')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        # Stock movements should be created automatically, not manually
        return False

    def has_change_permission(self, request, obj=None):
        # Stock movements should not be editable
        return False


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_change', 'reason', 'adjusted_by', 'created_at')
    list_filter = ('reason', 'created_at', 'product')
    search_fields = ('product__name', 'notes')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'is_active', 'shift_start', 'shift_end', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'employee_id')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Shift Details', {
            'fields': ('shift_start', 'shift_end')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CashierTransaction)
class CashierTransactionAdmin(admin.ModelAdmin):
    list_display = ('cashier', 'transaction_type', 'amount', 'customer', 'payment_method', 'created_at')
    list_filter = ('transaction_type', 'payment_method', 'created_at')
    search_fields = ('cashier__user__username', 'customer__username', 'notes')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing pending user registrations
    Allows admins to approve or reject registrations with ID verification
    """
    list_display = (
        'username', 
        'email', 
        'phone_number', 
        'id_type',
        'status_badge',
        'days_pending',
        'id_document_preview',
        'reviewed_by',
        'created_at',
        'actions_column'
    )
    list_filter = ('status', 'id_type', 'created_at', 'reviewed_by')
    search_fields = ('username', 'email', 'phone_number', 'id_number')
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'reviewed_at',
        'id_document_preview',
        'days_pending'
    )
    
    fieldsets = (
        ('Registration Information', {
            'fields': ('username', 'email', 'phone_number')
        }),
        ('Address & Instructions', {
            'fields': ('address', 'delivery_instructions')
        }),
        ('ID Verification', {
            'fields': ('id_type', 'id_number', 'id_document_preview'),
            'classes': ('wide',)
        }),
        ('Status & Review', {
            'fields': ('status', 'rejection_reason', 'reviewed_by', 'reviewed_at', 'days_pending')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_registrations', 'reject_with_reason']
    
    def status_badge(self, obj):
        """Display status as a colored badge"""
        colors = {
            'pending': '#ff6b35',
            'approved': '#10b981',
            'rejected': '#ef4444'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def id_document_preview(self, obj):
        """Display preview of the ID document"""
        if obj.id_document:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 200px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px;" /></a>',
                obj.id_document.url,
                obj.id_document.url
            )
        return 'No document'
    id_document_preview.short_description = 'ID Document'
    
    def actions_column(self, obj):
        """Display action buttons for quick approval/rejection"""
        if obj.status == 'pending':
            approve_url = f"{obj.id}/approve/"
            reject_url = f"{obj.id}/reject/"
            return format_html(
                '<a class="button" href="{}">Approve</a>&nbsp;'
                '<a class="button" style="background-color: #ef4444;" href="{}">Reject</a>',
                approve_url,
                reject_url
            )
        elif obj.status == 'approved':
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Approved</span>')
        else:
            return format_html('<span style="color: #ef4444; font-weight: bold;">✗ Rejected</span>')
    actions_column.short_description = 'Actions'
    
    def approve_registrations(self, request, queryset):
        """Bulk action to approve pending registrations"""
        pending = queryset.filter(status='pending')
        updated = 0
        for reg in pending:
            reg.approve(request.user)
            updated += 1
        self.message_user(request, f'{updated} registration(s) approved.')
    approve_registrations.short_description = "Approve selected registrations"
    
    def reject_with_reason(self, request, queryset):
        """Bulk action for rejection (simplified - logs rejection)"""
        pending = queryset.filter(status='pending')
        updated = 0
        for reg in pending:
            reg.reject(request.user, 'Bulk rejected by admin')
            updated += 1
        self.message_user(request, f'{updated} registration(s) rejected.')
    reject_with_reason.short_description = "Reject selected registrations"
    
    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly if already approved/rejected"""
        if obj and obj.status in ['approved', 'rejected']:
            return list(self.readonly_fields) + [
                'username', 'email', 'phone_number', 'address', 
                'delivery_instructions', 'id_type', 'id_number', 'id_document'
            ]
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of reviewed registrations"""
        if obj and obj.reviewed_at:
            return False
        return True
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('reviewed_by')
    
    class Media:
        css = {
            'all': ('admin/css/pending_registration.css',)
        }


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing customer notifications
    """
    list_display = ('customer', 'notification_type', 'title', 'is_read', 'created_at', 'read_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('customer__username', 'customer__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('customer', 'notification_type', 'order', 'title')
        }),
        ('Content', {
            'fields': ('message', 'reason')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # Notifications are created automatically, not manually
        return False
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('customer', 'order')
