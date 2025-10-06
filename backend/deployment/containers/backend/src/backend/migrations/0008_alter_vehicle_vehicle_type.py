from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_booking_sample_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_type',
            field=models.CharField(choices=[('unknown', '-'), ('bike', 'Fahrrad'), ('scooter', 'E-Scooter')], default='unknown', max_length=20),
        ),
    ]