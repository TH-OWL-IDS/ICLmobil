from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0043_backenduser_auth_key_external_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsentry',
            name='sub_header2',
            field=models.CharField(default='', max_length=500, verbose_name='Anriss 2'),
        ),
        migrations.AddField(
            model_name='newsentry',
            name='sub_header2_de',
            field=models.CharField(default='', max_length=500, null=True, verbose_name='Anriss 2'),
        ),
        migrations.AddField(
            model_name='newsentry',
            name='sub_header2_en',
            field=models.CharField(default='', max_length=500, null=True, verbose_name='Anriss 2'),
        ),
    ]