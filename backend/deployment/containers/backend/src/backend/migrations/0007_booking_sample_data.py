import datetime

import pytz
from django.db import migrations

from backend.enum import VehicleType, OptionType
from backend.models import Booking, BookingState, BackendUser, Vehicle

import logging
logging.basicConfig(level=logging.DEBUG)


def add_data(apps, schema_editor):
    from django.conf import settings
    from django.contrib.gis.geos import Point, LineString
    from django.db import connection
    user_id = BackendUser.objects.all().values_list('id')[0][0]
    th_owl = Point(8.9051603, 52.0181228, srid=4326)
    jahnplatz = Point(8.5311761, 52.023341,srid=4326)
    iosb = Point(8.8982288, 52.0171277,srid=4326)
    morning = datetime.datetime(2024,12,1, 8, 0, 0, tzinfo=pytz.timezone('Europe/Berlin'))
    scooter_2_id = 2  # Vehicle.objects.get(vehicle_type=VehicleType.scooter, vehicle_number='E3F-E07')
    trace = LineString([8.902234062982247, 52.01766556297247], [8.901861916946702, 52.01756525969974], [8.901707082464762, 52.0174415520203], [8.902147138360807, 52.017217539946415], [8.902767439279284, 52.017252962547964], [8.903513202871691, 52.01728050019546], [8.904398175668014, 52.01733557543964], [8.904418062697145, 52.017647667209154])
    # str(trace) -> LINESTRING (8.902234062982247 52.01766556297247, 8.901861916946702 52.01756525969974, 8.901707082464762 52.0174415520203, 8.902147138360807 52.017217539946415, 8.902767439279284 52.017252962547964, 8.903513202871691 52.01728050019546, 8.904398175668014 52.01733557543964, 8.904418062697145 52.017647667209154)
    with connection.cursor() as cursor:
        for (b_id, trip_mode, state,
             from_location, from_description,
             to_location, to_description,
             start_time, end_time,
             vehicle, trace, external_co2e) in (

                (1, OptionType.pt, BookingState.created,
                 jahnplatz, "Bielefeld, Jahnplatz",
                 th_owl, "Lemgo, TH OWL",
                 morning, morning+datetime.timedelta(minutes=70),
                 None, None, None),

                (2, OptionType.pt, BookingState.created,
                 th_owl, "Lemgo, TH OWL",
                 jahnplatz, "Bielefeld, Jahnplatz",
                 morning+datetime.timedelta(hours=8), morning + datetime.timedelta(hours=9),
                 None, None, None),

                (3, OptionType.pt, BookingState.finished,
                 jahnplatz, "Bielefeld, Jahnplatz",
                 th_owl, "Lemgo, TH OWL",
                 morning-datetime.timedelta(days=1), morning -datetime.timedelta(days=1)+ datetime.timedelta(minutes=70),
                 None, None, None),

                (4, OptionType.sharing, BookingState.finished,
                 iosb, "Lemgo, Fraunhofer IOSB-INA",
                 th_owl, "Lemgo, TH OWL",
                 morning, morning + datetime.timedelta(minutes=10),
                 scooter_2_id, trace, None),

        ):
            cursor.execute(
                """
                INSERT INTO backend_booking (
                    id,
                    user_id,
                    trip_mode,
                    state,
                    from_location,
                    from_description,
                    to_location,
                    to_description,
                    start_time,
                    end_time,
                    vehicle_id,
                    trace,
                    external_co2e
                ) VALUES (%s, %s, %s, %s, 
                ST_GeomFromText('POINT(%s %s)', 4326), %s, 
                ST_GeomFromText('POINT(%s %s)', 4326), %s, 
                %s, %s, %s, 
                __LINESTRING__, %s) ON CONFLICT DO NOTHING;
                """.replace('__LINESTRING__', f"ST_GeomFromText('{str(trace)}', 4326)" if trace else 'NULL'),
                # b_id, trip_mode, state,
                #              from_location, from_description,
                #              to_location, to_description,
                #              start_time, end_time,
                #              vehicle, trace, external_co2e)
                [
                    b_id,
                    user_id,
                    trip_mode.value,
                    state.value,
                    from_location[0], from_location[1],
                    from_description,
                    to_location[0], to_location[1],
                    to_description,
                    start_time,
                    end_time,
                    vehicle,
                    external_co2e
                ])


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0006_admin_user'),
    ]

    operations = [
        migrations.RunPython(add_data),
        migrations.RunSQL("""
        BEGIN;
        LOCK TABLE backend_booking IN EXCLUSIVE MODE;
        SELECT setval('backend_booking_id_seq',(SELECT GREATEST(MAX(id), nextval('backend_booking_id_seq')-1) FROM backend_booking));
        COMMIT;
        """),
    ]


