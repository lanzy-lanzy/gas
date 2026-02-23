# Customer Notifications Implementation Guide

## Overview

A complete in-app notification system has been implemented for customers. When orders are cancelled, customers receive notifications with cancellation reasons displayed in real-time.

## Features Implemented

### 1. **Notification Model**
- Stores all customer notifications
- Tracks notification type (order_cancelled, order_delivered, order_out_for_delivery, order_updated, system_message)
- Stores cancellation reason
- Marks notifications as read/unread
- Timestamps for creation and reading

### 2. **Order Model Enhancement**
Added fields to track cancellations:
- `cancellation_reason`: Stores the reason why the order was cancelled
- `cancelled_at`: Timestamp of when the order was cancelled
- `cancelled_by`: FK to User who cancelled the order

### 3. **Notification Bell UI Component**
- Displays unread notification count in a red badge
- Shows dropdown preview of latest 5 unread notifications
- Displays notification icon based on type
- Shows cancellation reason if applicable
- Quick access to mark as read

### 4. **Notifications List Page**
- Full page view of all notifications
- Pagination (20 notifications per page)
- Read/Unread status indicators
- Filtered view by status
- Cancellation reason displayed prominently
- Related order information

### 5. **Context Processor**
- Automatically makes unread notifications available in all templates
- Variables: `unread_notifications` and `unread_notification_count`
- Used by the notification bell component

### 6. **API Endpoints**
- `GET /api/notifications/unread-count/` - Get unread count
- `POST /customer/notifications/<id>/read/` - Mark notification as read
- `POST /customer/notifications/read-all/` - Mark all as read

## File Structure

```
core/
├── models.py (NEW Notification model + Order field updates)
├── views.py (NEW notification views)
├── urls.py (NEW notification URLs)
├── admin.py (NEW Notification admin + Order admin enhancement)
├── context_processors.py (NEW)
└── migrations/
    └── 0012_order_notification_fields.py (NEW)

templates/
├── components/
│   └── notification_bell.html (NEW)
└── customer/
    └── notifications.html (NEW)

PrycegasStation/
└── settings.py (context processor added)
```

## How It Works

### When an Order is Cancelled

1. **Admin/Cashier cancels order** via bulk operations
2. **Cancellation form** captures the reason
3. **Order updated** with:
   - Status = 'cancelled'
   - Cancellation reason
   - Cancelled timestamp
   - Cancelled by user
4. **Notification created** automatically for the customer
5. **Customer sees notification** in bell dropdown and notifications page

### Notification Flow

```
Order Cancellation
    ↓
Cancel Operation in Views
    ↓
Update Order Fields
    ↓
Create Notification Instance
    ↓
Notification appears in:
    - Bell dropdown (latest 5)
    - Notifications list page
    - API endpoints
    ↓
Customer can mark as read
```

## Usage

### In Templates

#### Add Notification Bell
```html
{% include 'components/notification_bell.html' %}
```

This automatically shows:
- Bell icon with unread count badge
- Dropdown with latest 5 notifications
- Quick mark as read buttons

#### Access Notifications in Context
```html
{{ unread_notification_count }}
{% for notif in unread_notifications %}
    {{ notif.title }}
    {{ notif.message }}
    {{ notif.reason }}
{% endfor %}
```

### In Views

#### Create a Notification
```python
from core.models import Notification, Order
from django.utils import timezone

order = Order.objects.get(id=1)
Notification.objects.create(
    customer=order.customer,
    notification_type='order_cancelled',
    order=order,
    title=f'Order #{order.id} Cancelled',
    message=f'Your order for {order.product.name} has been cancelled.',
    reason='Out of stock - unable to fulfill'
)
```

#### Get Unread Count
```python
from core.models import Notification

count = Notification.objects.filter(
    customer=user,
    is_read=False
).count()
```

#### Mark as Read
```python
notification = Notification.objects.get(id=1, customer=user)
notification.mark_as_read()
```

