# /usr/bin/python
# encoding: utf-8
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

import os, sys, argparse
from typing import Optional, List
import time
import traceback

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

import django

django.setup()
from django.contrib.auth.models import Group
from django.db.utils import OperationalError

from backend.models import BackendUser


def main(username: str, password: str, groups: List[str], is_superuser: bool, is_staff: bool):
    # Create new superuser
    for t in range(0, 3):
        u: Optional[BackendUser] = None
        try:
            u, created = BackendUser.objects.get_or_create(username=username,
                                                           defaults={'email': f"{username}@example.com"})
            # Changing the password will make django.contrib.auth.base_user.AbstractBaseUser::get_session_auth_hash()
            # be different (because of salting) which in turn logs out anyone logged in using the previous password.
            # That's a nice feature IF the password changed, but we don't want to log someone out if the password
            # is the same.
            if created:
                print(f"User {username} is new. Setting password.")
                u.set_password(password)
            elif u.check_password(password):
                print(f"Password for {username} is still valid.")
            else:
                print(f"Updating password for {username}. Expect all sessions of that user to be invalid.")
                u.set_password(password)

            u.is_superuser = is_superuser
            u.is_staff = is_staff
            u.is_active = True
            u.save()
            print(
                f"{'Created' if created else 'Updated'} user '{username}' with password of length '{len(password)}', staff={is_staff}, superuser={is_superuser}")
            for gn in groups:
                g, created = Group.objects.get_or_create(name=gn)
                if g not in u.groups.all():
                    u.groups.add(g.pk)
                    print("Added user '%s' to group '%s'." % (username, gn))
                else:
                    print("User '%s' already in group '%s'." % (username, gn))
            break
        except OperationalError:
            traceback.print_exc()
            print(f"OperationalError on {t + 1}. try. Sleeping.")
        finally:
            if u is None:
                print(f"User was not created - maybe the User post save hook threw an exception?")
        time.sleep(5)
    else:
        # for loop was not ended using break
        raise Exception(f"Database operation didn't work. Giving up.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Username of user to create or update")
    parser.add_argument("password", help="Password of new or updated user")
    parser.add_argument("groups", help="Comma-separated list of groups to add user to", nargs="?", default="")
    parser.add_argument("--superuser", help="Make user a superuser", action="store_true")
    parser.add_argument("--no-staff", help="Don't make user staff, e.g. deny interactive logon.",
                        dest="no_staff", action="store_true")
    args = parser.parse_args()

    while True:
        # noinspection PyBroadException
        try:
            groups = [g.strip() for g in args.groups.split(',') if g.strip()]
            main(args.username, args.password, groups, args.superuser, not args.no_staff)
            break
        except:
            traceback.print_exc()
            sys.exit(1)
    print("add_user succeeded")
