from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0030_own_scooter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='trip_mode',
            field=models.CharField(choices=[('pt', 'ÖPNV'), ('sharing', 'Sharing'), ('rriveUse', 'RRive als Mitfahrer'), ('rriveOffer', 'RRive Mitfahrt anbieten'), ('static', 'Statisches Angebot'), ('car', 'Auto'), ('walk', 'Fußweg'), ('own_bike', 'Fahrrad'), ('own_scooter', 'Scooter')], max_length=20),
        ),
        migrations.AlterField(
            model_name='co2eemission',
            name='mode_of_transport',
            field=models.CharField(choices=[('pt', 'ÖPNV'), ('sharing', 'Sharing'), ('rriveUse', 'RRive als Mitfahrer'), ('rriveOffer', 'RRive Mitfahrt anbieten'), ('static', 'Statisches Angebot'), ('car', 'Auto'), ('walk', 'Fußweg'), ('own_bike', 'Fahrrad'), ('own_scooter', 'Scooter')], max_length=20),
        ),
        migrations.AlterField(
            model_name='walletentry',
            name='trip_mode',
            field=models.CharField(blank=True, choices=[('pt', 'ÖPNV'), ('sharing', 'Sharing'), ('rriveUse', 'RRive als Mitfahrer'), ('rriveOffer', 'RRive Mitfahrt anbieten'), ('static', 'Statisches Angebot'), ('car', 'Auto'), ('walk', 'Fußweg'), ('own_bike', 'Fahrrad'), ('own_scooter', 'Scooter')], default=None, max_length=20, null=True),
        ),
    ]