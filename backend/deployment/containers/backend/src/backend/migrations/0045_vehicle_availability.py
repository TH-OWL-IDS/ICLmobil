from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0044_newsentry_sub_header2_newsentry_sub_header2_de_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='availability',
            field=models.CharField(choices=[('normal', 'Normal (sichtbar in Suchen)'), ('hidden', 'Unsichtbar (nicht sichtbar in Suchen)')], default='normal', max_length=30),
        ),
    ]