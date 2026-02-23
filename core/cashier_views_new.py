"""
Cashier Management Views
Admin-only resources for managing cashier staff and customer orders
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q, F
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date

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
    Similar to admin order_management but for cashier role
    """
    if not hasattr(request.user, 'cashier_profile'):
        return redirect('core:login')
    
    cashier = request.user.cashier_profile
    
    # Get ALL customer orders for processing (same as admin sees)
    # NOT limited to orders created by this cashier
    orders = Order.objects.select_related('customer', 'product').all().order_by('-order_date')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    # Filter by delivery type
    delivery_filter = request.GET.get('delivery_type', '')
    if delivery_filter and delivery_filter in dict(Order.DELIVERY_CHOICES):
        orders = orders.filter(delivery_type=delivery_filter)
    
    # Search functionality - customer name or order ID
    search_query = request.GET.get('search', '').strip()
    if search_query:
        orders = orders.filter(
            Q(customer__username__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(product__name__icontains=search_query) |
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
    
    # Calculate summary statistics
    summary_stats = orders.aggregate(
        total_orders=Count('id'),
        pending_count=Count('id', filter=Q(status='pending')),
        out_for_delivery_count=Count('id', filter=Q(status='out_for_delivery')),
        delivered_count=Count('id', filter=Q(status='delivered'))
    )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter choices for template
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
    
    # Recent transactions
    recent_transactions = cashier_transactions.select_related('order', 'customer')[:10]
    
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
    
    # Group by cashier
    daily_income_data = []
    cashiers = Cashier.objects.all()
    
    for cashier in cashiers:
        cashier_orders = orders.filter(processed_by=cashier)
        total_amount = cashier_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        order_count = cashier_orders.count()
        
        if order_count > 0 or request.GET.get('show_all'):
            daily_income_data.append({
                'cashier': cashier,
                'total_amount': total_amount,
                'order_count': order_count,
                'avg_order_value': total_amount / order_count if order_count > 0 else 0,
                'orders': cashier_orders,
            })
    
    # Sort by total amount
    daily_income_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Calculate totals
    total_all = sum(item['total_amount'] for item in daily_income_data)
    total_orders = sum(item['order_count'] for item in daily_income_data)
    
    # Pagination
    paginator = Paginator(daily_income_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'daily_income_data': page_obj.object_list,
        'date_from': date_from,
        'date_to': date_to,
        'total_amount': total_all,
        'total_orders': total_orders,
    }
    
    return render(request, 'admin/cashier_daily_income.html', context)


@login_required
@user_passes_test(is_admin, login_url='core:login')
def cashier_inventory_impact_report(request):
    """
    Admin view to monitor inventory impact of orders processed by cashiers
    Shows product-level breakdown of what each cashier delivered
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
    
    # Get all delivered orders by cashiers in date range
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


# CASHIER PERSONAL REVENUE REPORTS

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
        delivery_date__date=report_date,
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
        delivery_date__date__gte=month_start,
        delivery_date__date__lte=month_end,
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
        
        day_orders = orders.filter(delivery_date__date=day_date)
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
