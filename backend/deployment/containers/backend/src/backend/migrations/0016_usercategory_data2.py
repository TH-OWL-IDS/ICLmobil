from django.db import migrations

from backend.models import UserCategory


def add_data(apps, schema_editor):
    from django.conf import settings
    for uc_id, name, description in (
        (2, ('Schüler', 'Pupil'), ('Schüler', 'Pupil')),
        (3, ("Mitarbeiter Hochschule", "Employee Hochschule"),("Mitarbeiter Hochschule", "Employee Hochschule")),
        (4, ("Mitarbeiter Schule", "Employee School"),("Mitarbeiter Schule", "Employee School")),
        (5, ("Mitarbeiter Unternehmen", "Employee Company"),("Mitarbeiter Unternehmen", "Employee Company")),
    ):
        created, _ = UserCategory.objects.get_or_create(id=uc_id, defaults={
            'name': name[0],
            'name_de': name[0],
            'name_en': name[1],
            'description': description[0],
            'description_de': description[0],
            'description_en': description[1],
        })

class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_alter_booking_trip_mode_and_more'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]