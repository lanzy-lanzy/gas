# Prycegas LPG System - Quick Reference Guide

## 📊 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Prycegas LPG Management System               │
└──────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
        ┌───▼────┐      ┌────▼────┐      ┌───▼───┐
        │ Dealer │      │Customer │      │Driver │
        │Portal  │      │App      │      │App    │
        └───┬────┘      └────┬────┘      └───┬───┘
            │                │                │
            └────────────────┼────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Django Backend │
                    │  REST API/HTMX  │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
        ┌───▼────────┐  ┌───▼──────┐  ┌────▼──────┐
        │ PostgreSQL │  │  Redis   │  │IoT Sensors│
        │ Database   │  │ Cache    │  │(Optional) │
        └────────────┘  └──────────┘  └───────────┘
```

## 🗄️ Database Models Overview

### Tank Model
```python
Tank
├── name: CharField                    # "Tank A", "Tank B"
├── station: ForeignKey → Station
├── tank_type: CharField               # vertical/horizontal
├── capacity: FloatField               # Liters (e.g., 1000L)
├── current_level: FloatField          # 0-100%
├── pressure: FloatField               # Bar (PSI)
├── temperature: FloatField            # Celsius
├── valve_condition: CharField         # excellent/good/fair/poor
├── next_inspection: DateField
├── is_monitored: BooleanField
├── low_level_threshold: FloatField    # Alert at X%
└── health_status: Property            # HEALTHY/WARNING/CRITICAL

Methods:
├── is_inspection_overdue()            # Check if overdue
├── is_level_low()                     # Check if below threshold
├── capacity_remaining()               # Liters left
└── health_status()                    # Overall status
```

### SafetyAlert Model
```python
SafetyAlert
├── alert_type: CharField              # low_level, leak, inspection_overdue, etc.
├── tank: ForeignKey → Tank
├── severity: CharField                # low/medium/high/critical
├── message: TextField                 # Alert description
├── created_at: DateTimeField          # When alert created
├── resolved: BooleanField             # Status
├── resolved_at: DateTimeField         # When resolved
├── resolved_by: ForeignKey → User
└── resolution_notes: TextField
```

### DeliverySchedule Model
```python
DeliverySchedule
├── customer: ForeignKey → Customer
├── tank: ForeignKey → Tank
├── delivery_date: DateField
├── delivery_time: TimeField           # Optional
├── quantity: FloatField               # Liters
├── price_per_liter: DecimalField
├── total_price: DecimalField
├── frequency: CharField               # weekly/biweekly/monthly/on_demand
├── status: CharField                  # scheduled/in_progress/delivered/cancelled
├── driver: ForeignKey → User
├── delivered_at: DateTimeField
└── signature: ImageField              # Delivery proof
```

### TankInspection Model
```python
TankInspection
├── tank: ForeignKey → Tank
├── inspection_date: DateField
├── inspector_name: CharField
├── pressure_test: BooleanField
├── leak_test: BooleanField
├── surface_inspection: BooleanField
├── valve_inspection: BooleanField
├── safety_relief_test: BooleanField
├── status: CharField                  # passed/failed/conditional
├── findings: TextField
├── repair_required: BooleanField
├── repair_deadline: DateField
└── next_inspection: DateField
```

### IncidentReport Model
```python
IncidentReport
├── incident_type: CharField           # leak, fire, pressure_relief, etc.
├── tank: ForeignKey → Tank
├── station: ForeignKey → Station
├── incident_date: DateTimeField
├── description: TextField
├── severity: CharField                # minor/major/critical
├── injuries: TextField                # If any
├── property_damage: TextField         # If any
├── response_action: TextField         # What was done
├── emergency_services_called: BooleanField
├── reported_by: CharField
├── witness_names: TextField
├── photos: ImageField
├── follow_up_required: BooleanField
├── regulatory_report_submitted: BooleanField
└── incident_number: CharField         # Unique ID
```

### MaintenanceLog Model
```python
MaintenanceLog
├── tank: ForeignKey → Tank
├── maintenance_type: CharField        # inspection, cleaning, repair, etc.
├── status: CharField                  # scheduled/in_progress/completed
├── scheduled_date: DateField
├── completion_date: DateField
├── description: TextField
├── technician_name: CharField
├── findings: TextField
├── parts_replaced: TextField
├── cost: DecimalField
└── next_maintenance: DateField
```

### CustomerTankProfile Model
```python
CustomerTankProfile
├── customer: OneToOneField → Customer
├── tank_size: CharField               # 50kg, 100kg, 250kg, etc.
├── tank_age_years: IntegerField
├── tank_serial_number: CharField
├── last_tank_inspection: DateField
├── next_tank_inspection: DateField
├── tank_certified: BooleanField
├── preferred_delivery_day: CharField
├── preferred_delivery_time: TimeField
├── delivery_address: TextField
├── delivery_instructions: TextField
├── safety_briefing_completed: BooleanField
├── membership_tier: CharField         # basic/plus/premium
└── active: BooleanField
```

---

## 🎯 Common Use Cases

### Use Case 1: Monitor Tank Level
```
Dashboard → Real-time Tank View
├── Display current level (%)
├── Show pressure (bar)
├── Display temperature (°C)
├── Check valve condition
├── Next inspection date
└── Health status badge

