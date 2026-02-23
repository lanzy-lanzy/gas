# Admin User Management Dashboard

## Overview

Enhanced Django admin interface with a comprehensive user management dashboard showing real-time statistics about pending registrations, approved users, customers, and cashiers.

## Features

### Dashboard Home Page
When you login to Django admin, you'll now see a user management dashboard with:

#### Registration Statistics (Top Row)
- **Pending Approvals**: Count of registrations awaiting admin review (clickable - orange badge)
- **Approved**: Count of approved registrations (clickable - green badge)
- **Rejected**: Count of rejected registrations (clickable - red badge)
- **Total Registrations**: Overall count of all registrations (clickable - blue badge)

#### User Statistics (Bottom Row)
- **Total Customers**: Count of registered customer profiles (purple badge)
- **Total Cashiers**: Count of active cashiers (pink badge)

#### Quick Actions Bar
Fast access buttons to:
- View Pending Registrations
- Manage Customers
- Manage Cashiers

### Auto-Filtering
Clicking on status cards automatically filters registrations:
- "Pending Approvals" → Shows only pending registrations
- "Approved" → Shows only approved registrations
- "Rejected" → Shows only rejected registrations

## Implementation Details

### Changes to `core/admin.py`

#### 1. Custom Admin Site Class
```python
class PrycegasAdminSite(admin.AdminSite):
    """
    Custom admin site with enhanced user management dashboard
    """
    site_header = "Prycegas Station Administration"
    site_title = "Prycegas Admin"
    index_title = "Welcome to Prycegas Admin Panel"
    
    def index(self, request, extra_context=None):
        """Enhanced admin index with user management stats"""
        # Calculates pending, approved, rejected, total counts
        # Calculates total customers and cashiers
        # Passes all stats to template
```

#### 2. Updated Admin Registrations
All admin classes now use custom admin site:
```python
@admin_site.register(ModelName)  # Instead of @admin.register
class ModelAdmin(admin.ModelAdmin):
    ...
```

Affected models:
- CustomerProfile
- LPGProduct
- Order
- DeliveryLog
- ProductCategory
- Supplier
- StockMovement
- InventoryAdjustment
- Cashier
- CashierTransaction
- PendingRegistration

### New Template
`templates/admin/index.html` - Custom admin dashboard with:
- Stat cards with color-coded borders
- Quick action buttons
- Clickable stats that filter registrations
- Responsive grid layout

## Accessing the Dashboard

### URL
```
http://your-site.com/admin/
```

### Admin Menu (Sidebar)
The main admin page now has:
1. **User Management** Section (header)
2. **Registration Stats** Cards
3. **User Stats** Cards
4. **Quick Actions** Buttons

### Status Indicators
- **Orange**: Pending approval (needs action)
- **Green**: Approved (completed)
- **Red**: Rejected (declined)
- **Blue**: All registrations
- **Purple**: Customers
- **Pink**: Cashiers

## How to Use

### Viewing Statistics
1. Login to admin: `/admin/`
2. See stats on home page
3. Numbers update automatically as registrations are processed

### Quick Navigation
1. Click any stat card to view those registrations
2. Click "Quick Actions" buttons for fast access
3. Use sidebar navigation for other admin functions

### Pending Registrations Workflow
1. Login to admin
2. See "Pending Approvals" count on dashboard
3. Click "View Pending Registrations" quick action
4. Review registrations
5. Approve or reject each one
6. Stats update automatically

## Database Queries

The dashboard runs efficient queries:

```python
# Pending count
PendingRegistration.objects.filter(status='pending').count()

# Approved count
PendingRegistration.objects.filter(status='approved').count()

# Rejected count
PendingRegistration.objects.filter(status='rejected').count()

# Total count
PendingRegistration.objects.count()

# Customers count
CustomerProfile.objects.count()

# Cashiers count
Cashier.objects.count()
```

All queries use `.count()` for performance (not `.all().count()`).

## Customization

### Changing Colors
Edit `templates/admin/index.html` and update `border-left` colors in style attributes:
```html
border-left: 4px solid #ff6b35;  <!-- Orange for pending -->
```

