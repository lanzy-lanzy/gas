# Generated migration for adding delivery_person_name field to Order model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_order_processed_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_person_name',
            field=models.CharField(blank=True, help_text='Name of the delivery person who delivered the order', max_length=100),
        ),
    ]
