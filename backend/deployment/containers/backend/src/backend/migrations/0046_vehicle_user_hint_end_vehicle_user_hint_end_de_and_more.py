from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0045_vehicle_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='user_hint_end',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user that is displayed when the booking is finished. Example usage would be to indicate where a helmet should be placed.', null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='user_hint_end_de',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user that is displayed when the booking is finished. Example usage would be to indicate where a helmet should be placed.', null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='user_hint_end_en',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user that is displayed when the booking is finished. Example usage would be to indicate where a helmet should be placed.', null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='user_hint_start',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user that is displayed when the booking is started. Example usage would be to indicate where a helmet can be found.', null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='user_hint_start_de',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user that is displayed when the booking is started. Example usage would be to indicate where a helmet can be found.', null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='user_hint_start_en',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user that is displayed when the booking is started. Example usage would be to indicate where a helmet can be found.', null=True),
        ),
    ]