from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0036_supporttextentry_entry_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='provider_id',
            field=models.CharField(blank=True, help_text='Used to store a provider-specific ID usually returned by an earlier trip search', max_length=250, null=True),
        ),
    ]