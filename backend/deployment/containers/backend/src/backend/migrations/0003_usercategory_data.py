from django.db import migrations

from backend.models import UserCategory


def add_data(apps, schema_editor):
    from django.conf import settings
    for uc_id, name, description in (
        (0, ('Unbekannt', 'Unknown'), ('Unbekannt', 'Unknown')),
        (1, ('ICL e.V.', 'ICL e.V.'), ('Mitarbeitende des ICL e.V.', 'ICL e.V. staff')),
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
        ('backend', '0002_co2e_data'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]