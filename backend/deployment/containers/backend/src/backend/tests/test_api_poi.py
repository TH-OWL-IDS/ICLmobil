# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import base64
import io
import json
import os

import pytest
import pytest_subtests
from PIL import Image
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.http import HttpResponse

from .fixtures import api_url, django_client, ensure_superuser, login_superuser
from ..models import BackendUser, BackendRole


@pytest.mark.django_db
def test_api_GET_list_POST_create_POST_update_DELETE_delete(api_url, django_client):
    login_superuser(django_client)

    r: HttpResponse = django_client.post(f'{api_url}/poi/create', data={
        'name': 'SmartFactory OWL',
        'description': 'Eine gemeinsame Einrichtung des Fraunhofer IOSB-INA und der Technischen Hochschule OWL',
        'latitude': 52.017460729788304, 'longitude':8.903475808038054,
    }, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == dict
    poi_id = data['poiID']
    del r

    r: HttpResponse = django_client.get(f'{api_url}/poi/list')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 1
    assert data[0]['poiID'] == poi_id
    assert 'SmartFactory' in data[0]['name']
    assert 'Fraunhofer' in data[0]['description']
    assert 52 < data[0]['latitude'] < 53
    assert 8 < data[0]['longitude'] < 9
    del r

    updated = data[0].copy()
    updated['name'] = 'updated'

    r: HttpResponse = django_client.post(f'{api_url}/poi/update', data=updated, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    r: HttpResponse = django_client.get(f'{api_url}/poi/list')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 1
    assert data[0]['poiID'] == poi_id
    assert 'updated' in data[0]['name']
    del r



