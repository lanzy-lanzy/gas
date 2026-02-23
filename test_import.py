#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

try:
    from core.forms import PendingRegistrationForm
    print("SUCCESS: PendingRegistrationForm imported successfully")
    print(f"Form class: {PendingRegistrationForm}")
except ImportError as e:
    print(f"ERROR: Failed to import PendingRegistrationForm: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
