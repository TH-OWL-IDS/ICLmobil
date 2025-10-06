# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import base64
import io
import json
import os
from urllib.parse import urlencode

import pytest
import pytest_subtests
from PIL import Image
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.http import HttpResponse

from .fixtures import api_url, django_client, ensure_superuser, login_superuser
from ..models import BackendUser, BackendRole
from ..utils import generate_verification_code


def test_api_GET_getUserStatus():
    # unimplemented
    pass


@pytest.mark.django_db
def test_api_GET_getUserData(api_url, django_client):
    username, password = 'admin2', 'testtest'
    user = ensure_superuser(username, password)
    user_id = str(user.id)

    url = f'{api_url}/user/getUserData'

    r1: HttpResponse = django_client.get(url)
    assert r1.status_code == 401, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    del r1

    assert django_client.login(username=username, password=password)

    r2: HttpResponse = django_client.get(url)
    assert r2.status_code == 200, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
    data = json.loads(r2.content)
    assert type(data) == dict
    assert data['userid'] == user_id
    assert data['email'].startswith(username)
    assert data['email_is_verified'] == False
    del r2


@pytest.mark.django_db
def test_api_GET_getUsers(api_url, django_client):
    username, password = 'admin2', 'testtest'
    user = ensure_superuser(username, password)
    user_id = str(user.id)

    url = f'{api_url}/user/getUsers'

    r1: HttpResponse = django_client.get(url)
    assert r1.status_code == 401, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    del r1

    login_superuser(django_client)

    r2: HttpResponse = django_client.get(url)
    assert r2.status_code == 200, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
    data = json.loads(r2.content)
    assert type(data) == list
    assert len(data) == 2
    assert data[0]['userid'] == user_id
    del r2


@pytest.mark.django_db
def test_api_GET_getPermissions(api_url, django_client):
    url = f'{api_url}/user/getPermissions'

    r1: HttpResponse = django_client.get(url)
    assert r1.status_code == 401, f"{r1.status_code} {r1.reason_phrase} {r1.content}"
    del r1

    login_superuser(django_client)

    r2: HttpResponse = django_client.get(url)
    assert r2.status_code == 200, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
    data = json.loads(r2.content)
    assert type(data) == list
    assert len(data) > 2
    assert any(['readUsers' in x['permissionName'] for x in data]), data
    assert not any(['shouldNotExist' in x['permissionName'] for x in data]), data
    del r2


@pytest.mark.django_db
def test_api_GET_getGroups_POST_createGroup_PUT_updateGroup_deleteGroup(subtests: pytest_subtests.SubTests, api_url,
                                                                        django_client):
    url = f'{api_url}/user/'
    create_data = {
        'name': 'testgroup1',
        'description': 'testdescription',
        'permissions': "[{ bit:1, permissionName:'read dashboard' }]",
    }

    with subtests.test("POST createGroup unauth"):
        r: HttpResponse = django_client.post(url + 'createGroup', data=create_data, content_type="application/json")
        assert r.status_code == 401, f"{r.status_code} {r.reason_phrase} {r.content}"

    login_superuser(django_client)

    with subtests.test("POST createGroup"):
        r: HttpResponse = django_client.post(url + 'createGroup', data=create_data, content_type="application/json")
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert data.get('msg') == 'OK'

    with subtests.test("GET getGroups"):
        r: HttpResponse = django_client.get(url + 'getGroups')
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert type(data) == list
        created_groups = [e for e in data if e.get('name') == create_data['name']]
        assert len(created_groups) == 1, created_groups
        assert created_groups[0]['description'] == create_data['description']
        created_id = created_groups[0]['id']

    with subtests.test("PUT updateGroup"):
        update_data = {
            'groupID': created_id,
            'name': 'testgroup1',
            'description': 'updated',
        }
        r: HttpResponse = django_client.put(url + 'updateGroup', data=update_data,
                                            content_type="application/json")
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert data.get('msg') == 'OK'

    with subtests.test("Check update"):
        r: HttpResponse = django_client.get(url + 'getGroups')
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert type(data) == list
        created_groups = [e for e in data if e.get('name') == create_data['name']]
        assert len(created_groups) == 1, created_groups
        assert created_groups[0]['description'] == 'updated'

    with subtests.test("DELETE deleteGroup"):
        r: HttpResponse = django_client.delete(url + 'deleteGroup', data={'groupID': created_id},
                                               content_type="application/json")
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"

    with subtests.test("Check delete"):
        r: HttpResponse = django_client.get(url + 'getGroups')
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert type(data) == list
        created_groups = [e for e in data if e.get('id') == created_id]
        assert len(created_groups) == 0, created_groups


