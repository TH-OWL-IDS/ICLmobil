# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import argparse
import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

import django

django.setup()
from backend.constants import TASK_CELERY_BEAT_CHECK
from backend.models import BackendSyncProgress


def main(max_age_seconds: int):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    bsps = BackendSyncProgress.objects.filter(sync_key=TASK_CELERY_BEAT_CHECK)
    if not bsps:
        print(f"Could not find {TASK_CELERY_BEAT_CHECK} entry in database")
        sys.exit(2)
    bsp = bsps[0]
    if not bsp.sync_value_timestamp:
        print(f"Value not set for {TASK_CELERY_BEAT_CHECK} entry in database")
        sys.exit(3)
    age = (now-bsp.sync_value_timestamp).total_seconds()
    if age > max_age_seconds:
        print(f"Heartbeat was set {age:0.1f} seconds ago - too old!")
        sys.exit(4)
    print(f"Heartbeat was set {age:0.1f} < {max_age_seconds:0.1f} seconds ago - OK")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-age",
        type=int,
        default=60,
        help="Maximum age of celery beat heartbeat in database (in seconds, default: 60)"
    )
    args = parser.parse_args()

    main(args.max_age)