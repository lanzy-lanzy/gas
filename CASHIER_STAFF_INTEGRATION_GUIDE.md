# Cashier Management - Staff Integration Guide

## Overview

The cashier management system is now **fully integrated** into the Human Resources section of the PrycegasStation application. It's accessible through the sidebar navigation and follows the same design patterns as the existing staff management system.

## Integration Points

### 1. Sidebar Navigation
**Location**: `templates/components/sidebar.html`

The cashier management is integrated into the **Human Resources** section alongside Staff Members and Payroll:

```
Human Resources
├── Staff Members     (for general staff)
├── Cashiers          (NEW - for point of sale staff)
└── Payroll          (for salary management)
```

### 2. URL Structure
All cashier routes are organized under `/admin/cashiers/`:

```
/admin/cashiers/                    - List all cashiers
/admin/cashiers/create/             - Create new cashier
/admin/cashiers/<id>/update/        - Update cashier details
/admin/cashiers/<id>/toggle/        - Toggle active/inactive
/admin/cashiers/dashboard/          - View metrics and activity
/admin/cashiers/orders/manage/      - Create customer orders
/admin/cashiers/transactions/       - View all transactions
/admin/cashiers/payment/record/     - Record payments
/admin/cashiers/performance/        - View performance metrics
```

### 3. Template Organization
All cashier templates are located in `templates/dealer/`:

- `cashier_list.html` - List view with search
- `cashier_form.html` - Create/update form
- `cashier_dashboard.html` - Analytics dashboard
- `manage_customer_order.html` - Order creation interface

## Key Features

### Staff Management Integration

#### Separate but Complementary
- **Staff Members**: General employees with position and salary info
- **Cashiers**: Point-of-sale specialists with transaction tracking
- Both managed through the same HR section
- A staff member can also be a cashier

#### No Conflicts
- Separate models (Staff vs Cashier)
- Separate forms (StaffForm vs CashierCreationForm)
- Separate views (staff_list vs cashier_list)
- Separate templates and database tables
- Django admin remains unchanged and unaffected

### Cashier Dashboard
**URL**: `/admin/cashiers/dashboard/`

Real-time metrics:
- Today's transaction total (₱)
- Today's transaction count
- Total transactions (all-time)
- Active cashier count

Transaction breakdown by type:
- Customer Orders
- Payments Received
- Refunds
- Adjustments

Quick action buttons:
- Create Order (POS)
- Record Payment
- View Performance Metrics
- View All Transactions

### Cashier List Management
**URL**: `/admin/cashiers/`

Features:
- Search by name, username, or employee ID
- Pagination (20 per page)
- Status indicators (Active/Inactive)
- Shift schedule display
- Quick edit button
- Quick toggle (activate/deactivate)
- Creation timestamp

### Create/Update Cashier
**URL**: `/admin/cashiers/create/` and `/admin/cashiers/<id>/update/`

Sections:
1. **User Credentials**
   - Username (unique)
   - Email (unique)
   - First Name
   - Last Name
   - Password

2. **Cashier Details**
   - Employee ID (unique)
   - Active/Inactive toggle

3. **Shift Schedule**
   - Shift Start Time
   - Shift End Time

### Cashier Dashboard Analytics
**URL**: `/admin/cashiers/dashboard/`

Displays:
- Key metrics cards
- Transaction breakdown by type
- Amount totals per transaction type
- Recent transaction history
- Quick links to operations

### Manage Customer Orders
**URL**: `/admin/cashiers/orders/manage/`

For point-of-sale operations:
- Select customer
- Select product
- Enter quantity
- Choose delivery type (Pickup/Delivery)
- Enter delivery address (if delivery)
- Add optional notes
- Automatically creates transaction record
- Reserves stock

### Transaction Tracking
**URL**: `/admin/cashiers/transactions/`

Features:
- View all transactions
- Filter by cashier
- Filter by transaction type
- Filter by date range
- Sortable columns
- Pagination (50 per page)
- Total amount calculation

### Performance Metrics
**URL**: `/admin/cashiers/performance/`

Shows per-cashier:
- Total transaction amount
- Transaction count
- Average transaction amount
- Orders count
- Payments count
- Sorted by top performers

## Admin Interface (Django Admin)

### Cashier Model
**Location**: Django Admin → Core → Cashiers

- List view with key fields
- Search by username, name, or employee ID
- Filter by active status and creation date
- Quick edit of status field
- Full CRUD operations

### CashierTransaction Model
**Location**: Django Admin → Core → Cashier Transactions

- Read-only (transactions cannot be created/edited manually)
- View all transaction details
- Filter by type, method, and date
- Search by cashier or customer
- Audit trail with automatic timestamps

## Workflow Examples

### Example 1: Creating a New Cashier
1. Navigate to **Human Resources** → **Cashiers**
2. Click **Add Cashier**
3. Fill in user credentials (username, email, password, name)
4. Set employee ID (e.g., CSH-001)
5. Set shift times (optional)
6. Click **Create Cashier**
7. System creates User account and Cashier profile automatically
8. Cashier appears in the list and can log in