Action: If level < 20%, automatically create alert
```

### Use Case 2: Schedule Customer Delivery
```
Manager → Create Delivery Schedule
├── Select customer
├── Choose tank (auto-fill from customer profile)
├── Set delivery date & time
├── Input quantity (liters)
├── System calculates price
├── Assign driver
└── Send notification to customer

Action: Driver receives assignment
Action: Customer gets delivery tracking link
```

### Use Case 3: Log Tank Inspection
```
Inspector → Create Inspection Record
├── Select tank
├── Input inspection date
├── Test pressure? (Yes/No)
├── Leak detection? (Yes/No)
├── Surface condition check
├── Valve inspection
├── Safety relief test
├── Set status (Pass/Fail/Conditional)
├── Enter findings
└── Schedule next inspection

Action: Update tank's next_inspection date
Action: Alert if repairs needed
```

### Use Case 4: Report Safety Incident
```
Manager/Operator → Create Incident Report
├── Select incident type
├── Choose tank (if applicable)
├── Enter incident date/time
├── Describe what happened
├── Set severity level
├── Log response actions
├── Upload photos
├── Add witness names
├── Mark if follow-up needed
└── Submit regulatory report

Action: Assign incident number
Action: Notify relevant personnel
Action: Track until resolved
```

### Use Case 5: Track Customer Deliveries
```
Customer → View Delivery History
├── See upcoming deliveries
├── Track current delivery (real-time)
├── View past deliveries
├── See invoices
├── Check membership benefits
├── Get safety tips
└── Schedule next delivery

