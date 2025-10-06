import backend.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0042_booking_planned_end_time_booking_planned_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='backenduser',
            name='auth_key_external_service',
            field=models.CharField(default=backend.models.get_random_string_32, max_length=32),
        ),
    ]