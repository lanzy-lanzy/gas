#!/usr/bin/env python
"""
Script to automatically add |intcomma filter to all price displays in templates.
Adds intcomma to lines that have |currency_format filter.
"""

import os
import re
from pathlib import Path

def apply_intcomma_to_templates():
    """Add |intcomma filter to all price displays."""
    templates_dir = Path(__file__).parent / 'templates'
    
    if not templates_dir.exists():
        print(f"Error: Templates directory not found at {templates_dir}")
        return
    
    updated_count = 0
    file_count = 0
    
    # Walk through all HTML files in templates
    for html_file in templates_dir.rglob('*.html'):
        file_count += 1
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Find all lines with |currency_format and add |intcomma if not already present
            # Pattern: |currency_format }} or |currency_format }}&...
            pattern = r'\|currency_format(\s*[}\|])'
            replacement = r'|currency_format|intcomma\1'
            
            # Check if intcomma is already present to avoid duplicates
            if '|currency_format|intcomma' not in content:
                content = re.sub(pattern, replacement, content)
            
            # Write back if changed
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_count += 1
                print(f"[UPDATED] {html_file.relative_to(templates_dir)}")
            
        except Exception as e:
            print(f"[ERROR] processing {html_file}: {e}")
    
    print("")
    print("=" * 60)
    print("Summary:")
    print(f"  Total HTML files scanned: {file_count}")
    print(f"  Files updated: {updated_count}")
    print("=" * 60)

if __name__ == '__main__':
    apply_intcomma_to_templates()
