# Registration ID Verification & Admin Approval System

## Overview

This implementation adds a complete user registration workflow with ID document verification and admin approval process for Prycegas Station.

## Features Implemented

### 1. User Registration with ID Verification (3-Step Process)

#### Step 1: Basic Information
- Username (3-30 characters, alphanumeric + underscore)
- Email (unique, validated)
- Phone Number (Philippine format: 09XXXXXXXXX or +639XXXXXXXXX)

#### Step 2: Address & Password
- Complete delivery address
- Delivery instructions (optional)
- Password (min 8 characters)
- Confirm password

#### Step 3: ID Verification (NEW)
- ID Type selection (National ID, Driver's License, Passport, Barangay ID, SSS ID, TIN ID, Company ID, Other)
- ID Number
- ID Document upload (JPG, PNG, GIF, PDF - Max 5MB)
- Drag-and-drop file upload support

### 2. PendingRegistration Model

```python
class PendingRegistration(models.Model):
    # User registration data
    username, email, phone_number, address, delivery_instructions
    
    # ID verification
    id_type, id_number, id_document (ImageField)
    
    # Status tracking
    status (pending/approved/rejected)
    rejection_reason
    
    # Admin actions
    reviewed_by, reviewed_at
    
    # Timestamps
    created_at, updated_at
```

### 3. Enhanced Admin Interface

Access pending registrations at: `/admin/core/pendingregistration/`

#### Features:
- **List View**: See all pending registrations with status badges
- **Color-coded Status**: 
  - Orange: Pending
  - Green: Approved
  - Red: Rejected
- **ID Document Preview**: Click to view uploaded ID documents
- **Days Pending**: Shows how long registration has been waiting
- **Quick Actions**: Approve/Reject buttons on list view
- **Bulk Actions**: Select multiple registrations and approve/reject
- **Advanced Filtering**: Filter by status, ID type, date range
- **Search**: Search by username, email, phone, ID number

#### Admin Functions:
1. **Approve Registration**: Convert PendingRegistration to actual User account
2. **Reject Registration**: Store rejection reason for audit trail
3. **View Details**: Full edit form with read-only fields after review
4. **Search & Filter**: Quickly locate registrations

### 4. Registration Form (PendingRegistrationForm)

Located in `core/forms.py`

Includes validation for:
- Username uniqueness and format
- Email uniqueness
- ID document file type and size
- Password strength
- Phone number format

## Files Modified/Created

### Created Files:
1. `core/models.py` - Added PendingRegistration model
2. `core/forms.py` - Added PendingRegistrationForm
3. `core/admin.py` - Added PendingRegistrationAdmin
4. `core/migrations/0003_pendingregistration.py` - Database migration
5. `templates/auth/register_enhanced.html` - Updated with 3-step form
6. `templates/admin/core/pendingregistration/change_list.html` - Admin dashboard

### Updated Files:
1. `templates/auth/register_enhanced.html` - Added Step 3 with ID upload and Alpine.js handlers

## Implementation Steps

### 1. Run Database Migration

```bash
python manage.py migrate core
```

### 2. Update Views (if needed)

If you have a custom registration view, update it to:

```python
from core.forms import PendingRegistrationForm
from core.models import PendingRegistration

def register(request):
    if request.method == 'POST':
        form = PendingRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            pending_reg = form.save()
            messages.success(request, 
                'Registration submitted successfully! '
                'Your account is pending admin approval. '
                'You will receive an email notification once reviewed.')
            return redirect('login')
    else:
        form = PendingRegistrationForm()
    
    return render(request, 'auth/register_enhanced.html', {'form': form})
```

### 3. Configure Media Files

Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured in `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

Add to `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Admin Site Configuration

Already configured in `core/admin.py`:
- PendingRegistrationAdmin is registered
- Custom list display with badges and previews
- Bulk actions for approval/rejection
- Advanced filtering options

## Usage Guide

### For Users (Registration)

1. Navigate to registration page
2. Fill out Step 1 (Basic Information)
3. Fill out Step 2 (Address & Password)
4. Fill out Step 3 (ID Verification)
   - Select ID type
   - Enter ID number
   - Upload clear photo/scan of ID
5. Submit for review
6. Wait for admin approval (email notification will be sent)

### For Admins (Review & Approval)

1. Login to Django admin: `/admin/`
2. Navigate to "Pending Registrations" under Core
3. Review registrations:
   - Click on registration to view all details
   - View ID document preview
   - Check phone number and address for legitimacy

4. **To Approve:**
   - Option A: Click "Approve" button on list view
   - Option B: Open registration, change status to "Approved", save
   - Option C: Select multiple, use "Approve selected registrations" action

5. **To Reject:**
   - Open registration detail
   - Change status to "Rejected"
   - Enter rejection reason (e.g., "ID not clear", "Suspicious information")
   - Save
   - Optionally send email to user explaining rejection

## Security Features

1. **File Upload Validation**:
   - Only image and PDF files allowed
   - Max file size: 5MB
   - Files stored in `media/pending_registrations/` directory

2. **Admin Audit Trail**:
   - Track which admin reviewed each registration
   - Timestamp for review date/time
   - Rejection reasons stored

3. **Unique Constraints**:
   - Username unique (prevents duplicates)
   - Email unique (prevents duplicate registrations)

4. **Data Validation**:
   - Phone number format validation
   - ID type from predefined list
   - Password strength requirements

## Next Steps: Automating User Creation

To automatically create User accounts from approved registrations:

```python
# In a management command or signal handler
from core.models import PendingRegistration
from django.contrib.auth.models import User
from core.models import CustomerProfile

def create_user_from_pending(pending_reg):
    """Create actual User account from approved pending registration"""
    if pending_reg.status != 'approved':
        raise ValueError("Only approved registrations can be converted")
    
    # Create User
    user = User.objects.create_user(
        username=pending_reg.username,
        email=pending_reg.email,
        password=None  # User should reset password
    )
    
    # Create CustomerProfile
    CustomerProfile.objects.create(
        user=user,
        phone_number=pending_reg.phone_number,
        address=pending_reg.address,
        delivery_instructions=pending_reg.delivery_instructions
    )
    
    return user
```

## Admin Customization

### Customize List Display
Edit `PendingRegistrationAdmin.list_display` in `core/admin.py`

### Add Email Notifications
Add signals to send emails on approval/rejection:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=PendingRegistration)
def notify_on_status_change(sender, instance, created, **kwargs):
    if instance.status == 'approved':
        # Send approval email
        pass
    elif instance.status == 'rejected':
        # Send rejection email
        pass
