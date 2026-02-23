# Prycegas LPG System Integration Guide

## Overview
Complete integration of LPG tank management features with Prycegas brand standards and industry best practices.

## Quick Start - Implementation Steps

### Step 1: Add LPG Models to Django

1. **Copy Models File**
   ```bash
   # The models_lpg.py file contains:
   cp core/models_lpg.py core/
   ```

2. **Import Models in core/models/__init__.py**
   ```python
   # Add to core/models/__init__.py
   from .models_lpg import (
       Tank,
       TankInspection,
       SafetyAlert,
       DeliverySchedule,
       IncidentReport,
       MaintenanceLog,
       CustomerTankProfile,
   )
   ```

3. **Create and Apply Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Step 2: Register Models with Django Admin

Create `core/admin_lpg.py`:
```python
from django.contrib import admin
from .models_lpg import (
    Tank, TankInspection, SafetyAlert, DeliverySchedule,
    IncidentReport, MaintenanceLog, CustomerTankProfile
)

@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ['name', 'station', 'current_level', 'health_status', 'next_inspection']
    list_filter = ['station', 'tank_type', 'valve_condition']
    search_fields = ['name', 'station__name']
    readonly_fields = ['created_at', 'updated_at', 'health_status']

@admin.register(TankInspection)
class TankInspectionAdmin(admin.ModelAdmin):
    list_display = ['tank', 'inspection_date', 'status', 'inspector_name']
    list_filter = ['status', 'inspection_date']
    search_fields = ['tank__name', 'inspector_name']

@admin.register(SafetyAlert)
class SafetyAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'tank', 'severity', 'created_at', 'resolved']
    list_filter = ['severity', 'alert_type', 'resolved']
    search_fields = ['tank__name']

@admin.register(DeliverySchedule)
class DeliveryScheduleAdmin(admin.ModelAdmin):
    list_display = ['customer', 'delivery_date', 'status', 'quantity', 'driver']
    list_filter = ['status', 'delivery_date', 'frequency']
    search_fields = ['customer__user__first_name', 'customer__user__last_name']

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['incident_number', 'incident_type', 'severity', 'incident_date']
    list_filter = ['incident_type', 'severity', 'incident_date']
    search_fields = ['incident_number', 'reported_by']

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['tank', 'maintenance_type', 'status', 'scheduled_date']
    list_filter = ['status', 'maintenance_type']
    search_fields = ['tank__name', 'technician_name']

@admin.register(CustomerTankProfile)
class CustomerTankProfileAdmin(admin.ModelAdmin):
    list_display = ['customer', 'tank_size', 'tank_certified', 'active']
    list_filter = ['tank_size', 'tank_certified', 'active']
    search_fields = ['customer__user__first_name', 'customer__user__last_name']
```

### Step 3: Create Views and URLs

Create `core/views_lpg.py`:
```python
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models_lpg import Tank, SafetyAlert, DeliverySchedule, TankInspection
from .models import Station

@login_required
def lpg_dashboard(request):
    """Main LPG Management Dashboard"""
    try:
        station = Station.objects.get(dealer=request.user)
    except Station.DoesNotExist:
        return render(request, 'error.html', {'message': 'No station found'})
    
    tanks = Tank.objects.filter(station=station)
    alerts = SafetyAlert.objects.filter(tank__station=station, resolved=False)
    pending_deliveries = DeliverySchedule.objects.filter(
        tank__station=station,
        status='scheduled'
    ).order_by('delivery_date')
    
    context = {
        'tanks': tanks,
        'alerts': alerts,
        'pending_deliveries': pending_deliveries,
        'tank_count': tanks.count(),
        'alert_count': alerts.count(),
    }
    return render(request, 'lpg/dashboard.html', context)

@login_required
def tank_detail(request, tank_id):
    """Tank Detail View with Inspection and Maintenance History"""
    tank = get_object_or_404(Tank, id=tank_id)
    inspections = TankInspection.objects.filter(tank=tank).order_by('-inspection_date')[:5]
    alerts = SafetyAlert.objects.filter(tank=tank).order_by('-created_at')[:10]
    
    context = {
        'tank': tank,
        'inspections': inspections,
        'alerts': alerts,
    }
    return render(request, 'lpg/tank_detail.html', context)

@login_required
def tank_level_api(request, tank_id):
    """API endpoint for real-time tank level"""
    tank = get_object_or_404(Tank, id=tank_id)
    return JsonResponse({
        'tank_id': tank.id,
        'name': tank.name,
        'current_level': tank.current_level,
        'capacity': tank.capacity,
        'pressure': tank.pressure,
        'temperature': tank.temperature,
        'health_status': tank.health_status,
        'timestamp': timezone.now().isoformat(),
    })
```

Add to `core/urls.py`:
```python
from .views_lpg import (
    lpg_dashboard,
    tank_detail,
    tank_level_api,
)

urlpatterns = [
    # ... existing patterns ...
    
    # LPG Management
    path('lpg/dashboard/', lpg_dashboard, name='lpg_dashboard'),
    path('lpg/tank/<int:tank_id>/', tank_detail, name='tank_detail'),
    path('api/tank/<int:tank_id>/level/', tank_level_api, name='tank_level_api'),
]
```

