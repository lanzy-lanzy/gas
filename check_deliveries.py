import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrycegasStation.settings')
django.setup()

from core.models import DeliveryLog

deliveries = DeliveryLog.objects.all().order_by('delivery_date')
print(f"Total deliveries: {DeliveryLog.objects.count()}\n")
for d in deliveries:
    print(f"{d.delivery_date.strftime('%m/%d/%Y')} - {d.supplier_name}: {d.quantity_received} units")

print(f"\nToday's date: {timezone.now().strftime('%m/%d/%Y')}")
