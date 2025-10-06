# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
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
from ..models import BackendUser


@pytest.mark.django_db
def test_api_GET_user_isTokenValid(api_url, django_client):
    username="admin"
    email = username+"@example.com"
    admin_password = "testtest"
    user, created = BackendUser.objects.get_or_create(username=username, defaults={"email": email})
    user.set_password(admin_password)
    user.save()

    # Try raw
    r1: HttpResponse = django_client.get(f'{api_url}/user/isTokenValid')
    assert r1.status_code == 401, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    del r1

    # Login
    r2: HttpResponse = django_client.post(
        f'{api_url}/user/login', data={
            'email': email,
            'password': admin_password,
        },
        content_type="application/json"
    )
    assert r2.status_code == 200, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
    session_key = r2.cookies.get(settings.SESSION_COOKIE_NAME).value
    del r2

    # Test with cookie
    r3: HttpResponse = django_client.get(f'{api_url}/user/isTokenValid')
    assert r3.status_code == 200, f"{r3.status_code} {r3.reason_phrase} {r3.content}"
    del r3

    # Forget cookie
    django_client.cookies.clear()
    # Test without cookie
    r4: HttpResponse = django_client.get(f'{api_url}/user/isTokenValid')
    assert r4.status_code == 401, f"{r4.status_code} {r4.reason_phrase} {r4.content}"
    del r4

    # Test with header
    t5: HttpResponse = django_client.get(
        f'{api_url}/user/isTokenValid',
        headers={'Authorization': f"Bearer " + base64.b64encode(session_key.encode('utf-8')).decode('utf-8')}
    )
    assert t5.status_code == 200, f"{t5.status_code} {t5.reason_phrase} {t5.content}"
    del t5


@pytest.mark.django_db
def test_api_GET_verify(api_url, django_client):
    pass
    # TODO unimplemented


@pytest.mark.django_db
def test_api_POST_user_register(subtests: pytest_subtests.SubTests, api_url, django_client):
    username = "test1"
    email = username+"@example.com"
    password = uuid.uuid4().hex.upper()

    with subtests.test("User should not be able to log in yet"):
        response = django_client.post(
            f'{api_url}/user/login', data={
                'email': email,
                'password': password,
            },
            content_type='application/json',
        )
        assert response.status_code == 401, f"{response.status_code} {response.reason_phrase} {response.content}"

    with subtests.test("Get user categories"):
        response = django_client.get(
            f'{api_url}/user/category',
            content_type='application/json',
        )
        assert response.status_code == 200, f"{response.status_code} {response.reason_phrase} {response.content}"
        categories = json.loads(response.content)['categories']

    category = categories[-1]

    with subtests.test("Register user"):
        response: HttpResponse = django_client.post(f'{api_url}/user/register', data={
            'name': 'First Last',
            'password': password,
            'mobile_phone_number': '017145678912345',
            'category_id': category['id'],
            'email': email,
        }, content_type="application/json")
        assert response.status_code == 200, f"{response.status_code} {response.reason_phrase} {response.content}"
        assert 'application/json' in response.get('Content-Type')
        data = json.loads(response.content)
        assert data.get('msg') == 'OK'
        assert type(data.get('userID')) == str
        assert int(data.get('userID')) > 0
        del response

    with subtests.test("Login should succeed now"):
        django_client.cookies.clear()
        response: HttpResponse = django_client.post(
            f'{api_url}/user/login', data={
                'email': email,
                'password': password,
            },
            content_type="application/json"
        )
        assert response.status_code == 200, f"{response.status_code} {response.reason_phrase} {response.content}"
        user_id = json.loads(response.content)['user']['userid']
        print(f"Login was successful with response {response.content=}")

    with subtests.test("Check category"):
        url = f'{api_url}/user/getUserData'

        response: HttpResponse = django_client.get(url)
        assert response.status_code == 200, f"{response.status_code} {response.reason_phrase} {response.content}"
        data = json.loads(response.content)
        assert 'de' in data['category']['name'], data
        assert 'en' in data['category']['name'], data
        del response


