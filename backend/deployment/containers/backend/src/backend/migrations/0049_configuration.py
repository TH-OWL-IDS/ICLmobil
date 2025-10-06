import json

from django.db import migrations, models

def add_data(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        for rid, key, value, schema in (
                (1, "AppConfig", json.dumps({
  "MAPBOX_API": "https://api.mapbox.com",
  "MAPBOX_TOKEN": "",
  "MAPBOX_DRIVING_URI": "/directions/v5/mapbox/driving/",
  "MAPBOX_WALKING_URI": "/directions/v5/mapbox/walking/",
  "MAPBOX_CYCLING_URI": "/directions/v5/mapbox/cycling/",
  "MAPBOX_PLACES_URI": "/geocoding/v5/mapbox.places/",
  "MAPBOX_STYLE": "mapbox://styles/mapbox/streets-v12",
  "MAPBOX_BBOX_COORDS": [8.80576, 51.975857, 8.997129, 52.104398],
  "POOLING_DOWNLOAD_URLS": {
    "development": "https://rrive.com/Home/IclTestApps",
    "production": "https://rrive.com/Home/App"
  },
  "POOLING_URLS": {
    "development": "https://website-develop.rrive.com/dl-dev",
    "production": "https://rrive.com/dl"
  },
  "POOLING_REGISTER": "/icl/",
  "POOLING_PLANNED_DRIVER": "/tab/2/trips/planned/offer/",
  "POOLING_PREVIOUS_DRIVER": "/tab/2/trips/past/offer/",
  "POOLING_PLANNED_PASSENGER": "/tab/2/trips/planned/booking/",
  "POOLING_PREVIOUS_PASSENGER": "/tab/2/trips/past/booking/",
  "POOLING_RIDE_OFFER": "/tab/1/rideoffer/"
}, indent=4), 'backend.api_v1.schemas.FrontendAppConfig'),
        ):
            cursor.execute("INSERT INTO backend_configuration (id, key, value, schema) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;", [
                rid, key, value, schema
            ])


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0048_alter_booking_external_distance_m_and_more'),
    ]


    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=50, unique=True)),
                ('value', models.JSONField()),
                ('schema', models.CharField(blank=True, help_text='If set, the dot-delimited python module and class name of the schema to check the value against', null=True)),
            ],
        ),
        migrations.RunPython(add_data),
        migrations.RunSQL("""
            BEGIN;
                LOCK TABLE backend_configuration IN EXCLUSIVE MODE;
                SELECT setval('backend_configuration_id_seq',
                (SELECT GREATEST(1, MAX(id), nextval('backend_configuration_id_seq') - 1)
                FROM backend_configuration));
            COMMIT;
        """),
    ]