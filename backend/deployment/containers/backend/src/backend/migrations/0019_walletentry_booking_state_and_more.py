import backend.enum
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0018_vehicle_last_unlock_at_vehicle_last_unlock_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='walletentry',
            name='booking_state',
            field=models.CharField(blank=True, choices=[('created', 'Erzeugt'), ('planned', 'Geplant'), ('started', 'Gestartet'), ('finished', 'Abgeschlossen'), ('timeout', 'Timeout'), ('canceled', 'Storniert')], default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='walletentry',
            name='trip_distance_m',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='walletentry',
            name='trip_mode',
            field=models.CharField(blank=True, choices=[('pt', 'ÖPNV'), ('sharing', 'Sharing'), ('rriveUse', 'RRive als Mitfahrer'), ('rriveOffer', 'RRive Mitfahrt anbieten'), ('static', 'Statisches Angebot'), ('car', 'Auto'), ('walk', 'Fußweg')], default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='walletentry',
            name='vehicle_model',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='walletentry',
            name='vehicle_number',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='walletentry',
            name='vehicle_type',
            field=models.CharField(blank=True, choices=[('unknown', '-'), ('bike', 'Fahrrad'), ('scooter', 'E-Scooter')], default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='state',
            field=models.CharField(choices=[('created', 'Erzeugt'), ('planned', 'Geplant'), ('started', 'Gestartet'), ('finished', 'Abgeschlossen'), ('timeout', 'Timeout'), ('canceled', 'Storniert')], default=backend.enum.BookingState['created'], max_length=20),
        ),
    ]