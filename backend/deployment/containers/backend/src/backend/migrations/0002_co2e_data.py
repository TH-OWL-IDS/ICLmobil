from django.db import migrations

from backend.enum import OptionType
from backend.models import CO2eEmission


def add_data(apps, schema_editor):
    from django.db import connection
    # Data from: https://www.umweltbundesamt.de/bild/vergleich-der-durchschnittlichen-emissionen-0
    with connection.cursor() as cursor:
        for mot, quantity in (
            (OptionType.pt, 93),      # Linienbus Nahverkehr
            (OptionType.sharing, 3),  # E-Bike
            (OptionType.car, 166),    # Pkw
        ):
            cursor.execute(
                "INSERT INTO backend_co2eemission (mode_of_transport, per_unit, quantity) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                [
                    mot.value, 'g/Pkm', quantity
                ])

        #created, co2e = CO2eEmission.objects.get_or_create(mode_of_transport=mot, per_unit='g/Pkm', defaults={'quantity': quantity})
        #co2e.quantity = quantity
        #co2e.save()

class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]