@pytest.mark.django_db
def test_api_POST_user_login(api_url, django_client):
    admin_password = "testtest"
    username = "admin"
    email = username+"@example.com"

    user, created = BackendUser.objects.get_or_create(username='admin', defaults={"email": email})
    user.set_password(admin_password)
    user.save()

    # Try wrong password
    r1: HttpResponse = django_client.post(
        f'{api_url}/user/login', data={
            'email': email,
            'password': 'wrongwrong',
        },
        content_type="application/json"
    )
    assert r1.status_code == 401, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    del r1

    # Try correct password
    r2: HttpResponse = django_client.post(
        f'{api_url}/user/login', data={
            'email': email,
            'password': admin_password,
        },
        content_type="application/json"
    )
    assert r2.status_code == 200, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
    assert 'application/json' in r2.get('Content-Type')
    data = json.loads(r2.content)
    session_key = data['token']
    assert len(session_key) > 10

    # We should get the session as a cookie
    assert r2.cookies.get(settings.SESSION_COOKIE_NAME).value == session_key

    # We should get it in the JSON response
    assert data['token'] == session_key


@pytest.mark.django_db
def test_api_POST_validate_email(api_url, django_client):
    email = "test1@example.com"
    username = "test1"

    r2: HttpResponse = django_client.post(f'{api_url}/user/validateEmail', data={'email': email},
                                          content_type='application/json')
    assert r2.status_code == 200, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
    del r2

    user = ensure_superuser(username, 'test1', email=email)

    r2: HttpResponse = django_client.post(f'{api_url}/user/validateEmail', data={'email': email},
                                          content_type='application/json')
    assert r2.status_code == 409, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
    del r2


@pytest.mark.django_db
@override_settings(EMAIL_SUPPRESS=True)
def test_api_POST_recover_POST_reset(api_url, django_client):
    email = 'user1@example.com'
    user = ensure_superuser('user1', 'password1', email=email)

    r: HttpResponse = django_client.post(f'{api_url}/user/recover', data={'email': email},
                                         content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    user2 = BackendUser.objects.get(id=user.id)
    assert user2.password_reset_validity > datetime.datetime.now(tz=datetime.timezone.utc)
    assert len(user2.password_reset_secret) >= 6

    r: HttpResponse = django_client.post(f'{api_url}/user/reset', data={'email': email, 'code': 'wrong'},
                                         content_type='application/json')
    assert r.status_code == 400, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    r: HttpResponse = django_client.post(f'{api_url}/user/reset', data={
        'email': email,
        'newPassword': 'password2',
        'code': user2.password_reset_secret
    }, content_type='application/json')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    user3 = BackendUser.objects.get(id=user.id)

    assert user3.check_password('password2')

@pytest.mark.django_db
def test_api_POST_report_pooling_link_result(api_url, django_client):
    email = 'user1@example.com'
    user = ensure_superuser('user1', 'password1', email=email)

    user2 = BackendUser.objects.get(id=user.id)
    assert user2.pooling_is_linked == False, user2
    r: HttpResponse = django_client.post(f'{api_url}/user/reportPoolingLinkResult',
                                         data={'is_linked': True, 'user_id': str(user.id), 'key': 'WrongWrongWrong'},
                                         content_type='application/json')
    user2 = BackendUser.objects.get(id=user.id)
    assert r.status_code == 401, f"{r.status_code} {r.reason_phrase} {r.content}"
    assert user2.pooling_is_linked == False, user2
    del r

    user2 = BackendUser.objects.get(id=user.id)
    assert user2.pooling_is_linked == False, user2
    r: HttpResponse = django_client.post(f'{api_url}/user/reportPoolingLinkResult',
                                         data={'is_linked': True, 'user_id': str(user.id), 'key': user.auth_key_external_service},
                                         content_type='application/json')
    user2 = BackendUser.objects.get(id=user.id)
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    assert user2.pooling_is_linked == True, user2
    del r

