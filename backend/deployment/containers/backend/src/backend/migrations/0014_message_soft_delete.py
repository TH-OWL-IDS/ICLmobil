from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_pushnotificationdevice_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='soft_delete',
            field=models.BooleanField(default=False, help_text='Set when user manually deletes message'),
        ),
    ]