Driver → Mobile Delivery Tracking
├── Get delivery list for day
├── Navigate to customer
├── Confirm arrival
├── Check tank status
├── Complete delivery
├── Capture signature
├── Submit proof
```

---

## 📈 Dashboard Layouts

### Manager Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ Prycegas LPG Management - Dashboard                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ ┌──────────┐│
│  │Tanks: 5  │  │Alerts: 2 │  │Deliveries│ │Health:OK ││
│  │          │  │          │  │     12   │ │          ││
│  └──────────┘  └──────────┘  └──────────┘ └──────────┘│
│                                                          │
│  ┌──────────────────────────────────────────────────────┐
│  │ Tanks Overview                                       │
│  ├──────────────────────────────────────────────────────┤
│  │ Tank A    [████████░░] 80%  Healthy    Next: 12/15   │
│  │ Tank B    [████░░░░░░] 40%  WARNING    Next: 12/12   │
│  │ Tank C    [██░░░░░░░░] 20%  CRITICAL   OVERDUE      │
│  └──────────────────────────────────────────────────────┘
│                                                          │
│  ┌──────────────────────────────────────────────────────┐
│  │ ⚠️ Active Alerts (2)                                 │
│  ├──────────────────────────────────────────────────────┤
│  │ 🔴 CRITICAL: Tank C - Inspection Overdue              │
│  │    Due: 12/01/2024 | Created: 12/04/2024            │
│  │                                                       │
│  │ 🟡 HIGH: Tank B - Low Level Alert                    │
│  │    Level: 40% | Created: 12/04/2024                 │
│  └──────────────────────────────────────────────────────┘
│                                                          │
│  ┌──────────────────────────────────────────────────────┐
│  │ Upcoming Deliveries (Today)                          │
│  ├──────────────────────────────────────────────────────┤
│  │ Customer A  10:00 AM  100L  $60    Status: Pending   │
│  │ Customer B  02:00 PM   50L  $30    Status: Pending   │
│  └──────────────────────────────────────────────────────┘
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Tank Detail View
```
┌─────────────────────────────────────────────────────────┐
│ Tank A Details                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Status: HEALTHY ✓                                       │
│                                                          │
│ ┌─ Tank Information ──────────────────────────────────┐ │
│ │ Name: Tank A              Type: Vertical             │ │
│ │ Capacity: 1000L          Installation: 2020-05-15   │ │
│ │ Current Level: 80%       Pressure: 10.5 bar         │ │
│ │ Temperature: 25°C         Valve: Good                │ │
│ └────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─ Inspection Schedule ───────────────────────────────┐ │
│ │ Last: 2024-09-15        Next: 2024-12-15            │ │
│ │ Status: On Schedule ✓                               │ │
│ └────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─ Recent Inspections (Last 5) ──────────────────────┐ │
│ │ 2024-09-15 PASSED  Inspector: John Smith            │ │
│ │ 2024-06-15 PASSED  Inspector: Mary Johnson          │ │
│ │ 2024-03-15 PASSED  Inspector: John Smith            │ │
│ │ 2023-12-15 CONDITIONAL John Smith (Valve tested)   │ │
│ │ 2023-09-15 PASSED  Inspector: Mary Johnson          │ │
│ └────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─ Maintenance History ──────────────────────────────┐ │
│ │ 2024-08-01 COMPLETED  Surface Treatment            │ │
│ │ 2024-05-10 COMPLETED  Valve Repair                 │ │
│ │ 2024-02-20 COMPLETED  Internal Cleaning            │ │
│ └────────────────────────────────────────────────────┘ │
│                                                          │
│ [Schedule Inspection] [Log Maintenance] [View Alerts] │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 Alert Types & Severity

```
┌─────────────────────┬──────────┬────────────────────────────┐
│ Alert Type          │ Severity │ Auto-Resolution            │
├─────────────────────┼──────────┼────────────────────────────┤
│ Low Level           │ MEDIUM   │ When level increases       │
│ Low Level (<10%)    │ CRITICAL │ When level increases       │
│ High Pressure       │ CRITICAL │ When pressure normalizes   │
│ Leak Detected       │ CRITICAL │ Manual - After repair      │
│ Valve Issue         │ HIGH     │ Manual - After service     │
│ Maintenance Due     │ MEDIUM   │ When maintenance done      │
│ Inspection Overdue  │ HIGH     │ When inspection completed  │
│ Temperature High    │ HIGH     │ When temp normalizes       │
│ Low Pressure        │ MEDIUM   │ When pressure increases    │
└─────────────────────┴──────────┴────────────────────────────┘
```

---

## 📱 Mobile App Features

### Driver App
```
Morning Briefing:
├── Today's deliveries (3)
├── Route optimization
├── Customer instructions
├── Tank status checks
└── Safety reminders

During Delivery:
├── Navigate to customer
├── Confirm arrival
├── Take tank photos
├── Verify quantity
├── Get customer signature
├── Capture proof
└── Submit completion

End of Day:
├── Summary report
├── Expenses logged
├── Issues reported
└── Next day preview
```

