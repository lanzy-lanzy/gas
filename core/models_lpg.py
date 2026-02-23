"""
LPG Tank Management Models
Based on World LP Gas Association Standards and Best Practices
Integrated with Prycegas brand standards
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from core.models import User, Station, Customer


class Tank(models.Model):
    """Main LPG Storage Tank Model"""
    
    TANK_TYPES = [
        ('vertical', 'Vertical Tank'),
        ('horizontal', 'Horizontal Tank'),
    ]
    
    VALVE_CONDITIONS = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair - Requires Attention'),
        ('poor', 'Poor - Maintenance Required'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, help_text="Tank identifier (e.g., Tank A, Tank B)")
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='lpg_tanks')
    tank_type = models.CharField(max_length=20, choices=TANK_TYPES)
    
    # Specifications
    capacity = models.FloatField(validators=[MinValueValidator(0)], help_text="Capacity in liters")
    design_pressure = models.FloatField(validators=[MinValueValidator(0)], help_text="Design pressure in bar")
    installation_date = models.DateField()
    
    # Current Status
    current_level = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Current fill percentage (0-100%)"
    )
    pressure = models.FloatField(validators=[MinValueValidator(0)], help_text="Current pressure in bar")
    temperature = models.FloatField(help_text="Current temperature in Celsius")
    valve_condition = models.CharField(max_length=20, choices=VALVE_CONDITIONS, default='good')
    
    # Inspection & Compliance
    last_inspection = models.DateField(help_text="Date of last inspection")
    next_inspection = models.DateField(help_text="Scheduled date for next inspection")
    last_maintenance = models.DateField(null=True, blank=True)
    
    # Safety & Monitoring
    has_safety_valve = models.BooleanField(default=True)
    has_leak_detector = models.BooleanField(default=False)
    is_monitored = models.BooleanField(default=False, help_text="Real-time monitoring enabled")
    low_level_threshold = models.FloatField(default=20, help_text="Alert when level drops below this %")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['station', 'name']
        verbose_name = 'LPG Tank'
        verbose_name_plural = 'LPG Tanks'
    
    def __str__(self):
        return f"{self.station.name} - {self.name}"
    
    @property
    def is_inspection_overdue(self):
        """Check if inspection is overdue"""
        return timezone.now().date() > self.next_inspection
    
    @property
    def is_level_low(self):
        """Check if tank level is below threshold"""
        return self.current_level <= self.low_level_threshold
    
    @property
    def capacity_remaining(self):
        """Calculate remaining capacity in liters"""
        return (self.current_level / 100) * self.capacity
    
    @property
    def health_status(self):
        """Overall tank health status"""
        if self.is_inspection_overdue:
            return 'CRITICAL'
        if self.valve_condition == 'poor':
            return 'WARNING'
        if self.current_level <= 10:
            return 'CRITICAL'
        if self.is_level_low:
            return 'WARNING'
        return 'HEALTHY'


class TankInspection(models.Model):
    """Tank Inspection Records - Safety Compliance"""
    
    INSPECTION_STATUS = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('conditional', 'Conditional Pass - With Notes'),
    ]
    
    tank = models.ForeignKey(Tank, on_delete=models.CASCADE, related_name='inspections')
    inspection_date = models.DateField()
    inspector_name = models.CharField(max_length=100)
    inspector_email = models.EmailField(blank=True)
    
    # Inspection Details
    pressure_test = models.BooleanField(default=False)
    pressure_test_value = models.FloatField(null=True, blank=True, help_text="Pressure in bar")
    leak_test = models.BooleanField(default=False)
    surface_inspection = models.BooleanField(default=False)
    valve_inspection = models.BooleanField(default=False)
    safety_relief_test = models.BooleanField(default=False)
    
    # Results
    status = models.CharField(max_length=20, choices=INSPECTION_STATUS)
    findings = models.TextField(help_text="Detailed inspection findings")
    recommendations = models.TextField(blank=True)
    
    # Follow-up
    repair_required = models.BooleanField(default=False)
    repair_deadline = models.DateField(null=True, blank=True)
    
    # Scheduling
    next_inspection = models.DateField()
    scheduled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-inspection_date']
        verbose_name = 'Tank Inspection'
        verbose_name_plural = 'Tank Inspections'
    
    def __str__(self):
        return f"{self.tank.name} - {self.inspection_date} ({self.status})"


class SafetyAlert(models.Model):
    """Safety and Operational Alerts"""
    
    ALERT_TYPES = [
        ('low_level', 'Low Tank Level'),
        ('high_pressure', 'High Pressure Warning'),
        ('low_pressure', 'Low Pressure'),
        ('leak_detected', 'Leak Detected'),
        ('temperature_high', 'High Temperature'),
        ('maintenance_due', 'Maintenance Due'),
        ('inspection_overdue', 'Inspection Overdue'),
        ('valve_issue', 'Valve Issue'),
    ]
    
    SEVERITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Alert Information
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    tank = models.ForeignKey(Tank, on_delete=models.CASCADE, related_name='safety_alerts')
    severity = models.CharField(max_length=10, choices=SEVERITY)
    message = models.TextField()
    
    # Status
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Notification
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    notified_to = models.CharField(max_length=255, blank=True, help_text="Email addresses notified")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Safety Alert'
        verbose_name_plural = 'Safety Alerts'
    
    def __str__(self):
        return f"{self.alert_type} - {self.tank.name} ({self.severity})"


class DeliverySchedule(models.Model):
    """Customer Delivery Management"""
    
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('on_demand', 'On Demand'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]
    
    # Delivery Information
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='lpg_deliveries')
    tank = models.ForeignKey(Tank, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_date = models.DateField()
    delivery_time = models.TimeField(null=True, blank=True)
    
    # Delivery Details
    quantity = models.FloatField(validators=[MinValueValidator(0)], help_text="Quantity in liters")
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='on_demand')
    next_scheduled_delivery = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Safety Compliance
    customer_tank_inspected = models.BooleanField(default=False)
    delivery_notes = models.TextField(blank=True)
    signature = models.ImageField(upload_to='delivery_signatures/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['delivery_date']
        verbose_name = 'Delivery Schedule'
        verbose_name_plural = 'Delivery Schedules'
    
    def __str__(self):
        return f"{self.customer.user.get_full_name()} - {self.delivery_date}"


class IncidentReport(models.Model):
    """Safety Incident Documentation"""
    
    INCIDENT_TYPES = [
        ('leak', 'Leak'),
        ('fire', 'Fire/Explosion'),
        ('pressure_relief', 'Pressure Relief Activation'),
        ('valve_failure', 'Valve Failure'),
        ('customer_misuse', 'Customer Misuse'),
        ('equipment_failure', 'Equipment Failure'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ]
    
    # Incident Information
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    tank = models.ForeignKey(Tank, on_delete=models.SET_NULL, null=True, blank=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    incident_date = models.DateTimeField()
    
    # Details
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    injuries = models.TextField(blank=True, help_text="Description of any injuries")
    property_damage = models.TextField(blank=True)
    
    # Response
    response_action = models.TextField(help_text="Immediate action taken")
    emergency_services_called = models.BooleanField(default=False)
    responders = models.CharField(max_length=255, blank=True)
    
    # Documentation
    reported_by = models.CharField(max_length=100)
    reported_by_email = models.EmailField()
    witness_names = models.TextField(blank=True)
    photos = models.ImageField(upload_to='incident_photos/', null=True, blank=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    regulatory_report_submitted = models.BooleanField(default=False)
    
    # Metadata
    incident_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-incident_date']
        verbose_name = 'Incident Report'
        verbose_name_plural = 'Incident Reports'
    
    def __str__(self):
        return f"INC-{self.incident_number} - {self.incident_type}"


class MaintenanceLog(models.Model):
    """Tank Maintenance and Repair Records"""
    
    MAINTENANCE_TYPES = [
        ('inspection', 'Inspection'),
        ('cleaning', 'Internal Cleaning'),
        ('surface_treatment', 'Surface Treatment'),
        ('valve_repair', 'Valve Repair/Replacement'),
        ('safety_device', 'Safety Device Service'),
        ('re-certification', 'Re-certification'),
        ('repair', 'General Repair'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tank = models.ForeignKey(Tank, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=50, choices=MAINTENANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Dates
    scheduled_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    
    # Details
    description = models.TextField()
    technician_name = models.CharField(max_length=100)
    technician_email = models.EmailField(blank=True)
    
    # Results
    findings = models.TextField(blank=True)
    parts_replaced = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Scheduling
    next_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = 'Maintenance Log'
        verbose_name_plural = 'Maintenance Logs'
    
    def __str__(self):
        return f"{self.tank.name} - {self.maintenance_type} ({self.scheduled_date})"


class CustomerTankProfile(models.Model):
    """Customer's LPG Tank Information"""
    
    TANK_SIZES = [
        ('50', '50 kg'),
        ('100', '100 kg'),
        ('150', '150 kg'),
        ('250', '250 kg'),
        ('500', '500 kg'),
        ('1000', '1000 kg'),
        ('other', 'Other'),
    ]
    
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='lpg_tank_profile')
    tank_size = models.CharField(max_length=20, choices=TANK_SIZES)
    tank_age_years = models.IntegerField(null=True, blank=True)
    tank_serial_number = models.CharField(max_length=100, blank=True)
    
    # Safety Information
    last_tank_inspection = models.DateField(null=True, blank=True)
    next_tank_inspection = models.DateField(null=True, blank=True)
    tank_certified = models.BooleanField(default=True)
    
    # Delivery Preferences
    preferred_delivery_day = models.CharField(
        max_length=20,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ],
        blank=True
    )
    preferred_delivery_time = models.TimeField(null=True, blank=True)
    delivery_address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    
    # Safety Compliance
    safety_briefing_completed = models.BooleanField(default=False)
    safety_briefing_date = models.DateField(null=True, blank=True)
    accepts_safety_notifications = models.BooleanField(default=True)
    
    # Status
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer Tank Profile'
        verbose_name_plural = 'Customer Tank Profiles'
    
    def __str__(self):
        return f"{self.customer.user.get_full_name()} - {self.tank_size}"
