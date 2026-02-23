from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def currency_format(value):
    """Format a number as currency with comma separators"""
    try:
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, float):
            value = Decimal(str(value))
        elif not isinstance(value, Decimal):
            value = Decimal(value)
        
        # Format with 2 decimal places and use comma as thousands separator
        return format(value, ',.2f')
    except (ValueError, TypeError, AttributeError):
        return value

@register.filter
def intcomma_currency(value):
    """Add comma separators to number (alternative name for consistency)"""
    return currency_format(value)

@register.filter
def sum_total(orders):
    """Calculate sum of total_amount from a list of orders"""
    try:
        total = sum(Decimal(str(order.total_amount)) for order in orders if order.total_amount)
        return total
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')


@register.filter
def abs_value(value):
    """Return absolute value of a number"""
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
