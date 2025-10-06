from django.db import migrations

from backend.enum import VehicleType
from backend.models import Vehicle


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0022_co2e_data2'),
    ]

    operations = [
        migrations.RunSQL("""
BEGIN;
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE public.backend_booking
ADD CONSTRAINT unique_vehicle_planned_booking
EXCLUDE USING gist (
    vehicle_id WITH =,
    tstzrange(start_time, end_time, '[)') WITH &&
)
WHERE (state IN ('planned', 'started') AND vehicle_id IS NOT NULL);
COMMIT;
    """),

    ]


