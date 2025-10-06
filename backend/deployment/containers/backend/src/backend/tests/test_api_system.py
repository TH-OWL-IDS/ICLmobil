import base64
import datetime
import json
import uuid

import pytest
import pytest_subtests
from django.conf import settings
from django.http import HttpResponse
from django.test import override_settings

from .fixtures import api_url, django_client, ensure_superuser
from ..models import BackendUser, Configuration


@pytest.mark.django_db
def test_api_GET_appConfig(api_url, django_client):
    r1: HttpResponse = django_client.get(
        f'{api_url}/system/appConfig',
        content_type="application/json",
    )
    assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    data = json.loads(r1.content)
    assert 'mapbox.com' in data['MAPBOX_API']
    del r1

@pytest.mark.django_db
def test_api_GET_appConfig(api_url, django_client):
    r1: HttpResponse = django_client.get(
        f'{api_url}/system/appConfig',
        content_type="application/json",
    )
    assert r1.status_code == 400, f"{r1.status_code} {r1.reason_phrase} {r1.content}"

    c = Configuration.objects.get(key='AppConfig')
    c.value['MAPBOX_TOKEN'] = 'SeeminglyOKKey'
    c.save()


    r1: HttpResponse = django_client.get(
        f'{api_url}/system/appConfig',
        content_type="application/json",
    )
    assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    data = json.loads(r1.content)
    assert 'mapbox.com' in data['MAPBOX_API']
    del r1