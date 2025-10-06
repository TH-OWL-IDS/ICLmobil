import os

from django.db import migrations


def add_data(apps, schema_editor):
    from django.conf import settings
    from backend import files
    from filer.models import Folder
    folder, created = Folder.objects.get_or_create(name="CMS")
    files.filer_upload_all_from_folder(os.path.join(os.path.dirname(__file__), "images"), folder)

class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0008_alter_vehicle_vehicle_type'),
        ('easy_thumbnails', '0002_thumbnaildimensions'),
        ('filer', '0017_image__transparent'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]