@pytest.mark.django_db
def test_api_GET_getAssignedGroups_POST_createAssignedGroups(subtests: pytest_subtests.SubTests, api_url,
                                                             django_client):
    username, password = 'admin2', 'testtest'
    user = ensure_superuser(username, password)
    user_id = str(user.id)

    group = Group()
    group.name = "group1"
    group.save()
    group_id = str(group.id)

    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedGroups/{user_id}')
    assert r.status_code == 401, f"{r.status_code} {r.reason_phrase} {r.content}"

    login_superuser(django_client)

    """Check no assigned groups yet"""
    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedGroups/{user_id}')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 0

    """Assign group"""
    r: HttpResponse = django_client.post(f'{api_url}/user/createAssignedGroups', data={
        "userID": user_id,
        "groups": [{"id": group_id}]
    }, content_type="application/json")
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"

    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedGroups/{user_id}')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 1
    assert data[0]['id'] == group_id
    assert data[0]['name'] == 'group1'

    """Assign no group"""
    r: HttpResponse = django_client.post(f'{api_url}/user/createAssignedGroups', data={
        "userID": user_id,
        "groups": []
    }, content_type="application/json")
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"

    """Check no assigned groups again"""
    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedGroups/{user_id}')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 0


@pytest.mark.django_db
def test_api_GET_getAssignedRoles_POST_createAssignedRoles(subtests: pytest_subtests.SubTests, api_url,
                                                           django_client):
    username, password = 'admin2', 'testtest'
    user = ensure_superuser(username, password)
    user_id = str(user.id)

    role = BackendRole()
    role.name = "role1"
    role.description = "description1"
    role.permissions = 0
    role.save()
    role_id = str(role.id)

    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedRoles/{user_id}')
    assert r.status_code == 401, f"{r.status_code} {r.reason_phrase} {r.content}"

    login_superuser(django_client)

    """Check no assigned roles yet"""
    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedRoles/{user_id}')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 0

    """Assign role"""
    r: HttpResponse = django_client.post(f'{api_url}/user/createAssignedRoles', data={
        "userID": user_id,
        "roles": [{"id": role_id}]
    }, content_type="application/json")
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"

    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedRoles/{user_id}')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 1
    assert data[0]['id'] == role_id
    assert data[0]['name'] == 'role1'
    assert data[0]['permissions'] == '0', data
    assert data[0]['options']['editable'] == True

    """Assign no role"""
    r: HttpResponse = django_client.post(f'{api_url}/user/createAssignedRoles', data={
        "userID": user_id,
        "roles": []
    }, content_type="application/json")
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"

    """Check no assigned roles again"""
    r: HttpResponse = django_client.get(f'{api_url}/user/getAssignedRoles/{user_id}')
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    data = json.loads(r.content)
    assert type(data) == list
    assert len(data) == 0


@pytest.mark.django_db
def test_api_POST_refreshToken(api_url, django_client):
    # TODO unimplemented
    pass


