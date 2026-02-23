"""
Cashier Management Views
Admin-only resources for managing cashier staff and customer orders
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q, F
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO

from .models import Cashier, CashierTransaction, Order, LPGProduct
from .forms import (
    CashierCreationForm, CashierUpdateForm, CashierOrderForm,
    CashierTransactionForm
)


def is_admin(user):
    """Check if user is admin/superuser"""
    return user.is_superuser or (user.is_staff and not hasattr(user, 'cashier_profile'))


def is_cashier(user):
    """Check if user is a cashier (has cashier profile)"""
    return hasattr(user, 'cashier_profile') and user.cashier_profile.is_active


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_list(request):
    """
    List all cashiers - Admin only
    """
    cashiers = Cashier.objects.all().select_related('user')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        cashiers = cashiers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(cashiers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_cashiers = Cashier.objects.count()
    active_cashiers = Cashier.objects.filter(is_active=True).count()
    inactive_cashiers = total_cashiers - active_cashiers
    
    context = {
        'page_obj': page_obj,
        'cashiers': page_obj.object_list,
        'search_query': search_query,
        'total_cashiers': total_cashiers,
        'active_cashiers': active_cashiers,
        'inactive_cashiers': inactive_cashiers,
    }
    return render(request, 'admin/cashier_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
@require_http_methods(["GET", "POST"])
def cashier_create(request):
    """
    Create a new cashier account - Admin only
    """
    if request.method == 'POST':
        form = CashierCreationForm(request.POST)
        if form.is_valid():
            try:
                cashier = form.save()
                messages.success(request, f'Cashier account created successfully for {cashier.user.username}')
                return redirect('core:cashier_list')
            except Exception as e:
                messages.error(request, f'Error creating cashier: {str(e)}')
    else:
        form = CashierCreationForm()
    
    return render(request, 'admin/cashier_form.html', {'form': form, 'title': 'Create New Cashier'})


@login_required
@user_passes_test(is_admin, login_url='core:login')
@require_http_methods(["GET", "POST"])
def cashier_update(request, cashier_id):
    """
    Update cashier details - Admin only
    """
    cashier = get_object_or_404(Cashier, pk=cashier_id)
    
    if request.method == 'POST':
        form = CashierUpdateForm(request.POST, instance=cashier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cashier {cashier.user.username} updated successfully')
            return redirect('core:cashier_list')
    else:
        form = CashierUpdateForm(instance=cashier)
    
    return render(request, 'admin/cashier_form.html', {
        'form': form,
        'title': f'Update Cashier: {cashier.user.first_name or cashier.user.username}',
        'cashier': cashier
    })


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_toggle_status(request, cashier_id):
    """
    Toggle cashier active status - Admin only
    """
    cashier = get_object_or_404(Cashier, pk=cashier_id)
    cashier.is_active = not cashier.is_active
    cashier.save()
    
    status = 'activated' if cashier.is_active else 'deactivated'
    messages.success(request, f'Cashier {cashier.user.username} {status} successfully')
    
    return redirect('core:cashier_list')


@login_required
@user_passes_test(is_cashier, login_url='core:login')
def cashier_order_list(request):
    """
    Cashier's order list - shows ALL customer orders for processing
    Cashiers process customer orders (NOT their own orders)
    Batch orders are grouped together and shown as single entries
    """
    if not hasattr(request.user, 'cashier_profile'):
        return redirect('core:login')
    
    cashier = request.user.cashier_profile
    
    orders = Order.objects.select_related('customer', 'product').all().order_by('-order_date', 'batch_id', 'id')
    
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
            Q(product__name__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(batch_id__icontains=search_query)
        )
    
    sort_by = request.GET.get('sort', '-order_date')
    valid_sort_fields = [
        'order_date', '-order_date', 'status', '-status', 
        'total_amount', '-total_amount', 'customer__username', 
        '-customer__username', 'product__name', '-product__name'
    ]
    if sort_by in valid_sort_fields:
        orders = orders.order_by(sort_by, 'batch_id', 'id')
    else:
        orders = orders.order_by('-order_date', 'batch_id', 'id')
    
    seen_batches = set()
    unique_orders = []
    for order in orders:
        if order.batch_id not in seen_batches:
            seen_batches.add(order.batch_id)
            unique_orders.append(order)
    
    from django.db.models import Min
    all_orders = Order.objects.all()
    summary_stats = {
        'total_orders': all_orders.values('batch_id').distinct().count(),
        'pending_count': all_orders.filter(status='pending').values('batch_id').distinct().count(),
        'out_for_delivery_count': all_orders.filter(status='out_for_delivery').values('batch_id').distinct().count(),
        'delivered_count': all_orders.filter(status='delivered').values('batch_id').distinct().count()
    }
    
    from django.core.paginator import Paginator
    paginator = Paginator(unique_orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    status_choices = Order.STATUS_CHOICES
    delivery_choices = Order.DELIVERY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'delivery_filter': delivery_filter,
        'sort_by': sort_by,
        'summary_stats': summary_stats,
        'status_choices': status_choices,
        'delivery_choices': delivery_choices,
        'current_filters': {
            'status': status_filter,
            'delivery_type': delivery_filter,
            'search': search_query,
        },
        'cashier': cashier,
    }
    
    return render(request, 'dealer/cashier_order_list.html', context)


@login_required
@user_passes_test(is_cashier, login_url='core:login')
def cashier_personal_dashboard(request):
    """
    Cashier's personal dashboard - shows their own transactions
    """
    if not hasattr(request.user, 'cashier_profile'):
        return redirect('core:login')
    
    cashier = request.user.cashier_profile
    today = timezone.now().date()
    
    # Get this cashier's transactions
    cashier_transactions = CashierTransaction.objects.filter(cashier=cashier)
    today_transactions = cashier_transactions.filter(created_at__date=today)
    today_total = today_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Transaction breakdown
    transaction_breakdown = cashier_transactions.filter(created_at__date=today).values('transaction_type').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-count')
    
    # Recent transactions - filter by today only
    recent_transactions = today_transactions.select_related('order', 'customer').order_by('-created_at')[:10]
    
    # Performance metrics
    total_transactions = cashier_transactions.count()
    total_amount = cashier_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
    
    context = {
        'cashier': cashier,
        'today_total': today_total,
        'today_transaction_count': today_transactions.count(),
        'total_transactions': total_transactions,
        'total_amount': total_amount,
        'avg_transaction': avg_transaction,
        'transaction_breakdown': transaction_breakdown,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dealer/cashier_personal_dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_dashboard(request):
    """
    Cashier dashboard with transaction summary - Admin only
    """
    # Get all transactions
    today = timezone.now().date()
    
    today_transactions = CashierTransaction.objects.filter(created_at__date=today)
    today_total = today_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get cashier statistics
    total_transactions = CashierTransaction.objects.count()
    cashiers_count = Cashier.objects.filter(is_active=True).count()
    
    # Transaction breakdown by type
    transaction_breakdown = CashierTransaction.objects.values('transaction_type').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-count')
    
    # Recent transactions
    recent_transactions = CashierTransaction.objects.select_related('cashier', 'customer')[:10]
    
    context = {
        'today_total': today_total,
        'today_transaction_count': today_transactions.count(),
        'total_transactions': total_transactions,
        'active_cashiers': cashiers_count,
        'transaction_breakdown': transaction_breakdown,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'admin/cashier_dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
@require_http_methods(["GET", "POST"])
def manage_customer_order(request):
    """
    Manage customer orders - Cashiers can create/manage orders
    Admin interface
    """
    if request.method == 'POST':
        form = CashierOrderForm(request.POST)
        if form.is_valid():
            try:
                with db_transaction.atomic():
                    order = form.save(commit=False)
                    order.status = 'pending'
                    order.total_amount = order.product.price * order.quantity
                    order.save()
                    
                    # Reserve stock
                    product = order.product
                    product.reserve_stock(order.quantity)
                    
                    # Record transaction
                    if hasattr(request.user, 'cashier_profile'):
                        cashier = request.user.cashier_profile
                    else:
                        cashier, _ = Cashier.objects.get_or_create(
                            user=request.user,
                            defaults={'employee_id': f'ADMIN-{request.user.id}'}
                        )
                    
                    CashierTransaction.objects.create(
                        cashier=cashier,
                        order=order,
                        transaction_type='order',
                        amount=order.total_amount,
                        payment_method='pending',
                        customer=order.customer
                    )
                    
                    messages.success(request, f'Order created successfully for {order.customer.username}')
                    return redirect('core:cashier_dashboard')
            except Exception as e:
                messages.error(request, f'Error creating order: {str(e)}')
    else:
        form = CashierOrderForm()
    
    return render(request, 'admin/manage_customer_order.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_transactions(request):
    """
    View all cashier transactions - Admin only
    """
    transactions = CashierTransaction.objects.select_related('cashier', 'customer', 'order').all()
    
    # Filters
    cashier_id = request.GET.get('cashier')
    transaction_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if cashier_id:
        transactions = transactions.filter(cashier_id=cashier_id)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if date_from:
        transactions = transactions.filter(created_at__date__gte=date_from)
    if date_to:
        transactions = transactions.filter(created_at__date__lte=date_to)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    transactions = transactions.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_amount = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'page_obj': page_obj,
        'transactions': page_obj.object_list,
        'total_amount': total_amount,
        'cashiers': Cashier.objects.filter(is_active=True),
        'transaction_types': CashierTransaction.TRANSACTION_TYPES,
        'filters_applied': any([cashier_id, transaction_type, date_from, date_to]),
    }
    
    return render(request, 'admin/cashier_transactions.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
@require_http_methods(["GET", "POST"])
def record_payment(request):
    """
    Record a customer payment - Admin only
    """
    if request.method == 'POST':
        form = CashierTransactionForm(request.POST)
        if form.is_valid():
            try:
                transaction_obj = form.save(commit=False)
                # Get admin user's cashier profile
                if hasattr(request.user, 'cashier_profile'):
                    transaction_obj.cashier = request.user.cashier_profile
                else:
                    # Create a temporary cashier profile for admin if needed
                    cashier, _ = Cashier.objects.get_or_create(
                        user=request.user,
                        defaults={'employee_id': f'ADMIN-{request.user.id}'}
                    )
                    transaction_obj.cashier = cashier
                
                transaction_obj.save()
                messages.success(request, 'Payment recorded successfully')
                return redirect('core:cashier_dashboard')
            except Exception as e:
                messages.error(request, f'Error recording payment: {str(e)}')
    else:
        form = CashierTransactionForm()
    
    return render(request, 'admin/record_payment.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_performance(request):
    """
    View cashier performance metrics - Admin only
    """
    # Get performance metrics for each cashier
    cashiers = Cashier.objects.filter(is_active=True)
    
    performance_data = []
    for cashier in cashiers:
        transactions = CashierTransaction.objects.filter(cashier=cashier)
        total_amount = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        transaction_count = transactions.count()
        
        performance_data.append({
            'cashier': cashier,
            'total_amount': total_amount,
            'transaction_count': transaction_count,
            'avg_transaction': total_amount / transaction_count if transaction_count > 0 else 0,
            'orders': transactions.filter(transaction_type='order').count(),
            'payments': transactions.filter(transaction_type='payment').count(),
        })
    
    # Sort by total amount
    performance_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    context = {
        'performance_data': performance_data,
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
    }
    
    return render(request, 'admin/cashier_performance.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_daily_income_report(request):
    """
    Admin view to monitor daily income by cashier
    Shows breakdown of orders processed by each cashier
    """
    today = timezone.now().date()
    
    # Date range filter
    date_from = request.GET.get('date_from', str(today))
    date_to = request.GET.get('date_to', str(today))
    
    try:
        from datetime import datetime
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    except:
        date_from = today
        date_to = today
    
    # Get all orders delivered in date range by cashiers
    orders = Order.objects.filter(
        status='delivered',
        delivery_date__date__gte=date_from,
        delivery_date__date__lte=date_to,
        processed_by__isnull=False
    ).select_related('processed_by', 'product', 'customer')
    
    # Group by product and cashier
    inventory_impact_data = {}
    
    for order in orders:
        product = order.product
        cashier = order.processed_by
        key = (product.id, cashier.id)
        
        if key not in inventory_impact_data:
            inventory_impact_data[key] = {
                'product': product,
                'cashier': cashier,
                'total_quantity': 0,
                'total_amount': 0,
                'order_count': 0,
            }
        
        inventory_impact_data[key]['total_quantity'] += order.quantity
        inventory_impact_data[key]['total_amount'] += order.total_amount
        inventory_impact_data[key]['order_count'] += 1
    
    # Convert to list and sort
    impact_list = list(inventory_impact_data.values())
    impact_list.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Get product-level summary
    product_summary = {}
    for item in impact_list:
        product_id = item['product'].id
        if product_id not in product_summary:
            product_summary[product_id] = {
                'product': item['product'],
                'total_quantity': 0,
                'total_amount': 0,
            }
        product_summary[product_id]['total_quantity'] += item['total_quantity']
        product_summary[product_id]['total_amount'] += item['total_amount']
    
    product_summary = list(product_summary.values())
    product_summary.sort(key=lambda x: x['total_quantity'], reverse=True)
    
    # Pagination
    paginator = Paginator(impact_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'inventory_impact_data': page_obj.object_list,
        'product_summary': product_summary,
        'date_from': date_from,
        'date_to': date_to,
        'total_quantity': sum(item['total_quantity'] for item in impact_list),
        'total_amount': sum(item['total_amount'] for item in impact_list),
    }
    
    return render(request, 'admin/cashier_inventory_impact.html', context)


@login_required
@user_passes_test(is_cashier)
def export_daily_report_pdf(request):
    """
    Export cashier's daily revenue report as PDF
    """
    today = timezone.now().date()
    report_date = request.GET.get('date', str(today))
    
    try:
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    except:
        report_date = today
    
    # Get current cashier
    cashier = request.user.cashier_profile
    
    # Get delivered orders for this cashier on the selected date
    orders = Order.objects.filter(
       status='delivered',
       order_date__date=report_date,
       processed_by=cashier
    ).select_related('product', 'customer')
    
    # Income summary
    total_income = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    avg_order = total_income / total_orders if total_orders > 0 else 0
    
    # Product breakdown
    product_data = []
    for product in LPGProduct.objects.all():
        product_orders = orders.filter(product=product)
        qty = product_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        revenue = product_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        if qty > 0:
            product_data.append({
                'product': product,
                'quantity': qty,
                'revenue': revenue,
                'avg_price': revenue / qty if qty > 0 else 0,
                'orders': product_orders.count(),
            })
    
    product_data.sort(key=lambda x: x['revenue'], reverse=True)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#FF6B00'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    # Header
    elements.append(Paragraph("PRYCEGAS CASHIER DAILY SALES REPORT", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Report info with cashier name
    info_data = [
        ['Cashier Name:', f'{cashier.user.get_full_name() or cashier.user.username}'],
        ['Report Date:', report_date.strftime('%B %d, %Y')],
        ['Generated:', timezone.now().strftime('%B %d, %Y %I:%M %p')],
    ]
    info_table = Table(info_data, colWidths=[1.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Summary
    elements.append(Paragraph("SUMMARY", heading_style))
    summary_data = [
        ['Total Revenue', '₱' + f'{total_income:,.2f}'],
        ['Orders Completed', str(total_orders)],
        ['Average Order Value', '₱' + f'{avg_order:,.2f}'],
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F2937')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#FF6B00')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Orders List
    if orders:
        elements.append(Paragraph("ORDERS DELIVERED TODAY", heading_style))
        orders_data = [['Order ID', 'Customer', 'Product', 'Qty', 'Amount']]
        for order in orders:
            customer_name = order.customer.get_full_name() or order.customer.username if order.customer else 'Walk-in'
            orders_data.append([
                f'#{order.id}',
                customer_name[:20],
                f"{order.product.name} ({order.product.size})"[:30],
                str(order.quantity),
                f"₱{order.total_amount:,.2f}"
            ])
        
        orders_table = Table(orders_data, colWidths=[0.8*inch, 1.3*inch, 1.8*inch, 0.5*inch, 1*inch])
        orders_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
            ('ALIGN', (0, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(orders_table)
        elements.append(Spacer(1, 0.15*inch))
    
    # Product Breakdown
    if product_data:
        elements.append(Paragraph("PRODUCT DISTRIBUTION", heading_style))
        product_table_data = [['Product', 'Size', 'Qty', 'Revenue', 'Avg Price', 'Orders']]
        for item in product_data:
            product_table_data.append([
                item['product'].name,
                item['product'].size,
                str(item['quantity']),
                f"₱{item['revenue']:,.2f}",
                f"₱{item['avg_price']:,.2f}",
                str(item['orders'])
            ])
        
        product_table = Table(product_table_data, colWidths=[1*inch, 0.8*inch, 0.6*inch, 1*inch, 1*inch, 0.6*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(product_table)
    
    # Signature section
    elements.append(Spacer(1, 0.3*inch))
    signature_data = [
        ['Prepared By:', '_' * 40],
        ['', ''],
        ['Signatory:', '_' * 40],
    ]
    signature_table = Table(signature_data, colWidths=[1.5*inch, 3.5*inch])
    signature_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(signature_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cashier_daily_report_{report_date}.pdf"'
    
    return response


@login_required
@user_passes_test(is_cashier)
def export_monthly_report_pdf(request):
    """
    Export cashier's monthly revenue report as PDF
    """
    today = timezone.now().date()
    date_str = request.GET.get('date', str(today))
    
    try:
        report_date = datetime.strptime(date_str, '%Y-%m').date()
    except:
        report_date = today.replace(day=1)
    
    # Get current cashier
    cashier = request.user.cashier_profile
    
    # Get delivered orders for this cashier in the selected month
    from_date = report_date.replace(day=1)
    if report_date.month == 12:
        to_date = report_date.replace(year=report_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        to_date = report_date.replace(month=report_date.month + 1, day=1) - timedelta(days=1)
    
    orders = Order.objects.filter(
        status='delivered',
        order_date__date__gte=from_date,
        order_date__date__lte=to_date,
        processed_by=cashier
    ).select_related('product', 'customer')
    
    # Income summary
    total_income = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    avg_order = total_income / total_orders if total_orders > 0 else 0
    
    # Product breakdown
    product_data = []
    for product in LPGProduct.objects.all():
        product_orders = orders.filter(product=product)
        qty = product_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        revenue = product_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        if qty > 0:
            product_data.append({
                'product': product,
                'quantity': qty,
                'revenue': revenue,
                'avg_price': revenue / qty if qty > 0 else 0,
                'orders': product_orders.count(),
            })
    
    product_data.sort(key=lambda x: x['revenue'], reverse=True)
    
    # Daily breakdown
    daily_data = []
    current_date = from_date
    while current_date <= to_date:
        day_orders = orders.filter(order_date__date=current_date)
        day_income = day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        day_count = day_orders.count()
        
        if day_count > 0:
            daily_data.append({
                'date': current_date,
                'income': day_income,
                'orders': day_count,
            })
        
        current_date += timedelta(days=1)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#FF6B00'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    # Header
    elements.append(Paragraph("PRYCEGAS CASHIER MONTHLY SALES REPORT", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Report info with cashier name
    info_data = [
       ['Cashier Name:', f'{cashier.user.get_full_name() or cashier.user.username}'],
       ['Report Period:', f'{from_date.strftime("%B %Y")}'],
       ['Generated:', timezone.now().strftime('%B %d, %Y %I:%M %p')],
    ]
    info_table = Table(info_data, colWidths=[1.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
       ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
       ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
       ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F2937')),
       ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
       ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
       ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Summary
    elements.append(Paragraph("SUMMARY", heading_style))
    summary_data = [
       ['Total Revenue', '₱' + f'{total_income:,.2f}'],
       ['Orders Completed', str(total_orders)],
       ['Average Order Value', '₱' + f'{avg_order:,.2f}'],
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
       ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
       ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 10),
       ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F2937')),
       ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#FF6B00')),
       ('ALIGN', (0, 0), (0, -1), 'LEFT'),
       ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
       ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
       ('TOPPADDING', (0, 0), (-1, -1), 6),
       ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
       ('LEFTPADDING', (0, 0), (-1, -1), 10),
       ('RIGHTPADDING', (0, 0), (-1, -1), 10),
       ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Daily breakdown
    if daily_data:
       elements.append(Paragraph("DAILY BREAKDOWN", heading_style))
       daily_table_data = [['Date', 'Orders', 'Revenue']]
       for day_item in daily_data:
           daily_table_data.append([
               day_item['date'].strftime('%b %d, %Y'),
               str(day_item['orders']),
               f"₱{day_item['income']:,.2f}"
           ])
       
       daily_table = Table(daily_table_data, colWidths=[2*inch, 1*inch, 2*inch])
       daily_table.setStyle(TableStyle([
           ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
           ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
           ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
           ('ALIGN', (0, 0), (0, -1), 'LEFT'),
           ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
           ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
           ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
           ('TOPPADDING', (0, 0), (-1, -1), 4),
           ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
           ('LEFTPADDING', (0, 0), (-1, -1), 4),
           ('RIGHTPADDING', (0, 0), (-1, -1), 4),
       ]))
       elements.append(daily_table)
       elements.append(Spacer(1, 0.15*inch))
    
    # Product breakdown
    if product_data:
       elements.append(Paragraph("PRODUCT DISTRIBUTION", heading_style))
       product_table_data = [['Product', 'Size', 'Qty', 'Revenue', 'Avg Price', 'Orders']]
       for item in product_data:
           product_table_data.append([
               item['product'].name,
               item['product'].size,
               str(item['quantity']),
               f"₱{item['revenue']:,.2f}",
               f"₱{item['avg_price']:,.2f}",
               str(item['orders'])
           ])
       
       product_table = Table(product_table_data, colWidths=[1*inch, 0.8*inch, 0.6*inch, 1*inch, 1*inch, 0.6*inch])
       product_table.setStyle(TableStyle([
           ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
           ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
           ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
           ('ALIGN', (0, 0), (1, -1), 'LEFT'),
           ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
           ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
           ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
           ('TOPPADDING', (0, 0), (-1, -1), 4),
           ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
           ('LEFTPADDING', (0, 0), (-1, -1), 4),
           ('RIGHTPADDING', (0, 0), (-1, -1), 4),
       ]))
       elements.append(product_table)
       
       # Signature section
       elements.append(Spacer(1, 0.3*inch))
       signature_data = [
        ['Prepared By:', '_' * 40],
        ['', ''],
        ['Signatory:', '_' * 40],
       ]
       signature_table = Table(signature_data, colWidths=[1.5*inch, 3.5*inch])
       signature_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
       ]))
       elements.append(signature_table)
       
       # Build PDF
       doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cashier_monthly_report_{from_date.strftime("%Y-%m")}.pdf"'
    
    return response


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_reports(request):
    """
    Main cashier reports dashboard with daily, monthly, yearly options
    """
    report_type = request.GET.get('type', 'daily')
    
    if report_type == 'monthly':
        return cashier_monthly_report(request)
    elif report_type == 'yearly':
        return cashier_yearly_report(request)
    else:
        return cashier_daily_report(request)


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_daily_report(request):
    """
    Detailed daily report: Income and Inventory by Cashier
    """
    today = timezone.now().date()
    report_date = request.GET.get('date', str(today))
    
    try:
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    except:
        report_date = today
    
    # Get all delivered orders for the day
    orders = Order.objects.filter(
        status='delivered',
        delivery_date__date=report_date,
        processed_by__isnull=False
    ).select_related('processed_by', 'product', 'customer')
    
    # Income data by cashier
    income_data = []
    for cashier in Cashier.objects.all():
        cashier_orders = orders.filter(processed_by=cashier)
        total_amount = cashier_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        order_count = cashier_orders.count()
        
        if order_count > 0:
            income_data.append({
                'cashier': cashier,
                'total_amount': total_amount,
                'order_count': order_count,
                'avg_order': total_amount / order_count if order_count > 0 else 0,
            })
    
    income_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Inventory/Stock data by product
    stock_data = []
    for product in LPGProduct.objects.all():
        product_orders = orders.filter(product=product)
        total_qty = product_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_revenue = product_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        if total_qty > 0:
            stock_data.append({
                'product': product,
                'quantity_delivered': total_qty,
                'total_revenue': total_revenue,
                'avg_price': total_revenue / total_qty if total_qty > 0 else 0,
                'orders': product_orders.count(),
            })
    
    stock_data.sort(key=lambda x: x['quantity_delivered'], reverse=True)
    
    total_income = sum(item['total_amount'] for item in income_data)
    total_orders = sum(item['order_count'] for item in income_data)
    total_units = sum(item['quantity_delivered'] for item in stock_data)
    
    context = {
        'report_type': 'daily',
        'report_date': report_date,
        'income_data': income_data,
        'stock_data': stock_data,
        'total_income': total_income,
        'total_orders': total_orders,
        'total_units': total_units,
    }
    
    return render(request, 'admin/cashier_reports.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_monthly_report(request):
    """
    Monthly report: Income and Inventory by Cashier
    """
    today = timezone.now().date()
    year = request.GET.get('year', str(today.year))
    month = request.GET.get('month', str(today.month))
    
    try:
        year = int(year)
        month = int(month)
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
    except:
        month_start = date(today.year, today.month, 1)
        if today.month == 12:
            month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    # Get all delivered orders for the month
    orders = Order.objects.filter(
        status='delivered',
        delivery_date__date__gte=month_start,
        delivery_date__date__lte=month_end,
        processed_by__isnull=False
    ).select_related('processed_by', 'product', 'customer')
    
    # Income data by cashier
    income_data = []
    for cashier in Cashier.objects.all():
        cashier_orders = orders.filter(processed_by=cashier)
        total_amount = cashier_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        order_count = cashier_orders.count()
        
        if order_count > 0:
            income_data.append({
                'cashier': cashier,
                'total_amount': total_amount,
                'order_count': order_count,
                'avg_order': total_amount / order_count if order_count > 0 else 0,
            })
    
    income_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Inventory/Stock data by product
    stock_data = []
    for product in LPGProduct.objects.all():
        product_orders = orders.filter(product=product)
        total_qty = product_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_revenue = product_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        if total_qty > 0:
            stock_data.append({
                'product': product,
                'quantity_delivered': total_qty,
                'total_revenue': total_revenue,
                'avg_price': total_revenue / total_qty if total_qty > 0 else 0,
                'orders': product_orders.count(),
            })
    
    stock_data.sort(key=lambda x: x['quantity_delivered'], reverse=True)
    
    total_income = sum(item['total_amount'] for item in income_data)
    total_orders = sum(item['order_count'] for item in income_data)
    total_units = sum(item['quantity_delivered'] for item in stock_data)
    
    context = {
        'report_type': 'monthly',
        'month_start': month_start,
        'month_end': month_end,
        'year': year,
        'month': month,
        'income_data': income_data,
        'stock_data': stock_data,
        'total_income': total_income,
        'total_orders': total_orders,
        'total_units': total_units,
    }
    
    return render(request, 'admin/cashier_reports.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_yearly_report(request):
    """
    Yearly report: Income and Inventory by Cashier
    """
    today = timezone.now().date()
    year = request.GET.get('year', str(today.year))
    
    try:
        year = int(year)
    except:
        year = today.year
    
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    
    # Get all delivered orders for the year
    orders = Order.objects.filter(
        status='delivered',
        delivery_date__date__gte=year_start,
        delivery_date__date__lte=year_end,
        processed_by__isnull=False
    ).select_related('processed_by', 'product', 'customer')
    
    # Income data by cashier
    income_data = []
    for cashier in Cashier.objects.all():
        cashier_orders = orders.filter(processed_by=cashier)
        total_amount = cashier_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        order_count = cashier_orders.count()
        
        if order_count > 0:
            income_data.append({
                'cashier': cashier,
                'total_amount': total_amount,
                'order_count': order_count,
                'avg_order': total_amount / order_count if order_count > 0 else 0,
            })
    
    income_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Inventory/Stock data by product
    stock_data = []
    for product in LPGProduct.objects.all():
        product_orders = orders.filter(product=product)
        total_qty = product_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_revenue = product_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        if total_qty > 0:
            stock_data.append({
                'product': product,
                'quantity_delivered': total_qty,
                'total_revenue': total_revenue,
                'avg_price': total_revenue / total_qty if total_qty > 0 else 0,
                'orders': product_orders.count(),
            })
    
    stock_data.sort(key=lambda x: x['quantity_delivered'], reverse=True)
    
    # Monthly breakdown for the year
    monthly_breakdown = []
    for m in range(1, 13):
        month_start = date(year, m, 1)
        if m == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, m + 1, 1) - timedelta(days=1)
        
        month_orders = orders.filter(
            delivery_date__date__gte=month_start,
            delivery_date__date__lte=month_end
        )
        month_income = month_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        month_qty = month_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        monthly_breakdown.append({
            'month': m,
            'month_name': datetime(year, m, 1).strftime('%B'),
            'income': month_income,
            'quantity': month_qty,
            'orders': month_orders.count(),
        })
    
    total_income = sum(item['total_amount'] for item in income_data)
    total_orders = sum(item['order_count'] for item in income_data)
    total_units = sum(item['quantity_delivered'] for item in stock_data)
    
    context = {
        'report_type': 'yearly',
        'year': year,
        'income_data': income_data,
        'stock_data': stock_data,
        'monthly_breakdown': monthly_breakdown,
        'total_income': total_income,
        'total_orders': total_orders,
        'total_units': total_units,
    }
    
    return render(request, 'admin/cashier_reports.html', context)


@login_required
@user_passes_test(is_cashier, login_url='core:login')
def cashier_personal_reports_daily(request):
    """
    Cashier's personal daily revenue report
    """
    today = timezone.now().date()
    report_date = request.GET.get('date', str(today))
    
    try:
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    except:
        report_date = today
    
    # Get current cashier
    cashier = request.user.cashier_profile
    
    # Get delivered orders for this cashier on the selected date
    orders = Order.objects.filter(
        status='delivered',
        order_date__date=report_date,
        processed_by=cashier
    ).select_related('product', 'customer')
    
    # Income summary
    total_income = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    avg_order = total_income / total_orders if total_orders > 0 else 0
    
    # Product breakdown
    product_data = []
    for product in LPGProduct.objects.all():
        product_orders = orders.filter(product=product)
        qty = product_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        revenue = product_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        if qty > 0:
            product_data.append({
                'product': product,
                'quantity': qty,
                'revenue': revenue,
                'avg_price': revenue / qty if qty > 0 else 0,
                'orders': product_orders.count(),
            })
    
    product_data.sort(key=lambda x: x['revenue'], reverse=True)
    
    context = {
        'report_type': 'daily',
        'report_date': report_date,
        'cashier': cashier,
        'orders': orders,
        'product_data': product_data,
        'total_income': total_income,
        'total_orders': total_orders,
        'avg_order': avg_order,
    }
    
    return render(request, 'cashier/personal_reports_daily.html', context)


@login_required
@user_passes_test(is_cashier, login_url='core:login')
def cashier_personal_reports_monthly(request):
    """
    Cashier's personal monthly revenue report
    """
    today = timezone.now().date()
    year = request.GET.get('year', str(today.year))
    month = request.GET.get('month', str(today.month))
    
    try:
        year = int(year)
        month = int(month)
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
    except:
        month_start = date(today.year, today.month, 1)
        if today.month == 12:
            month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        year = today.year
        month = today.month
    
    # Get current cashier
    cashier = request.user.cashier_profile
    
    # Get delivered orders for this cashier in the selected month
    orders = Order.objects.filter(
        status='delivered',
        order_date__date__gte=month_start,
        order_date__date__lte=month_end,
        processed_by=cashier
    ).select_related('product', 'customer')
    
    # Income summary
    total_income = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    avg_order = total_income / total_orders if total_orders > 0 else 0
    
    # Product breakdown
    product_data = []
    for product in LPGProduct.objects.all():
        product_orders = orders.filter(product=product)
        qty = product_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        revenue = product_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        if qty > 0:
            product_data.append({
                'product': product,
                'quantity': qty,
                'revenue': revenue,
                'avg_price': revenue / qty if qty > 0 else 0,
                'orders': product_orders.count(),
            })
    
    product_data.sort(key=lambda x: x['revenue'], reverse=True)
    
    # Daily breakdown
    daily_data = []
    for day in range(1, 32):
        try:
            day_date = date(year, month, day)
            if day_date > month_end:
                break
        except ValueError:
            break
        
        day_orders = orders.filter(order_date__date=day_date)
        if day_orders.exists():
            day_revenue = day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            daily_data.append({
                'date': day_date,
                'orders': day_orders.count(),
                'revenue': day_revenue,
            })
    
    context = {
        'report_type': 'monthly',
        'month_start': month_start,
        'month_end': month_end,
        'year': year,
        'month': month,
        'month_name': month_start.strftime('%B'),
        'cashier': cashier,
        'orders': orders,
        'product_data': product_data,
        'daily_data': daily_data,
        'total_income': total_income,
        'total_orders': total_orders,
        'avg_order': avg_order,
    }
    
    return render(request, 'cashier/personal_reports_monthly.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_inventory_impact_report(request):
    """
    Admin view to monitor inventory impact by cashier
    Shows breakdown of stock movements processed by each cashier
    """
    today = timezone.now().date()
    
    # Date range filter
    date_from = request.GET.get('date_from', str(today))
    date_to = request.GET.get('date_to', str(today))
    
    try:
        from datetime import datetime
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    except:
        date_from = today
        date_to = today
    
    # Get all orders delivered in date range by cashiers
    orders = Order.objects.filter(
        status='delivered',
        delivery_date__date__gte=date_from,
        delivery_date__date__lte=date_to,
        processed_by__isnull=False
    ).select_related('processed_by', 'product', 'customer')
    
    # Group by product and cashier
    inventory_impact_data = {}
    
    for order in orders:
        product = order.product
        cashier = order.processed_by
        key = (product.id, cashier.id)
        
        if key not in inventory_impact_data:
            inventory_impact_data[key] = {
                'product': product,
                'cashier': cashier,
                'total_quantity': 0,
                'total_amount': 0,
                'order_count': 0,
            }
        
        inventory_impact_data[key]['total_quantity'] += order.quantity
        inventory_impact_data[key]['total_amount'] += order.total_amount
        inventory_impact_data[key]['order_count'] += 1
    
    # Convert to list and sort
    impact_list = list(inventory_impact_data.values())
    impact_list.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Get product-level summary
    product_summary = {}
    for item in impact_list:
        product_id = item['product'].id
        if product_id not in product_summary:
            product_summary[product_id] = {
                'product': item['product'],
                'total_quantity': 0,
                'total_amount': 0,
            }
        product_summary[product_id]['total_quantity'] += item['total_quantity']
        product_summary[product_id]['total_amount'] += item['total_amount']
    
    product_summary = list(product_summary.values())
    product_summary.sort(key=lambda x: x['total_quantity'], reverse=True)
    
    # Pagination
    paginator = Paginator(impact_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'inventory_impact_data': page_obj.object_list,
        'product_summary': product_summary,
        'date_from': date_from,
        'date_to': date_to,
        'total_quantity': sum(item['total_quantity'] for item in impact_list),
        'total_amount': sum(item['total_amount'] for item in impact_list),
    }
    
    return render(request, 'admin/cashier_inventory_impact.html', context)
