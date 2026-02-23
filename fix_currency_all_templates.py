#!/usr/bin/env python
"""
Fix all currency formatting in templates
"""
import re
import os
from pathlib import Path

def process_file(filepath):
    """Process a single template file"""
    path = Path(filepath)
    if not path.exists():
        return False, "not found"
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Step 1: Add load tag if not present
    if 'currency_filters' not in content and 'floatformat' in content:
        if content.startswith('{% extends'):
            # Find end of extends line
            end = content.find('\n', content.find('{% extends'))
            if end > 0:
                content = content[:end+1] + '{% load currency_filters %}\n' + content[end+1:]
        elif content.startswith('<!-- '):
            # Comment at top - add after it and initial comments
            idx = 0
            while idx < len(content) and content[idx:idx+4] == '<!-- ':
                next_close = content.find('-->\n', idx)
                if next_close < 0:
                    break
                idx = next_close + 4
            content = content[:idx] + '{% load currency_filters %}\n' + content[idx:]
        else:
            content = '{% load currency_filters %}\n' + content
    
    # Step 2: Add |currency_format to all floatformat filters
    # Pattern for ₱{{ ... |floatformat:N }}
    pattern = r'(₱\{\{[^}]*?)\|floatformat:(\d+)(\}\})'
    
    def add_currency_format(m):
        if 'currency_format' in m.group(0):
            return m.group(0)
        return m.group(1) + '|floatformat:' + m.group(2) + '|currency_format' + m.group(3)
    
    content = re.sub(pattern, add_currency_format, content)
    
    # Also handle non-₱ currency values with floatformat
    pattern2 = r'(\{\{[^}]*?)\|floatformat:(\d+)(\}\})'
    def add_currency_format2(m):
        # Only add if it looks like it's a monetary value and not already has currency_format
        text = m.group(0)
        if 'currency_format' in text or 'profit' in text.lower() or '%' in text:
            return text
        if any(money_term in text for money_term in ['amount', 'total', 'cost', 'revenue', 'price', 'income', 'value', 'spent']):
            return m.group(1) + '|floatformat:' + m.group(2) + '|currency_format' + m.group(3)
        return text
    
    content = re.sub(pattern2, add_currency_format2, content)
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "updated"
    return False, "no changes"

# Process all HTML templates
template_dir = Path('templates')
updated_count = 0
total_count = 0

for html_file in template_dir.rglob('*.html'):
    if 'floatformat' in html_file.read_text():
        total_count += 1
        success, msg = process_file(str(html_file))
        if success:
            updated_count += 1
            print(f"✓ {html_file.relative_to(template_dir)}")
        else:
            print(f"- {html_file.relative_to(template_dir)} ({msg})")

print(f"\n✓ Updated {updated_count}/{total_count} files")
