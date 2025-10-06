import datetime
import json

import pytest
from django.contrib.gis.geos import Point
from django.http import HttpResponse

from .fixtures import api_url, django_client, ensure_superuser
from ..enum import VehicleType
from ..models import Vehicle


@pytest.mark.django_db
def test_trips_api(api_url, django_client):
    u1 = 'user1'
    ensure_superuser(u1, u1)
    assert django_client.login(username=u1, password=u1)

    """Only return invalid sharing options"""
    q = {
        "start_timestamp": "2024-09-16T08:00:00+02:00",
        "location_from_latitude": 52.0234109,
        "location_from_longitude": 8.532586,
        "location_to_latitude": 52.0175792,
        "location_to_longitude": 8.9018994,
        "user_location_latitude": None,
        "user_location_longitude": None,
        "include_invalid_trips": True,
    }
    r = django_client.post(f'{api_url}/trip/search', data=q, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == dict
    options = data['options']
    vehicle_count = Vehicle.objects.count()
    sharing_options = [o for o in options if o['optionType'] == 'sharing']
    assert len(sharing_options) == vehicle_count
    assert all([o['valid'] == False for o in sharing_options])
    del r

    v = Vehicle.objects.get(provider_name='ICL', vehicle_number='E3F-E07')
    q = {
        "start_timestamp": "2024-09-16T08:00:00+02:00",
        "location_from_latitude": v.location[1]+0.001,
        "location_from_longitude": v.location[0],
        "location_to_latitude": v.location[1],
        "location_to_longitude": v.location[0],
        "include_invalid_trips": False,
    }
    r = django_client.post(f'{api_url}/trip/search', data=q, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    sharing_options = [o for o in data['options'] if o['optionType'] == 'sharing']
    o = sharing_options[0]
    assert o['vehicleNumber'] == 'E3F-E07'
    assert o['valid'] == True
    assert abs(o['distanceM']-111) < 1.0
    del r

@pytest.mark.django_db
def test_01_no_busy_vehicle(api_url, django_client):
    u1 = 'user1'
    u2 = 'user2'
    ensure_superuser(u1, u1)
    ensure_superuser(u2, u2)
    assert django_client.login(username=u1, password=u1)

    lat = 52.017436
    lng = 8.9015183
    location = Point(lng, lat, srid=4326)

    location2 = Point(lng+0.05, lat+0.05, srid=4326)

    vehicle1 = Vehicle.objects.create(
        vehicle_type=VehicleType.scooter,
        vehicle_model="Test vehicle",
        vehicle_number="ABC1",
        provider_name="Test",
        provider_id="ABC1",
        location=location,
    )
    vehicle1_id = str(vehicle1.id)

    vehicle2 = Vehicle.objects.create(
        vehicle_type=VehicleType.scooter,
        vehicle_model="Test vehicle",
        vehicle_number="ABC2",
        provider_name="Test",
        provider_id="ABC2",
        location=location,
    )
    vehicle2_id = str(vehicle2.id)

    start_time1 = datetime.datetime.now(tz=datetime.timezone.utc)
    start_time2 = start_time1+datetime.timedelta(minutes=120)
    #start_time3 = start_time1+datetime.timedelta(minutes=60)

    """Create user booking A in 2h"""
    create = {
        "trip_mode": "sharing",
        "state": "planned",
        "vehicle_id": vehicle1_id,
        "start_time": start_time2.isoformat(),
        "end_time": (start_time2+datetime.timedelta(hours=1)).isoformat(),
    }
    r: HttpResponse = django_client.post(f'{api_url}/booking/create', data=create, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """Try to find vehicles"""
    q = {
        "start_timestamp": start_time1.isoformat(),
        "location_from_latitude": location[1],
        "location_from_longitude": location[0],
        "location_to_latitude": location2[1],
        "location_to_longitude": location2[0],
        "user_location_latitude": None,
        "user_location_longitude": None,
        "include_invalid_trips": False,
    }
    r = django_client.post(f'{api_url}/trip/search', data=q, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == dict
    options = data['options']
    # vehicle_count = Vehicle.objects.count()
    sharing_options = [o for o in options if o['optionType'] == 'sharing' and o['vehicleModel'] == 'Test vehicle']
    assert len(sharing_options) == 2, sharing_options
    v1 = [o for o in sharing_options if o['vehicleNumber'] == 'ABC1'][0]
    v2 = [o for o in sharing_options if o['vehicleNumber'] == 'ABC2'][0]
    assert v1['maximumDurationH'] == 2.0, v1
    assert v2['maximumDurationH'] > 3.0, v2  #  should actually be settings.SHARING_MAXIMUM_DURATION_SECONDS
    del r


