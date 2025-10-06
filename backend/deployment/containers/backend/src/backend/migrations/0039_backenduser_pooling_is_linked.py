from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0038_userimagefeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='backenduser',
            name='pooling_is_linked',
            field=models.BooleanField(default=False),
        ),
    ]