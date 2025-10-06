from django.db import migrations

from backend.enum import VehicleType
from backend.models import Vehicle


def add_data(apps, schema_editor):
    from django.conf import settings
    from django.contrib.gis.geos import Point
    from django.db import connection
    with connection.cursor() as cursor:
        for v_id, vt, model, vehicle_number, provider_name, provider_id, battery_level_percent, remaining_range_km, location in (
                (0, VehicleType.bike, 'Dummy Bike', '#1001', 'ICL', 'ABC', None, None, Point(8.9051603, 52.0181228, srid=4326)), # Lon/Lat
                (1, VehicleType.bike, 'Dummy Bike', '#1002', 'ICL', 'DEF', None, None, Point(8.9091419, 52.025383, srid=4326)),  # Lon/Lat
                (2, VehicleType.scooter, 'Dummy E-Scooter', 'E3F-E07', 'ICL', 'E3F-E07', 100.0, 40.0, Point(8.90350, 52.0179178 , srid=4326)),  # Lon/Lat
                (3, VehicleType.scooter, 'Dummy E-Scooter', 'ONE-BDI', 'ICL', 'ONE-BDI', 80.0, 32.0, Point(8.90351, 52.0179178, srid=4326)),  # Lon/Lat
                (4, VehicleType.scooter, 'Dummy E-Scooter', 'YE5-PH3', 'ICL', 'YE5-PH3', 10.0, 4.0, Point(8.90352, 52.0179178, srid=4326)),  # Lon/Lat
                (5, VehicleType.scooter, 'Dummy E-Scooter', 'UTH-8AU', 'ICL', 'UTH-8AU', 0.0, 0.0, Point(8.90353, 52.0179178, srid=4326)),  # Lon/Lat
        ):
            cursor.execute("INSERT INTO backend_vehicle (id, vehicle_type, vehicle_model, vehicle_number, provider_name, provider_id, battery_level_percent, remaining_range_km, location, last_updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText('POINT(%s %s)', 4326), current_timestamp) ON CONFLICT DO NOTHING;", [
                v_id,
                vt,
                model,
                vehicle_number,
                provider_name,
                provider_id,
                battery_level_percent,
                remaining_range_km,
                location[0], location[1],
            ])


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0003_usercategory_data'),
    ]

    operations = [
        migrations.RunPython(add_data),
        migrations.RunSQL("""
    BEGIN;
    LOCK TABLE backend_vehicle IN EXCLUSIVE MODE;
    SELECT setval('backend_vehicle_id_seq',(SELECT GREATEST(MAX(id), nextval('backend_vehicle_id_seq')-1) FROM backend_vehicle));
    COMMIT;
    """),

    ]


