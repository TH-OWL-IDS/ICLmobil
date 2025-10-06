from django.db import migrations



def add_data(apps, schema_editor):
    from django.db import connection
    from backend.enum import OptionType
    with connection.cursor() as cursor:
        for mot, quantity in (
                (OptionType.own_scooter, 0),
        ):
            cursor.execute("INSERT INTO backend_co2eemission (mode_of_transport, per_unit, quantity) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", [
                mot.value, 'g/Pkm', quantity
            ])


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0029_fix_sequences'),
    ]

    operations = [
        migrations.RunPython(add_data),
        migrations.RunSQL("""
            BEGIN;
            LOCK TABLE backend_co2eemission IN EXCLUSIVE MODE;
            SELECT setval('backend_co2eemission_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_co2eemission_id_seq')-1) FROM backend_co2eemission));
            COMMIT;
            """),
    ]


