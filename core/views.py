from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Sum, Q, F, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from .forms import (
    CustomerRegistrationForm, CustomerLoginForm, CustomerProfileForm,
    UserUpdateForm, OrderForm, DeliveryLogForm, ProductForm,
    InventoryAdjustmentForm, ProductCategoryForm, SupplierForm,
    StaffForm, PayrollForm, StaffCreationForm, CashierCreationForm,
    CashierUpdateForm, CashierOrderForm, CashierTransactionForm,
    PendingRegistrationForm
)
from .models import (
    CustomerProfile, LPGProduct, Order, DeliveryLog,
    ProductCategory, Supplier, StockMovement, InventoryAdjustment,
    Staff, Payroll, Cashier, CashierTransaction, PendingRegistration,
    Notification
)


def test_base_template(request):
    """Test view to verify base template functionality"""
    return render(request, 'test_base.html')


# Authentication Views
@csrf_protect
def customer_register(request):
    """
    Customer registration view with ID verification
    Requirements: Registration with ID document upload and admin approval
    """
    if request.user.is_authenticated:
        return redirect('core:customer_dashboard')
    
    if request.method == 'POST':
        form = PendingRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the pending registration
                pending_reg = form.save(commit=False)
                # Hash and store the password
                password = form.cleaned_data.get('password1')
                from django.contrib.auth.hashers import make_password
                pending_reg.password = make_password(password)
                pending_reg.save()
                
                username = form.cleaned_data.get('username')
                messages.success(
                    request, 
                    f'Registration submitted successfully! Your account is pending admin approval. '
                    f'We\'ll email you at {form.cleaned_data.get("email")} once approved.'
                )
                return redirect('core:login')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            # Form has validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = PendingRegistrationForm()
    
    return render(request, 'auth/register_enhanced.html', {'form': form})


