from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0026_vehicle_unlock_secret_user_hint_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='backenduser',
            name='score_experience',
            field=models.FloatField(default=0.0, help_text='Score from 0 to 5 that rises with experience in the app'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='score_points',
            field=models.IntegerField(default=0, help_text='Different actions in the app lead to an increase in points'),
        ),
        migrations.AddField(
            model_name='booking',
            name='score_needs_update',
            field=models.BooleanField(default=False, verbose_name='Set on save to trigger background recalculation of user score'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['score_needs_update'], include=('user',), name='booking_snuu'),
        ),
    ]