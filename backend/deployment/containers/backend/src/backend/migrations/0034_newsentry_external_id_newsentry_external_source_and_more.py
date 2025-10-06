from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0033_data_supporttext'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsentry',
            name='external_id',
            field=models.CharField(blank=True, db_index=True, help_text='ID des Eintrags bei extern synchronisierten News', max_length=100, null=True, verbose_name='Externe ID'),
        ),
        migrations.AddField(
            model_name='newsentry',
            name='external_source',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Bezeichnung einer externen News-Quelle'),
        ),
        migrations.AddField(
            model_name='newsentry',
            name='external_url',
            field=models.URLField(blank=True, db_index=True, help_text='URL, unter dem der Artikel außerhalb eingesehen werden kann. Wird bei extern synchronisierten News verwendet.', max_length=500, null=True, verbose_name='Externe URL'),
        ),
        migrations.AddField(
            model_name='newsentry',
            name='image_url',
            field=models.URLField(blank=True, help_text='URL als Ersatz für das Bild. Wird verwendet, wenn das Bild-Feld leer ist.', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='newsentry',
            name='sort_order',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='newsentry',
            name='header',
            field=models.CharField(max_length=500, verbose_name='Überschrift'),
        ),
        migrations.AlterField(
            model_name='newsentry',
            name='header_de',
            field=models.CharField(max_length=500, null=True, verbose_name='Überschrift'),
        ),
        migrations.AlterField(
            model_name='newsentry',
            name='header_en',
            field=models.CharField(max_length=500, null=True, verbose_name='Überschrift'),
        ),
        migrations.AlterField(
            model_name='newsentry',
            name='news_type',
            field=models.CharField(choices=[('unknown', '-'), ('icl_news', 'ICL News'), ('campus_news', 'Campus News'), ('events', 'Events'), ('food_and_drinks', 'Food & Drinks')], default='campus_news', max_length=20),
        ),
        migrations.AlterField(
            model_name='newsentry',
            name='sub_header',
            field=models.CharField(max_length=500, verbose_name='Anriss'),
        ),
        migrations.AlterField(
            model_name='newsentry',
            name='sub_header_de',
            field=models.CharField(max_length=500, null=True, verbose_name='Anriss'),
        ),
        migrations.AlterField(
            model_name='newsentry',
            name='sub_header_en',
            field=models.CharField(max_length=500, null=True, verbose_name='Anriss'),
        ),
    ]