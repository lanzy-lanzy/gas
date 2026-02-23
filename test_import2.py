#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

print("Attempting to import views...")
try:
    from core import views
    print("SUCCESS: views imported")
    print(f"Has PendingRegistrationForm: {hasattr(views, 'PendingRegistrationForm')}")
except Exception as e:
    print(f"ERROR importing views: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