## Customization

### Add New Notification Types

1. **Update Model** (models.py):
```python
NOTIFICATION_TYPES = [
    # ... existing types ...
    ('my_new_type', 'My New Type'),
]
```

2. **Create Notification**:
```python
Notification.objects.create(
    customer=user,
    notification_type='my_new_type',
    title='...',
    message='...'
)
```

3. **Update Template** (notification_bell.html):
```html
{% elif notification.notification_type == 'my_new_type' %}
    <!-- Display custom icon/styling -->
{% endif %}
```

### Modify Bell Component Styling

Edit `templates/components/notification_bell.html` CSS section:
- `.notification-bell` - Bell icon styling
- `.notification-badge` - Badge styling
- `.notification-dropdown` - Dropdown styling
- `.notification-item` - Individual notification styling

### Customize Notifications List

Edit `templates/customer/notifications.html`:
- Card styling
- Icon display
- Reason display
- Related information

## Database Migration

The migration file `0012_order_notification_fields.py` will:

1. Add fields to Order model:
   - `cancellation_reason` (TextField)
   - `cancelled_at` (DateTimeField)
   - `cancelled_by` (ForeignKey to User)

2. Create Notification model with indexes:
   - Index on (customer, -created_at)
   - Index on (customer, is_read)

### Apply Migration
```bash
python manage.py migrate
```

## Admin Features

### Notification Admin
- View all notifications
- Filter by type, read status, date
- Search by customer username/email
- View-only access (auto-created, not manually added)

### Order Admin Enhancement
- New fieldset for cancellation details
- Shows cancellation reason, who cancelled, when

## Security Considerations

✅ **Implemented:**
- User authentication required for all notification endpoints
- Only customers can see their own notifications
- CSRF protection on all POST requests
- Proper permission checks in views

## Performance

✅ **Optimized:**
- Context processor uses `is_read=False` filter to reduce queries
- Database indexes on frequently queried fields
- Pagination on notifications list (20 per page)
- Select_related in admin for DB optimization

## Browser Compatibility

Works on all modern browsers:
- Chrome/Chromium
- Firefox
- Safari
- Edge

## Testing the Implementation

### 1. Create Test Notification
```bash
python manage.py shell

from django.contrib.auth.models import User
from core.models import Notification

user = User.objects.first()
Notification.objects.create(
    customer=user,
    notification_type='order_cancelled',
    title='Test Notification',
    message='This is a test notification.',
    reason='Testing the system'
)
```

### 2. Login as Customer
- Navigate to customer dashboard
- Notification bell should show count
- Hover over bell to see dropdown
- Click to view all notifications

### 3. Test Mark as Read
- Click "Mark as read" button in dropdown
- Notification should be marked as read
- Count should decrease

### 4. Test Admin
- Login as admin
- Go to Notifications section
- Should see all notifications with filters

## Troubleshooting

### Notification not appearing?
1. Check customer is logged in
2. Verify `customer` field is set on Notification
3. Check context processor is registered in settings.py
4. Clear browser cache and reload

### Badge not showing count?
1. Check JavaScript console for errors
2. Verify CSRF token is correct
3. Check unread_notification_count context variable

### Migration failed?
1. Backup database
2. Check migration 0012 file exists
3. Run `python manage.py migrate core`

## Future Enhancements

Potential additions:
1. Email notifications for important orders
2. SMS notification option
3. Notification settings per user
4. Notification templates (customizable messages)
5. Bulk notification system for announcements
6. Real-time notifications using WebSockets
7. Notification history export
8. Notification preferences (notification frequency, types)

## Support

For issues or questions about the notification system, refer to:
- Django admin interface (Notifications section)
- Order details page (shows cancellation reason)
- Customer notifications page (`/customer/notifications/`)

---

**Last Updated:** December 2024
**Status:** Production Ready
