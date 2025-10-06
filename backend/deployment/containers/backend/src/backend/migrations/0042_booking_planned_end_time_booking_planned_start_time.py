from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0041_booking_external_distance_m'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='planned_end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='planned_start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]