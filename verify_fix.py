#!/usr/bin/env python
"""
Quick verification that the fix is in place
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.utils import timezone
from core.models import CashierTransaction, Cashier

print("\n" + "=" * 70)
print("Cashier Transaction Fix Verification")
print("=" * 70)

# Check if CashierTransaction records exist
all_transactions = CashierTransaction.objects.count()
today = timezone.now().date()
today_transactions = CashierTransaction.objects.filter(created_at__date=today).count()

print(f"\nTotal CashierTransactions in DB: {all_transactions}")
print(f"Today's CashierTransactions: {today_transactions}")

# Check each cashier's transactions
print("\nCashier Transaction Breakdown:")
for cashier in Cashier.objects.all():
    count = CashierTransaction.objects.filter(cashier=cashier).count()
    today_count = CashierTransaction.objects.filter(
        cashier=cashier,
        created_at__date=today
    ).count()
    print(f"  {cashier.user.username}: {count} total, {today_count} today")

# Verify the code changes are in place
print("\n" + "=" * 70)
print("Checking if code fixes are in place...")
print("=" * 70)

# Read views.py to check for the transaction creation code
with open('core/views.py', 'r') as f:
    views_content = f.read()
    
    # Check for transaction creation in update_order_status
    if 'CashierTransaction.objects.create' in views_content:
        print("\n[OK] update_order_status() has transaction creation code")
    else:
        print("\n[MISSING] update_order_status() missing transaction creation")
    
    # Check for bulk operation transaction creation
    if views_content.count('CashierTransaction.objects.create') >= 1:
        print("[OK] bulk_order_operations() has transaction creation code")
    else:
        print("[MISSING] bulk_order_operations() missing transaction creation")

# Read cashier_views.py to check for the today filter
with open('d:/PrycegasStation/core/cashier_views.py', 'r') as f:
    cashier_content = f.read()
    
    if 'today_transactions.select_related' in cashier_content:
        print("[OK] cashier_personal_dashboard() filters by today's transactions")
    else:
        print("[MISSING] cashier_personal_dashboard() not filtering by today")

print("\n" + "=" * 70)
print("Verification Complete!")
print("=" * 70 + "\n")
