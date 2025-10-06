from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0034_newsentry_external_id_newsentry_external_source_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='supporttextcategory',
            options={'ordering': ('sort_order', 'id')},
        ),
        migrations.AlterModelOptions(
            name='supporttextentry',
            options={'ordering': ('category__sort_order', 'category__title', 'sort_order', 'id')},
        ),
        migrations.AddField(
            model_name='supporttextcategory',
            name='sort_order',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]