@csrf_protect
def customer_login(request):
    """
    Customer login view using Django's built-in authentication
    Requirements: 1.4 - Customer login functionality
    """
    if request.user.is_authenticated:
        return redirect('core:customer_dashboard')
    
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page if specified, otherwise to dashboard
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('core:customer_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerLoginForm()
    
    return render(request, 'auth/login_enhanced.html', {'form': form})


@require_http_methods(["POST"])
def customer_logout(request):
    """
    Customer logout functionality
    Requirements: 1.5 - Customer logout functionality
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'You have been logged out successfully, {username}.')
    return redirect('core:login')


@login_required
@csrf_protect
def customer_profile(request):
    """
    Customer profile view for updating profile information
    Requirements: 1.2 - Customer profile management
    """
    try:
        customer_profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        customer_profile = CustomerProfile.objects.create(
            user=request.user,
            phone_number='',
            address='',
            delivery_instructions=''
        )
    
    is_ajax_upload = request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.FILES.get('profile_picture')
    
    if request.method == 'POST':
        if is_ajax_upload:
            profile_form = CustomerProfileForm(request.POST, request.FILES, instance=customer_profile)
            profile_form.set_ajax_mode()
            if profile_form.is_valid():
                profile_form.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Profile picture updated!',
                    'image_url': customer_profile.get_profile_picture_url()
                })
            return JsonResponse({'success': False, 'message': 'Invalid file'})
        
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=customer_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('core:profile')
        else:
            for form in [user_form, profile_form]:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=customer_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'customer_profile': customer_profile
    }
    return render(request, 'customer/profile.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_protect
def remove_profile_picture(request):
    """
    Remove the customer's profile picture
    """
    try:
        customer_profile = request.user.customer_profile
        if customer_profile.profile_picture:
            customer_profile.profile_picture.delete(save=True)
            return JsonResponse({'success': True, 'message': 'Profile picture removed successfully.'})
        return JsonResponse({'success': False, 'message': 'No profile picture to remove.'})
    except CustomerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Profile not found.'}, status=404)


# HTMX Views for enhanced form validation
@csrf_protect
def validate_username(request):
    """
    Enhanced HTMX endpoint for real-time username validation with security
    Requirements: 10.1, 10.2, 10.3 - Form validation with security measures
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        # Input sanitization
        from django.utils.html import strip_tags
        username = strip_tags(username)
        
        if username:
            # Length validation
            if len(username) < 3:
                return JsonResponse({
                    'valid': False,
                    'message': 'Username must be at least 3 characters long.'
                })
            elif len(username) > 30:
                return JsonResponse({
                    'valid': False,
                    'message': 'Username cannot exceed 30 characters.'
                })
            
            # Character validation
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return JsonResponse({
                    'valid': False,
                    'message': 'Username can only contain letters, numbers, and underscores.'
                })
            
            # Uniqueness validation
            if User.objects.filter(username__iexact=username).exists():
                return JsonResponse({
                    'valid': False,
                    'message': 'This username is already taken.'
                })
            
            return JsonResponse({
                'valid': True,
                'message': 'Username is available.'
            })
        
        return JsonResponse({
            'valid': False,
            'message': 'Username is required.'
        })
    
    return JsonResponse({'valid': False, 'message': 'Invalid request method.'})


@csrf_protect
def validate_email(request):
    """
    Enhanced HTMX endpoint for real-time email validation with security
    Requirements: 10.1, 10.2, 10.3 - Form validation with security measures
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user_id = request.POST.get('user_id')  # For profile updates
        
        # Input sanitization
        from django.utils.html import strip_tags
        email = strip_tags(email).lower()
        
        if email:
            # Email format validation
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return JsonResponse({
                    'valid': False,
                    'message': 'Please enter a valid email address.'
                })
            
            # Uniqueness validation
            query = User.objects.filter(email__iexact=email)
            if user_id:
                try:
                    query = query.exclude(pk=int(user_id))
                except (ValueError, TypeError):
                    pass
            
            if query.exists():
                return JsonResponse({
                    'valid': False,
                    'message': 'This email is already registered.'
                })
            
            return JsonResponse({
                'valid': True,
                'message': 'Email is available.'
            })
        
        return JsonResponse({
            'valid': False,
            'message': 'Email is required.'
        })
    
    return JsonResponse({'valid': False, 'message': 'Invalid request method.'})


# Customer Dashboard View
@login_required
def customer_dashboard(request):
    """
    Customer dashboard showing recent orders and quick actions
    Requirements: 3.1 - Customer order history display
    Optimized: Added select_related to prevent N+1 queries
    Batch orders are grouped together
    """
    all_orders = Order.objects.filter(customer=request.user).select_related('product').order_by('-order_date')
    
    seen_batches = set()
    unique_orders = []
    for order in all_orders:
        if order.batch_id not in seen_batches:
            seen_batches.add(order.batch_id)
            unique_orders.append(order)
        if len(unique_orders) >= 5:
            break
    
    order_stats = {
        'total_orders': len(seen_batches),
        'pending_orders': Order.objects.filter(customer=request.user, status='pending').values('batch_id').distinct().count(),
        'delivered_orders': Order.objects.filter(customer=request.user, status='delivered').values('batch_id').distinct().count(),
    }
    
    context = {
        'recent_orders': unique_orders,
        'total_orders': order_stats['total_orders'],
        'pending_orders': order_stats['pending_orders'],
        'delivered_orders': order_stats['delivered_orders'],
    }
    return render(request, 'customer/dashboard.html', context)


# Order Placement Views
@login_required
@csrf_protect
def place_order(request):
    """
    Customer order placement view with product selection and delivery options
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5 - Order placement system with multiple items support
    CUSTOMERS ONLY - Cashiers cannot place orders; they process customer orders
    """
    import json
    import traceback
    
    # Restrict access to customers only - NOT cashiers
    if hasattr(request.user, 'cashier_profile') and request.user.cashier_profile.is_active:
        messages.error(request, 'Cashiers cannot place orders. Use order management to process customer orders.')
        return redirect('core:cashier_order_list')
    
    # Also prevent staff/admin from accessing this endpoint
    if request.user.is_staff:
        messages.error(request, 'Use order management to create orders.')
        return redirect('core:order_management')
    
    if request.method == 'POST':
        try:
            # Get cart items from the request
            cart_items_json = request.POST.get('cart_items', '[]')
            cart_items = json.loads(cart_items_json)
            
            if not cart_items:
                raise ValueError('No items in cart')
            
            # Get delivery details from form
            delivery_type = request.POST.get('delivery_type')
            delivery_address = request.POST.get('delivery_address', '')
            notes = request.POST.get('notes', '')
            
            # Validate delivery
            if delivery_type == 'delivery' and not delivery_address.strip():
                raise ValueError('Delivery address is required for delivery orders')
            
            with transaction.atomic():
                orders = []
                total_amount = Decimal('0.00')
                batch_id = uuid.uuid4()
                
                for item in cart_items:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity', 1)
                    
                    try:
                        product = LPGProduct.objects.get(id=product_id, is_active=True)
                    except LPGProduct.DoesNotExist:
                        raise ValueError(f'Product ID {product_id} not found')
                    
                    if not product.can_fulfill_order(quantity):
                        raise ValueError(f'Insufficient stock for {product.name}. Only {product.current_stock} available.')
                    
                    order_total = product.price * quantity
                    total_amount += order_total
                    
                    order = Order(
                        batch_id=batch_id,
                        customer=request.user,
                        product=product,
                        quantity=quantity,
                        delivery_type=delivery_type,
                        delivery_address=delivery_address if delivery_type == 'delivery' else '',
                        notes=notes,
                        total_amount=order_total
                    )
                    order.save()
                    
                    product.current_stock -= quantity
                    product.save()
                    
                    orders.append(order)
                
                if len(orders) == 1:
                    messages.success(
                        request,
                        f'Order #{orders[0].id} placed successfully! Total: ₱{total_amount:.2f}'
                    )
                else:
                    messages.success(
                        request,
                        f'Batch Order placed successfully! {len(orders)} items (Batch #{batch_id})! Total: ₱{total_amount:.2f}'
                    )
                
                # Return JSON response for AJAX requests
                if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'{len(orders)} order(s) placed successfully!',
                        'order_ids': [o.id for o in orders],
                        'total_amount': float(total_amount),
                        'redirect': '/customer/dashboard/'
                    })
                
                return redirect('core:customer_dashboard')
                
        except json.JSONDecodeError:
            error_msg = 'Invalid request format'
            is_ajax = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        except ValueError as e:
            error_msg = str(e)
            is_ajax = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        except Exception as e:
            error_msg = f'Error placing order: {str(e)}'
            print(f'Order placement error: {error_msg}')
            print(traceback.format_exc())
            is_ajax = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
    else:
        form = OrderForm(user=request.user)
    
    # Get available products for display
    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    
    context = {
        'form': form,
        'products': products,
    }
    return render(request, 'customer/place_order.html', context)


@login_required
def check_stock(request):
    """
    HTMX endpoint for real-time stock checking
    Requirements: 2.4 - Real-time inventory checking using HTMX
    """
    product_id = request.GET.get('product')
    quantity = request.GET.get('quantity', 1)
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    if not product_id:
        return render(request, 'customer/stock_info.html', {
            'show_info': False
        })
    
    try:
        product = LPGProduct.objects.get(id=product_id, is_active=True)
        
        # Calculate total price
        total_price = product.price * quantity
        
        # Check stock availability
        stock_available = product.can_fulfill_order(quantity)
        stock_status = 'available' if stock_available else 'insufficient'
        
        # Determine stock level status
        if product.current_stock == 0:
            stock_level = 'out_of_stock'
        elif product.is_low_stock:
            stock_level = 'low_stock'
        else:
            stock_level = 'in_stock'
        
        context = {
            'show_info': True,
            'product': product,
            'quantity': quantity,
            'total_price': total_price,
            'stock_available': stock_available,
            'stock_status': stock_status,
            'stock_level': stock_level,
        }
        
    except LPGProduct.DoesNotExist:
        context = {
            'show_info': False,
            'error': 'Product not found'
        }
    
    return render(request, 'customer/stock_info.html', context)


@login_required
def get_product_details(request):
    """
    API endpoint for getting product details (price, stock) for the cart system
    """
    product_id = request.GET.get('product_id')
    
    if not product_id:
        return JsonResponse({
            'success': False,
            'message': 'Product ID is required'
        })
    
    try:
        product = LPGProduct.objects.get(id=product_id, is_active=True)
        
        return JsonResponse({
            'success': True,
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'current_stock': product.current_stock,
            'can_fulfill': product.can_fulfill_order(1)
        })
    except LPGProduct.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
def order_history(request):
    """
    Customer order history view with filtering and status tracking
    Requirements: 3.1, 3.2, 3.3 - Order history and tracking
    Optimized: Added pagination and query optimization
    Batch orders are grouped together
    """
    from django.core.paginator import Paginator
    
    orders = Order.objects.filter(customer=request.user).select_related('product').order_by('-order_date', 'batch_id', 'id')
    
    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    sort_by = request.GET.get('sort', '-order_date')
    if sort_by in ['-order_date', 'order_date', '-total_amount', 'total_amount', 'status']:
        orders = orders.order_by(sort_by, 'batch_id', 'id')
    
    seen_batches = set()
    unique_orders = []
    for order in orders:
        if order.batch_id not in seen_batches:
            seen_batches.add(order.batch_id)
            unique_orders.append(order)
    
    paginator = Paginator(unique_orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
        'current_sort': sort_by,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'customer/order_history.html', context)


@login_required
def export_order_history_pdf(request):
    """
    Export customer order history as PDF using ReportLab
    """
    # Get filter and sort parameters
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-order_date')
    
    # Fetch orders with filters
    orders = Order.objects.filter(customer=request.user).select_related('product')
    
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    if sort_by in ['-order_date', 'order_date', '-total_amount', 'total_amount', 'status']:
        orders = orders.order_by(sort_by)
    else:
        orders = orders.order_by('-order_date')
    
    # Create PDF buffer
    pdf_buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Order History"
    )
    
    # Container for PDF elements
    elements = []
    
    # Custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF6B35'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#FF6B35'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("Prycegas Station", title_style))
    elements.append(Paragraph("Order History Report", header_style))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", header_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer Info
    elements.append(Paragraph("Customer Information", heading_style))
    customer_name = request.user.get_full_name() or request.user.username
    try:
        customer_profile = request.user.customer_profile
        customer_phone = customer_profile.phone_number
        customer_address = customer_profile.address[:50] + "..." if len(customer_profile.address) > 50 else customer_profile.address
    except:
        customer_phone = "N/A"
        customer_address = "N/A"
    
    customer_info = f"Name: {customer_name} | Phone: {customer_phone} | Address: {customer_address}"
    elements.append(Paragraph(customer_info, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Orders summary
    if orders.exists():
        elements.append(Paragraph("Order Details", heading_style))
        
        # Prepare table data
        table_data = [
            [
                Paragraph("Order #", styles['Normal']),
                Paragraph("Date", styles['Normal']),
                Paragraph("Product", styles['Normal']),
                Paragraph("Qty", styles['Normal']),
                Paragraph("Price/Unit", styles['Normal']),
                Paragraph("Total", styles['Normal']),
                Paragraph("Status", styles['Normal']),
                Paragraph("Type", styles['Normal']),
            ]
        ]
        
        # Add order rows
        for order in orders:
            status_display = dict(Order.STATUS_CHOICES).get(order.status, order.status)
            delivery_display = dict(Order.DELIVERY_CHOICES).get(order.delivery_type, order.delivery_type)
            
            table_data.append([
                Paragraph(f"#{order.id}", styles['Normal']),
                Paragraph(order.order_date.strftime("%b %d, %Y"), styles['Normal']),
                Paragraph(order.product.name, styles['Normal']),
                Paragraph(str(order.quantity), styles['Normal']),
                Paragraph(f"₦{order.product.price:,.2f}", styles['Normal']),
                Paragraph(f"₦{order.total_amount:,.2f}", styles['Normal']),
                Paragraph(status_display, styles['Normal']),
                Paragraph(delivery_display.capitalize(), styles['Normal']),
            ])
        
        # Create table
        table = Table(table_data, colWidths=[0.8*inch, 0.9*inch, 1.2*inch, 0.5*inch, 0.9*inch, 1*inch, 1*inch, 0.8*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Align numeric columns to the right
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (6, -1), 'RIGHT'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary statistics
        total_orders = orders.count()
        total_amount = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        pending_count = orders.filter(status='pending').count()
        delivered_count = orders.filter(status='delivered').count()
        
        summary_text = f"""
        <b>Summary:</b> Total Orders: {total_orders} | Pending: {pending_count} | Delivered: {delivered_count} | 
        Total Amount: ₦{total_amount:,.2f}
        """
        elements.append(Paragraph(summary_text, styles['Normal']))
    else:
        elements.append(Paragraph("No orders found.", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = "This is an official document from Prycegas Station. For inquiries, please contact support."
    elements.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
        borderPadding=10,
        borderColor=colors.grey,
        borderWidth=0.5
    )))
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF as response
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_history_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response


@login_required
def order_detail(request, order_id):
    """
    Customer order detail view with delivery tracking information
    Requirements: 3.3, 3.4 - Order detail view with tracking
    Shows all products if batch order
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    batch_items = order.batch_items
    batch_total = order.batch_total
    
    status_progress = {
        'pending': 25,
        'out_for_delivery': 75,
        'delivered': 100,
        'cancelled': 0
    }
    
    context = {
        'order': order,
        'batch_items': batch_items,
        'batch_total': batch_total,
        'progress_percentage': status_progress.get(order.status, 0),
    }
    return render(request, 'customer/order_detail.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_protect
def mark_order_received(request, order_id):
    """
    Mark an order as received by the customer
    Requirements: 3.5 - Customer marks order as received
    Marks all items in the batch order as delivered
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    batch_items = order.batch_items.filter(status='out_for_delivery')
    if not batch_items.exists():
        messages.error(request, 'Order is not out for delivery.')
        if request.headers.get('HX-Request'):
            return redirect('core:order_detail', order_id=order.id)
        return redirect('core:order_detail', order_id=order.id)
    
    try:
        with transaction.atomic():
            from .models import Cashier, CashierTransaction
            
            delivered_count = 0
            for item in batch_items:
                item.status = 'delivered'
                item.delivery_date = timezone.now()
                
                if not item.processed_by:
                    cashiers = Cashier.objects.filter(is_active=True)
                    if cashiers.exists():
                        item.processed_by = cashiers.first()
                
                item.save()
                delivered_count += 1
                
                if item.processed_by:
                    existing = CashierTransaction.objects.filter(order=item).exists()
                    if not existing:
                        CashierTransaction.objects.create(
                            cashier=item.processed_by,
                            order=item,
                            transaction_type='order',
                            amount=item.total_amount,
                            payment_method='cash',
                            customer=item.customer
                        )
            
            messages.success(request, f'Order marked as received successfully! {delivered_count} item(s) delivered.')
    except Exception as e:
        messages.error(request, f'Error marking order as received: {str(e)}')
        if request.headers.get('HX-Request'):
            return redirect('core:order_detail', order_id=order.id)
        return redirect('core:order_detail', order_id=order.id)
    
    if request.headers.get('HX-Request'):
        status_progress = {
            'pending': 25,
            'out_for_delivery': 75,
            'delivered': 100,
            'cancelled': 0
        }
        order.refresh_from_db()
        batch_items = order.batch_items
        batch_total = order.batch_total
        context = {
            'order': order,
            'batch_items': batch_items,
            'batch_total': batch_total,
            'progress_percentage': status_progress.get(order.status, 0),
        }
        return render(request, 'customer/order_detail_section.html', context)
    
    return redirect('core:order_detail', order_id=order.id)


@login_required
@require_http_methods(["POST"])
@csrf_protect
def cancel_order(request, order_id):
    """
    Cancel a customer order if it's still pending
    Requirements: 3.6 - Customer can cancel pending orders
    Cancels all items in the batch order
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    cancellation_reason = request.POST.get('cancellation_reason', 'Customer requested cancellation')
    
    batch_items = order.batch_items
    first_pending = batch_items.filter(status='pending').first()
    
    if not first_pending:
        messages.error(request, f'Cannot cancel order. Items are no longer pending.')
        return redirect('core:order_detail', order_id=order.id)
    
    try:
        with transaction.atomic():
            cancelled_count = 0
            for item in batch_items.filter(status='pending'):
                item.product.release_stock(item.quantity)
                
                item.status = 'cancelled'
                item.cancellation_reason = cancellation_reason
                item.cancelled_by = request.user
                item.cancelled_at = timezone.now()
                item.save()
                cancelled_count += 1
            
            from .models import Notification
            Notification.objects.create(
                customer=request.user,
                notification_type='order_cancelled',
                order=order,
                title=f'Order #{order.id} Cancelled',
                message=f'Your order ({cancelled_count} item(s)) has been cancelled.',
                reason=cancellation_reason
            )
            
            messages.success(request, f'Order cancelled successfully! {cancelled_count} item(s) cancelled.')
    except Exception as e:
        messages.error(request, f'Error cancelling order: {str(e)}')
        return redirect('core:order_detail', order_id=order.id)
    
    if request.headers.get('HX-Request'):
        status_progress = {
            'pending': 25,
            'out_for_delivery': 75,
            'delivered': 100,
            'cancelled': 0
        }
        order.refresh_from_db()
        batch_items = order.batch_items
        batch_total = order.batch_total
        context = {
            'order': order,
            'batch_items': batch_items,
            'batch_total': batch_total,
            'progress_percentage': status_progress.get(order.status, 0),
        }
        return render(request, 'customer/order_detail_section.html', context)
    
    return redirect('core:order_detail', order_id=order.id)


@login_required
def refresh_order_status(request):
    """
    HTMX endpoint for real-time order status updates
    Requirements: 3.2 - Real-time order status updates using HTMX
    """
    if request.headers.get('HX-Request'):
        orders = Order.objects.filter(customer=request.user).select_related('product').order_by('-order_date')
        
        # Apply same filters as order_history
        status_filter = request.GET.get('status')
        if status_filter and status_filter in dict(Order.STATUS_CHOICES):
            orders = orders.filter(status=status_filter)
        
        sort_by = request.GET.get('sort', '-order_date')
        if sort_by in ['-order_date', 'order_date', '-total_amount', 'total_amount', 'status']:
            orders = orders.order_by(sort_by)
        
        context = {
            'orders': orders,
            'current_status': status_filter,
        }
        return render(request, 'customer/order_list_partial.html', context)
    
    return redirect('core:order_history')


# Dealer/Admin Authentication Helper
def is_dealer(user):
    """
    Check if user is a dealer/admin (staff member)
    Requirements: 4.1 - Dealer authentication and permission system
    """
    return user.is_authenticated and user.is_staff


# Dealer/Admin Dashboard Views
@user_passes_test(is_dealer, login_url='core:login')
def dealer_dashboard(request):
    """
    Main dealer dashboard with order counts, inventory levels, and recent activity
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5 - Dealer dashboard with overview
    Optimized: Combined queries and added caching for better performance
    """
    from django.core.cache import cache
    
    # Try to get cached dashboard stats first
    cache_key = 'dealer_dashboard_stats'
    dashboard_stats = cache.get(cache_key)
    
    if not dashboard_stats:
        # Calculate dashboard statistics with optimized queries
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Use aggregate queries for better performance
        order_stats = Order.objects.aggregate(
            total_orders=Count('id'),
            pending_orders=Count('id', filter=Q(status='pending')),
            out_for_delivery=Count('id', filter=Q(status='out_for_delivery')),
            delivered_today=Count('id', filter=Q(status='delivered', delivery_date__date=today)),
            weekly_orders=Count('id', filter=Q(order_date__date__gte=week_ago)),
            weekly_revenue=Sum('total_amount', filter=Q(order_date__date__gte=week_ago, status='delivered'))
        )
        
        # Inventory statistics with single query
        inventory_stats = LPGProduct.objects.filter(is_active=True).aggregate(
            total_products=Count('id'),
            low_stock_products=Count('id', filter=Q(current_stock__lte=F('minimum_stock'))),
            out_of_stock=Count('id', filter=Q(current_stock=0)),
            total_stock_value=Sum(F('current_stock') * F('price'))
        )
        
        dashboard_stats = {
            **order_stats,
            **inventory_stats,
            'weekly_revenue': order_stats['weekly_revenue'] or 0,
            'total_stock_value': inventory_stats['total_stock_value'] or 0,
        }
        
        # Cache for 30 seconds to reduce database load
        cache.set(cache_key, dashboard_stats, 30)
    
    # Recent activity with optimized queries
    recent_orders = Order.objects.select_related('customer', 'product').order_by('-order_date')[:10]
    recent_deliveries = DeliveryLog.objects.select_related('product', 'logged_by').order_by('-created_at')[:5]
    low_stock_alerts = LPGProduct.objects.filter(
        is_active=True,
        current_stock__lte=F('minimum_stock')
    ).order_by('current_stock')[:5]
    
    context = {
        'dashboard_stats': dashboard_stats,
        'recent_orders': recent_orders,
        'recent_deliveries': recent_deliveries,
        'low_stock_alerts': low_stock_alerts,
    }
    
    return render(request, 'dealer/dashboard.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def refresh_dashboard_stats(request):
    """
    HTMX endpoint for refreshing dashboard statistics with real-time updates
    Requirements: 4.4, 4.5 - Real-time dashboard updates using Unpoly
    """
    if request.headers.get('HX-Request') or request.headers.get('X-Up-Target'):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Recalculate statistics
        dashboard_stats = {
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'out_for_delivery': Order.objects.filter(status='out_for_delivery').count(),
            'delivered_today': Order.objects.filter(
                status='delivered',
                delivery_date__date=today
            ).count(),
            'weekly_orders': Order.objects.filter(order_date__date__gte=week_ago).count(),
            'weekly_revenue': Order.objects.filter(
                order_date__date__gte=week_ago,
                status='delivered'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            'total_products': LPGProduct.objects.filter(is_active=True).count(),
            'low_stock_products': LPGProduct.objects.filter(
                is_active=True,
                current_stock__lte=F('minimum_stock')
            ).count(),
            'out_of_stock': LPGProduct.objects.filter(
                is_active=True,
                current_stock=0
            ).count(),
            'total_stock_value': LPGProduct.objects.filter(is_active=True).aggregate(
                total=Sum(F('current_stock') * F('price'))
            )['total'] or 0,
        }
        
        context = {'dashboard_stats': dashboard_stats}
        return render(request, 'dealer/dashboard_stats_partial.html', context)
    
    return redirect('core:dealer_dashboard')


@user_passes_test(is_dealer, login_url='core:login')
def refresh_recent_activity(request):
    """
    HTMX endpoint for refreshing recent activity section
    Requirements: 4.4, 4.5 - Real-time activity updates
    """
    if request.headers.get('HX-Request') or request.headers.get('X-Up-Target'):
        recent_orders = Order.objects.select_related('customer', 'product').order_by('-order_date')[:10]
        recent_deliveries = DeliveryLog.objects.select_related('product', 'logged_by').order_by('-created_at')[:5]
        low_stock_alerts = LPGProduct.objects.filter(
            is_active=True,
            current_stock__lte=F('minimum_stock')
        ).order_by('current_stock')[:5]
        
        context = {
            'recent_orders': recent_orders,
            'recent_deliveries': recent_deliveries,
            'low_stock_alerts': low_stock_alerts,
        }
        return render(request, 'dealer/recent_activity_partial.html', context)
    
    return redirect('core:dealer_dashboard')


# Order Management Views for Dealers
@user_passes_test(is_dealer, login_url='core:login')
def order_management(request):
    """
    Order list view with sortable and filterable table for dealers
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5 - Order management system
    Optimized: Added pagination and query optimization for large datasets
    """
    from django.core.paginator import Paginator
    
    # Start with optimized base query
    orders = Order.objects.select_related('customer', 'product').all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    # Filter by delivery type
    delivery_filter = request.GET.get('delivery_type', '')
    if delivery_filter and delivery_filter in dict(Order.DELIVERY_CHOICES):
        orders = orders.filter(delivery_type=delivery_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(order_date__date__gte=from_date)
        except ValueError:
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(order_date__date__lte=to_date)
        except ValueError:
            pass
    
    # Search by customer name or order ID
    search_query = request.GET.get('search', '').strip()
    if search_query:
        orders = orders.filter(
            Q(customer__username__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Sort orders
    sort_by = request.GET.get('sort', '-order_date')
    valid_sort_fields = [
        'order_date', '-order_date', 'status', '-status', 
        'total_amount', '-total_amount', 'customer__username', 
        '-customer__username', 'product__name', '-product__name'
    ]
    if sort_by in valid_sort_fields:
        orders = orders.order_by(sort_by)
    else:
        orders = orders.order_by('-order_date')
    
    # Calculate summary statistics before pagination using aggregate
    summary_stats = orders.aggregate(
        total_orders=Count('id'),
        pending_count=Count('id', filter=Q(status='pending')),
        out_for_delivery_count=Count('id', filter=Q(status='out_for_delivery')),
        delivered_count=Count('id', filter=Q(status='delivered'))
    )
    
    # Add pagination for better performance
    paginator = Paginator(orders, 25)  # Show 25 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter choices for template
    status_choices = Order.STATUS_CHOICES
    delivery_choices = Order.DELIVERY_CHOICES
    
    context = {
        'orders': page_obj,
        'status_choices': status_choices,
        'delivery_choices': delivery_choices,
        'current_filters': {
            'status': status_filter,
            'delivery_type': delivery_filter,
            'date_from': date_from,
            'date_to': date_to,
            'search': search_query,
            'sort': sort_by,
        },
        'summary_stats': summary_stats,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'dealer/order_management.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_protect
def update_order_status(request, order_id):
    """
    Update order status with HTMX support
    Allows both dealers and cashiers to update order status
    Requirements: 5.2, 5.3 - Order status updates without page refresh
    """
    # Check if user is dealer or cashier
    is_dealer_user = hasattr(request.user, 'dealer_profile') or request.user.is_superuser
    is_cashier_user = hasattr(request.user, 'cashier_profile') and request.user.cashier_profile.is_active
    
    if not (is_dealer_user or is_cashier_user):
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to update orders.'
            }, status=403)
        messages.error(request, 'You do not have permission to update orders.')
        return redirect('core:login')
    
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    if new_status not in dict(Order.STATUS_CHOICES):
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': False,
                'message': 'Invalid status provided.'
            }, status=400)
        messages.error(request, 'Invalid status provided.')
        return redirect('core:order_management')
    
    # Validate status transition
    valid_transitions = {
        'pending': ['out_for_delivery', 'cancelled'],
        'out_for_delivery': ['delivered', 'cancelled'],
        'delivered': [],  # Cannot change from delivered
        'cancelled': []   # Cannot change from cancelled
    }
    
    if new_status not in valid_transitions.get(order.status, []):
        error_msg = f'Cannot change status from {order.get_status_display()} to {dict(Order.STATUS_CHOICES)[new_status]}.'
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=400)
        messages.error(request, error_msg)
        return redirect('core:order_management')
    
    # Update order status
    old_status = order.status
    order.status = new_status
    
    # Handle cancellation specific logic
    if new_status == 'cancelled':
        cancellation_reason = request.POST.get('cancellation_reason', 'No reason provided')
        order.cancellation_reason = cancellation_reason
        order.cancelled_at = timezone.now()
        order.cancelled_by = request.user
        
        # Create notification for the customer if order has a customer
        if order.customer:
            Notification.objects.create(
                customer=order.customer,
                notification_type='order_cancelled',
                order=order,
                title=f'Order #{order.id} Cancelled',
                message=f'Your order for {order.product.name} (Qty: {order.quantity}) has been cancelled.',
                reason=cancellation_reason
            )
    
    # Track which cashier is processing (set on out_for_delivery or delivered)
    if is_cashier_user and not order.processed_by:
        if new_status in ['out_for_delivery', 'delivered']:
            order.processed_by = request.user.cashier_profile
    
    # Set delivery date when order is delivered
    if new_status == 'delivered' and not order.delivery_date:
        order.delivery_date = timezone.now()
    
    order.save()
    
    # Create CashierTransaction record when order is delivered
    if new_status == 'delivered':
        from .models import CashierTransaction, Cashier
        # Get the cashier who processed this order
        cashier = order.processed_by
        if not cashier and is_cashier_user:
            cashier = request.user.cashier_profile
        
        # Create transaction record if we have a cashier
        if cashier:
            CashierTransaction.objects.create(
                cashier=cashier,
                order=order,
                transaction_type='order',
                amount=order.total_amount,
                payment_method='cash',
                customer=order.customer
            )
    
    success_msg = f'Order #{order.id} status updated from {dict(Order.STATUS_CHOICES)[old_status]} to {order.get_status_display()}.'
    
    # Check if it's an AJAX request (XMLHttpRequest or HX-Request)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for AJAX requests
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'order_id': order.id,
            'new_status': order.status,
            'status_display': order.get_status_display()
        })
    
    if request.headers.get('HX-Request'):
        # Return updated order row for HTMX
        context = {
            'order': order,
            'show_success_message': True,
            'success_message': success_msg
        }
        return render(request, 'dealer/order_row_partial.html', context)
    
    messages.success(request, success_msg)
    
    # Redirect to appropriate dashboard
    if is_cashier_user:
        return redirect('core:cashier_order_list')
    else:
        return redirect('core:order_management')


# Lazy loading views for performance optimization
@user_passes_test(is_dealer, login_url='core:login')
def lazy_load_orders(request):
    """
    Lazy load orders for infinite scroll or pagination
    Requirements: 9.1, 9.2 - Performance optimization with lazy loading
    """
    from django.core.paginator import Paginator
    
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))
    
    # Apply same filters as order_management
    orders = Order.objects.select_related('customer', 'product').all()
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    delivery_filter = request.GET.get('delivery_type', '')
    if delivery_filter and delivery_filter in dict(Order.DELIVERY_CHOICES):
        orders = orders.filter(delivery_type=delivery_filter)
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        orders = orders.filter(
            Q(customer__username__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    sort_by = request.GET.get('sort', '-order_date')
    valid_sort_fields = [
        'order_date', '-order_date', 'status', '-status', 
        'total_amount', '-total_amount', 'customer__username', 
        '-customer__username', 'product__name', '-product__name'
    ]
    if sort_by in valid_sort_fields:
        orders = orders.order_by(sort_by)
    
    paginator = Paginator(orders, page_size)
    page_obj = paginator.get_page(page)
    
    context = {
        'orders': page_obj,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    }
    
    return render(request, 'dealer/order_rows_partial.html', context)


@login_required
def lazy_load_customer_orders(request):
    """
    Lazy load customer orders for infinite scroll
    Requirements: 9.1, 9.2 - Performance optimization with lazy loading
    """
    from django.core.paginator import Paginator
    
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    orders = Order.objects.filter(customer=request.user).select_related('product').order_by('-order_date')
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    sort_by = request.GET.get('sort', '-order_date')
    if sort_by in ['-order_date', 'order_date', '-total_amount', 'total_amount', 'status']:
        orders = orders.order_by(sort_by)
    
    paginator = Paginator(orders, page_size)
    page_obj = paginator.get_page(page)
    
    context = {
        'orders': page_obj,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    }
    
    return render(request, 'customer/order_rows_partial.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def refresh_order_table(request):
    """
    HTMX endpoint for refreshing order table with current filters
    Requirements: 5.3 - Real-time updates without page refresh
    """
    # Reuse the same logic as order_management but return only the table
    from django.core.paginator import Paginator
    
    orders = Order.objects.select_related('customer', 'product').all()
    
    # Apply all filters
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    delivery_filter = request.GET.get('delivery_type', '')
    if delivery_filter and delivery_filter in dict(Order.DELIVERY_CHOICES):
        orders = orders.filter(delivery_type=delivery_filter)
    
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(order_date__date__gte=from_date)
        except ValueError:
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(order_date__date__lte=to_date)
        except ValueError:
            pass
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        orders = orders.filter(
            Q(customer__username__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    sort_by = request.GET.get('sort', '-order_date')
    valid_sort_fields = [
        'order_date', '-order_date', 'status', '-status', 
        'total_amount', '-total_amount', 'customer__username', 
        '-customer__username', 'product__name', '-product__name'
    ]
    if sort_by in valid_sort_fields:
        orders = orders.order_by(sort_by)
    
    # Add pagination
    paginator = Paginator(orders, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'dealer/order_table_partial.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def order_detail_modal(request, order_id):
    """
    Order detail modal with customer information and delivery details
    Requirements: 5.4 - Order detail modal with customer information
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Get customer profile if available
    customer_profile = None
    if hasattr(order.customer, 'customer_profile'):
        customer_profile = order.customer.customer_profile
    
    context = {
        'order': order,
        'customer_profile': customer_profile,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'dealer/order_detail_modal.html', context)
    
    # Fallback for non-HTMX requests
    return render(request, 'dealer/order_detail.html', context)


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["POST"])
@csrf_protect
def bulk_order_operations(request):
    """
    Handle bulk operations on orders
    Requirements: 5.5 - Bulk order operations
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Bulk operation request from user: {request.user}")
    logger.info(f"POST data: {request.POST}")
    logger.info(f"Headers: {dict(request.headers)}")

    operation = request.POST.get('operation')
    order_ids = request.POST.getlist('order_ids')

    logger.info(f"Operation: {operation}, Order IDs: {order_ids}")

    if not order_ids:
        logger.warning("No order IDs provided")
        if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'No orders selected.'
            }, status=400)
        messages.error(request, 'No orders selected.')
        return redirect('core:order_management')
    
    try:
        order_ids = [int(id) for id in order_ids]
        orders = Order.objects.filter(id__in=order_ids)
        
        if not orders.exists():
            raise ValueError("No valid orders found.")
        
        success_count = 0
        error_messages = []
        
        if operation == 'mark_out_for_delivery':
            for order in orders:
                if order.status == 'pending':
                    order.status = 'out_for_delivery'
                    order.save()
                    success_count += 1
                else:
                    error_messages.append(f'Order #{order.id} cannot be marked as out for delivery (current status: {order.get_status_display()})')
        
        elif operation == 'mark_delivered':
            from .models import CashierTransaction, Cashier
            for order in orders:
                if order.status == 'out_for_delivery':
                    order.status = 'delivered'
                    if not order.delivery_date:
                        order.delivery_date = timezone.now()
                    # Set processed_by to current user if cashier
                    if hasattr(request.user, 'cashier_profile') and not order.processed_by:
                        order.processed_by = request.user.cashier_profile
                    order.save()
                    
                    # Create CashierTransaction record
                    if order.processed_by:
                        CashierTransaction.objects.create(
                            cashier=order.processed_by,
                            order=order,
                            transaction_type='order',
                            amount=order.total_amount,
                            payment_method='cash',
                            customer=order.customer
                        )
                    
                    success_count += 1
                else:
                    error_messages.append(f'Order #{order.id} cannot be marked as delivered (current status: {order.get_status_display()})')
        
        elif operation == 'cancel_orders':
            cancellation_reason = request.POST.get('cancellation_reason', 'Order cancelled by staff')
            for order in orders:
                if order.status in ['pending', 'out_for_delivery']:
                    order.status = 'cancelled'
                    order.cancellation_reason = cancellation_reason
                    order.cancelled_at = timezone.now()
                    order.cancelled_by = request.user
                    order.save()
                    
                    # Create notification if order has a customer
                    if order.customer:
                        Notification.objects.create(
                            customer=order.customer,
                            notification_type='order_cancelled',
                            order=order,
                            title=f'Order #{order.id} Cancelled',
                            message=f'Your order for {order.product.name} (Qty: {order.quantity}) has been cancelled.',
                            reason=cancellation_reason
                        )
                    
                    success_count += 1
                else:
                    error_messages.append(f'Order #{order.id} cannot be cancelled (current status: {order.get_status_display()})')
        
        else:
            raise ValueError("Invalid operation.")
        
        # Prepare response message
        if success_count > 0:
            success_msg = f'Successfully processed {success_count} order(s).'
            if error_messages:
                success_msg += f' {len(error_messages)} order(s) could not be processed.'
        else:
            success_msg = 'No orders were processed.'
        
        logger.info(f"Bulk operation completed. Success count: {success_count}, Errors: {len(error_messages)}")

        if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Refresh the order table
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'refresh_table': True,
                'errors': error_messages
            })

        messages.success(request, success_msg)
        for error in error_messages:
            messages.warning(request, error)

    except (ValueError, TypeError) as e:
        error_msg = f'Error processing bulk operation: {str(e)}'
        logger.error(f"Bulk operation error: {error_msg}")
        if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=400)
        messages.error(request, error_msg)
    
    return redirect('core:order_management')


@user_passes_test(is_dealer, login_url='core:login')
def refresh_order_table(request):
    """
    HTMX endpoint for refreshing the order management table
    Requirements: 5.3 - HTMX-powered updates without page refresh
    """
    if request.headers.get('HX-Request'):
        # Use the same filtering logic as order_management view
        orders = Order.objects.select_related('customer', 'product').all()
        
        # Apply filters (same logic as order_management)
        status_filter = request.GET.get('status', '')
        if status_filter and status_filter in dict(Order.STATUS_CHOICES):
            orders = orders.filter(status=status_filter)
        
        delivery_filter = request.GET.get('delivery_type', '')
        if delivery_filter and delivery_filter in dict(Order.DELIVERY_CHOICES):
            orders = orders.filter(delivery_type=delivery_filter)
        
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                orders = orders.filter(order_date__date__gte=from_date)
            except ValueError:
                pass
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                orders = orders.filter(order_date__date__lte=to_date)
            except ValueError:
                pass
        
        search_query = request.GET.get('search', '').strip()
        if search_query:
            orders = orders.filter(
                Q(customer__username__icontains=search_query) |
                Q(customer__first_name__icontains=search_query) |
                Q(customer__last_name__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        sort_by = request.GET.get('sort', '-order_date')
        valid_sort_fields = [
            'order_date', '-order_date', 'status', '-status', 
            'total_amount', '-total_amount', 'customer__username', 
            '-customer__username', 'product__name', '-product__name'
        ]
        if sort_by in valid_sort_fields:
            orders = orders.order_by(sort_by)
        else:
            orders = orders.order_by('-order_date')
        
        context = {
            'orders': orders,
            'current_filters': {
                'status': status_filter,
                'delivery_type': delivery_filter,
                'date_from': date_from,
                'date_to': date_to,
                'search': search_query,
                'sort': sort_by,
            }
        }
        
        return render(request, 'dealer/order_table_partial.html', context)
    
    return redirect('core:order_management')


@login_required
def batch_order_detail_modal(request, batch_id):
    """
    Batch order detail modal showing all items in a batch order
    """
    import uuid
    try:
        batch_uuid = uuid.UUID(str(batch_id))
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid batch ID'}, status=400)
    
    orders = Order.objects.filter(batch_id=batch_uuid).select_related('customer', 'product').order_by('id')
    
    if not orders.exists():
        return JsonResponse({'success': False, 'message': 'Batch order not found'}, status=404)
    
    first_order = orders.first()
    batch_total = sum(order.total_amount for order in orders)
    
    customer_profile = None
    if first_order.customer and hasattr(first_order.customer, 'customer_profile'):
        customer_profile = first_order.customer.customer_profile
    
    context = {
        'orders': orders,
        'first_order': first_order,
        'batch_total': batch_total,
        'batch_item_count': orders.count(),
        'customer_profile': customer_profile,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'dealer/batch_order_detail_modal.html', context)
    
    return render(request, 'dealer/batch_order_detail.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_protect
def update_batch_order_status(request, batch_id):
    """
    Update the status of all orders in a batch
    """
    import uuid
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        batch_uuid = uuid.UUID(str(batch_id))
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid batch ID'}, status=400)
    
    orders = Order.objects.filter(batch_id=batch_uuid)
    
    if not orders.exists():
        return JsonResponse({'success': False, 'message': 'Batch order not found'}, status=404)
    
    new_status = request.POST.get('status')
    if new_status not in dict(Order.STATUS_CHOICES):
        return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
    
    try:
        success_count = 0
        cancellation_reason = request.POST.get('cancellation_reason', '')
        
        for order in orders:
            if new_status == 'out_for_delivery' and order.status == 'pending':
                order.status = 'out_for_delivery'
                order.save()
                success_count += 1
            elif new_status == 'delivered' and order.status == 'out_for_delivery':
                order.status = 'delivered'
                if not order.delivery_date:
                    order.delivery_date = timezone.now()
                if hasattr(request.user, 'cashier_profile') and not order.processed_by:
                    order.processed_by = request.user.cashier_profile
                order.save()
                
                from .models import CashierTransaction
                if order.processed_by:
                    CashierTransaction.objects.create(
                        cashier=order.processed_by,
                        order=order,
                        transaction_type='order',
                        amount=order.total_amount,
                        payment_method='cash',
                        customer=order.customer
                    )
                success_count += 1
            elif new_status == 'cancelled' and order.status in ['pending', 'out_for_delivery']:
                order.status = 'cancelled'
                order.cancellation_reason = cancellation_reason
                order.cancelled_at = timezone.now()
                order.cancelled_by = request.user
                order.save()
                
                if order.customer:
                    Notification.objects.create(
                        customer=order.customer,
                        notification_type='order_cancelled',
                        order=order,
                        title=f'Order #{order.id} Cancelled',
                        message=f'Your order for {order.product.name} (Qty: {order.quantity}) has been cancelled.',
                        reason=cancellation_reason
                    )
                success_count += 1
        
        if success_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'Successfully updated {success_count} item(s) in batch order.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No items could be updated. Check current status.'
            })
    except Exception as e:
        logger.error(f"Error updating batch order status: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error updating batch order: {str(e)}'
        }, status=500)


@login_required
def refresh_dashboard_orders(request):
    """
    HTMX endpoint for refreshing dashboard order statistics
    Requirements: 3.2 - Real-time updates for dashboard
    Batch orders are grouped together
    """
    if request.headers.get('HX-Request'):
        all_orders = Order.objects.filter(customer=request.user).select_related('product').order_by('-order_date')
        
        seen_batches = set()
        unique_orders = []
        for order in all_orders:
            if order.batch_id not in seen_batches:
                seen_batches.add(order.batch_id)
                unique_orders.append(order)
            if len(unique_orders) >= 5:
                break
        
        context = {
            'recent_orders': unique_orders,
            'total_orders': len(seen_batches),
            'pending_orders': Order.objects.filter(customer=request.user, status='pending').values('batch_id').distinct().count(),
            'delivered_orders': Order.objects.filter(customer=request.user, status='delivered').values('batch_id').distinct().count(),
        }
        return render(request, 'customer/dashboard_orders_partial.html', context)
    
    return redirect('core:customer_dashboard')


# Inventory Management Views
@user_passes_test(is_dealer, login_url='core:login')
def inventory_management(request):
    """
    Inventory dashboard showing current stock levels and low stock warnings
    Requirements: 6.1, 6.3 - Inventory dashboard with stock levels and warnings
    """
    # Get all products with stock information
    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    
    # Get low stock products
    low_stock_products = [product for product in products if product.is_low_stock]
    
    # Get recent delivery logs for stock movement history
    recent_deliveries = DeliveryLog.objects.select_related('product', 'logged_by').order_by('-delivery_date')[:10]
    
    # Calculate inventory statistics
    total_products = products.count()
    low_stock_count = len(low_stock_products)
    total_stock_value = sum(product.current_stock * product.price for product in products)
    
    # Get stock movement data for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_stock_movements = DeliveryLog.objects.filter(
        delivery_date__gte=thirty_days_ago
    ).select_related('product', 'logged_by').order_by('-delivery_date')
    
    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'recent_deliveries': recent_deliveries,
        'recent_stock_movements': recent_stock_movements,
        'inventory_stats': {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'total_stock_value': total_stock_value,
        }
    }
    
    return render(request, 'dealer/inventory.html', context)


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["POST"])
@csrf_protect
def log_delivery(request):
    """
    Log new distributor delivery with automatic inventory adjustment
    Requirements: 6.2, 6.4 - Delivery logging with automatic stock updates
    """
    if request.method == 'POST':
        form = DeliveryLogForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    delivery_log = form.save(commit=False)
                    delivery_log.logged_by = request.user
                    
                    # Calculate total cost if not provided
                    if not delivery_log.total_cost:
                        delivery_log.total_cost = delivery_log.cost_per_unit * delivery_log.quantity_received
                    
                    # Save delivery log (this will automatically update product stock via model save method)
                    delivery_log.save()
                    
                    success_msg = f'Successfully logged delivery of {delivery_log.quantity_received}x {delivery_log.product.name} from {delivery_log.supplier_name}.'
                    
                    # Log successful delivery for audit trail
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Delivery logged: {delivery_log.quantity_received}x {delivery_log.product.name} from {delivery_log.supplier_name} by user {request.user.username}")
                    
                    if request.headers.get('HX-Request'):
                        # Return success message and close modal
                        context = {
                            'success': True,
                            'message': success_msg,
                            'delivery_log': delivery_log
                        }
                        return render(request, 'dealer/delivery_success_partial.html', context)
                    
                    messages.success(request, success_msg)
                    return redirect('core:inventory_management')
                    
            except Exception as e:
                error_msg = f'Error logging delivery: {str(e)}'
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error logging delivery: {str(e)}", exc_info=True)
                
                if request.headers.get('HX-Request'):
                    return JsonResponse({
                        'success': False,
                        'message': error_msg
                    }, status=400)
                messages.error(request, error_msg)
        else:
            # Form validation errors
            if request.headers.get('HX-Request'):
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f'{field}: {error}')
                return JsonResponse({
                    'success': False,
                    'message': 'Form validation failed.',
                    'errors': errors
                }, status=400)
            
            # Add form errors to messages for non-HTMX requests
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('core:inventory_management')


