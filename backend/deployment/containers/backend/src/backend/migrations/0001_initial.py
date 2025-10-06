import backend.enum
import dirtyfields.dirtyfields
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.gis.db.models.fields
import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackendUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('password_reset_secret', models.CharField(blank=True, max_length=100, null=True)),
                ('password_reset_validity', models.DateTimeField(blank=True, null=True)),
                ('profile_image_data', models.BinaryField(blank=True, max_length=10485760, null=True)),
                ('profile_image_mimetype', models.CharField(blank=True, choices=[('PNG', 'image/png'), ('JPEG', 'image/jpeg')], default=None, max_length=20, null=True)),
                ('mobile_number', models.CharField(blank=True, default='', max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+49170999999999'. Up to 15 digits allowed.", regex='^\\+[1-9]\\d{1,14}$')])),
                ('mobile_number_verified', models.BooleanField(default=False)),
                ('email_verification_code', models.CharField(blank=True, default=None, max_length=32, null=True)),
                ('email_verification_valid_until', models.DateTimeField(blank=True, default=None, null=True)),
                ('email_verified', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BackendPoi',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('poi_type', models.IntegerField(choices=[(0, 'Unbekannt'), (1, 'Bushaltestelle'), (2, 'Straßenbahn'), (3, 'Zug')], default=0)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('source_type', models.CharField(blank=True, max_length=100, null=True)),
                ('source_id', models.CharField(blank=True, max_length=40, null=True)),
                ('source_properties', models.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('source_acquired_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'POI',
                'verbose_name_plural': 'POIs',
            },
        ),
        migrations.CreateModel(
            name='BackendRole',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Role')),
                ('description', models.TextField(verbose_name='Description')),
                ('permissions', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('trip_mode', models.CharField(choices=[('pt', 'ÖPNV'), ('sharing', 'Sharing'), ('rriveUse', 'RRive als Mitfahrer'), ('rriveOffer', 'RRive Mitfahrt anbieten'), ('static', 'Statisches Angebot'), ('car', 'Auto')], max_length=20)),
                ('state', models.CharField(choices=[('created', 'Erzeugt'), ('planned', 'Geplant'), ('started', 'Gestartet'), ('finished', 'Abgeschlossen'), ('timeout', 'Timeout')], default=backend.enum.BookingState['created'], max_length=20)),
                ('from_location', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('from_description', models.CharField(blank=True, max_length=250, null=True)),
                ('to_location', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('to_description', models.CharField(blank=True, max_length=250, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('trace', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=4326)),
                ('external_co2e', models.FloatField(blank=True, help_text='CO2-equivalent emissions reported by external source', null=True, verbose_name='External CO2e')),
            ],
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CO2eEmission',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('mode_of_transport', models.CharField(choices=[('pt', 'ÖPNV'), ('sharing', 'Sharing'), ('rriveUse', 'RRive als Mitfahrer'), ('rriveOffer', 'RRive Mitfahrt anbieten'), ('static', 'Statisches Angebot'), ('car', 'Auto')], max_length=20)),
                ('per_unit', models.CharField(choices=[('g/Pkm', 'g per person per km')], default='g/Pkm', max_length=20)),
                ('quantity', models.FloatField()),
            ],
            options={
                'verbose_name': 'CO₂e emission',
            },
        ),
        migrations.CreateModel(
            name='UserCategory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Kategorie')),
                ('name_de', models.CharField(max_length=100, null=True, unique=True, verbose_name='Kategorie')),
                ('name_en', models.CharField(max_length=100, null=True, unique=True, verbose_name='Kategorie')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Beschreibung')),
                ('description_de', models.TextField(blank=True, null=True, verbose_name='Beschreibung')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Beschreibung')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vehicle_type', models.CharField(choices=[('unknown', '-'), ('bike', 'Fahrrad'), ('escooter', 'E-Scooter')], default='unknown', max_length=20)),
                ('vehicle_model', models.CharField(max_length=50)),
                ('vehicle_number', models.CharField(max_length=20)),
                ('provider_name', models.CharField(max_length=20)),
                ('provider_id', models.CharField(max_length=50)),
                ('battery_level_percent', models.FloatField(blank=True, help_text='Battery level in percent (0-100)', null=True)),
                ('remaining_range_km', models.FloatField(blank=True, help_text='Remaining range in kilometers with current battery charge', null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
            ],
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='WalletEntry',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('wallet', models.CharField(choices=[('CO2e', 'CO₂ äquivalent')], default='CO2e', max_length=20, verbose_name='Wallet')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('unit', models.CharField(choices=[('g CO2e', 'g CO₂ äquivalent')], default='g CO2e', max_length=20, verbose_name='Unit')),
                ('quantity', models.FloatField()),
                ('source_information', models.TextField(blank=True, null=True)),
                ('external_co2e', models.FloatField(blank=True, help_text='CO2-equivalent emissions reported by external source', null=True, verbose_name='External CO₂e')),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.booking')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupMetadata',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.TextField(verbose_name='Description')),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
            ],
        ),
        migrations.AddConstraint(
            model_name='co2eemission',
            constraint=models.UniqueConstraint(fields=('mode_of_transport', 'per_unit'), name='unique_mp'),
        ),
        migrations.AddField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='booking',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.vehicle'),
        ),
        migrations.AddIndex(
            model_name='backendpoi',
            index=models.Index(fields=['source_type', 'source_id'], name='backend_bac_source__6171fb_idx'),
        ),
        migrations.AddConstraint(
            model_name='backendpoi',
            constraint=models.UniqueConstraint(fields=('source_type', 'source_id'), name='unique_source_type_source_id'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='category',
            field=models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='backend.usercategory'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='roles',
            field=models.ManyToManyField(to='backend.backendrole'),
        ),
        migrations.AddField(
            model_name='backenduser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddConstraint(
            model_name='walletentry',
            constraint=models.UniqueConstraint(fields=('wallet', 'user', 'booking', 'unit'), name='unique_wubu'),
        ),
    ]