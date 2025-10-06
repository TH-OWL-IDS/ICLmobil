from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0040_backendsyncprogress'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='external_distance_m',
            field=models.FloatField(blank=True, default=None, help_text='Distanz in Metern gemeldet von externer Quelle', null=True, verbose_name='Externe Distanz'),
        ),
    ]