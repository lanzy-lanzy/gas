# Generated migration for PendingRegistration model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0007_order_delivery_person_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('delivery_instructions', models.TextField(blank=True)),
                ('id_type', models.CharField(choices=[('national_id', 'National ID'), ('drivers_license', "Driver's License"), ('passport', 'Passport'), ('barangay_id', 'Barangay ID'), ('sss_id', 'SSS ID'), ('tin_id', 'TIN ID'), ('company_id', 'Company ID'), ('other', 'Other')], max_length=50)),
                ('id_number', models.CharField(max_length=100)),
                ('id_document', models.ImageField(help_text='Upload a clear image of the ID document', upload_to='pending_registrations/id_documents/%Y/%m/%d/')),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('rejection_reason', models.TextField(blank=True, help_text='Reason for rejection')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reviewed_by', models.ForeignKey(blank=True, help_text='Admin user who reviewed this registration', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_registrations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pending Registration',
                'verbose_name_plural': 'Pending Registrations',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pendingregistration',
            index=models.Index(fields=['status', '-created_at'], name='core_pending__status_idx'),
        ),
        migrations.AddIndex(
            model_name='pendingregistration',
            index=models.Index(fields=['-created_at'], name='core_pending__created_idx'),
        ),
    ]
