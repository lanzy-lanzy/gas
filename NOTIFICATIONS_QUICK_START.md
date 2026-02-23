# Customer Notifications - Quick Start Guide

## 🚀 What's New

A complete customer notification system with **order cancellation tracking** and **notification bell UI**.

## ✨ Key Features

1. **📲 Notification Bell** - Displays in customer navbar
   - Shows unread count badge
   - Hover dropdown preview
   - Mark notifications as read

2. **📋 Notifications Page** - Full list view
   - All notifications paginated
   - Read/unread status
   - Filter and search

3. **🔔 Smart Notifications** - Automatic creation
   - Order cancellation with reason
   - Delivered status updates
   - Out for delivery alerts

4. **💾 Database Tracking** - Complete history
   - Reason for cancellation
   - Who cancelled the order
   - When it was cancelled

## 📦 What Was Added

### Database
- ✅ `Notification` model - New table for notifications
- ✅ Order fields - `cancellation_reason`, `cancelled_at`, `cancelled_by`

### Backend
- ✅ Context processor - Available on all templates
- ✅ Views - 4 new views for notifications
- ✅ URLs - 4 new endpoints
- ✅ Admin - Notification management interface

### Frontend
- ✅ Notification bell component
- ✅ Notifications list page
- ✅ Dropdown preview with latest 5

### Admin
- ✅ Notification admin interface
- ✅ Order admin enhancement for cancellation tracking

## 🔧 Installation Steps

### 1. Apply Migration
```bash
python manage.py migrate
```

### 2. Add Notification Bell to Base Template

Edit your base template and add the bell component in the navbar:

```html
<!-- In navbar, near user profile -->
{% include 'components/notification_bell.html' %}
```

Example location in navbar:
```html
<nav class="navbar">
    <div class="navbar-right">
        {% include 'components/notification_bell.html' %}
        <a href="{% url 'core:profile' %}">Profile</a>
        <a href="{% url 'core:logout' %}">Logout</a>
    </div>
</nav>
```

### 3. Add Link to Notifications Page

In customer dashboard or profile:
```html
<a href="{% url 'core:customer_notifications' %}" class="btn btn-primary">
    View all notifications
</a>
```

## 📝 Usage Examples

### Cancelling an Order with Reason

When using bulk operations to cancel orders:

```
1. Select orders to cancel
2. Click "Cancel Selected"
3. Enter cancellation reason
4. Click confirm
5. Customer receives notification with reason
```

### Customer View

1. **Bell Icon** - Click to see dropdown
   - Shows latest 5 notifications
   - Badge shows unread count
   - Click "Mark as read" to dismiss

2. **Notifications Page** - Click "View all notifications"
   - See all notifications (paginated)
   - Shows cancellation reasons
   - Mark individual or all as read

## 🎯 Features by User Role

### Customers
- ✅ Receive cancellation notifications
- ✅ View notification history
- ✅ Mark notifications as read
- ✅ See cancellation reason
- ✅ Check related order details

### Admins/Dealers
- ✅ Cancel orders with reason
- ✅ Manage notifications in admin panel
- ✅ View all customer notifications
- ✅ See notification read status

## 🔌 API Endpoints

### Get Unread Count
```
GET /api/notifications/unread-count/
Response: { "unread_count": 3 }
```

### Mark as Read
```
POST /customer/notifications/<id>/read/
Response: { "success": true }
```

### Mark All as Read
```
POST /customer/notifications/read-all/
Response: { "success": true }
```

## 🎨 Customizing Appearance

### Bell Icon Color
Edit `templates/components/notification_bell.html`:
```css
.notification-bell {
    color: #333;  /* Change this */
}
```

### Badge Color
```css
.notification-badge {
    background-color: #ff4444;  /* Change this */
}
```

### Dropdown Width
```css
.notification-dropdown {
    width: 350px;  /* Adjust width */
}
```

### Notification Card Styling
Edit `templates/customer/notifications.html` to customize the cards.

## 🔍 Testing

### Test Order Cancellation
1. Place an order as customer
2. Login as admin/dealer
3. Go to order management
4. Select order and cancel with reason
5. Login as customer
6. Check notification bell (should show 1 unread)
7. Click bell to see notification with reason

### Test Notifications Page
1. Click bell → "View all notifications"
2. Should see full notification details
3. Click "Mark as read"
4. Should appear as read

### Test Admin Interface
1. Go to Django admin
2. Navigate to Notifications
3. Should see all customer notifications
4. Filter by type, status, or date

## 📊 Database Schema

### Notification Model
```
- id (BigAutoField)
- customer (ForeignKey → User)
- notification_type (CharField) - order_cancelled, order_delivered, etc.
- order (ForeignKey → Order, nullable)
- title (CharField)
- message (TextField)
- reason (TextField) - cancellation reason
- is_read (BooleanField) - default False
- created_at (DateTimeField) - auto
- read_at (DateTimeField) - nullable
```

### Order Model (New Fields)
```
- cancellation_reason (TextField)
- cancelled_at (DateTimeField)
- cancelled_by (ForeignKey → User)
```

## 🚨 Important Notes

1. **Migration Required** - Must run migration before using
2. **Context Processor** - Already added to settings.py
3. **Base Template** - Need to add notification bell component
4. **No Cache Issues** - Fresh notifications on every load
5. **Mobile Friendly** - Responsive design included

## 📈 Performance

- Queries optimized with indexes
- Pagination to prevent large loads
- Context processor only fetches unread
- Admin uses select_related for efficiency

## 🔐 Security

- ✅ Login required for all views
- ✅ Users only see own notifications
- ✅ CSRF protection on POST requests
- ✅ Permission checks in views

## ❓ FAQ

**Q: Will this work on my existing orders?**
A: Yes, but only new cancellations will create notifications.

**Q: Can I customize the notification text?**
A: Yes, edit the message creation in views.py line 1527-1533.

**Q: Do customers get email notifications too?**
A: Not currently, only in-app. Email can be added later.

**Q: How long are notifications kept?**
A: Indefinitely. You can add retention policy in admin.

**Q: Can I send notifications manually?**
A: Yes, via Django admin → Notifications (read-only, must be via code).

**Q: Mobile responsive?**
A: Yes, fully responsive design included.

## 📞 Support

For issues:
1. Check the full documentation: `CUSTOMER_NOTIFICATIONS_IMPLEMENTATION.md`
2. Check Django admin → Notifications for debugging
3. Check browser console for JavaScript errors

## 🎉 Next Steps

1. Apply migration
2. Update base template with bell component
3. Test order cancellation
4. Customize styling if needed
5. Monitor admin interface

---

**Version:** 1.0  
**Status:** Ready to Use  
**Last Updated:** December 2024
