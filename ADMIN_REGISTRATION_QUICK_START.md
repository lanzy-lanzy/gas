# Admin Registration Management Quick Start

## Accessing Pending Registrations

1. Login to Django Admin: `http://your-site.com/admin/`
2. Under **CORE** section, click **Pending Registrations**

## Dashboard Overview

### Status Indicators
- **Orange Badge**: Pending approval
- **Green Badge**: Approved
- **Red Badge**: Rejected

### Key Information Displayed
- Username and Email
- Phone number
- ID type (National ID, Driver's License, etc.)
- Days pending (how long waiting for review)
- ID document preview (clickable thumbnail)

## Reviewing a Registration

### Quick Review (List View)
1. Find registration in list
2. Click registration to open details
3. Review ID document
4. Click "Approve" or "Reject" button

### Detailed Review
1. Click username or "Review Details" link
2. See full form with all information:
   - Personal info (username, email, phone)
   - Address and delivery instructions
   - ID document (large preview, clickable for full size)
   - Current status
   - Review notes/rejection reason
3. Make decision:
   - **To Approve**: Change status to "Approved" → Click Save
   - **To Reject**: Change status to "Rejected" → Enter reason → Click Save

## Bulk Actions

### Approve Multiple Registrations
1. On list view, check boxes next to registrations
2. Select "Approve selected registrations" from action dropdown
3. Click "Go"

### Reject Multiple Registrations
1. On list view, check boxes next to registrations
2. Select "Reject selected registrations" from action dropdown
3. Click "Go"

## Searching & Filtering

### Search By
- Username
- Email
- Phone number
- ID number

**How to use**: Type in search box at top right, press Enter

### Filter By
- **Status**: Show pending, approved, or rejected only
- **ID Type**: Filter by National ID, Driver's License, Passport, etc.
- **Date Range**: Show registrations from specific dates
- **Reviewed By**: Show registrations reviewed by specific admin

## Important Notes

### Before Approving
- ✓ ID document is clear and readable
- ✓ ID number matches document
- ✓ Phone number is valid
- ✓ Address is complete and legitimate
- ✓ Username doesn't contain suspicious characters
- ✓ Email looks legitimate (not spam)

### Rejection Best Practices
**Good rejection reasons:**
- "ID document not clear - please resubmit with clearer photo"
- "Suspicious phone number - appears to be shared device"
- "ID number doesn't match ID type"
- "Address incomplete or suspicious"

**Not recommended:**
- "No" (too vague)
- "Rejected" (no helpful reason)
- "Not approved" (no explanation)

## FAQs

### Q: How do I view the ID document in full size?
A: Click the ID document thumbnail in the registration details. It will open in a new window at full size.

### Q: Can I change a decision after approving/rejecting?
A: Yes, open the registration, change the status, and save. Be sure to update the review timestamp and reason if needed.

### Q: What happens after I approve a registration?
A: The registration is marked as approved. An account creation workflow should follow (handled by system automatically or manually).

### Q: Where do uploaded ID documents get stored?
A: In `media/pending_registrations/id_documents/` directory on the server.

### Q: Can I download/export all registrations?
A: Yes, Django admin supports exporting. Select registrations and use the admin action, or use Django's built-in CSV export.

### Q: How long should I keep rejected registrations?
A: Keep them for at least 90 days for audit purposes. Archive or delete after 6+ months if not needed.

## Troubleshooting

### I can't see the ID document preview
- Ensure `MEDIA_ROOT` is properly configured
- Check that the file still exists in the server's `media/` directory
- Try refreshing the page

### The search isn't finding registrations
- Make sure spelling is correct
- Try searching with exact values (e.g., full phone number)
- Try filtering instead of searching

### I can't approve a registration
- Make sure you have admin permissions
- Check if you're logged in as superuser or have "Can change pending registration" permission
- Try a different browser (clear cache first)

## Keyboard Shortcuts

- **Ctrl+S** or **Cmd+S**: Save form
- **Tab**: Move to next field
- **Shift+Tab**: Move to previous field

## Contact & Support

If you encounter issues:
1. Check the error message in browser console (F12)
2. Check server logs for Django errors
3. Contact system administrator with:
   - Exact error message
   - Username affected
   - Time of incident
