from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0046_vehicle_user_hint_end_vehicle_user_hint_end_de_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsCategory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('news_type', models.CharField(choices=[('unknown', '-'), ('icl_news', 'ICL News'), ('campus_news', 'Campus News'), ('events', 'Events'), ('food_and_drinks', 'Food & Drinks')], max_length=20, unique=True)),
                ('more_link_url', models.CharField(blank=True, max_length=255, null=True, verbose_name='Link zu einer Webseite mit weiteren oder den gleichen News')),
                ('more_link_label', models.CharField(blank=True, max_length=255, null=True, verbose_name='Beschriftung des Buttons in der App')),
                ('more_link_label_de', models.CharField(blank=True, max_length=255, null=True, verbose_name='Beschriftung des Buttons in der App')),
                ('more_link_label_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Beschriftung des Buttons in der App')),
            ],
        ),
    ]