# Customers List - PDF Export Implementation

## Summary of Changes

### 1. **Page Title Update**
   - Changed "Pending Registrations" → "Customers List"
   - Updated in: `templates/dealer/pending_registrations_list.html` (Line 7)

### 2. **Export PDF Functionality Added**
   - Added export buttons for each registration status:
     - **Export Pending**: Exports only pending registrations (Orange button)
     - **Export Approved**: Exports only approved registrations (Green button)
     - **Export Rejected**: Exports only rejected registrations (Red button)
     - **Export All**: Exports all registrations regardless of status (Blue button)

### 3. **New Backend Function**
   - Created `export_registrations_pdf()` view in `core/views.py`
   - Location: Lines 3122-3237
   - Features:
     - Filters registrations by status (pending, approved, rejected, all)
     - Generates professional PDF with:
       - Branded header with Prycegas colors (#FF6633)
       - Summary statistics (total counts by status)
       - Formatted table with columns:
         * Username
         * Email
         * Phone
         * ID Type
         * Status
         * Submitted Date
       - Footer with generation timestamp
     - Automatic filename based on filter: `customers_list_{status}.pdf`

### 4. **URL Route**
   - Added new route in `core/urls.py` (Line 129):
     ```
     path('dealer/pending-registrations/export/pdf/', export_registrations_pdf, name='export_registrations_pdf')
     ```
   - Imported function in urls.py Line 16

### 5. **Security**
   - Protected with `@user_passes_test(is_dealer, login_url='core:login')`
   - Only dealer users can access the export functionality
   - Protected view requires authentication

### 6. **UI/UX Features**
   - Export buttons appear conditionally based on current filter view
   - Color-coded buttons matching status indicators
   - Responsive layout with buttons aligned to the right
   - Icons using Font Awesome (fa-file-pdf)
   - Hover effects for better UX

## Files Modified
1. `templates/dealer/pending_registrations_list.html` - Added export buttons
2. `core/views.py` - Added export_registrations_pdf function
3. `core/urls.py` - Added URL route and imported new function

## How to Use
1. Navigate to "Customers List" page (Dealer menu > Pending Registrations)
2. Select desired status filter (Pending, Approved, Rejected, or All)
3. Click the corresponding "Export [Status]" button
4. PDF will download automatically with filtered registration data

## PDF Export Format
- **Page Size**: A4
- **Orientation**: Portrait
- **Styling**: Professional table with alternating row colors
- **Title**: Branded with Prycegas orange color
- **Summary**: Shows counts of all registration statuses
- **Timestamp**: Generated date/time in footer

## Testing
- Test each status filter (Pending, Approved, Rejected, All)
- Verify PDF downloads with correct filename
- Verify only authorized users (dealers) can access
- Confirm data accuracy in exported PDF