Available Prycegas colors:
- Orange: #ff6b35 (pending)
- Green: #10b981 (approved)
- Red: #ef4444 (rejected)
- Blue: #3b82f6 (total)
- Purple: #8b5cf6 (customers)
- Pink: #ec4899 (cashiers)

### Adding More Stats
Edit the `index()` method in `PrycegasAdminSite`:

```python
def index(self, request, extra_context=None):
    # ... existing code ...
    
    # Add new stat
    new_stat = YourModel.objects.filter(some_condition).count()
    extra_context['new_stat_name'] = new_stat
    
    return super().index(request, extra_context)
```

Then add card in template:
```html
<div style="background: white; border-left: 4px solid #YOUR_COLOR; ...">
    <div>New Stat Name</div>
    <div>{{ new_stat_name }}</div>
</div>
```

### Hiding Sections
To hide the user management section on admin home:
1. Delete `templates/admin/index.html`
2. Comment out the PendingRegistration card in the template
3. Or create a simpler template

## Performance Considerations

✓ All counts use efficient `.count()` queries
✓ No joins required (simple counting)
✓ Queries run only when admin home page loaded
✓ Caching can be added if needed:

```python
from django.core.cache import cache

def index(self, request, extra_context=None):
    # Try cache first
    pending_count = cache.get('pending_reg_count')
    if pending_count is None:
        pending_count = PendingRegistration.objects.filter(status='pending').count()
        cache.set('pending_reg_count', pending_count, 60)  # Cache for 1 minute
    
    # ... rest of code
```

## Troubleshooting

### Dashboard Not Showing
1. Clear Django cache: `python manage.py shell`
   ```python
   from django.core.cache import cache
   cache.clear()
   ```
2. Restart Django server
3. Clear browser cache (Ctrl+Shift+Del)

### Stats Not Updating
1. Hard refresh browser (Ctrl+F5)
2. Check database has records
3. Verify PendingRegistration model has data

### Custom Admin Site Not Working
1. Verify all `@admin.register` changed to `@admin_site.register`
2. Check `admin_site` variable is defined
3. Ensure `templates/admin/` directory exists
4. Django templates can be overridden at this path

### Links Not Working
1. Verify reverse URL names are correct
2. Check `admin:` namespace is available
3. Test individual links in Django shell:
   ```python
   from django.urls import reverse
   print(reverse('admin:core_pendingregistration_changelist'))
   ```

## Integration Points

### Registration Workflow
1. User registers → PendingRegistration created
2. Count increases on dashboard
3. Admin reviews
4. Approve/Reject → Count updates
5. Approved → Can create User account

### Dashboard Display
1. Admin logs in → `index()` method called
2. Queries run → Stats calculated
3. Template rendered → Stats displayed
4. Click stat → Filtered view shown

## Future Enhancements

Possible additions:
1. **Charts**: Show registration trends over time
2. **Recent Activity**: List latest 5 pending registrations
3. **Alerts**: Highlight registrations pending >7 days
4. **Export**: Export registration statistics to CSV
5. **Bulk Actions**: Quick approve/reject from dashboard
6. **Filters**: Filter stats by date range
7. **Notifications**: Show new registrations real-time

## Admin User Permissions

To access the dashboard, user must:
1. Have `is_staff = True`
2. Have admin site access
3. Can view `PendingRegistration` (optional for dashboard)

Optional: Add specific permissions:
```python
class PendingRegistrationAdmin(admin.ModelAdmin):
    def has_view_permission(self, request):
        return True  # Allow viewing
    
    def has_add_permission(self, request):
        return False  # Prevent adding manually
    
    def has_delete_permission(self, request, obj=None):
        return False if obj and obj.reviewed_at else True
```

## Support & Documentation

Related files:
- REGISTRATION_ID_VERIFICATION_GUIDE.md - Full implementation
- ADMIN_REGISTRATION_QUICK_START.md - Admin quick reference
- IMPLEMENTATION_CHECKLIST.md - Deployment checklist

## Files Modified

1. `prycegas/core/admin.py`
   - Added PycegasAdminSite class
   - Changed all @admin.register to @admin_site.register

2. `prycegas/templates/admin/index.html` (NEW)
   - Custom dashboard with statistics
   - Quick action buttons
   - Responsive grid layout
