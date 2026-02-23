#!/usr/bin/env python
"""
Script to add currency formatting to all templates
"""
import re
from pathlib import Path

template_files = [
    'templates/customer/place_order.html',
    'templates/customer/order_rows_partial.html',
    'templates/customer/stock_info.html',
    'templates/cashier/personal_reports_monthly.html',
    'templates/cashier/personal_reports_daily.html',
    'templates/dealer/cashier_dashboard.html',
    'templates/dealer/cashier_order_list.html',
    'templates/dealer/dashboard_stats_partial.html',
    'templates/dealer/order_detail_modal.html',
    'templates/dealer/order_detail.html',
    'templates/dealer/order_rows_partial.html',
    'templates/dealer/order_row_partial.html',
    'templates/dealer/recent_activity_partial.html',
    'templates/dealer/delivery_log.html',
    'templates/dealer/delivery_success_partial.html',
    'templates/dealer/inventory.html',
    'templates/dealer/inventory_dashboard_partial.html',
    'templates/dealer/inventory_reports.html',
    'templates/dealer/reports_dashboard.html',
    'templates/dealer/sales_report.html',
    'templates/dealer/stock_movements_partial.html',
    'templates/dealer/stock_report.html',
    'templates/admin/cashier_daily_income.html',
    'templates/admin/cashier_inventory_impact.html',
    'templates/admin/cashier_performance.html',
    'templates/admin/cashier_reports.html',
    'templates/admin/cashier_transactions.html',
]

def update_template(filepath):
    """Update a template file with currency formatting"""
    path = Path(filepath)
    
    if not path.exists():
        print(f"SKIP (not found): {filepath}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it already has currency_filters loaded
    if 'currency_filters' in content:
        print(f"SKIP (already loaded): {filepath}")
        return False
    
    # Check if it has floatformat (the pattern we need to update)
    if 'floatformat' not in content:
        print(f"SKIP (no floatformat): {filepath}")
        return False
    
    original_content = content
    
    # Add load tag after the extends or at the top
    if content.startswith('{% extends'):
        # Find the end of the extends line
        extends_end = content.find('\n', content.find('{% extends'))
        if extends_end > -1:
            # Check if next line is block
            rest = content[extends_end+1:]
            if rest.startswith('\n') or rest.startswith('{% block'):
                insert_pos = extends_end + 1
                content = content[:insert_pos] + '\n{% load currency_filters %}' + content[insert_pos:]
            else:
                content = content[:extends_end+1] + '\n{% load currency_filters %}' + content[extends_end+1:]
    elif '{% load' not in content:
        content = '{% load currency_filters %}\n' + content
    
    # Replace ₱{{ ... |floatformat:2 }} with ₱{{ ... |floatformat:2|currency_format }}
    # Be careful to only add if not already there
    pattern = r'(₱\{\{[^}]*\|floatformat:\d+)(\}\})'
    def replace_currency(match):
        if 'currency_format' in match.group(0):
            return match.group(0)
        return match.group(1) + '|currency_format' + match.group(2)
    
    content = re.sub(pattern, replace_currency, content)
    
    # Also handle cases with variables not starting with ₱
    pattern2 = r'(\{\{[^}]*)\|floatformat:(\d+)(\}\})'
    def replace_floatformat(match):
        if 'currency_format' in match.group(0):
            return match.group(0)
        return match.group(1) + '|floatformat:' + match.group(2) + '|currency_format' + match.group(3)
    
    content = re.sub(pattern2, replace_floatformat, content)
    
    if content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"UPDATED: {filepath}")
        return True
    else:
        print(f"NO CHANGES: {filepath}")
        return False

if __name__ == '__main__':
    updated_count = 0
    for template_file in template_files:
        if update_template(template_file):
            updated_count += 1
    
    print(f"\n✓ Total updated: {updated_count}/{len(template_files)}")