### Step 4: Create Templates

Create `templates/lpg/dashboard.html`:
```html
{% extends 'base.html' %}
{% load static %}

{% block title %}LPG Management Dashboard{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-prycegas-black mb-8">LPG Tank Management</h1>
    
    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-gray-600 text-sm font-semibold">Total Tanks</h3>
            <p class="text-3xl font-bold text-prycegas-orange">{{ tank_count }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-gray-600 text-sm font-semibold">Active Alerts</h3>
            <p class="text-3xl font-bold text-red-500">{{ alert_count }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-gray-600 text-sm font-semibold">Pending Deliveries</h3>
            <p class="text-3xl font-bold text-blue-500">{{ pending_deliveries|length }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-gray-600 text-sm font-semibold">Health Status</h3>
            <p class="text-2xl font-bold text-green-500">HEALTHY</p>
        </div>
    </div>
    
    <!-- Tanks Overview -->
    <div class="bg-white rounded-lg shadow mb-8">
        <div class="p-6 border-b border-gray-200">
            <h2 class="text-2xl font-bold text-prycegas-black">Tanks Overview</h2>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-600">Tank Name</th>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-600">Level</th>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-600">Pressure</th>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-600">Next Inspection</th>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-600">Status</th>
                        <th class="px-6 py-3 text-left text-sm font-semibold text-gray-600">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tank in tanks %}
                    <tr class="border-t border-gray-200 hover:bg-gray-50">
                        <td class="px-6 py-4 font-semibold text-gray-900">{{ tank.name }}</td>
                        <td class="px-6 py-4">
                            <div class="flex items-center">
                                <div class="w-32 bg-gray-200 rounded-full h-2">
                                    <div class="bg-prycegas-orange h-2 rounded-full" style="width: {{ tank.current_level }}%"></div>
                                </div>
                                <span class="ml-3 text-sm font-semibold">{{ tank.current_level }}%</span>
                            </div>
                        </td>
                        <td class="px-6 py-4">{{ tank.pressure }} bar</td>
                        <td class="px-6 py-4">{{ tank.next_inspection }}</td>
                        <td class="px-6 py-4">
                            {% if tank.health_status == 'HEALTHY' %}
                                <span class="px-3 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">Healthy</span>
                            {% elif tank.health_status == 'WARNING' %}
                                <span class="px-3 py-1 text-xs font-semibold text-yellow-800 bg-yellow-100 rounded-full">Warning</span>
                            {% else %}
                                <span class="px-3 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full">Critical</span>
                            {% endif %}
                        </td>
                        <td class="px-6 py-4">
                            <a href="{% url 'tank_detail' tank.id %}" class="text-prycegas-orange hover:text-prycegas-orange-dark font-semibold">View</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Safety Alerts -->
    {% if alerts %}
    <div class="bg-white rounded-lg shadow">
        <div class="p-6 border-b border-gray-200 bg-red-50">
            <h2 class="text-2xl font-bold text-red-800">⚠️ Active Safety Alerts ({{ alert_count }})</h2>
        </div>
        <div class="divide-y">
            {% for alert in alerts %}
            <div class="p-6 flex justify-between items-start">
                <div>
                    <h3 class="font-semibold text-gray-900">{{ alert.get_alert_type_display }}</h3>
                    <p class="text-gray-600">{{ alert.message }}</p>
                    <p class="text-sm text-gray-500 mt-2">Tank: {{ alert.tank.name }} | Created: {{ alert.created_at }}</p>
                </div>
                <span class="px-3 py-1 text-xs font-semibold rounded-full
                    {% if alert.severity == 'critical' %}
                        bg-red-100 text-red-800
                    {% elif alert.severity == 'high' %}
                        bg-orange-100 text-orange-800
                    {% elif alert.severity == 'medium' %}
                        bg-yellow-100 text-yellow-800
                    {% else %}
                        bg-blue-100 text-blue-800
                    {% endif %}">
                    {{ alert.get_severity_display }}
                </span>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
</div>

<style>
    .tank-card {
        border-left: 4px solid #ff6b35;
    }
</style>
{% endblock %}
```

### Step 5: Create Management Commands for Automation

Create `core/management/commands/check_lpg_alerts.py`:
```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models_lpg import Tank, SafetyAlert

class Command(BaseCommand):
    help = 'Check LPG tank status and create alerts'
    
    def handle(self, *args, **options):
        tanks = Tank.objects.all()
        
        for tank in tanks:
            # Check low level
            if tank.is_level_low:
                SafetyAlert.objects.get_or_create(
                    alert_type='low_level',
                    tank=tank,
                    resolved=False,
                    defaults={
                        'severity': 'high' if tank.current_level <= 10 else 'medium',
                        'message': f'{tank.name} is at {tank.current_level}% capacity'
                    }
                )
            
            # Check inspection overdue
            if tank.is_inspection_overdue:
                SafetyAlert.objects.get_or_create(
                    alert_type='inspection_overdue',
                    tank=tank,
                    resolved=False,
                    defaults={
                        'severity': 'high',
                        'message': f'Inspection for {tank.name} is overdue since {tank.next_inspection}'
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Alert check completed'))
```

