# Final Setup Guide - Registration ID Verification System

## Quick Start (5 Minutes)

### Step 1: Run Database Migration
```bash
cd g:\app_2025\prycegas
python manage.py migrate core
```

Expected output:
```
Applying core.0008_pendingregistration... OK
```

### Step 2: Restart Django Server
```bash
python manage.py runserver
```

### Step 3: Access Admin Dashboard
1. Go to: `http://127.0.0.1:8000/admin/`
2. Login with admin account
3. See **User Management** dashboard on home page

### Step 4: Test Registration Flow
1. Go to: `http://127.0.0.1:8000/register/`
2. Fill Step 1: Username, Email, Phone
3. Click "Continue"
4. Fill Step 2: Address, Password
5. Click "Continue"
6. Fill Step 3: ID Type, ID Number, Upload ID document
7. Click "Submit Registration"
8. See success message

### Step 5: Approve Registration
1. Go to admin: `/admin/`
2. See pending count on dashboard
3. Click "View Pending Registrations"
4. Click on registration to review
5. View ID document by clicking image
6. Click "Approve" or change status and save

Done! The registration system is now active.

---

## What's Installed

### Files Created:
- ✅ `core/models.py` - PendingRegistration model (updated)
- ✅ `core/forms.py` - PendingRegistrationForm (updated)
- ✅ `core/admin.py` - Admin interface with dashboard (updated)
- ✅ `core/migrations/0008_pendingregistration.py` - Database migration
- ✅ `templates/auth/register_enhanced.html` - 3-step form (updated)
- ✅ `templates/admin/index.html` - Admin dashboard
- ✅ Documentation files (8 guides)

### Features:
- ✅ 3-step registration form
- ✅ ID document upload with drag-and-drop
- ✅ Admin approval workflow
- ✅ User management dashboard
- ✅ Status tracking (pending/approved/rejected)
- ✅ Audit trail (who, when, why)
- ✅ File validation (size, type)
- ✅ Unique constraints (username, email)

---

## Common Tasks

### View Pending Registrations
1. Login to admin: `/admin/`
2. Click on pending count card (orange)
3. Or navigate: CORE → Pending Registrations

### Approve a Registration
1. Click on registration in list
2. Review ID document (click image)
3. Click "Approve" button in list, OR
4. Change status to "Approved" and save

### Reject with Reason
1. Click on registration
2. Change status to "Rejected"
3. Enter rejection reason
4. Click "Save"

### Search Registrations
1. Go to Pending Registrations list
2. Use search box (top right):
   - Search by username
   - Search by email
   - Search by phone
   - Search by ID number

### Filter Registrations
1. Go to Pending Registrations list
2. Click filter on right side:
   - By Status (pending, approved, rejected)
   - By ID Type
   - By Date
   - By Reviewer

---

## Important Files Reference

| File | Purpose | Location |
|------|---------|----------|
| Admin Dashboard | Stat cards, quick actions | `/admin/` |
| Pending Registrations | Review & approve users | `/admin/core/pendingregistration/` |
| Registration Form | User signup | `/register/` |
| Documentation | Setup & usage guides | Root directory |

---

## Troubleshooting

### Migration Error
**Problem**: Migration fails
**Solution**: 
```bash
python manage.py migrate core --verbosity 3
# Check error message
# Run: python manage.py showmigrations core
```

### Admin Not Showing Stats
**Problem**: Dashboard shows no stats
**Solution**:
1. Hard refresh browser (Ctrl+Shift+Del)
2. Clear Django cache: `python manage.py shell` → `from django.core.cache import cache` → `cache.clear()`
3. Restart Django server

### Registration Form Not Showing Step 3
**Problem**: Only see Steps 1 and 2
**Solution**: 
1. Check `register_enhanced.html` is in correct location
2. Verify template loads without errors
3. Check browser console for JavaScript errors

### File Upload Not Working
**Problem**: Can't upload ID document
**Solution**:
1. Check `MEDIA_ROOT` in settings.py exists
2. Create directory: `mkdir media/pending_registrations/id_documents`
3. Verify permissions: `chmod 755 media/`
4. Check file size < 5MB
5. Try different file format (JPG, PNG, PDF)