@pytest.mark.django_db
def test_api_GET_getRoles_POST_createRole_PUT_updateRole_GET_getRolePermissions_DELETE_deleteRole(
        subtests: pytest_subtests.SubTests, api_url, django_client):
    login_superuser(django_client)

    url_create = f'{api_url}/user/createRole'
    with subtests.test("POST createRole"):
        r1: HttpResponse = django_client.post(url_create, data={
            "name": "role1",
            "description": "lorem ipsum",
            "permissions": json.dumps(
                [{'bit': 1, 'permissionName': 'whatever'}, {'bit': 4, 'permissionName': 'whatever'}])
        }, content_type="application/json")
        assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"

    url_get = f'{api_url}/user/getRoles'
    with subtests.test("GET getRoles"):
        r2: HttpResponse = django_client.get(url_get)
        assert r2.status_code == 200, f"{r2.status_code} {r2.reason_phrase} {r2.content}"
        data = json.loads(r2.content)
        assert type(data) == list
        assert len(data) == 1
        assert data[0]['name'] == 'role1'
        assert data[0]['permissions'] == '5'
        role_id = data[0]['id']

    with subtests.test("GET getRolePermissions"):
        r: HttpResponse = django_client.get(f'{api_url}/user/getRolePermissions/{role_id}')
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert type(data) == list
        assert len(data) == 2
        assert any([e.get('bit') == 4 for e in data]), data

    with subtests.test("PUT updateRole"):
        r1: HttpResponse = django_client.put(f'{api_url}/user/updateRole', data={
            "roleID": role_id,
            "name": "updated",
            "description": "updated",
            "permissions": json.dumps(
                [{'bit': 8, 'permissionName': 'whatever'}, {'bit': 16, 'permissionName': 'whatever'}]),
        }, content_type="application/json")
        assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"

    with subtests.test("Check update"):
        r: HttpResponse = django_client.get(url_get)
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert type(data) == list
        assert len(data) == 1
        assert data[0]['name'] == 'updated'
        assert data[0]['description'] == 'updated'
        assert data[0]['permissions'] == '24'

    with subtests.test("DELETE deleteRole"):
        r1: HttpResponse = django_client.delete(f'{api_url}/user/deleteRole', data={
            "roleID": role_id
        }, content_type="application/json")
        assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"

    with subtests.test("Check delete"):
        r: HttpResponse = django_client.get(url_get)
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert type(data) == list
        assert len(data) == 0


@pytest.mark.django_db
def test_api_POST_uploadProfileImage_GET_getProfileImage(api_url, django_client):
    username, password = 'admin2', 'testtest'
    user = ensure_superuser(username, password)
    user_id = str(user.id)

    assert django_client.login(username=username, password=password)

    image_b64 = base64.b64encode(open(os.path.join(os.path.dirname(__file__), 'example.jpg'), mode='rb').read())
    r: HttpResponse = django_client.post(f'{api_url}/user/uploadProfileImage', data={
        "profileImage": image_b64.decode('utf-8'),
    }, content_type="application/json")
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    del r

    url = f'{api_url.replace("/api/", "/file/")}/user/getProfileImage/'

    r: HttpResponse = django_client.get(url+user_id)
    assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
    assert r.headers.get('Content-Type') == 'image/jpeg'
    image = Image.open(io.BytesIO(r.content))
    assert image.format == 'JPEG', image.format
    del r

    r: HttpResponse = django_client.get(url+"12345")
    assert r.status_code == 404, f"{r.status_code} {r.reason_phrase} {r.content}"
    assert r.headers.get('Content-Type') == 'application/json'
    assert 'error' in json.loads(r.content)
    del r


@pytest.mark.django_db
def test_api_PUT_updateUserStatus(api_url, django_client):
    pass
    # TODO unimplemented (not needed?)


@pytest.mark.django_db
def test_api_PUT_logout(subtests: pytest_subtests.SubTests, api_url, django_client):
    url = f'{api_url}/user/getUsers'

    with subtests.test("Unauthenticated"):
        r1: HttpResponse = django_client.get(url)
        assert r1.status_code == 401, f"{r1.status_code} {r1.reason_phrase} {r1.content}"

    login_superuser(django_client)

    with subtests.test("Authenticated"):
        r1: HttpResponse = django_client.get(url)
        assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"

    with subtests.test("Logout"):
        r1: HttpResponse = django_client.put(f'{api_url}/user/logout')
        assert r1.status_code == 200, f"{r1.status_code} {r1.reason_phrase} {r1.content}"

    with subtests.test("Unauthenticated"):
        r1: HttpResponse = django_client.get(url)
        assert r1.status_code == 401, f"{r1.status_code} {r1.reason_phrase} {r1.content}"


