#!/usr/bin/env python
"""
Test script for currency_filters template tag
Run with: python manage.py shell < test_currency_filter.py
Or: python test_currency_filter.py
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

# Import the filters
from core.templatetags.currency_filters import currency_format, sum_total

print("=" * 60)
print("Testing Currency Filters")
print("=" * 60)

# Test 1: Basic currency_format
print("\n1. Testing currency_format filter:")
test_values = [
    100,
    1000,
    10000,
    100000,
    1234.56,
    Decimal('1234.56'),
    "1234.56",
    0,
]

for val in test_values:
    result = currency_format(val)
    print(f"   {val:>20} → {result}")

# Test 2: Error handling
print("\n2. Testing error handling:")
error_values = [
    None,
    "invalid",
    [],
    {},
]

for val in error_values:
    result = currency_format(val)
    print(f"   {str(val):>20} → {result} (returned as-is)")

# Test 3: Testing with template
print("\n3. Testing with Django Template:")
from django.template import Template, Context

template_str = """
{% load currency_filters %}
Amount: ₱{{ amount|floatformat:2|currency_format }}
"""

try:
    template = Template(template_str)
    context = Context({'amount': 1234.56})
    output = template.render(context)
    print(f"   Template result: {output.strip()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: sum_total filter
print("\n4. Testing sum_total filter:")
try:
    # Create mock order objects
    class MockOrder:
        def __init__(self, amount):
            self.total_amount = Decimal(str(amount))
    
    orders = [
        MockOrder(100),
        MockOrder(200),
        MockOrder(300),
    ]
    
    total = sum_total(orders)
    formatted = currency_format(total)
    print(f"   Orders: [100, 200, 300]")
    print(f"   Sum: {total}")
    print(f"   Formatted: ₱{currency_format(total)}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
print("\nIf you see formatted amounts (with commas), the filter is working!")
print("If you see errors, check that Django is properly configured.")
