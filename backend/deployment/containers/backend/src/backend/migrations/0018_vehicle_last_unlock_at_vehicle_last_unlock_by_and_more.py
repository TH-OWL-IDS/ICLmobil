from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_alter_backendpoi_poi_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='last_unlock_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='last_unlock_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='last_unlock_for_booking',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='backend.booking'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='lock_state',
            field=models.CharField(choices=[('unknown', 'Unbekannt'), ('locked', 'Verriegelt'), ('unlocked', 'Entriegelt'), ('failure', 'Fehler')], default='unknown', help_text='Last known lock state (if supported by device)', max_length=20),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='unlock_secret',
            field=models.CharField(blank=True, default=None, help_text='If the user needs to enter something to unlock the vehicle, it must be stored here.', max_length=20, null=True),
        ),
    ]