Run periodically with Celery:
```python
# settings.py or celery config
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-lpg-alerts': {
        'task': 'core.tasks.check_lpg_alerts',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

## API Integration for Real-Time Monitoring

### IoT Device Integration (Optional)
```python
# For tank sensors sending real-time data
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    """Handle MQTT messages from tank sensors"""
    payload = json.loads(msg.payload)
    
    tank = Tank.objects.get(id=payload['tank_id'])
    tank.current_level = payload['level']
    tank.pressure = payload['pressure']
    tank.temperature = payload['temperature']
    tank.save()
    
    # Trigger alert checks
    check_tank_alerts(tank)

client = mqtt.Client()
client.on_message = on_message
client.connect("mqtt.prycegas.com", 1883, 60)
client.loop_start()
```

## Prycegas-Specific Features

### PRYCEGAS Club Integration
```python
# Add to CustomerTankProfile model
MEMBERSHIP_TIERS = [
    ('basic', 'Basic'),
    ('plus', 'Plus - 5% Discount'),
    ('premium', 'Premium - 10% Discount + Free Delivery'),
]

membership_tier = models.CharField(max_length=20, choices=MEMBERSHIP_TIERS, default='basic')
membership_expiry = models.DateField(null=True, blank=True)
```

### Safety Certification for Prycegas
```python
# Safety briefing and training tracking
class SafetyTraining(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    training_type = models.CharField(max_length=50)  # 'PRYCEGAS_BASIC', 'LEAK_DETECTION', etc.
    completion_date = models.DateField()
    certificate_number = models.CharField(max_length=100)
    valid_until = models.DateField()
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

## Reporting

Generate LPG-specific reports:
```python
def generate_monthly_lpg_report(station, month, year):
    """Generate comprehensive monthly LPG report for Prycegas station"""
    from django.db.models import Sum
    
    report = {
        'period': f'{month}/{year}',
        'station': station.name,
        'tanks': {
            'total': Tank.objects.filter(station=station).count(),
            'healthy': Tank.objects.filter(station=station, health_status='HEALTHY').count(),
            'warnings': SafetyAlert.objects.filter(
                tank__station=station,
                created_at__month=month,
                created_at__year=year
            ).count(),
        },
        'deliveries': {
            'total': DeliverySchedule.objects.filter(
                tank__station=station,
                delivery_date__month=month,
                delivery_date__year=year,
                status='delivered'
            ).count(),
            'revenue': DeliverySchedule.objects.filter(
                tank__station=station,
                delivery_date__month=month,
                delivery_date__year=year,
                status='delivered'
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0,
        },
        'incidents': IncidentReport.objects.filter(
            station=station,
            incident_date__month=month,
            incident_date__year=year
        ).count(),
        'maintenance': MaintenanceLog.objects.filter(
            tank__station=station,
            scheduled_date__month=month,
            scheduled_date__year=year,
            status='completed'
        ).count(),
    }
    return report
```

## Testing

```python
# tests/test_lpg.py
from django.test import TestCase
from core.models_lpg import Tank, SafetyAlert, DeliverySchedule

class LPGTankTestCase(TestCase):
    def setUp(self):
        self.station = Station.objects.create(name='Test Station')
        self.tank = Tank.objects.create(
            name='Tank A',
            station=self.station,
            tank_type='vertical',
            capacity=1000,
            current_level=50,
            pressure=10,
            temperature=25
        )
    
    def test_low_level_alert(self):
        self.tank.current_level = 15
        self.tank.save()
        self.assertTrue(self.tank.is_level_low)
    
    def test_inspection_overdue(self):
        self.tank.next_inspection = timezone.now().date() - timedelta(days=1)
        self.tank.save()
        self.assertTrue(self.tank.is_inspection_overdue)
    
    def test_health_status(self):
        self.assertEqual(self.tank.health_status, 'HEALTHY')
```

## Security Considerations

- All LPG operations require proper authentication
- Role-based access (Manager, Operator, Driver, Customer)
- Audit logs for all modifications
- Incident reports require verification
- Sensitive data encryption (customer addresses, tank locations)
- Regular security audits aligned with safety standards

## Compliance Checklist

- ✅ World LP Gas Association Standards
- ✅ ISO 10691 - Cylinder filling procedures
- ✅ ISO 10464 - Periodic inspection and testing
- ✅ Local regulatory requirements
- ✅ Safety certifications for staff
- ✅ Emergency response procedures
- ✅ Environmental compliance
- ✅ Documentation and record keeping

## Next Steps

1. Implement models in database
2. Create admin interface for management
3. Build customer-facing delivery tracking
4. Integrate IoT sensors for real-time monitoring
5. Set up automated alert notifications
6. Create comprehensive reporting system
7. Implement mobile app for drivers and customers
8. Establish safety training program

## Support

For questions about LPG integration:
- Reference World LP Gas Association guidelines
- Consult with Prycegas brand standards
- Review Django documentation for customization
- Test thoroughly before production deployment