@user_passes_test(is_dealer, login_url='core:login')
def refresh_inventory_dashboard(request):
    """
    HTMX/Unpoly endpoint for refreshing inventory dashboard
    Requirements: 6.5 - Real-time inventory displays with Unpoly updates
    """
    if request.headers.get('HX-Request') or request.headers.get('X-Up-Target'):
        # Get updated inventory data
        products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
        low_stock_products = [product for product in products if product.is_low_stock]
        
        # Calculate updated statistics
        total_products = products.count()
        low_stock_count = len(low_stock_products)
        total_stock_value = sum(product.current_stock * product.price for product in products)
        
        context = {
            'products': products,
            'low_stock_products': low_stock_products,
            'inventory_stats': {
                'total_products': total_products,
                'low_stock_count': low_stock_count,
                'total_stock_value': total_stock_value,
            }
        }
        
        return render(request, 'dealer/inventory_dashboard_partial.html', context)
    
    return redirect('core:inventory_management')


@user_passes_test(is_dealer, login_url='core:login')
def refresh_stock_movements(request):
    """
    HTMX endpoint for refreshing stock movement history
    Requirements: 6.4 - Stock movement history and tracking
    """
    if request.headers.get('HX-Request'):
        # Get stock movement data for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_stock_movements = DeliveryLog.objects.filter(
            delivery_date__gte=thirty_days_ago
        ).select_related('product', 'logged_by').order_by('-delivery_date')
        
        context = {
            'recent_stock_movements': recent_stock_movements,
        }
        
        return render(request, 'dealer/stock_movements_partial.html', context)
    
    return redirect('core:inventory_management')


