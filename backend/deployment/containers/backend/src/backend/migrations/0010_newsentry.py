from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.image
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('backend', '0009_folder_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsEntry',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('news_type', models.CharField(choices=[('unknown', '-'), ('icl_news', 'ICL News'), ('campus_news', 'Campus News')], default='campus_news', max_length=20)),
                ('header', models.CharField(max_length=200, verbose_name='Überschrift')),
                ('header_de', models.CharField(max_length=200, null=True, verbose_name='Überschrift')),
                ('header_en', models.CharField(max_length=200, null=True, verbose_name='Überschrift')),
                ('sub_header', models.CharField(max_length=200, verbose_name='Anriss')),
                ('sub_header_de', models.CharField(max_length=200, null=True, verbose_name='Anriss')),
                ('sub_header_en', models.CharField(max_length=200, null=True, verbose_name='Anriss')),
                ('text', tinymce.models.HTMLField()),
                ('text_de', tinymce.models.HTMLField(null=True)),
                ('text_en', tinymce.models.HTMLField(null=True)),
                ('publish_from', models.DateTimeField(blank=True, help_text='Eintrag erst ab diesem Zeitpunkt zeigen oder ab sofort, wenn nicht gesetzt', null=True, verbose_name='Sichtbar ab')),
                ('publish_until', models.DateTimeField(blank=True, help_text='Eintrag bis zu diesem Zeitpunkt zeigen oder für immer, wenn nicht gesetzt', null=True, verbose_name='Sichtbar bis')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('image', filer.fields.image.FilerImageField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.FILER_IMAGE_MODEL, verbose_name='Bild')),
            ],
            options={
                'ordering': ('-created_at', 'id'),
            },
        ),
    ]