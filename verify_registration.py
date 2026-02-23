#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from core.models import PendingRegistration

# Check if the pending registration was created
pending = PendingRegistration.objects.filter(username='testuser123').first()
if pending:
    print(f"SUCCESS: Pending registration created")
    print(f"  Username: {pending.username}")
    print(f"  Email: {pending.email}")
    print(f"  Status: {pending.status}")
    print(f"  ID Type: {pending.id_type}")
    print(f"  ID Number: {pending.id_number}")
    print(f"  ID Document: {pending.id_document}")
    print(f"  Created: {pending.created_at}")
else:
    print("ERROR: No pending registration found")