@user_passes_test(is_dealer, login_url='core:login')
def get_delivery_form(request):
    """
    HTMX endpoint to get delivery logging form modal
    Requirements: 6.2 - Delivery logging modal with Alpine.js
    """
    if request.headers.get('HX-Request'):
        form = DeliveryLogForm()
        products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')

        context = {
            'form': form,
            'products': products,
        }

        return render(request, 'dealer/delivery_form_modal.html', context)

    return redirect('core:inventory_management')


@login_required
@user_passes_test(is_dealer, login_url='core:login')
def get_delivery_detail(request, delivery_id):
    """
    HTMX endpoint to get delivery detail modal with buying/selling breakdown
    """
    delivery = get_object_or_404(DeliveryLog.objects.select_related('product', 'logged_by'), id=delivery_id)
    
    potential_revenue = delivery.quantity_received * delivery.product.price
    profit_potential = potential_revenue - delivery.total_cost
    profit_margin = (profit_potential / potential_revenue * 100) if potential_revenue > 0 else 0
    
    context = {
        'delivery': delivery,
        'potential_revenue': potential_revenue,
        'profit_potential': profit_potential,
        'profit_margin': profit_margin,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'dealer/delivery_detail_modal.html', context)
    
    return render(request, 'dealer/delivery_detail_modal.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def delivery_log(request):
    """
    Dedicated delivery log page with filtering and search
    Requirements: 6.2 - Comprehensive delivery log management
    """
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')
    supplier_filter = request.GET.get('supplier', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-delivery_date')

    # Set default date range (last 30 days)
    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        date_from = date_from or start_date.strftime('%Y-%m-%d')
        date_to = date_to or end_date.strftime('%Y-%m-%d')

    # Build queryset
    deliveries = DeliveryLog.objects.select_related('product', 'logged_by')

    # Apply date filters
    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        deliveries = deliveries.filter(
            delivery_date__date__gte=from_date,
            delivery_date__date__lte=to_date
        )
    except ValueError:
        pass

    # Apply other filters
    if product_filter:
        deliveries = deliveries.filter(product_id=product_filter)

    if supplier_filter:
        deliveries = deliveries.filter(supplier_name__icontains=supplier_filter)

    if search:
        deliveries = deliveries.filter(
            Q(supplier_name__icontains=search) |
            Q(product__name__icontains=search) |
            Q(notes__icontains=search)
        )

    # Apply sorting
    deliveries = deliveries.order_by(sort)

    # Pagination
    paginator = Paginator(deliveries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate summary statistics
    total_deliveries = deliveries.count()
    total_cost = deliveries.aggregate(total=Sum('total_cost'))['total'] or 0
    total_quantity = deliveries.aggregate(total=Sum('quantity_received'))['total'] or 0
    unique_suppliers = deliveries.values('supplier_name').distinct().count()
    
    total_potential_revenue = 0
    for delivery in deliveries:
        total_potential_revenue += delivery.quantity_received * delivery.product.price
    
    total_profit_potential = total_potential_revenue - total_cost

    # Get filter options
    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    suppliers = DeliveryLog.objects.values_list('supplier_name', flat=True).distinct().order_by('supplier_name')

    context = {
        'page_obj': page_obj,
        'deliveries': page_obj.object_list,
        'products': products,
        'suppliers': suppliers,
        'current_filters': {
            'date_from': date_from,
            'date_to': date_to,
            'product': product_filter,
            'supplier': supplier_filter,
            'search': search,
            'sort': sort,
        },
        'summary_stats': {
            'total_deliveries': total_deliveries,
            'total_cost': total_cost,
            'total_quantity': total_quantity,
            'unique_suppliers': unique_suppliers,
            'total_potential_revenue': total_potential_revenue,
            'total_profit_potential': total_profit_potential,
        },
        'sort_choices': [
            ('-delivery_date', 'Newest First'),
            ('delivery_date', 'Oldest First'),
            ('-total_cost', 'Highest Cost'),
            ('total_cost', 'Lowest Cost'),
            ('supplier_name', 'Supplier A-Z'),
            ('-supplier_name', 'Supplier Z-A'),
            ('product__name', 'Product A-Z'),
            ('-product__name', 'Product Z-A'),
        ]
    }

    return render(request, 'dealer/delivery_log.html', context)

# Reporting System Views
@user_passes_test(is_dealer, login_url='core:login')
def reports_dashboard(request):
    """
    Main reports dashboard with report options and quick stats
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5 - Report generation system
    """
    # Calculate quick statistics for the dashboard
    today = timezone.now().date()
    current_month = today.replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    # Monthly statistics
    current_month_orders = Order.objects.filter(
        order_date__date__gte=current_month,
        status='delivered'
    ).count()
    
    current_month_revenue = Order.objects.filter(
        order_date__date__gte=current_month,
        status='delivered'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    last_month_orders = Order.objects.filter(
        order_date__date__gte=last_month,
        order_date__date__lt=current_month,
        status='delivered'
    ).count()
    
    last_month_revenue = Order.objects.filter(
        order_date__date__gte=last_month,
        order_date__date__lt=current_month,
        status='delivered'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Inventory statistics
    total_stock_value = LPGProduct.objects.filter(is_active=True).aggregate(
        total=Sum(F('current_stock') * F('price'))
    )['total'] or 0
    
    low_stock_count = LPGProduct.objects.filter(
        is_active=True,
        current_stock__lte=F('minimum_stock')
    ).count()
    
    # Recent deliveries value
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_deliveries_value = DeliveryLog.objects.filter(
        delivery_date__gte=thirty_days_ago
    ).aggregate(total=Sum('total_cost'))['total'] or 0
    
    context = {
        'quick_stats': {
            'current_month_orders': current_month_orders,
            'current_month_revenue': current_month_revenue,
            'last_month_orders': last_month_orders,
            'last_month_revenue': last_month_revenue,
            'total_stock_value': total_stock_value,
            'low_stock_count': low_stock_count,
            'recent_deliveries_value': recent_deliveries_value,
        },
        'products': LPGProduct.objects.filter(is_active=True).order_by('name', 'size'),
        'customers': User.objects.filter(orders__isnull=False).distinct().order_by('username'),
    }
    
    return render(request, 'dealer/reports_dashboard.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def sales_report(request):
    """
    Generate sales report with date range filtering
    Requirements: 7.1, 7.3, 7.4 - Sales report generation with filtering
    """
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')
    customer_filter = request.GET.get('customer', '')
    
    # Default to last 30 days if no dates provided
    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        if not date_from:
            date_from = start_date.strftime('%Y-%m-%d')
        if not date_to:
            date_to = end_date.strftime('%Y-%m-%d')
    
    # Build query for delivered orders
    orders = Order.objects.filter(status='delivered').select_related('customer', 'product')
    
    # Apply date filters
    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        orders = orders.filter(
            delivery_date__date__gte=from_date,
            delivery_date__date__lte=to_date
        )
    except ValueError:
        # Invalid date format, use default
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        orders = orders.filter(
            delivery_date__date__gte=start_date,
            delivery_date__date__lte=end_date
        )
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
    
    # Apply product filter
    if product_filter:
        try:
            product_id = int(product_filter)
            orders = orders.filter(product_id=product_id)
        except (ValueError, TypeError):
            pass
    
    # Apply customer filter
    if customer_filter:
        try:
            customer_id = int(customer_filter)
            orders = orders.filter(customer_id=customer_id)
        except (ValueError, TypeError):
            pass
    
    # Calculate summary statistics
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_quantity = orders.aggregate(total=Sum('quantity'))['total'] or 0
    average_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    # Product breakdown
    product_stats = orders.values(
        'product__name', 'product__size'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_amount'),
        order_count=Count('id')
    ).order_by('-total_revenue')
    
    # Customer breakdown
    customer_stats = orders.values(
        'customer__username', 'customer__first_name', 'customer__last_name'
    ).annotate(
        total_orders=Count('id'),
        total_spent=Sum('total_amount'),
        total_quantity=Sum('quantity')
    ).order_by('-total_spent')
    
    # Daily sales trend
    daily_sales = orders.extra(
        select={'day': 'DATE(delivery_date)'}
    ).values('day').annotate(
        daily_orders=Count('id'),
        daily_revenue=Sum('total_amount')
    ).order_by('day')
    
    context = {
        'report_type': 'sales',
        'orders': orders.order_by('-delivery_date'),
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'product': product_filter,
            'customer': customer_filter,
        },
        'summary': {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_quantity': total_quantity,
            'average_order_value': average_order_value,
        },
        'product_stats': product_stats,
        'customer_stats': customer_stats,
        'daily_sales': daily_sales,
        'products': LPGProduct.objects.filter(is_active=True).order_by('name', 'size'),
        'customers': User.objects.filter(orders__isnull=False).distinct().order_by('username'),
    }
    
    return render(request, 'dealer/sales_report.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def export_sales_report_pdf(request):
    """
    Export sales report as PDF using ReportLab
    """
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')
    customer_filter = request.GET.get('customer', '')

    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        if not date_from:
            date_from = start_date.strftime('%Y-%m-%d')
        if not date_to:
            date_to = end_date.strftime('%Y-%m-%d')

    orders = Order.objects.filter(status='delivered').select_related('customer', 'product')

    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        orders = orders.filter(delivery_date__date__gte=from_date, delivery_date__date__lte=to_date)
    except ValueError:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        orders = orders.filter(delivery_date__date__gte=start_date, delivery_date__date__lte=end_date)
        from_date = start_date
        to_date = end_date

    if product_filter:
        try:
            pid = int(product_filter)
            orders = orders.filter(product_id=pid)
        except (ValueError, TypeError):
            pass

    if customer_filter:
        try:
            cid = int(customer_filter)
            orders = orders.filter(customer_id=cid)
        except (ValueError, TypeError):
            pass

    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_quantity = orders.aggregate(total=Sum('quantity'))['total'] or 0

    product_stats = orders.values('product__name', 'product__size').annotate(
        total_quantity=Sum('quantity'), total_revenue=Sum('total_amount'), order_count=Count('id')
    ).order_by('-total_revenue')

    customer_stats = orders.values('customer__username').annotate(
        total_orders=Count('id'), total_spent=Sum('total_amount'), total_quantity=Sum('quantity')
    ).order_by('-total_spent')

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Sales Report"
    )

    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#FF6B35'), alignment=TA_CENTER)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#FF6B35'))

    elements.append(Paragraph('Prycegas Station', title_style))
    elements.append(Paragraph('Sales Report', styles['Heading2']))
    elements.append(Paragraph(f"Period: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph('Summary', heading_style))
    summary_text = f"Total Orders: {total_orders} | Units Sold: {total_quantity} | Total Revenue: ₱{total_revenue:,.2f}"
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.15*inch))

    if product_stats:
        elements.append(Paragraph('Sales by Product', heading_style))
        pdata = [[Paragraph('Product', styles['Normal']), Paragraph('Orders', styles['Normal']), Paragraph('Quantity', styles['Normal']), Paragraph('Revenue', styles['Normal'])]]
        for ps in product_stats:
            prod_name = f"{ps.get('product__name')} {ps.get('product__size') or ''}".strip()
            pdata.append([Paragraph(prod_name, styles['Normal']), Paragraph(str(ps.get('order_count')), styles['Normal']), Paragraph(str(ps.get('total_quantity')), styles['Normal']), Paragraph(f"₱{ps.get('total_revenue') or 0:,.2f}", styles['Normal'])])

        ptable = Table(pdata, colWidths=[2.5*inch, 0.8*inch, 0.9*inch, 1.2*inch])
        ptable.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ]))
        elements.append(ptable)
        elements.append(Spacer(1, 0.15*inch))

    if customer_stats:
        elements.append(Paragraph('Top Customers', heading_style))
        cdata = [[Paragraph('Customer', styles['Normal']), Paragraph('Orders', styles['Normal']), Paragraph('Qty', styles['Normal']), Paragraph('Total Spent', styles['Normal'])]]
        for cs in customer_stats[:20]:
            cdata.append([Paragraph(cs.get('customer__username'), styles['Normal']), Paragraph(str(cs.get('total_orders')), styles['Normal']), Paragraph(str(cs.get('total_quantity')), styles['Normal']), Paragraph(f"₱{cs.get('total_spent') or 0:,.2f}", styles['Normal'])])

        ctable = Table(cdata, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 1.2*inch])
        ctable.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ]))
        elements.append(ctable)
        elements.append(Spacer(1, 0.15*inch))

    elements.append(Paragraph('Order Details (latest)', heading_style))
    odata = [[Paragraph('Order #', styles['Normal']), Paragraph('Date', styles['Normal']), Paragraph('Customer', styles['Normal']), Paragraph('Product', styles['Normal']), Paragraph('Qty', styles['Normal']), Paragraph('Amount', styles['Normal'])]]
    for order in orders.order_by('-delivery_date')[:200]:
        odata.append([
            Paragraph(f"#{order.id}", styles['Normal']),
            Paragraph(order.delivery_date.strftime('%b %d, %Y'), styles['Normal']),
            Paragraph(order.customer.username, styles['Normal']),
            Paragraph(f"{order.product.name} {order.product.size}", styles['Normal']),
            Paragraph(str(order.quantity), styles['Normal']),
            Paragraph(f"₱{order.total_amount:,.2f}", styles['Normal']),
        ])
    
    # Add Grand Total row
    odata.append([
        Paragraph('', styles['Normal']),
        Paragraph('', styles['Normal']),
        Paragraph('', styles['Normal']),
        Paragraph('GRAND TOTAL', ParagraphStyle('Bold', parent=styles['Normal'], fontSize=11, textColor=colors.black)),
        Paragraph(f"{total_quantity}", ParagraphStyle('Bold', parent=styles['Normal'], fontSize=11, textColor=colors.black)),
        Paragraph(f"₱{total_revenue:,.2f}", ParagraphStyle('Bold', parent=styles['Normal'], fontSize=11, textColor=colors.black)),
    ])

    otable = Table(odata, colWidths=[0.8*inch, 0.9*inch, 1.6*inch, 1.6*inch, 0.6*inch, 1*inch])
    otable.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F5F5F5')]),
        ('BACKGROUND', (-2,-1), (-1,-1), colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (-2,-1), (-1,-1), colors.whitesmoke),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (4,1), (5,-1), 'RIGHT'),
    ]))
    elements.append(otable)

    elements.append(Spacer(1, 0.2*inch))
    footer = Paragraph('This is an official report from Prycegas Station.', ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER))
    elements.append(footer)

    doc.build(elements)
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


