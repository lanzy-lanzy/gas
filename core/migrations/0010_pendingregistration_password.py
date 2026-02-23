# Generated migration to add password field to PendingRegistration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_core_pending__status_idx_core_pendin_status_2239f1_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingregistration',
            name='password',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