### Admin Site Header Incorrect
**Problem**: Admin title still shows old text
**Solution**:
1. Hard refresh admin page
2. Clear browser cache
3. Restart Django server
4. Check `admin.site.site_header = "..."` in core/admin.py

---

## Testing Checklist

- [ ] Database migration runs without errors
- [ ] Admin site loads at `/admin/`
- [ ] Dashboard shows stats (even if 0)
- [ ] Registration form shows 3 steps
- [ ] Can fill all fields in registration
- [ ] Can upload ID document
- [ ] File upload validation works (try 10MB file)
- [ ] Pending registrations appear in admin
- [ ] Can approve registration
- [ ] Can reject registration
- [ ] Search works
- [ ] Filters work
- [ ] Status badges show correct colors

---

## Database Structure

**Table**: `core_pendingregistration`

```
Columns:
  - id (auto)
  - username (unique)
  - email (unique)
  - phone_number
  - address
  - delivery_instructions
  - id_type (choice)
  - id_number
  - id_document (image file path)
  - status (choice: pending/approved/rejected)
  - rejection_reason (text)
  - reviewed_by_id (FK to User)
  - reviewed_at (datetime)
  - created_at (datetime)
  - updated_at (datetime)
```

---

## Next Steps (Optional)

### 1. Send Email Notifications
Add email when registration approved/rejected:
```python
# In core/admin.py after approval
from django.core.mail import send_mail

def approve_registrations(self, request, queryset):
    for reg in queryset.filter(status='pending'):
        reg.approve(request.user)
        # Send email
        send_mail(
            'Registration Approved',
            f'Your registration for {reg.username} has been approved!',
            'admin@prycegas.com',
            [reg.email],
        )
```

### 2. Auto-Create User Accounts
Convert approved registrations to User accounts:
```bash
# Create management command
python manage.py startapp utils

# Create: utils/management/commands/create_users_from_approved.py
```

### 3. Add SMS Verification
Verify phone numbers via SMS before approval

### 4. Generate Reports
Export registration stats to CSV/PDF

### 5. Dashboard Analytics
Show registration trends over time

---

## Support Documents

For more detailed information:
1. **REGISTRATION_ID_VERIFICATION_GUIDE.md** - Complete feature documentation
2. **ADMIN_REGISTRATION_QUICK_START.md** - Admin user reference
3. **ADMIN_USER_MANAGEMENT_DASHBOARD.md** - Dashboard customization
4. **IMPLEMENTATION_CHECKLIST.md** - Deployment checklist
5. **COMPLETE_IMPLEMENTATION_SUMMARY.txt** - Executive summary

---

## Need Help?

### Check These First:
1. Verify migration ran: `python manage.py showmigrations core`
2. Check for errors: Look at Django console output
3. Test admin: Can you see other models?
4. Test registration: Does form load?

### Browser Issues:
1. Clear cache: Ctrl+Shift+Del
2. Hard refresh: Ctrl+Shift+R
3. Try incognito mode
4. Check console errors: F12

### Django Issues:
1. Check manage.py is in correct directory
2. Verify settings.py INSTALLED_APPS includes 'core'
3. Check for Python syntax errors
4. Restart Django server

---

## Production Checklist

Before going live:

- [ ] Test migration on staging database
- [ ] Set up media directory with proper permissions
- [ ] Configure MEDIA_URL and MEDIA_ROOT
- [ ] Enable HTTPS (important for file uploads)
- [ ] Set DEBUG=False in production
- [ ] Configure email backend for notifications
- [ ] Set up database backups
- [ ] Test all registration steps
- [ ] Train admins on approval workflow
- [ ] Set up monitoring/logging

---

## Contact & Support

For issues or questions:
1. Review the detailed guides in root directory
2. Check troubleshooting section above
3. Review Django error messages in console
4. Test with simple data first

---

**Status**: ✅ Implementation Complete
**Version**: 1.0
**Last Updated**: December 17, 2025