@user_passes_test(is_dealer, login_url='core:login')
def stock_report(request):
    """
    Generate stock report showing inventory levels and movement
    Requirements: 7.2, 7.3, 7.4 - Stock report with inventory levels and movement
    """
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')
    
    # Default to last 30 days if no dates provided
    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        if not date_from:
            date_from = start_date.strftime('%Y-%m-%d')
        if not date_to:
            date_to = end_date.strftime('%Y-%m-%d')
    
    # Get all active products
    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    
    # Apply product filter
    if product_filter:
        try:
            product_id = int(product_filter)
            products = products.filter(id=product_id)
        except (ValueError, TypeError):
            pass
    
    # Get delivery logs for the period
    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        deliveries = DeliveryLog.objects.filter(
            delivery_date__date__gte=from_date,
            delivery_date__date__lte=to_date
        ).select_related('product', 'logged_by')
    except ValueError:
        # Invalid date format, use default
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        deliveries = DeliveryLog.objects.filter(
            delivery_date__date__gte=start_date,
            delivery_date__date__lte=end_date
        ).select_related('product', 'logged_by')
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
    
    # Apply product filter to deliveries
    if product_filter:
        try:
            product_id = int(product_filter)
            deliveries = deliveries.filter(product_id=product_id)
        except (ValueError, TypeError):
            pass
    
    # Get sales for the period (delivered orders)
    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        sales = Order.objects.filter(
            status='delivered',
            delivery_date__date__gte=from_date,
            delivery_date__date__lte=to_date
        ).select_related('product', 'customer')
    except ValueError:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        sales = Order.objects.filter(
            status='delivered',
            delivery_date__date__gte=start_date,
            delivery_date__date__lte=end_date
        ).select_related('product', 'customer')
    
    # Apply product filter to sales
    if product_filter:
        try:
            product_id = int(product_filter)
            sales = sales.filter(product_id=product_id)
        except (ValueError, TypeError):
            pass
    
    # Calculate inventory statistics
    total_stock_value = products.aggregate(
        total=Sum(F('current_stock') * F('price'))
    )['total'] or 0
    
    total_current_stock = products.aggregate(
        total=Sum('current_stock')
    )['total'] or 0
    
    low_stock_products = products.filter(
        current_stock__lte=F('minimum_stock')
    ).count()
    
    out_of_stock_products = products.filter(current_stock=0).count()
    
    # Delivery statistics
    total_deliveries = deliveries.count()
    total_delivered_quantity = deliveries.aggregate(
        total=Sum('quantity_received')
    )['total'] or 0
    total_delivery_cost = deliveries.aggregate(
        total=Sum('total_cost')
    )['total'] or 0
    
    # Sales statistics
    total_sales = sales.count()
    total_sold_quantity = sales.aggregate(
        total=Sum('quantity')
    )['total'] or 0
    total_sales_revenue = sales.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Product-wise inventory details
    product_details = []
    for product in products:
        # Get deliveries for this product in the period
        product_deliveries = deliveries.filter(product=product)
        delivered_qty = product_deliveries.aggregate(
            total=Sum('quantity_received')
        )['total'] or 0
        delivery_cost = product_deliveries.aggregate(
            total=Sum('total_cost')
        )['total'] or 0
        
        # Get sales for this product in the period
        product_sales = sales.filter(product=product)
        sold_qty = product_sales.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        sales_revenue = product_sales.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate stock movement
        net_movement = delivered_qty - sold_qty
        stock_value = product.current_stock * product.price
        
        product_details.append({
            'product': product,
            'current_stock': product.current_stock,
            'minimum_stock': product.minimum_stock,
            'stock_value': stock_value,
            'delivered_qty': delivered_qty,
            'sold_qty': sold_qty,
            'net_movement': net_movement,
            'delivery_cost': delivery_cost,
            'sales_revenue': sales_revenue,
            'is_low_stock': product.is_low_stock,
            'is_out_of_stock': product.current_stock == 0,
        })
    
    # Recent stock movements
    recent_movements = deliveries.order_by('-delivery_date')[:20]
    
    context = {
        'report_type': 'stock',
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'product': product_filter,
        },
        'inventory_summary': {
            'total_stock_value': total_stock_value,
            'total_current_stock': total_current_stock,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
        },
        'period_summary': {
            'total_deliveries': total_deliveries,
            'total_delivered_quantity': total_delivered_quantity,
            'total_delivery_cost': total_delivery_cost,
            'total_sales': total_sales,
            'total_sold_quantity': total_sold_quantity,
            'total_sales_revenue': total_sales_revenue,
        },
        'product_details': product_details,
        'recent_movements': recent_movements,
        'products': LPGProduct.objects.filter(is_active=True).order_by('name', 'size'),
    }
    
    return render(request, 'dealer/stock_report.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def export_stock_report_pdf(request):
    """
    Export stock report as PDF using ReportLab
    """
    # Get filter parameters (reuse same defaults as stock_report)
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')

    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        if not date_from:
            date_from = start_date.strftime('%Y-%m-%d')
        if not date_to:
            date_to = end_date.strftime('%Y-%m-%d')

    # Base product queryset
    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    if product_filter:
        try:
            product_id = int(product_filter)
            products = products.filter(id=product_id)
        except (ValueError, TypeError):
            pass

    # Parse dates and fetch deliveries/sales
    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        to_date = timezone.now().date()
        from_date = to_date - timedelta(days=30)

    deliveries = DeliveryLog.objects.filter(
        delivery_date__date__gte=from_date,
        delivery_date__date__lte=to_date
    ).select_related('product', 'logged_by')
    sales = Order.objects.filter(
        status='delivered',
        delivery_date__date__gte=from_date,
        delivery_date__date__lte=to_date
    ).select_related('product', 'customer')

    if product_filter:
        try:
            pid = int(product_filter)
            deliveries = deliveries.filter(product_id=pid)
            sales = sales.filter(product_id=pid)
        except (ValueError, TypeError):
            pass

    # Build product details list
    product_details = []
    for product in products:
        product_deliveries = deliveries.filter(product=product)
        delivered_qty = product_deliveries.aggregate(total=Sum('quantity_received'))['total'] or 0
        delivery_cost = product_deliveries.aggregate(total=Sum('total_cost'))['total'] or 0

        product_sales = sales.filter(product=product)
        sold_qty = product_sales.aggregate(total=Sum('quantity'))['total'] or 0
        sales_revenue = product_sales.aggregate(total=Sum('total_amount'))['total'] or 0

        net_movement = delivered_qty - sold_qty
        stock_value = product.current_stock * product.price

        product_details.append({
            'product': product,
            'current_stock': product.current_stock,
            'minimum_stock': product.minimum_stock,
            'stock_value': stock_value,
            'delivered_qty': delivered_qty,
            'sold_qty': sold_qty,
            'net_movement': net_movement,
            'delivery_cost': delivery_cost,
            'sales_revenue': sales_revenue,
            'is_low_stock': product.is_low_stock,
            'is_out_of_stock': product.current_stock == 0,
        })

    # Inventory summary
    total_stock_value = products.aggregate(total=Sum(F('current_stock') * F('price')))['total'] or 0
    total_current_stock = products.aggregate(total=Sum('current_stock'))['total'] or 0

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Stock Report"
    )

    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=20,
        textColor=colors.HexColor('#FF6B35'), alignment=TA_CENTER
    )
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#FF6B35'))

    elements.append(Paragraph('Prycegas Station', title_style))
    elements.append(Paragraph('Stock & Inventory Report', styles['Heading2']))
    elements.append(Paragraph(f"Movement Period: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Inventory summary
    elements.append(Paragraph('Inventory Summary', heading_style))
    summary_text = f"Total Stock Value: ₦{total_stock_value:,.2f} | Total Units: {total_current_stock}"
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.15*inch))

    # Table header
    table_data = [[
        Paragraph('Product', styles['Normal']),
        Paragraph('Current', styles['Normal']),
        Paragraph('Min', styles['Normal']),
        Paragraph('Stock Value', styles['Normal']),
        Paragraph('Delivered', styles['Normal']),
        Paragraph('Sold', styles['Normal']),
        Paragraph('Net', styles['Normal']),
        Paragraph('Delivery Cost', styles['Normal']),
        Paragraph('Sales Revenue', styles['Normal']),
    ]]

    for pd in product_details:
        prod = pd['product']
        table_data.append([
            Paragraph(f"{prod.name} {prod.size}", styles['Normal']),
            Paragraph(str(pd['current_stock']), styles['Normal']),
            Paragraph(str(pd['minimum_stock']), styles['Normal']),
            Paragraph(f"₦{pd['stock_value']:,.2f}", styles['Normal']),
            Paragraph(str(pd['delivered_qty']), styles['Normal']),
            Paragraph(str(pd['sold_qty']), styles['Normal']),
            Paragraph(str(pd['net_movement']), styles['Normal']),
            Paragraph(f"₦{pd['delivery_cost']:,.2f}", styles['Normal']),
            Paragraph(f"₦{pd['sales_revenue']:,.2f}", styles['Normal']),
        ])

    table = Table(table_data, colWidths=[1.6*inch, 0.6*inch, 0.6*inch, 1*inch, 0.7*inch, 0.6*inch, 0.6*inch, 0.9*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))

    footer = Paragraph('This is an official report from Prycegas Station.', ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER))
    elements.append(footer)

    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="stock_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


