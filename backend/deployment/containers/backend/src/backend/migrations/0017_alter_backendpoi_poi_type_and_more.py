import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_usercategory_data2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backendpoi',
            name='poi_type',
            field=models.IntegerField(choices=[(0, 'Unbekannt'), (1, 'Bushaltestelle'), (2, 'Straßenbahn'), (3, 'Zug'), (5, 'Well-known')], default=0),
        ),
        migrations.AlterField(
            model_name='backendpoi',
            name='source_acquired_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Only relevant for automatic POI sync: When was this POI acquired', null=True),
        ),
        migrations.AlterField(
            model_name='backendpoi',
            name='source_id',
            field=models.CharField(blank=True, help_text='Only relevant for automatic POI sync: Distinguishes between POIs of one sync source', max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='backendpoi',
            name='source_properties',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Only relevant for automatic POI sync: Metadata from POI source for this ID', null=True),
        ),
        migrations.AlterField(
            model_name='backendpoi',
            name='source_type',
            field=models.CharField(blank=True, help_text='Only relevant for automatic POI sync: Distinguishes between different sync sources', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='push_notification_done',
            field=models.BooleanField(default=False, help_text='Wird gesetzt, nachdem alle registrierten Device Tokens bedient wurden'),
        ),
        migrations.AlterField(
            model_name='message',
            name='push_notification_no_later_than',
            field=models.DateTimeField(blank=True, help_text='Erstes oder wiederholtes senden von Push Notifications nicht nach diesem Zeitpunkt', null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='push_notification_requested',
            field=models.BooleanField(default=False, help_text='Push Notification an registrierte Geräte senden'),
        ),
        migrations.AlterField(
            model_name='message',
            name='soft_delete',
            field=models.BooleanField(default=False, help_text='Wird gesetzt, wenn der Benutzer die Message löscht'),
        ),
    ]