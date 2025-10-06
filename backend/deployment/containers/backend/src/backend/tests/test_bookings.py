import datetime
import itertools
import time
import json

import pytest
import pytz
from django.contrib.gis.geos import Point, LineString
from django.db.models import Max
from django.http import HttpResponse
from dns.update import Update

from .fixtures import api_url, django_client, ensure_superuser
from ..enum import OptionType, BookingState, VehicleType
from ..models import BackendUser, Booking, WalletEntry, CO2eEmission, Vehicle


# Manual testing:
# Start normal docker-compose deployment with db services port switched to 5432:5432
# bash -o pipefail -ec 'export $(grep -v '^#' .env | xargs) ; cd containers/backend/src ; export POSTGRES_BACKEND_USERNAME=postgres ; export POSTGRES_BACKEND_PASSWORD=$POSTGRES_PASSWORD ; export BACKEND_DB_HOSTNAME_OVERRIDE=127.0.0.1 ; env | grep POSTG ; ~/venv.iclmobil/bin/pytest -s'

@pytest.mark.django_db
def test_bookings_01_orm(api_url, django_client):
    admin_password = "testtest"
    user, created = BackendUser.objects.get_or_create(username='admin')
    user.set_password(admin_password)
    user.save()

    b = Booking.objects.create(
        user=user,
        trip_mode=OptionType.pt,
        start_time=datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
        end_time=datetime.datetime(2024, 1, 1, 1, 0, 0, tzinfo=pytz.UTC),
        trace=None,
    )
    b.save()
    assert b.state == BookingState.created
    source, distance = b.get_distance()
    assert source == 'none'
    assert distance is None

    b.from_location = Point(8.518567085266113, 52.055076653642246)  # distance: 1835m
    b.to_location = Point(8.545303344726562, 52.0557099804489)
    b.save()
    assert abs(b.from_location[0] - 8.5) < 0.1, "Unexpected coordinate - are lon/lat ordered right?"
    source, distance = b.get_distance()
    assert source == 'endpoints'
    assert abs(distance - 1835) < 1, f"Distance should be ~1835m, got {source} {distance}"

    # 49622m
    b.trace = LineString([
        [8.527450561523438, 52.019543202230835],
        [8.381881713867188, 51.907001886740986],
        [8.762969970703125, 51.71894646414401],
    ])
    b.save()
    source, distance = b.get_distance()
    assert source == 'trace'
    expected_m = 49622
    assert abs(distance - expected_m) < 1, f"Distance should be ~{expected_m}m, got {source} {distance}"

    """Make sure a WalletEntry is created when Booking reaches "finished"."""
    wes = WalletEntry.objects.filter(booking=b).all()
    assert len(wes) == 0
    b.state = BookingState.finished
    b.save()
    wes = WalletEntry.objects.filter(booking=b).all()
    assert len(wes) == 1

    we: WalletEntry = wes[0]

    emission = CO2eEmission.objects.get(mode_of_transport=OptionType.pt, per_unit='g/Pkm')
    assert abs(we.quantity - (
                expected_m * emission.quantity / 1000)) < 1, f"Unexpected emission for {expected_m}m: {we} {emission.quantity}"


