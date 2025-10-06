from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_walletentry_booking_state_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='push_notification_done',
            field=models.BooleanField(default=False, help_text='Will be set once all registered device tokens were serviced'),
        ),
        migrations.AlterField(
            model_name='message',
            name='push_notification_no_later_than',
            field=models.DateTimeField(blank=True, help_text="Don't send or resend after this point in time", null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='push_notification_requested',
            field=models.BooleanField(default=False, help_text='Send push notification to registered devices'),
        ),
        migrations.AlterField(
            model_name='message',
            name='soft_delete',
            field=models.BooleanField(default=False, help_text='Set if user deletes message'),
        ),
    ]