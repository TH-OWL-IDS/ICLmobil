from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0024_message_booking_message_publish_after_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(check=models.Q(('start_time__isnull', True), ('end_time__isnull', True), ('start_time__lte', models.F('end_time')), _connector='OR'), name='start_time_before_end_time'),
        ),
    ]