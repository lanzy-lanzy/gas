#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.test import Client

client = Client()
response = client.get('/register/')
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS: Register page loaded")
    if response.context:
        if 'form' in response.context:
            print(f"Form type: {type(response.context['form'])}")
        else:
            print("WARNING: No form in context")
    else:
        print("WARNING: No context")
else:
    print(f"ERROR: Unexpected status code {response.status_code}")
