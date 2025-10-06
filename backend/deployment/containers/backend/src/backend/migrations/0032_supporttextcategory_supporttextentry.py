from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0031_alter_booking_trip_mode_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportTextCategory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('title_de', models.CharField(max_length=200, null=True, verbose_name='Titel')),
                ('title_en', models.CharField(max_length=200, null=True, verbose_name='Titel')),
                ('description', models.CharField(blank=True, max_length=600, verbose_name='Beschreibung')),
                ('description_de', models.CharField(blank=True, max_length=600, null=True, verbose_name='Beschreibung')),
                ('description_en', models.CharField(blank=True, max_length=600, null=True, verbose_name='Beschreibung')),
            ],
        ),
        migrations.CreateModel(
            name='SupportTextEntry',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sort_order', models.PositiveIntegerField(db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('title_de', models.CharField(max_length=200, null=True, verbose_name='Titel')),
                ('title_en', models.CharField(max_length=200, null=True, verbose_name='Titel')),
                ('text', models.CharField(max_length=200, verbose_name='Untertitel')),
                ('text_de', models.CharField(max_length=200, null=True, verbose_name='Untertitel')),
                ('text_en', models.CharField(max_length=200, null=True, verbose_name='Untertitel')),
                ('content', tinymce.models.HTMLField(verbose_name='Inhalt')),
                ('content_de', tinymce.models.HTMLField(null=True, verbose_name='Inhalt')),
                ('content_en', tinymce.models.HTMLField(null=True, verbose_name='Inhalt')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.supporttextcategory')),
            ],
            options={
                'ordering': ('category__title', 'sort_order', 'id'),
            },
        ),
    ]