### Customer App
```
Track Delivery:
├── Live GPS tracking
├── Driver details
├── Estimated arrival
├── Chat with driver
└── Delivery proof

Account:
├── Delivery history
├── Past invoices
├── Tank information
├── Membership details
├── Safety certifications
└── Preferences

Schedule:
├── View upcoming
├── Reschedule
├── One-time orders
├── Recurring setup
└── Payment methods
```

---

## 🔐 Security & Access Control

```
┌─────────────────┬──────────────┬──────────────────────────┐
│ Role            │ Permissions  │ Dashboard Access         │
├─────────────────┼──────────────┼──────────────────────────┤
│ Owner/Manager   │ Full         │ All dashboards           │
│ Operator        │ Read/Write   │ Tank, Delivery, Alerts   │
│ Inspector       │ Write Insp.  │ Inspection, Maintenance  │
│ Driver          │ Limited      │ Assigned deliveries only │
│ Customer        │ View Own     │ Own deliveries & profile │
│ Admin           │ Full system  │ All + admin functions    │
└─────────────────┴──────────────┴──────────────────────────┘
```

---

## 🎨 Color Scheme (Prycegas Branding)

```
Primary Colors:
├── Prycegas Orange: #ff6b35     (Main actions, highlights)
├── Prycegas Dark Orange: #e55a2b (Hover states)
├── Prycegas Light Orange: #ff8c5a (Secondary)
└── Prycegas Black: #1a1a1a      (Text, backgrounds)

Status Colors:
├── Healthy: #10b981   (Green)
├── Warning: #f59e0b   (Amber)
├── Critical: #ef4444  (Red)
└── Info: #3b82f6     (Blue)
```

---

## 📊 Sample Data Queries

### Check all tanks with low levels
```python
from core.models_lpg import Tank

low_tanks = Tank.objects.filter(current_level__lte=F('low_level_threshold'))
# Returns tanks below their alert threshold
```

### Get active delivery deliveries
```python
from core.models_lpg import DeliverySchedule
from django.utils import timezone

today_deliveries = DeliverySchedule.objects.filter(
    delivery_date=timezone.now().date(),
    status__in=['scheduled', 'in_progress']
).order_by('delivery_time')
```

### Pending inspections
```python
from core.models_lpg import Tank
from django.utils import timezone

overdue = Tank.objects.filter(
    next_inspection__lt=timezone.now().date()
)
```

### Unresolved alerts
```python
from core.models_lpg import SafetyAlert

critical_alerts = SafetyAlert.objects.filter(
    resolved=False,
    severity='critical'
).order_by('-created_at')
```

---

## 🧪 Testing Checklist

```
✓ Models
  ├─ Tank creation and updates
  ├─ Alert creation and resolution
  ├─ Inspection logging
  └─ Delivery scheduling

✓ Views/APIs
  ├─ Dashboard loading
  ├─ Real-time data updates
  ├─ CRUD operations
  └─ Permission checks

✓ Business Logic
  ├─ Alert triggers (low level, overdue, etc.)
  ├─ Health status calculations
  ├─ Delivery notifications
  └─ Report generation

✓ Frontend
  ├─ Responsive design
  ├─ Real-time updates
  ├─ Form validations
  └─ Error handling

✓ Security
  ├─ Authentication
  ├─ Authorization
  ├─ Data encryption
  └─ Audit logging
```

---

## 📞 Support Contact Points

**For Database Issues:**
- Check migrations: `python manage.py showmigrations`
- View model relationships in admin

**For Display Issues:**
- Check template rendering
- Validate CSS classes
- Test on different screen sizes

**For Alert Issues:**
- Check SafetyAlert creation
- Verify threshold values
- Test notification sending

**For Delivery Issues:**
- Check DeliverySchedule status
- Verify driver assignments
- Test mobile tracking

---

**Last Updated**: December 4, 2025
**Version**: 1.0
**Status**: Ready for Development
