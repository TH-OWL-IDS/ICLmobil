from django.db import migrations



def add_data(apps, schema_editor):
    from django.db import connection
    from backend.enum import OptionType
    with connection.cursor() as cursor:
        for mot, quantity in (
                (OptionType.own_bike, 0),
        ):
            cursor.execute("INSERT INTO backend_co2eemission (mode_of_transport, per_unit, quantity) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", [
                mot.value, 'g/Pkm', quantity
            ])


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0021_alter_booking_trip_mode_and_more'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]


