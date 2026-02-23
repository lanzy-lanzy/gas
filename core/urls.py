from django.urls import path
from .views import (
    test_base_template, customer_register, customer_login, customer_logout,
    customer_profile, validate_username, validate_email, customer_dashboard,
    place_order, check_stock, get_product_details, order_history, order_detail, refresh_order_status,
    mark_order_received, refresh_dashboard_orders, dealer_dashboard, refresh_dashboard_stats,
    refresh_recent_activity, order_management, update_order_status,
    order_detail_modal, bulk_order_operations, refresh_order_table,
    batch_order_detail_modal, update_batch_order_status,
    inventory_management, log_delivery, refresh_inventory_dashboard,
    refresh_stock_movements, get_delivery_form, delivery_log, reports_dashboard,
    product_info,
    sales_report, stock_report, print_report, lazy_load_orders,
    lazy_load_customer_orders, product_management, add_product, edit_product,
    delete_product, reactivate_product, inventory_adjustment, stock_movements, low_stock_alert, inventory_reports,
    staff_list, staff_detail, staff_create, staff_update, staff_delete, payroll_list, payroll_create, payroll_report,
    pending_registrations_list, pending_registration_detail, approve_registration, reject_registration, export_registrations_pdf,
    create_category, get_categories, export_order_history_pdf
    , export_stock_report_pdf, export_sales_report_pdf,
    customer_notifications, mark_notification_as_read, mark_all_notifications_as_read, 
    get_unread_notifications_count, cancel_order,
    stock_in_list, stock_out_list,
    remove_profile_picture
)
from .cashier_views import (
    cashier_list, cashier_create, cashier_update, cashier_toggle_status,
    cashier_dashboard, cashier_personal_dashboard, cashier_order_list, manage_customer_order, cashier_transactions,
    record_payment, cashier_performance, cashier_daily_income_report, cashier_inventory_impact_report,
    cashier_personal_reports_daily, cashier_personal_reports_monthly, export_daily_report_pdf, export_monthly_report_pdf
)
from .cashier_reports import (
    cashier_reports, cashier_daily_report, cashier_monthly_report, cashier_yearly_report
)
from .cashier_walkin_view import cashier_walkin_order

app_name = 'core'

