#!/usr/bin/env python
"""
Script to add {% load humanize %} to all templates that use intcomma filter.
"""

import re
from pathlib import Path

def add_humanize_load_tag():
    """Add {% load humanize %} to templates that use intcomma."""
    templates_dir = Path(__file__).parent / 'templates'
    
    if not templates_dir.exists():
        print(f"Error: Templates directory not found at {templates_dir}")
        return
    
    updated_count = 0
    
    # Find all templates with intcomma
    for html_file in templates_dir.rglob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Only process files that use intcomma
            if 'intcomma' not in content:
                continue
            
            # Check if humanize is already loaded
            if '{% load humanize' in content:
                continue
            
            # Find the first {% load or {% block or the start
            # Add load humanize after first {% load if exists, or at the very top
            
            load_pattern = r'^(\s*)({%\s*load\s+[^%]*%})'
            match = re.search(load_pattern, content, re.MULTILINE)
            
            if match:
                # Insert after existing load tag
                end_pos = match.end()
                # Find the end of the line
                newline_pos = content.find('\n', end_pos)
                if newline_pos != -1:
                    insertion_point = newline_pos + 1
                else:
                    insertion_point = end_pos
                content = content[:insertion_point] + '{% load humanize %}\n' + content[insertion_point:]
            else:
                # Insert at the very beginning
                content = '{% load humanize %}\n' + content
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            updated_count += 1
            rel_path = html_file.relative_to(templates_dir)
            print(f"[UPDATED] {rel_path}")
            
        except Exception as e:
            print(f"[ERROR] {html_file}: {e}")
    
    print("")
    print("=" * 60)
    print(f"Templates updated: {updated_count}")
    print("=" * 60)

if __name__ == '__main__':
    add_humanize_load_tag()
