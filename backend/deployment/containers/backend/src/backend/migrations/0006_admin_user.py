import datetime
import logging
import random
import string

import pytz
from django.db import migrations

from backend.enum import VehicleType, OptionType
from backend.models import Booking, BookingState, BackendUser, Vehicle

logger = logging.getLogger(__name__)

def add_data(apps, schema_editor):
    from django.contrib.auth import get_user_model

    username = 'admin'
    email = 'admin@example.com'
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO backend_backenduser (
                password,
                username,
                first_name,
                last_name,
                email,
                is_superuser,
                is_staff,
                is_active,
                date_joined,
                mobile_number_verified,
                mobile_number_unverified,
                email_is_verified,
                mobile_number_is_verified,
                category_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT DO NOTHING;
            """,
            [
                'INVALID',
                username,
                '',
                '',
                email,
                True,
                True,
                True,
                now,
                '',
                '',
                True,
                True,
                0,
            ])


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0005_rename_email_verified_backenduser_email_is_verified_and_more'),
    ]

    operations = [
        migrations.RunPython(add_data),
        migrations.RunSQL("""
        BEGIN;
        LOCK TABLE backend_backenduser IN EXCLUSIVE MODE;
        SELECT setval('backend_backenduser_id_seq',(SELECT GREATEST(MAX(id), nextval('backend_backenduser_id_seq')-1) FROM backend_backenduser));
        COMMIT;
        """),
    ]


