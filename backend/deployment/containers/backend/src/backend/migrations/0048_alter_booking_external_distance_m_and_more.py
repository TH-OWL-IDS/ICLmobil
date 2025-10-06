from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0047_newscategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='external_distance_m',
            field=models.FloatField(blank=True, default=None, help_text='CO2-equivalent emissions reported by external source', null=True, verbose_name='External distance'),
        ),
        migrations.AlterField(
            model_name='newscategory',
            name='more_link_label',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Label of button in the app'),
        ),
        migrations.AlterField(
            model_name='newscategory',
            name='more_link_label_de',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Label of button in the app'),
        ),
        migrations.AlterField(
            model_name='newscategory',
            name='more_link_label_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Label of button in the app'),
        ),
        migrations.AlterField(
            model_name='newscategory',
            name='more_link_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Link to a website with more or the same news'),
        ),
    ]