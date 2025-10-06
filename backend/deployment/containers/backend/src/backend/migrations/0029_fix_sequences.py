from django.db import migrations

from backend.enum import VehicleType
from backend.models import Vehicle



class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0028_userfeedback'),
    ]

    operations = [
        migrations.RunSQL("""
    BEGIN;
    LOCK TABLE backend_co2eemission IN EXCLUSIVE MODE;
    SELECT setval('backend_co2eemission_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_co2eemission_id_seq')-1) FROM backend_co2eemission));
    LOCK TABLE backend_backenduser IN EXCLUSIVE MODE;
    SELECT setval('backend_backenduser_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_backenduser_id_seq')-1) FROM backend_backenduser));
    LOCK TABLE backend_booking IN EXCLUSIVE MODE;
    SELECT setval('backend_booking_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_booking_id_seq')-1) FROM backend_booking));
    LOCK TABLE backend_userfeedback IN EXCLUSIVE MODE;
    SELECT setval('backend_userfeedback_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_userfeedback_id_seq')-1) FROM backend_userfeedback));
    LOCK TABLE backend_usercategory IN EXCLUSIVE MODE;
    SELECT setval('backend_usercategory_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_usercategory_id_seq')-1) FROM backend_usercategory));
    COMMIT;
    """),

    ]


