"""
Cashier Reports Views
Daily, Monthly, and Yearly reports for cashier income and inventory tracking
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta, date

from .models import Cashier, Order, LPGProduct


def is_admin(user):
    """Check if user is admin/superuser"""
    return user.is_superuser or (user.is_staff and not hasattr(user, 'cashier_profile'))


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
