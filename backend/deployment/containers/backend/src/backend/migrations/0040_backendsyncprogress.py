from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0039_backenduser_pooling_is_linked'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackendSyncProgress',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sync_key', models.CharField(max_length=50, unique=True)),
                ('sync_value_int', models.BigIntegerField(blank=True, null=True)),
                ('sync_value_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]