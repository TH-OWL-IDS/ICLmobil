from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0035_alter_supporttextcategory_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='supporttextentry',
            name='entry_name',
            field=models.CharField(blank=True, help_text="(Technischer) Name für einen Eintrag, der eine spezielle Bedeutung im Frontend hat. Z.B. 'about', 'AGB' usw. Bitte nur bei diesen Einträgen benutzen und sonst leer lassen.", max_length=50, null=True, verbose_name='Name des Eintrags'),
        ),
    ]