from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0025_booking_start_time_before_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='unlock_secret_user_hint',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user where the unlock secret is found. Is shown to the user before they need to enter the unlock secret.', null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='unlock_secret_user_hint_de',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user where the unlock secret is found. Is shown to the user before they need to enter the unlock secret.', null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='unlock_secret_user_hint_en',
            field=models.TextField(blank=True, default=None, help_text='A hint for the user where the unlock secret is found. Is shown to the user before they need to enter the unlock secret.', null=True),
        ),
    ]