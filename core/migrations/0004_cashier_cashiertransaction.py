# Generated migration for Cashier models

from django.conf import settings
from django.core import validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0003_productcategory_supplier_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cashier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(help_text='Unique employee ID', max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Cashier status')),
                ('shift_start', models.TimeField(blank=True, help_text='Cashier shift start time', null=True)),
                ('shift_end', models.TimeField(blank=True, help_text='Cashier shift end time', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cashier_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cashier',
                'verbose_name_plural': 'Cashiers',
                'ordering': ['user__username'],
            },
        ),
        migrations.CreateModel(
            name='CashierTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('order', 'Customer Order'), ('payment', 'Payment Received'), ('refund', 'Refund'), ('adjustment', 'Transaction Adjustment')], help_text='Type of transaction', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Transaction amount', max_digits=10, validators=[validators.MinValueValidator(0)])),
                ('payment_method', models.CharField(default='cash', help_text='Payment method (cash, card, check, etc.)', max_length=50)),
                ('notes', models.TextField(blank=True, help_text='Additional transaction notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cashier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.cashier')),
                ('customer', models.ForeignKey(help_text='Customer involved in the transaction', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cashier_transactions', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cashier_transactions', to='core.order')),
            ],
            options={
                'verbose_name': 'Cashier Transaction',
                'verbose_name_plural': 'Cashier Transactions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='cashiertransaction',
            index=models.Index(fields=['cashier', '-created_at'], name='core_cashier_cashier_7a8b9c_idx'),
        ),
        migrations.AddIndex(
            model_name='cashiertransaction',
            index=models.Index(fields=['transaction_type', '-created_at'], name='core_cashier_transac_2f1a8b_idx'),
        ),
    ]
