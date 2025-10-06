# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from django.http import HttpResponse

from .fixtures import api_url, django_client
from ..api_v1.schemas import CreateRoleRequest


def test_GET_openapi_json(api_url, django_client):
    r1: HttpResponse = django_client.post(f'{api_url}/openapi.json')
    assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    del r1
    x = CreateRoleRequest.model_validate_json(r'{"name": "dfj", "description": "dskjf", "permissions": "[{\"bit\": 1, \"permissionName\": \"dsfdsf\"}]"}')
    print(x)
