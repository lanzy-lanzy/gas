import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
django.setup()

# Now run migration
from django.core.management import call_command
call_command('migrate', 'core', '0010_pendingregistration_password')
print("Migration applied successfully!")
