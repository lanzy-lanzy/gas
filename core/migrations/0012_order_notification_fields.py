# Generated migration for Order and Notification models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_order_customer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancellation_reason',
            field=models.TextField(blank=True, help_text='Reason for order cancellation (if cancelled)'),
        ),
        migrations.AddField(
            model_name='order',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, help_text='When the order was cancelled', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='cancelled_by',
            field=models.ForeignKey(blank=True, help_text='User who cancelled the order', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cancelled_orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('order_cancelled', 'Order Cancelled'), ('order_updated', 'Order Updated'), ('order_delivered', 'Order Delivered'), ('order_out_for_delivery', 'Order Out for Delivery'), ('system_message', 'System Message')], help_text='Type of notification', max_length=50)),
                ('title', models.CharField(help_text='Notification title', max_length=255)),
                ('message', models.TextField(help_text='Notification message content')),
                ('reason', models.TextField(blank=True, help_text='Reason for cancellation (if order cancelled)')),
                ('is_read', models.BooleanField(default=False, help_text='Whether the customer has read this notification')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, help_text='When the notification was read', null=True)),
                ('customer', models.ForeignKey(help_text='Customer receiving the notification', on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, help_text='Related order (if applicable)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='core.order')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['customer', '-created_at'], name='core_notifi_custome_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['customer', 'is_read'], name='core_notifi_custome_is_read_idx'),
        ),
    ]
