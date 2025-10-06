from django.db import migrations

from backend.constants import TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT


def add_periodic_task_poit_update(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")  # type: import django_celery_beat.models.CrontabSchedule
    cs, _ = CrontabSchedule.objects.get_or_create(
        hour='4',
        minute='0',
    )
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    pt, _ = PeriodicTask.objects.get_or_create(
        name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT,
        defaults={
            'task': TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT,
            'crontab': cs,
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0011_news_sampledata'),
        ('django_celery_beat', '0019_alter_periodictasks_options'),
    ]

    operations = [
        migrations.RunPython(add_periodic_task_poit_update),
    ]