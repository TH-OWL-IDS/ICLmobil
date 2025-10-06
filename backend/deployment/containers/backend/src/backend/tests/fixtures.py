# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from typing import Generator, Tuple

import django.test
import pytest
from django.conf import settings

from backend.models import BackendUser


@pytest.fixture
def api_url():
    return "/api/v1"  # http://localhost:8000


@pytest.fixture
def django_client() -> Generator[django.test.Client, None, None]:
    c = django.test.Client()
    yield c


def ensure_superuser(username: str, password: str, email: str | None = None) -> BackendUser:
    user, created = BackendUser.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    if email:
        user.email = email
    else:
        user.email = username+"@example.com"
    user.save()
    return user


def login_superuser(django_client):
    ensure_superuser('admin', 'testtest')
    result = django_client.login(username='admin', password='testtest')
    assert result, "Login failed"