@pytest.mark.django_db
def test_bookings_api(api_url, django_client):
    u1 = 'user1'
    u2 = 'user2'
    ensure_superuser(u1, u1)
    ensure_superuser(u2, u2)
    assert django_client.login(username=u1, password=u1)

    """No user1 booking exists yet"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/list')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 0
    del r

    """Create user booking"""
    create = {
        "trip_mode": "pt",
        "provider_id": "abc",
    }
    r: HttpResponse = django_client.post(f'{api_url}/booking/create', data=create, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """user1 booking exists"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/list')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 1
    b1 = data[0]
    assert b1['state'] == 'created', b1
    assert b1['provider_id'] == 'abc', b1
    del r

    assert django_client.login(username=u2, password=u2)

    """user2 cannot see user1's booking"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/list')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 0
    del r

    """user2 cannot delete user1's booking"""
    r: HttpResponse = django_client.delete(f'{api_url}/booking/delete/{b1["id"]}')
    assert r.status_code == 404, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    assert django_client.login(username=u1, password=u1)

    """Update user1 booking"""
    update = {
        "from_location_latitude": 52.017460729788304,
        "from_location_longitude": 8.903475808038054,
        "start_time": "2024-10-07T15:47:54.270Z",
        "end_time": "2024-10-07T15:47:54.270Z",
        "provider_id": "updated1",
    }
    r: HttpResponse = django_client.patch(f'{api_url}/booking/update/{b1["id"]}', data=update, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """No fantasy states"""
    update = {
        "state": "lol",
    }
    r: HttpResponse = django_client.patch(f'{api_url}/booking/update/{b1["id"]}', data=update, content_type='application/json')
    assert r.status_code == 400, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """user1 booking is updated"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/list')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 1
    b1 = data[0]
    assert abs(b1['from_location_latitude'] - 52.017) < 0.001
    assert b1['provider_id'] == 'updated1', b1
    del r

    """Delete user1 booking"""
    r: HttpResponse = django_client.delete(f'{api_url}/booking/delete/{b1["id"]}')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """user1 booking is gone"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/list')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 0
    del r


@pytest.mark.django_db(transaction=True)
def test_bookings_01_frontend_api(api_url, django_client):
    u1 = 'user1'
    u2 = 'user2'
    ensure_superuser(u1, u1)
    ensure_superuser(u2, u2)
    assert django_client.login(username=u1, password=u1)

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    """Create user booking in the future"""
    create = {
        "trip_mode": "pt",
        "from_location_latitude": 52.017460729788304,
        "from_location_longitude": 8.903475808038054,
        "from_description": "FUTURE from",
        "to_location_latitude": 52.1,
        "to_location_longitude": 8.8,
        "to_description": "FUTURE to",
        "start_time": (now+datetime.timedelta(hours=1)).isoformat(),
        "end_time": (now+datetime.timedelta(hours=2)).isoformat(),
        "provider_id": "def",
    }
    r: HttpResponse = django_client.post(f'{api_url}/booking/create', data=create, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    next_id = data['created_id']
    del r

    """Create user booking in the past"""
    create = {
        "trip_mode": "pt",
        "from_location_latitude": 52.017460729788304,
        "from_location_longitude": 8.903475808038054,
        "from_description": "PAST from",
        "to_location_latitude": 52.1,
        "to_location_longitude": 8.8,
        "to_description": "PAST to",
        "start_time": (now-datetime.timedelta(hours=2)).isoformat(),
        "end_time": (now-datetime.timedelta(hours=1)).isoformat(),
    }
    r: HttpResponse = django_client.post(f'{api_url}/booking/create', data=create, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    previous_id = data['created_id']
    del r

    """Check list of bookings"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/list/frontend')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    print("Check list of bookings", r.content)
    data = json.loads(r.content)
    previous_by_id = {e['id']: e for e in data['previousRides']}
    next_by_id = {e['id']: e for e in data['nextRides']}
    assert previous_id in previous_by_id, f"previous_id {previous_id} should be in previousRides. but data is: {data}"
    assert next_id in next_by_id, f"next_id {next_id} should be in nextRides. but data is: {data}"
    assert previous_by_id[previous_id]['rideDestination'] == 'PAST to', repr(previous_by_id[previous_id])
    assert previous_by_id[previous_id]['provider_id'] is None, previous_by_id[previous_id]
    assert next_by_id[next_id]['rideDestination'] == 'FUTURE to', repr(next_by_id[next_id])
    assert next_by_id[next_id]['provider_id'] == 'def', repr(next_by_id[next_id])
    assert bool(previous_by_id[previous_id]['source_link_more_information']), f"Expected source_link_more_information in: {previous_by_id[previous_id]}"
    del r

    """Set state of future booking"""
    update = {
        "state": "finished",
    }
    r: HttpResponse = django_client.patch(f'{api_url}/booking/update/{next_id}', data=update, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """Check future booking in previous rides"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/list/frontend')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert next_id in {e['id'] for e in data['previousRides']}, f"next_id {next_id} should be in previousRides. but data is: {data}"

    del r

    """Check points"""
    r: HttpResponse = django_client.get(f'{api_url}/booking/{next_id}/frontend')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert 'score_points' in data, r.content
    assert abs(data['score_points']-23) < 1.0, r.content

    del r



@pytest.mark.django_db
def test_bookings_vehicle_busy(api_url, django_client):
    u1 = 'user1'
    u2 = 'user2'
    ensure_superuser(u1, u1)
    ensure_superuser(u2, u2)
    assert django_client.login(username=u1, password=u1)

    vehicle = Vehicle.objects.create(
        vehicle_type=VehicleType.scooter,
        vehicle_model="Test vehicle",
        vehicle_number="ABC",
        provider_name="Test",
        provider_id="ABC",
    )
    vehicle_id = str(vehicle.id)

    start_time1 = datetime.datetime.now(tz=datetime.timezone.utc)
    start_time2 = datetime.datetime.now(tz=datetime.timezone.utc)+datetime.timedelta(minutes=30)
    start_time3 = datetime.datetime.now(tz=datetime.timezone.utc)+datetime.timedelta(minutes=60)

    """Create user booking A"""
    create = {
        "trip_mode": "sharing",
        "state": "planned",
        "vehicle_id": vehicle_id,
        "start_time": start_time1.isoformat(),
        "end_time": (start_time1+datetime.timedelta(hours=1)).isoformat(),
    }
    r: HttpResponse = django_client.post(f'{api_url}/booking/create', data=create, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """Create user booking B - conflict"""
    create = {
        "trip_mode": "sharing",
        "state": "planned",
        "vehicle_id": vehicle_id,
        "start_time": start_time2.isoformat(),
        "end_time": (start_time2+datetime.timedelta(hours=1)).isoformat(),
    }
    r: HttpResponse = django_client.post(f'{api_url}/booking/create', data=create, content_type='application/json')
    assert r.status_code == 409, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """Create user booking B - back to back"""
    create = {
        "trip_mode": "sharing",
        "state": "planned",
        "vehicle_id": vehicle_id,
        "start_time": start_time3.isoformat(),
        "end_time": (start_time3+datetime.timedelta(hours=1)).isoformat(),
    }
    r: HttpResponse = django_client.post(f'{api_url}/booking/create', data=create, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    booking_b_id = str(Booking.objects.aggregate(Max('id'))['id__max'])

    """Update booking B - conflicting time but state makes it OK"""
    update = {
        "trip_mode": "sharing",
        "state": "created",
        "start_time": start_time2.isoformat(),
        "end_time": (start_time2+datetime.timedelta(hours=1)).isoformat(),
    }
    r: HttpResponse = django_client.patch(f'{api_url}/booking/update/{booking_b_id}', data=update, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    """Update booking B - state planned makes it a conflict"""
    update = {
        "trip_mode": "sharing",
        "state": "planned",
    }
    r: HttpResponse = django_client.patch(f'{api_url}/booking/update/{booking_b_id}', data=update, content_type='application/json')
    assert r.status_code == 409, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