@pytest.mark.django_db
def test_api_PUT_updateStaleUserStatus(api_url, django_client):
    pass
    # TODO unimplemented


@pytest.mark.django_db
def test_api_PUT_updateUserProfile(api_url, django_client):
    pass
    # TODO unimplemented


@pytest.mark.django_db
def test_api_PUT_updateUser_DELETE_deleteUser(subtests: pytest_subtests.SubTests, api_url, django_client):
    username = "testuser1"
    password = "testpassword1"
    email_initial = "initial@example.com"
    email_new = "new@example.com"

    user = ensure_superuser(username, password, email=email_initial)
    user_id = str(user.id)
    del user

    assert django_client.login(username=username, password=password)

    update_data = {
        "name": "updated1",
        "password": "password2",
        "email": email_new,
        "category_id": "0",
    }

    with subtests.test("PUT updateUser"):
        r = django_client.post(f'{api_url}/user/updateUser', data=update_data,
                                             content_type="application/json")
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"

    with subtests.test("Check update"):
        user2 = BackendUser.objects.get(id=user_id)
        assert user2.last_name == update_data['name']
        assert user2.email == email_initial
        assert user2.email_next == email_new
        assert authenticate(username=username, password=password) is None, "Password should have been changed"
        assert authenticate(username=username,
                            password=update_data['password']) is not None, "Password should have been changed"

    assert django_client.login(username=username, password=update_data['password'])

    with subtests.test("Email verification"):
        code, url = user2.start_email_verification(test_mode=True, request=None)
        r = django_client.post(f'{api_url}/user/checkEmailVerificationCode', data={"code": "BAD"},
                                             content_type="application/json")
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert data['verified'] == False
        user3 = BackendUser.objects.get(id=user_id)
        assert user3.email == email_initial
        assert user3.email_next == email_new
        del user3


        r = django_client.post(f'{api_url}/user/checkEmailVerificationCode', data={"code": code},
                                             content_type="application/json")
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        data = json.loads(r.content)
        assert data['verified'] == True
        user3 = BackendUser.objects.get(id=user_id)
        assert user3.email == email_new
        assert user3.email_next == email_new
        assert user3.email_is_verified == True
        del user3

    with subtests.test("Email verification 2"):
        user4 = BackendUser.objects.get(id=user_id)
        user4.email_is_verified = False
        user4.save()

        code, url = user4.start_email_verification(test_mode=True, request=None)
        r = django_client.get(f'{url}')
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"
        assert code in r.content.decode(), f"Expected '{code}' in body: {r.content}"
        del user4

        assert not BackendUser.objects.get(id=user_id).email_is_verified

        data = {
            'code': code,
            'email': email_new,
        }
        r = django_client.post(f'{url}', urlencode(data), content_type="application/x-www-form-urlencoded")
        assert r.status_code == 200, f"{url} {data} {r.status_code} {r.reason_phrase} {r.content}"
        assert BackendUser.objects.get(id=user_id).email_is_verified

    # Cannot delete last superuser, so... generate another one first
    ensure_superuser("user2", "password")

    with subtests.test("DELETE deleteUser"):
        r: HttpResponse = django_client.delete(f'{api_url}/user/deleteUser', data={
            'userID': user_id
        }, content_type="application/json")
        assert r.status_code == 200, f"{r.status_code} {r.reason_phrase} {r.content}"

    with subtests.test("Check update"):
        with pytest.raises(BackendUser.DoesNotExist):
            BackendUser.objects.get(id=user_id)
        with pytest.raises(BackendUser.DoesNotExist):
            BackendUser.objects.get(username=username)