@user_passes_test(is_dealer, login_url='core:login')
def print_report(request):
    """
    Generate printable version of reports
    Requirements: 7.5 - Mobile-responsive and printable reports
    """
    report_type = request.GET.get('type', 'sales')
    
    if report_type == 'sales':
        # Redirect to sales report with print parameter
        query_params = request.GET.copy()
        query_params['print'] = '1'
        return redirect(f"{request.build_absolute_uri('/dealer/reports/sales/')}?{query_params.urlencode()}")
    elif report_type == 'stock':
        # Redirect to stock report with print parameter
        query_params = request.GET.copy()
        query_params['print'] = '1'
        return redirect(f"{request.build_absolute_uri('/dealer/reports/stock/')}?{query_params.urlencode()}")
    
    return redirect('core:reports_dashboard')


# Enhanced Inventory Management Views

@user_passes_test(is_dealer, login_url='core:login')
def product_management(request):
    """
    Product management dashboard for CRUD operations
    """
    products = LPGProduct.objects.all().order_by('name', 'size')
    categories = ProductCategory.objects.filter(is_active=True)

    # Filter by status (active/inactive/all)
    status_filter = request.GET.get('status', 'active')  # Default to active only
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)
    # 'all' shows both active and inactive

    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(size__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'status_filter': status_filter
    }

    return render(request, 'dealer/product_management.html', context)


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["GET", "POST"])
def add_product(request):
    """
    Add new product
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name} - {product.size}" added successfully!')
            return redirect('core:product_management')
    else:
        form = ProductForm()

    return render(request, 'dealer/add_product.html', {'form': form})


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["GET", "POST"])
def edit_product(request, product_id):
    """
    Edit existing product
    """
    product = get_object_or_404(LPGProduct, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name} - {product.size}" updated successfully!')
            return redirect('core:product_management')
    else:
        form = ProductForm(instance=product)

    return render(request, 'dealer/edit_product.html', {'form': form, 'product': product})


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["POST"])
@csrf_protect
def delete_product(request, product_id):
    """
    Delete product (soft delete by setting is_active=False)
    """
    try:
        product = get_object_or_404(LPGProduct, id=product_id)

        # Check if product has pending orders
        pending_orders = Order.objects.filter(product=product, status__in=['pending', 'out_for_delivery']).count()

        if pending_orders > 0:
            messages.error(request, f'Cannot deactivate "{product.name} - {product.size}". It has {pending_orders} pending order(s).')
            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot deactivate "{product.name} - {product.size}". It has {pending_orders} pending order(s).'
                }, status=400)
        else:
            product.is_active = False
            product.save()
            success_msg = f'Product "{product.name} - {product.size}" deactivated successfully!'
            messages.success(request, success_msg)

            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'refresh_table': True
                })

    except Exception as e:
        error_msg = f'Error deactivating product: {str(e)}'
        messages.error(request, error_msg)
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=500)

    return redirect('core:product_management')


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["POST"])
@csrf_protect
def reactivate_product(request, product_id):
    """
    Reactivate product (set is_active=True)
    """
# Staff Management Views
@user_passes_test(is_dealer, login_url='core:login')
def staff_list(request):
    """
    Display a list of all staff members.
    """
    staff = Staff.objects.all()
    context = {
        'staff': staff,
    }
    return render(request, 'dealer/staff_list.html', context)

@user_passes_test(is_dealer, login_url='core:login')
def staff_detail(request, staff_id):
    """
    Display details of a single staff member.
    """
    staff = get_object_or_404(Staff, id=staff_id)
    payrolls = Payroll.objects.filter(staff=staff).order_by('-payment_date')
    context = {
        'staff': staff,
        'payrolls': payrolls,
    }
    return render(request, 'dealer/staff_detail.html', context)

@user_passes_test(is_dealer, login_url='core:login')
def staff_create(request):
    """
    Create a new staff member.
    """
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff member "{staff.user.username}" created successfully!')
            return redirect('core:staff_list')
    else:
        form = StaffCreationForm()
    return render(request, 'dealer/staff_form.html', {'form': form})

@user_passes_test(is_dealer, login_url='core:login')
def staff_update(request, staff_id):
    """
    Update an existing staff member.
    """
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff member "{staff.user.username}" updated successfully!')
            return redirect('core:staff_list')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'dealer/staff_form.html', {'form': form})

@user_passes_test(is_dealer, login_url='core:login')
def staff_delete(request, staff_id):
    """
    Delete a staff member.
    """
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, f'Staff member "{staff.user.username}" deleted successfully!')
        return redirect('core:staff_list')
    return render(request, 'dealer/staff_confirm_delete.html', {'staff': staff})

# Payroll Management Views
@user_passes_test(is_dealer, login_url='core:login')
def payroll_list(request):
    """
    Display a list of all payroll records.
    """
    payrolls = Payroll.objects.all().order_by('-payment_date')
    context = {
        'payrolls': payrolls,
    }
    return render(request, 'dealer/payroll_list.html', context)

@user_passes_test(is_dealer, login_url='core:login')
def payroll_create(request):
    """
    Create a new payroll record.
    """
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save()
            messages.success(request, f'Payroll for "{payroll.staff.user.username}" created successfully!')
            return redirect('core:payroll_list')
    else:
        form = PayrollForm()
    return render(request, 'dealer/payroll_form.html', {'form': form})

@user_passes_test(is_dealer, login_url='core:login')
def payroll_report(request):
    """
    Generate a PDF report of all payrolls.
    """
    payrolls = Payroll.objects.all().order_by('-payment_date')
    template_path = 'dealer/payroll_report.html'
    context = {'payrolls': payrolls}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payroll_report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# Pending Registrations Management Views

@user_passes_test(is_dealer, login_url='core:login')
def pending_registrations_list(request):
    """
    Display a list of all pending registrations awaiting admin approval.
    """
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'all':
        registrations = PendingRegistration.objects.all().order_by('-created_at')
    else:
        registrations = PendingRegistration.objects.filter(status=status_filter).order_by('-created_at')
    
    # Get counts for status tabs
    pending_count = PendingRegistration.objects.filter(status='pending').count()
    approved_count = PendingRegistration.objects.filter(status='approved').count()
    rejected_count = PendingRegistration.objects.filter(status='rejected').count()
    
    context = {
        'registrations': registrations,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'dealer/pending_registrations_list.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def pending_registration_detail(request, registration_id):
    """
    Show detailed view of a pending registration.
    """
    registration = get_object_or_404(PendingRegistration, id=registration_id)
    return render(request, 'dealer/registration_detail.html', {'registration': registration})


@user_passes_test(is_dealer, login_url='core:login')
def approve_registration(request, registration_id):
    """
    Approve a pending registration and create the user account.
    """
    registration = get_object_or_404(PendingRegistration, id=registration_id)
    
    try:
        # Create the user account with the stored password
        user = User.objects.create_user(
            username=registration.username,
            email=registration.email,
        )
        # Set the password using the hashed password from registration
        user.password = registration.password
        user.is_active = True  # Ensure user is active
        user.save()
        
        # Create customer profile
        CustomerProfile.objects.create(
            user=user,
            phone_number=registration.phone_number,
            address=registration.address,
            delivery_instructions=registration.delivery_instructions
        )
        
        # Update registration status
        registration.status = 'approved'
        registration.reviewed_by = request.user
        registration.reviewed_at = timezone.now()
        registration.save()
        
        messages.success(request, f'Registration for {registration.username} approved successfully! User account created.')
        return redirect('core:pending_registrations')
    except Exception as e:
        messages.error(request, f'Error approving registration: {str(e)}')
        return redirect('core:registration_detail', registration_id=registration_id)


@user_passes_test(is_dealer, login_url='core:login')
def reject_registration(request, registration_id):
    """
    Reject a pending registration.
    """
    registration = get_object_or_404(PendingRegistration, id=registration_id)
    
    rejection_reason = request.POST.get('rejection_reason', 'No reason provided')
    registration.status = 'rejected'
    registration.rejection_reason = rejection_reason
    registration.reviewed_by = request.user
    registration.reviewed_at = timezone.now()
    registration.save()
    
    messages.success(request, f'Registration for {registration.username} rejected.')
    return redirect('core:pending_registrations')


@user_passes_test(is_dealer, login_url='core:login')
def export_registrations_pdf(request):
    """
    Export customer registrations as PDF based on status filter.
    Supports: pending, approved, rejected, all
    """
    status_filter = request.GET.get('status', 'all')
    
    # Get registrations based on status filter
    if status_filter == 'all':
        registrations = PendingRegistration.objects.all().order_by('-created_at')
        filename = 'customers_list_all.pdf'
    elif status_filter in ['pending', 'approved', 'rejected']:
        registrations = PendingRegistration.objects.filter(status=status_filter).order_by('-created_at')
        filename = f'customers_list_{status_filter}.pdf'
    else:
        registrations = PendingRegistration.objects.all().order_by('-created_at')
        filename = 'customers_list.pdf'
    
    # Create PDF using reportlab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FF6633'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    # Add title
    title = Paragraph(f'<b>Registrations</b>', title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Prepare table data
    table_data = [[
        'Username',
        'Email',
        'Phone',
        'ID Type',
        'Status',
        'Submitted Date'
    ]]
    
    # Add registration data
    for reg in registrations:
        status_display = reg.get_status_display()
        table_data.append([
            reg.username,
            reg.email,
            reg.phone_number,
            reg.get_id_type_display(),
            status_display,
            reg.created_at.strftime('%m/%d/%Y') if reg.created_at else 'N/A'
        ])
    
    # Create table
    table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.1*inch])
    
    # Apply table styling
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6633')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add footer with timestamp
    footer_text = f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}"
    elements.append(Paragraph(f'<i>{footer_text}</i>', styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    return response
    
    try:
        product = get_object_or_404(LPGProduct, id=product_id)

        if product.is_active:
            messages.warning(request, f'Product "{product.name} - {product.size}" is already active.')
        else:
            product.is_active = True
            product.save()
            success_msg = f'Product "{product.name} - {product.size}" reactivated successfully!'
            messages.success(request, success_msg)

            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'refresh_table': True
                })

    except Exception as e:
        error_msg = f'Error reactivating product: {str(e)}'
        messages.error(request, error_msg)
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=500)

    return redirect('core:product_management')


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["GET", "POST"])
def inventory_adjustment(request):
    """
    Make inventory adjustments
    """
    print(f"\n[DEBUG] inventory_adjustment() - Method: {request.method}")
    
    if request.method == 'POST':
        print(f"[DEBUG] POST request received")
        print(f"[DEBUG] POST data: {request.POST}")
        
        form = InventoryAdjustmentForm(request.POST)
        print(f"[DEBUG] Form created: {form}")
        print(f"[DEBUG] Form is_valid(): {form.is_valid()}")
        
        if not form.is_valid():
            print(f"[DEBUG] Form errors: {form.errors}")
            return render(request, 'dealer/inventory_adjustment.html', {'form': form})
        
        print(f"[DEBUG] Form is valid! Processing...")
        
        # Save the form which will convert adjustment_type and quantity to quantity_change
        print(f"[DEBUG] Calling form.save(commit=False)...")
        adjustment = form.save(commit=False)
        print(f"[DEBUG] Form saved (commit=False)")
        print(f"[DEBUG] adjustment object: {adjustment}")
        print(f"[DEBUG] adjustment.quantity_change: {adjustment.quantity_change}")
        
        adjustment.adjusted_by = request.user
        print(f"[DEBUG] Set adjusted_by to: {adjustment.adjusted_by}")
        
        # Verify quantity_change is set
        print(f"[DEBUG] Verifying quantity_change is set...")
        if not hasattr(adjustment, 'quantity_change'):
            print(f"[ERROR] quantity_change attribute does not exist!")
            messages.error(request, 'Error: Quantity change attribute missing.')
            return render(request, 'dealer/inventory_adjustment.html', {'form': form})
        
        if adjustment.quantity_change is None:
            print(f"[ERROR] quantity_change is None!")
            messages.error(request, 'Error: Quantity change is None.')
            return render(request, 'dealer/inventory_adjustment.html', {'form': form})
        
        print(f"[DEBUG] quantity_change verified: {adjustment.quantity_change}")

        # Check if adjustment would result in negative stock
        print(f"[DEBUG] Checking for negative stock...")
        product = adjustment.product
        print(f"[DEBUG] Product: {product}")
        print(f"[DEBUG] Current stock: {product.current_stock}")
        print(f"[DEBUG] Adjustment amount: {adjustment.quantity_change}")
        
        try:
            new_stock = product.current_stock + adjustment.quantity_change
            print(f"[DEBUG] Calculated new_stock: {new_stock}")
        except Exception as e:
            print(f"[ERROR] Error calculating stock: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error calculating stock: {str(e)}')
            return render(request, 'dealer/inventory_adjustment.html', {'form': form})

        if new_stock < 0:
            print(f"[ERROR] New stock would be negative: {new_stock}")
            messages.error(request, f'Adjustment would result in negative stock. Current stock: {product.current_stock}, Adjustment: {adjustment.quantity_change}')
            return render(request, 'dealer/inventory_adjustment.html', {'form': form})

        print(f"[DEBUG] Stock validation passed. Ready to save adjustment.")
        
        # Save adjustment inside a transaction and ensure product is refreshed
        try:
            print(f"[DEBUG] Starting database transaction...")
            with transaction.atomic():
                print(f"[DEBUG] Inside transaction - calling adjustment.save()...")
                adjustment.save()
                print(f"[DEBUG] Adjustment saved! ID: {adjustment.id}")
                
                # Refresh product from DB to ensure updated stock value
                print(f"[DEBUG] Refreshing product from DB...")
                product.refresh_from_db()
                print(f"[DEBUG] Product refreshed. New stock in DB: {product.current_stock}")
            
            print(f"[DEBUG] Transaction completed successfully")
            success_msg = f'Inventory adjustment completed for {product.name} - {product.size}. Stock adjusted by {adjustment.quantity_change}'
            print(f"[DEBUG] Success message: {success_msg}")
            messages.success(request, success_msg)
            return redirect('core:inventory_management')
            
        except Exception as e:
            # Log and show a helpful error
            print(f"[ERROR] Exception in transaction/save: {str(e)}")
            import traceback
            error_msg = f'Error applying inventory adjustment: {str(e)}'
            print(f"[ERROR] {error_msg}")
            print(traceback.format_exc())
            messages.error(request, error_msg)
            return render(request, 'dealer/inventory_adjustment.html', {'form': form})
    else:
        print(f"[DEBUG] GET request - showing empty form")
        form = InventoryAdjustmentForm()

    return render(request, 'dealer/inventory_adjustment.html', {'form': form})


@user_passes_test(is_dealer, login_url='core:login')
def product_info(request, product_id):
    """
    Return basic product info (current stock, price, minimum) as JSON
    Used by inventory adjustment UI to show current stock before applying changes
    """
    try:
        product = LPGProduct.objects.get(id=product_id, is_active=True)
        data = {
            'id': product.id,
            'name': product.name,
            'size': product.size,
            'current_stock': product.current_stock,
            'minimum_stock': product.minimum_stock,
            'price': float(product.price) if product.price is not None else 0,
        }
        return JsonResponse({'success': True, 'product': data})
    except LPGProduct.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)


@user_passes_test(is_dealer, login_url='core:login')
def stock_movements(request):
    """
    View detailed stock movements
    """
    movements = StockMovement.objects.select_related('product', 'created_by').order_by('-created_at')

    # Filter by product if specified
    product_id = request.GET.get('product')
    if product_id:
        movements = movements.filter(product_id=product_id)

    # Filter by movement type if specified
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    # Date range filter
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        movements = movements.filter(created_at__date__gte=from_date)
    if to_date:
        movements = movements.filter(created_at__date__lte=to_date)

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(movements, 50)  # Show 50 movements per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'products': LPGProduct.objects.filter(is_active=True),
        'movement_types': StockMovement.MOVEMENT_TYPES,
        'filters': {
            'product': product_id,
            'type': movement_type,
            'from_date': from_date,
            'to_date': to_date,
        }
    }

    return render(request, 'dealer/stock_movements.html', context)


@login_required
@user_passes_test(is_dealer, login_url='core:login')
def stock_in_list(request):
    """
    Stock In List - Display all deliveries received (stock additions)
    Shows delivery logs with filtering capabilities
    """
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')
    supplier_filter = request.GET.get('supplier', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-delivery_date')

    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        date_from = date_from or start_date.strftime('%Y-%m-%d')
        date_to = date_to or end_date.strftime('%Y-%m-%d')

    stock_in_items = DeliveryLog.objects.select_related('product', 'logged_by')

    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        stock_in_items = stock_in_items.filter(
            delivery_date__date__gte=from_date,
            delivery_date__date__lte=to_date
        )
    except ValueError:
        pass

    if product_filter:
        stock_in_items = stock_in_items.filter(product_id=product_filter)

    if supplier_filter:
        stock_in_items = stock_in_items.filter(supplier_name__icontains=supplier_filter)

    if search:
        stock_in_items = stock_in_items.filter(
            Q(supplier_name__icontains=search) |
            Q(product__name__icontains=search) |
            Q(notes__icontains=search)
        )

    stock_in_items = stock_in_items.order_by(sort)

    paginator = Paginator(stock_in_items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_items = stock_in_items.count()
    total_cost = stock_in_items.aggregate(total=Sum('total_cost'))['total'] or 0
    total_quantity = stock_in_items.aggregate(total=Sum('quantity_received'))['total'] or 0
    unique_suppliers = stock_in_items.values('supplier_name').distinct().count()
    
    total_potential_revenue = 0
    for item in stock_in_items:
        total_potential_revenue += item.quantity_received * item.product.price
    
    total_profit_potential = total_potential_revenue - total_cost

    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    suppliers = DeliveryLog.objects.values_list('supplier_name', flat=True).distinct().order_by('supplier_name')

    context = {
        'page_obj': page_obj,
        'stock_in_items': page_obj.object_list,
        'products': products,
        'suppliers': suppliers,
        'current_filters': {
            'date_from': date_from,
            'date_to': date_to,
            'product': product_filter,
            'supplier': supplier_filter,
            'search': search,
            'sort': sort,
        },
        'summary_stats': {
            'total_items': total_items,
            'total_cost': total_cost,
            'total_quantity': total_quantity,
            'unique_suppliers': unique_suppliers,
            'total_potential_revenue': total_potential_revenue,
            'total_profit_potential': total_profit_potential,
        },
        'sort_choices': [
            ('-delivery_date', 'Newest First'),
            ('delivery_date', 'Oldest First'),
            ('-total_cost', 'Highest Cost'),
            ('total_cost', 'Lowest Cost'),
            ('supplier_name', 'Supplier A-Z'),
            ('-supplier_name', 'Supplier Z-A'),
            ('product__name', 'Product A-Z'),
            ('-product__name', 'Product Z-A'),
        ]
    }

    return render(request, 'dealer/stock_in_list.html', context)


@login_required
@user_passes_test(is_dealer, login_url='core:login')
def stock_out_list(request):
    """
    Stock Out List - Display all stock going out (sales, adjustments)
    Shows stock movements with negative quantities and delivered orders
    """
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    product_filter = request.GET.get('product', '')
    movement_type = request.GET.get('type', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')

    if not date_from or not date_to:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        date_from = date_from or start_date.strftime('%Y-%m-%d')
        date_to = date_to or end_date.strftime('%Y-%m-%d')

    stock_out_movements = StockMovement.objects.select_related('product', 'created_by').exclude(movement_type='delivery')

    try:
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        stock_out_movements = stock_out_movements.filter(
            created_at__date__gte=from_date,
            created_at__date__lte=to_date
        )
    except ValueError:
        pass

    if product_filter:
        stock_out_movements = stock_out_movements.filter(product_id=product_filter)

    if movement_type:
        stock_out_movements = stock_out_movements.filter(movement_type=movement_type)

    if search:
        stock_out_movements = stock_out_movements.filter(
            Q(product__name__icontains=search) |
            Q(notes__icontains=search) |
            Q(reference_id__icontains=search)
        )

    stock_out_movements = stock_out_movements.order_by(sort)

    paginator = Paginator(stock_out_movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_movements = stock_out_movements.count()
    total_out = stock_out_movements.aggregate(total=Sum('quantity'))['total'] or 0
    sale_movements = stock_out_movements.filter(movement_type='sale').count()
    adjustment_movements = stock_out_movements.filter(movement_type='adjustment').count()
    
    total_revenue = 0
    total_cost_of_goods = 0
    sale_movement_ids = []
    for movement in stock_out_movements.filter(movement_type='sale'):
        if movement.reference_id:
            try:
                sale_movement_ids.append(int(movement.reference_id))
            except (ValueError, TypeError):
                pass
    
    if sale_movement_ids:
        orders = Order.objects.filter(id__in=sale_movement_ids)
        for order in orders:
            total_revenue += order.total_amount
            total_cost_of_goods += order.quantity * order.product.cost_price
    
    total_gross_profit = total_revenue - total_cost_of_goods

    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    
    out_types = [t for t in StockMovement.MOVEMENT_TYPES if t[0] != 'delivery']

    context = {
        'page_obj': page_obj,
        'stock_out_items': page_obj.object_list,
        'products': products,
        'movement_types': out_types,
        'current_filters': {
            'date_from': date_from,
            'date_to': date_to,
            'product': product_filter,
            'type': movement_type,
            'search': search,
            'sort': sort,
        },
        'summary_stats': {
            'total_movements': total_movements,
            'total_out': abs(total_out) if total_out else 0,
            'sale_movements': sale_movements,
            'adjustment_movements': adjustment_movements,
            'total_revenue': total_revenue,
            'total_cost_of_goods': total_cost_of_goods,
            'total_gross_profit': total_gross_profit,
        },
        'sort_choices': [
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-quantity', 'Highest Quantity'),
            ('quantity', 'Lowest Quantity'),
            ('product__name', 'Product A-Z'),
            ('-product__name', 'Product Z-A'),
        ]
    }

    return render(request, 'dealer/stock_out_list.html', context)


@login_required
@user_passes_test(is_dealer, login_url='core:login')
def low_stock_alert(request):
    """
    View products with low stock or requiring reorder
    """
    products = LPGProduct.objects.filter(is_active=True)

    low_stock_products = [p for p in products if p.is_low_stock]
    reorder_products = [p for p in products if p.is_reorder_needed]

    context = {
        'low_stock_products': low_stock_products,
        'reorder_products': reorder_products,
    }

    return render(request, 'dealer/low_stock_alert.html', context)


@user_passes_test(is_dealer, login_url='core:login')
def inventory_reports(request):
    """
    Comprehensive inventory reports and analytics dashboard
    Requirements: 6.5 - Inventory reporting and analytics
    """
    from django.db.models import Sum, Avg, Count, Q
    from datetime import datetime, timedelta

    # Get date range for reports (default to last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()

    # Inventory Valuation Report
    products = LPGProduct.objects.filter(is_active=True)
    total_inventory_value = sum(product.stock_value for product in products)
    total_cost_value = sum(product.current_stock * (product.cost_price or 0) for product in products)

    # Stock Movement Analysis
    movements = StockMovement.objects.filter(
        created_at__date__range=[start_date, end_date]
    )

    movement_summary = movements.aggregate(
        total_movements=Count('id'),
        total_in=Sum('quantity', filter=Q(quantity__gt=0)),
        total_out=Sum('quantity', filter=Q(quantity__lt=0))
    )

    # Top Moving Products
    top_products = movements.values('product__name', 'product__size').annotate(
        total_movement=Sum('quantity'),
        movement_count=Count('id')
    ).order_by('-movement_count')[:10]

    # Supplier Performance (based on deliveries)
    supplier_performance = DeliveryLog.objects.filter(
        delivery_date__date__range=[start_date, end_date]
    ).values('supplier_name').annotate(
        total_deliveries=Count('id'),
        total_quantity=Sum('quantity_received'),
        total_cost=Sum('total_cost'),
        avg_cost_per_unit=Avg('cost_per_unit')
    ).order_by('-total_deliveries')[:10]

    # Low Stock Analysis
    low_stock_products = products.filter(current_stock__lte=F('minimum_stock'))
    reorder_needed = products.filter(current_stock__lte=F('reorder_point'))

    # ABC Analysis (based on stock value)
    products_with_value = [(p, p.stock_value) for p in products if p.stock_value > 0]
    products_with_value.sort(key=lambda x: x[1], reverse=True)

    total_value = sum(value for _, value in products_with_value)
    cumulative_value = 0
    abc_analysis = {'A': [], 'B': [], 'C': []}

    for product, value in products_with_value:
        cumulative_value += value
        percentage = (cumulative_value / total_value) * 100 if total_value > 0 else 0

        if percentage <= 80:
            abc_analysis['A'].append(product)
        elif percentage <= 95:
            abc_analysis['B'].append(product)
        else:
            abc_analysis['C'].append(product)

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_inventory_value': total_inventory_value,
        'total_cost_value': total_cost_value,
        'potential_profit': total_inventory_value - total_cost_value,
        'movement_summary': movement_summary,
        'top_products': top_products,
        'supplier_performance': supplier_performance,
        'low_stock_count': low_stock_products.count(),
        'reorder_needed_count': reorder_needed.count(),
        'abc_analysis': abc_analysis,
        'products': products,
    }

    return render(request, 'dealer/inventory_reports.html', context)


@user_passes_test(is_dealer, login_url='core:login')
@require_http_methods(["POST"])
@csrf_protect
def create_category(request):
    """
    AJAX endpoint to create a new product category
    """
    from .models import ProductCategory
    from .forms import ProductCategoryForm
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'Category name is required.'
                }, status=400)
            
            # Check if category already exists
            if ProductCategory.objects.filter(name__iexact=name).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Category "{name}" already exists.'
                }, status=400)
            
            # Create the category
            category = ProductCategory.objects.create(
                name=name,
                description=description,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Category "{name}" created successfully.',
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid request format.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error creating category: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@require_http_methods(["GET"])
def get_categories(request):
    """
    AJAX endpoint to fetch all active categories as JSON
    """
    from .models import ProductCategory
    
    categories = ProductCategory.objects.filter(is_active=True).values('id', 'name').order_by('name')
    return JsonResponse({
        'success': True,
        'categories': list(categories)
    })


# Notification Views for Customers
@login_required
@require_http_methods(["GET"])
def customer_notifications(request):
    """
    Customer notifications list view
    """
    notifications = Notification.objects.filter(customer=request.user).order_by('-created_at')
    
    # Paginate notifications
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
    }
    return render(request, 'customer/notifications.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_as_read(request, notification_id):
    """
    Mark a notification as read
    """
    notification = get_object_or_404(Notification, id=notification_id, customer=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_as_read(request):
    """
    Mark all unread notifications as read
    """
    unread = Notification.objects.filter(customer=request.user, is_read=False)
    unread.update(is_read=True, read_at=timezone.now())
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Marked {unread.count()} notification(s) as read'
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))


@login_required
@require_http_methods(["GET"])
def get_unread_notifications_count(request):
    """
    AJAX endpoint to get unread notifications count
    """
    count = Notification.objects.filter(
        customer=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({
        'success': True,
        'unread_count': count
    })