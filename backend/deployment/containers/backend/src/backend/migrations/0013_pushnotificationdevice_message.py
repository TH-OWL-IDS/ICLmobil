from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_data_crontabtasks'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotificationDevice',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('device_model', models.CharField(blank=True, max_length=200, null=True, verbose_name='Gerätetyp')),
                ('push_system', models.CharField(choices=[('apple', 'Apple APNS'), ('android', 'Android')], max_length=20)),
                ('token', models.CharField(max_length=200, verbose_name='Token')),
                ('state', models.CharField(choices=[('valid', 'Valid'), ('invalid', 'Invalid')], default='valid', help_text='\nTokens are considered valid until sending a notification produces a (permanent) error that indicates the token is\nnot usable for push notification anymore. Then it is marked as invalid for later removal from the database.\n', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_push_attempt_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['user', 'token'], name='user_token')],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('sub_title', models.CharField(max_length=200, verbose_name='Untertitel')),
                ('content', models.TextField(verbose_name='Inhalt')),
                ('push_notification_requested', models.BooleanField(default=False, help_text='Try to send push notifications to registered devices')),
                ('push_notification_done', models.BooleanField(default=False, help_text='Set after all registered device tokens have successfully been serviced')),
                ('push_notification_no_later_than', models.DateTimeField(blank=True, help_text="When trying to send push notifications, don't try or retry after this timestamp.", null=True)),
                ('push_notification_state', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['push_notification_requested', 'push_notification_done'], name='pnr_pnd')],
            },
        ),
    ]