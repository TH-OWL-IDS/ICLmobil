from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0023_booking_non_overlapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='booking',
            field=models.ForeignKey(blank=True, default=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.booking'),
        ),
        migrations.AddField(
            model_name='message',
            name='publish_after',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='purpose',
            field=models.CharField(blank=True, choices=[('booking_start_reminder', 'Erinnerung an bevorstehende Buchung')], default=None, max_length=50, null=True),
        ),
    ]