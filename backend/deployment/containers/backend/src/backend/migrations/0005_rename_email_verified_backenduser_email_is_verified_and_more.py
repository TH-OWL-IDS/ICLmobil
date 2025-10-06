import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_vehicle_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='backenduser',
            old_name='email_verified',
            new_name='email_is_verified',
        ),
        migrations.RenameField(
            model_name='backenduser',
            old_name='mobile_number',
            new_name='mobile_number_unverified',
        ),
        migrations.AddField(
            model_name='backenduser',
            name='email_next',
            field=models.EmailField(blank=True, default=None, max_length=254, null=True, unique=True, verbose_name='Neue, noch nicht verifizierte E-Mail-Adresse'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='mobile_number_is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='backenduser',
            name='mobile_number_verified',
            field=models.CharField(blank=True, default='', max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+49170999999999'. Up to 15 digits allowed.", regex='^\\+[1-9]\\d{1,14}$')]),
        ),
    ]