### Example 2: Processing a Customer Order at POS
1. Navigate to **Cashier Dashboard**
2. Click **Create Order**
3. Select customer from dropdown
4. Select product (only in-stock items shown)
5. Enter quantity
6. Choose delivery type
7. If delivery, enter address
8. Add any notes
9. Click **Create Order**
10. System:
    - Creates Order record
    - Reserves stock
    - Creates CashierTransaction record
    - Redirects to dashboard

### Example 3: Viewing Transaction History
1. Navigate to **Cashier Dashboard**
2. Click **All Transactions**
3. Use filters:
   - By cashier
   - By transaction type
   - By date range
4. View transaction details
5. Pagination for large datasets

### Example 4: Monitoring Cashier Performance
1. Navigate to **Cashier Dashboard**
2. Click **Performance**
3. View metrics for each cashier:
   - Total amount processed
   - Transaction count
   - Average transaction value
   - Breakdown by type

## Security Features

### Admin-Only Access
- All cashier routes protected with `@user_passes_test(is_admin)`
- Only superusers and staff can access
- Regular staff members cannot access cashier management

### Data Integrity
- Unique constraints on username, email, employee ID
- Stock validation before order creation
- Delivery address validation
- Amount validation (must be positive)
- Atomic transactions (all-or-nothing)

### Audit Trail
- All transactions logged with timestamp
- Cashier attribution
- Customer reference
- Payment method documentation
- Optional notes field

### No Manual Data Entry
- CashierTransactions are read-only in admin
- Transactions only created through forms
- Prevents unauthorized manual adjustments
- Complete audit trail for all operations

## Design System Consistency

### Templates
- Follow Tailwind CSS design patterns
- Use existing color scheme (Orange, Blue, Green)
- Consistent spacing and typography
- Responsive grid layouts
- Hover states and transitions

### Navigation
- Integrated into sidebar
- Uses existing icon styles
- Follows menu structure
- Active state indicators

### Forms
- Consistent input styling
- Validation messaging
- Helper text and tooltips
- Section grouping with icons

### Cards and Sections
- Consistent border-radius (rounded-xl)
- Shadow consistency
- Color-coded status badges
- Icon usage patterns

## Database Schema

### Cashier Table
```sql
CREATE TABLE core_cashier (
    id BIGINT PRIMARY KEY,
    user_id INT UNIQUE,
    employee_id VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    shift_start TIME NULL,
    shift_end TIME NULL,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);
```

### CashierTransaction Table
```sql
CREATE TABLE core_cashiertransaction (
    id UUID PRIMARY KEY,
    cashier_id INT,
    order_id INT NULL,
    transaction_type VARCHAR(20),
    amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    customer_id INT NULL,
    notes TEXT,
    created_at DATETIME,
    FOREIGN KEY (cashier_id) REFERENCES core_cashier(id),
    FOREIGN KEY (order_id) REFERENCES core_order(id),
    FOREIGN KEY (customer_id) REFERENCES auth_user(id),
    INDEX (cashier_id, created_at),
    INDEX (transaction_type, created_at)
);
```

## Differences from Staff Management

| Feature | Staff | Cashier |
|---------|-------|---------|
| **Table** | Staff | Cashier + CashierTransaction |
| **Purpose** | General employees | Point-of-sale operations |
| **Fields** | Position, Salary, Hire Date | Employee ID, Shift Times |
| **Transactions** | No tracking | Full audit trail |
| **Access** | General admin | Limited to orders only |
| **Dashboard** | Staff details | Activity metrics |
| **Main Function** | HR management | Order processing |

## Future Enhancements

1. **Shift Clock In/Out**
   - Track actual work hours
   - Compare to scheduled shifts

2. **Commission Calculation**
   - Calculate bonuses based on transactions
   - Monthly commission reports

3. **Export Reports**
   - CSV/PDF export of transactions
   - Customizable date ranges

4. **Role-Based Permissions**
   - Manager override capabilities
   - Different access levels

5. **Performance Alerts**
   - Low performance notifications
   - High transaction alerts

6. **Multi-Cashier Reconciliation**
   - End of shift reconciliation
   - Cash drawer balancing

7. **Refund Processing**
   - Structured refund workflow
   - Approval requirements

8. **Real-Time Notifications**
   - New order alerts
   - Payment confirmations

## Troubleshooting

### Issue: Cashier list page is empty
**Solution**: Navigate to `/admin/cashiers/create/` to add your first cashier

### Issue: Can't create order - product not showing
**Solution**: Make sure the product is active (is_active=True) and has available stock

### Issue: Transactions not appearing in dashboard
**Solution**: Check that transactions were created through the forms, not manually in admin

### Issue: Sidebar link not showing
**Solution**: Ensure you're logged in as a staff/admin user. Customer accounts won't see HR section

## Support & Documentation

For more information:
- Backend: `CASHIER_MANAGEMENT_IMPLEMENTATION.md`
- Quick Reference: `CASHIER_QUICK_REFERENCE.md`
- Django Admin: Built-in documentation
- Source Code: `core/cashier_views.py`, `core/forms.py`, `core/models.py`
