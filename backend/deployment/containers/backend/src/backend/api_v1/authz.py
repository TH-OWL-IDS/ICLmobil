# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from django.contrib.auth.models import AbstractUser


def can_administer_users(requesting_user: AbstractUser):
    return requesting_user.is_active and requesting_user.is_superuser


def can_administer_roles(requesting_user: AbstractUser):
    return can_administer_users(requesting_user)


def can_administer_groups(requesting_user: AbstractUser):
    return can_administer_users(requesting_user)


def can_administer_poi(requesting_user: AbstractUser):
    return can_administer_users(requesting_user)


def is_user_with_id(requesting_user: AbstractUser, user_id: str):
    if requesting_user.is_anonymous:
        return False
    return str(requesting_user.id) == user_id