```

### Custom Rejection Reasons
Create a separate model to track common rejection reasons:

```python
class RejectionReason(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
```

## Troubleshooting

### Migration Issues
If migration fails, check:
1. Database connectivity
2. MEDIA_URL/MEDIA_ROOT configuration
3. PIL/Pillow installed for ImageField

```bash
pip install Pillow
python manage.py migrate core
```

### File Upload Not Working
1. Ensure `MEDIA_ROOT` directory exists and is writable
2. Check file permissions: `chmod 755 media/`
3. Verify file size < 5MB
4. Check file format is JPG, PNG, GIF, or PDF

### Admin Dashboard Not Showing
1. Clear browser cache
2. Restart Django development server
3. Check for template errors in console

## Performance Optimization

### For Large Volume
1. Add pagination in admin (already configured)
2. Use `select_related()` for reviewed_by
3. Add database indexes on status and created_at (already in model)
4. Consider archiving old registrations

```python
# Archive old rejected registrations (older than 90 days)
from django.utils import timezone
from datetime import timedelta

ninety_days_ago = timezone.now() - timedelta(days=90)
PendingRegistration.objects.filter(
    status='rejected',
    updated_at__lt=ninety_days_ago
).delete()
```

## Support & Questions

For issues or customization requests, refer to:
- Django Admin Documentation: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
- File Upload Docs: https://docs.djangoproject.com/en/stable/topics/files/
- Form Validation: https://docs.djangoproject.com/en/stable/ref/forms/validation/
