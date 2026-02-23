#!/usr/bin/env python
import os
import sys
import django
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

# Create a simple image file
image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x00\x00\x00\x00:~\x9bU\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
image_file = SimpleUploadedFile("test_id.png", image_content, content_type="image/png")

client = Client()

# Prepare form data
data = {
    'username': 'testuser123',
    'email': 'testuser@example.com',
    'phone_number': '09123456789',
    'address': '123 Main Street, Test City',
    'delivery_instructions': 'Leave at door',
    'id_type': 'national_id',
    'id_number': '12345-6789-0',
    'password1': 'SecurePass123',
    'password2': 'SecurePass123',
    'id_document': image_file,
}

# Try to submit the registration form
response = client.post('/register/', data)
print(f"Status Code: {response.status_code}")

if response.status_code == 302:
    print("SUCCESS: Form submitted and redirected")
    print(f"Redirect location: {response.url}")
elif response.status_code == 200:
    print("Form reloaded (has errors)")
    if response.context and 'form' in response.context:
        form = response.context['form']
        if form.errors:
            print(f"Form errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
        if form.non_field_errors():
            print(f"Non-field errors: {form.non_field_errors()}")
else:
    print(f"ERROR: Unexpected status code {response.status_code}")
