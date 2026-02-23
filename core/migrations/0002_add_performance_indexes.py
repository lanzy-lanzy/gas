# Generated migration for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_order_customer_status ON core_order(customer_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_order_customer_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_order_date_status ON core_order(order_date, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_order_date_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_order_product_date ON core_order(product_id, order_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_order_product_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_stock_active ON core_lpgproduct(current_stock, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_stock_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_delivery_log_product_date ON core_deliverylog(product_id, delivery_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_delivery_log_product_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_customer_profile_user ON core_customerprofile(user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_customer_profile_user;"
        ),
    ]