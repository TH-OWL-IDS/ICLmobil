import backend.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0049_configuration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuration',
            name='value',
            field=models.JSONField(encoder=backend.models.PrettyJSONEncoder),
        ),
    ]