urlpatterns = [
    path('', test_base_template, name='home'),
    path('test/', test_base_template, name='test_base'),

    # Authentication URLs
    path('register/', customer_register, name='register'),
    path('login/', customer_login, name='login'),
    path('logout/', customer_logout, name='logout'),
    path('profile/', customer_profile, name='profile'),
    path('profile/remove-picture/', remove_profile_picture, name='remove_profile_picture'),

    # HTMX validation endpoints
    path('validate-username/', validate_username, name='validate_username'),
    path('validate-email/', validate_email, name='validate_email'),

    # Customer URLs
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'),
    path('customer/order/', place_order, name='place_order'),
    path('customer/history/', order_history, name='order_history'),
    path('customer/history/export-pdf/', export_order_history_pdf, name='export_order_history_pdf'),
    path('customer/order/<int:order_id>/', order_detail, name='order_detail'),
    path('customer/order/<int:order_id>/received/', mark_order_received, name='mark_order_received'),
    path('customer/order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    
    # Notification URLs
    path('customer/notifications/', customer_notifications, name='customer_notifications'),
    path('customer/notifications/<int:notification_id>/read/', mark_notification_as_read, name='mark_notification_as_read'),
    path('customer/notifications/read-all/', mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('api/notifications/unread-count/', get_unread_notifications_count, name='get_unread_notifications_count'),
    
    # HTMX endpoints for order system
    path('check-stock/', check_stock, name='check_stock'),
    path('get-product-details/', get_product_details, name='get_product_details'),
    path('refresh-orders/', refresh_order_status, name='refresh_order_status'),
    path('refresh-dashboard/', refresh_dashboard_orders, name='refresh_dashboard_orders'),

    # Dealer URLs
    path('dealer/dashboard/', dealer_dashboard, name='dealer_dashboard'),
    path('dealer/orders/', order_management, name='order_management'),
    path('dealer/inventory/', inventory_management, name='inventory_management'),
    path('dealer/delivery-log/', delivery_log, name='delivery_log'),
    path('dealer/reports/', reports_dashboard, name='reports_dashboard'),
    path('dealer/reports/sales/', sales_report, name='sales_report'),
    path('dealer/reports/stock/', stock_report, name='stock_report'),
    path('dealer/reports/stock/export-pdf/', export_stock_report_pdf, name='export_stock_report_pdf'),
    path('dealer/reports/sales/export-pdf/', export_sales_report_pdf, name='export_sales_report_pdf'),
    path('dealer/reports/print/', print_report, name='print_report'),
    
    # HTMX/Unpoly endpoints for dealer dashboard
    path('dealer/refresh-stats/', refresh_dashboard_stats, name='refresh_dashboard_stats'),
    path('dealer/refresh-activity/', refresh_recent_activity, name='refresh_recent_activity'),
    
    # Order management endpoints
    path('dealer/orders/update/<int:order_id>/', update_order_status, name='update_order_status'),
    path('dealer/orders/detail/<int:order_id>/', order_detail_modal, name='order_detail_modal'),
    path('dealer/orders/bulk/', bulk_order_operations, name='bulk_order_operations'),
    path('dealer/orders/refresh/', refresh_order_table, name='refresh_order_table'),
    path('dealer/orders/batch/<uuid:batch_id>/detail/', batch_order_detail_modal, name='batch_order_detail_modal'),
    path('dealer/orders/batch/<uuid:batch_id>/update/', update_batch_order_status, name='update_batch_order_status'),
    
    # Inventory management endpoints
    path('dealer/inventory/log-delivery/', log_delivery, name='log_delivery'),
    path('dealer/inventory/refresh/', refresh_inventory_dashboard, name='refresh_inventory_dashboard'),
    path('dealer/inventory/movements/', refresh_stock_movements, name='refresh_stock_movements'),
    path('dealer/inventory/delivery-form/', get_delivery_form, name='get_delivery_form'),
    path('dealer/inventory/product-info/<int:product_id>/', product_info, name='product_info'),

    # Enhanced inventory management endpoints
    path('dealer/products/', product_management, name='product_management'),
    path('dealer/products/add/', add_product, name='add_product'),
    path('dealer/products/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('dealer/products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('dealer/products/<int:product_id>/reactivate/', reactivate_product, name='reactivate_product'),
    path('dealer/inventory/adjustment/', inventory_adjustment, name='inventory_adjustment'),
    path('dealer/inventory/stock-movements/', stock_movements, name='stock_movements'),
    path('dealer/inventory/low-stock/', low_stock_alert, name='low_stock_alert'),
    path('dealer/inventory/reports/', inventory_reports, name='inventory_reports'),
    path('dealer/inventory/stock-in/', stock_in_list, name='stock_in_list'),
    path('dealer/inventory/stock-out/', stock_out_list, name='stock_out_list'),
    
    # Category management API endpoints
    path('api/categories/create/', create_category, name='create_category'),
    path('api/categories/', get_categories, name='get_categories'),

    # Staff and Payroll URLs
    path('dealer/staff/', staff_list, name='staff_list'),
    path('dealer/staff/create/', staff_create, name='staff_create'),
    path('dealer/staff/<int:staff_id>/', staff_detail, name='staff_detail'),
    path('dealer/staff/<int:staff_id>/update/', staff_update, name='staff_update'),
    path('dealer/staff/<int:staff_id>/delete/', staff_delete, name='staff_delete'),
    path('dealer/payroll/', payroll_list, name='payroll_list'),
    path('dealer/payroll/create/', payroll_create, name='payroll_create'),
    path('dealer/payroll/report/', payroll_report, name='payroll_report'),
    
    # Pending Registrations
    path('dealer/pending-registrations/', pending_registrations_list, name='pending_registrations'),
    path('dealer/pending-registrations/<int:registration_id>/', pending_registration_detail, name='registration_detail'),
    path('dealer/pending-registrations/<int:registration_id>/approve/', approve_registration, name='approve_registration'),
    path('dealer/pending-registrations/<int:registration_id>/reject/', reject_registration, name='reject_registration'),
    path('dealer/pending-registrations/export/pdf/', export_registrations_pdf, name='export_registrations_pdf'),
    
    # Lazy loading endpoints for performance optimization
    path('api/orders/lazy/', lazy_load_orders, name='lazy_load_orders'),
    path('api/customer/orders/lazy/', lazy_load_customer_orders, name='lazy_load_customer_orders'),

    # Cashier URLs (for cashier users)
    path('cashier/dashboard/', cashier_personal_dashboard, name='cashier_personal_dashboard'),
    path('cashier/orders/', cashier_order_list, name='cashier_order_list'),
    path('cashier/walkin-order/', cashier_walkin_order, name='cashier_walkin_order'),
    path('cashier/reports/daily/', cashier_personal_reports_daily, name='cashier_personal_reports_daily'),
    path('cashier/reports/monthly/', cashier_personal_reports_monthly, name='cashier_personal_reports_monthly'),
    path('cashier/reports/daily/export-pdf/', export_daily_report_pdf, name='export_daily_report_pdf'),
    path('cashier/reports/monthly/export-pdf/', export_monthly_report_pdf, name='export_monthly_report_pdf'),
    
    # Cashier Management URLs (Admin only)
    path('dealer/cashiers/', cashier_list, name='cashier_list'),
    path('dealer/cashiers/create/', cashier_create, name='cashier_create'),
    path('dealer/cashiers/<int:cashier_id>/update/', cashier_update, name='cashier_update'),
    path('dealer/cashiers/<int:cashier_id>/toggle/', cashier_toggle_status, name='cashier_toggle_status'),
    path('dealer/cashiers/dashboard/', cashier_dashboard, name='cashier_dashboard'),
    path('dealer/cashiers/orders/manage/', manage_customer_order, name='manage_customer_order'),
    path('dealer/cashiers/transactions/', cashier_transactions, name='cashier_transactions'),
    path('dealer/cashiers/payment/record/', record_payment, name='record_payment'),
    path('dealer/cashiers/performance/', cashier_performance, name='cashier_performance'),
    path('dealer/cashiers/reports/daily-income/', cashier_daily_income_report, name='cashier_daily_income_report'),
    path('dealer/cashiers/reports/inventory-impact/', cashier_inventory_impact_report, name='cashier_inventory_impact_report'),
    path('dealer/cashiers/reports/', cashier_reports, name='cashier_reports'),
    path('dealer/cashiers/reports/daily/', cashier_daily_report, name='cashier_reports_daily'),
    path('dealer/cashiers/reports/monthly/', cashier_monthly_report, name='cashier_reports_monthly'),
    path('dealer/cashiers/reports/yearly/', cashier_yearly_report, name='cashier_reports_yearly'),
]
