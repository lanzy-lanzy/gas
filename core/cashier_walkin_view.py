"""
Walk-in Customer Order Processing for Cashiers
Allows cashiers to process orders for walk-in customers without requiring customer accounts
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json
import uuid

from .models import Order, LPGProduct, CashierTransaction
from .cashier_views import is_cashier


@login_required
@user_passes_test(is_cashier, login_url='core:login')
def cashier_walkin_order(request):
    """
    Process walk-in customer orders
    Cashiers can create orders for customers who walk into the store
    Similar to customer place_order but for cashier use
    """
    if not hasattr(request.user, 'cashier_profile'):
        messages.error(request, 'You must be a cashier to access this page.')
        return redirect('core:login')
    
    cashier = request.user.cashier_profile
    
    if request.method == 'POST':
        try:
            # Get cart items from the request
            cart_items_json = request.POST.get('cart_items', '[]')
            cart_items = json.loads(cart_items_json)
            
            if not cart_items:
                raise ValueError('No items in cart')
            
            # Get customer details
            customer_name = request.POST.get('customer_name', '').strip()
            customer_phone = request.POST.get('customer_phone', '').strip()
            delivery_type = request.POST.get('delivery_type', 'pickup')
            delivery_address = request.POST.get('delivery_address', '').strip()
            notes = request.POST.get('notes', '').strip()
            payment_method = request.POST.get('payment_method', 'cash')
            
            # Validate required fields
            if not customer_name:
                raise ValueError('Customer name is required')
            if not customer_phone:
                raise ValueError('Customer phone number is required')
            if delivery_type == 'delivery' and not delivery_address:
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
                        customer=None,
                        product=product,
                        quantity=quantity,
                        delivery_type=delivery_type,
                        delivery_address=delivery_address if delivery_type == 'delivery' else 'Walk-in Pickup',
                        notes=f"Walk-in Customer: {customer_name} | Phone: {customer_phone}" + (f" | {notes}" if notes else ""),
                        total_amount=order_total,
                        status='delivered',
                        processed_by=cashier
                    )
                    order.save()
                    
                    product.current_stock -= quantity
                    product.save()
                    
                    CashierTransaction.objects.create(
                        cashier=cashier,
                        order=order,
                        transaction_type='order',
                        amount=order_total,
                        payment_method=payment_method,
                        customer=None,
                        notes=f"Walk-in: {customer_name}"
                    )
                    
                    orders.append(order)
                
                if len(orders) == 1:
                    messages.success(
                        request,
                        f'Walk-in order #{orders[0].id} created successfully for {customer_name}! Total: ₱{total_amount:.2f}'
                    )
                else:
                    messages.success(
                        request,
                        f'Batch walk-in order created for {customer_name}! {len(orders)} items (Batch #{batch_id})! Total: ₱{total_amount:.2f}'
                    )
                
                # Return JSON response for AJAX requests
                if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'{len(orders)} order(s) placed successfully!',
                        'order_ids': [o.id for o in orders],
                        'total_amount': float(total_amount),
                        'redirect': '/cashier/orders/'
                    })
                
                return redirect('core:cashier_order_list')
                
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
            print(f'Walk-in order error: {error_msg}')
            is_ajax = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
    
    # GET request - show the form
    products = LPGProduct.objects.filter(is_active=True).order_by('name', 'size')
    
    # Define payment methods
    payment_methods = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
    ]
    
    context = {
        'products': products,
        'cashier': cashier,
        'payment_methods': payment_methods,
    }
    return render(request, 'dealer/cashier_walkin_order.html', context)
