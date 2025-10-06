# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import json

import pytest
from django.http import HttpResponse

from .fixtures import api_url, django_client
from ..api_v1.utils import HttpErrorNotImplemented


def test_api_GET_system_getAPIStatus(api_url, django_client):
    response: HttpResponse = django_client.get(f'{api_url}/system/getAPIStatus')
    assert response.status_code == 200
    assert 'application/json' in response.get('Content-Type')
    data = json.loads(response.content)
    assert data['status'] == 'ok'

