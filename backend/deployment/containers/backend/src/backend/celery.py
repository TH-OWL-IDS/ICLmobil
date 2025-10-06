# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import os
import time
import logging

import celery
import logging_tree
from celery import Celery
from celery.signals import worker_ready
from django.conf import settings
from efa.client import import_efa_stops_as_pois

from backend.constants import TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT, TASK_NAME_SEND_SMS, TASK_RRIVE_HEALTHCHECK, \
    TASK_USER_SCORE_UPDATE_SCHEDULER, TASK_NEWS_EXTERNAL_SYNC, TASK_CELERY_BEAT_CHECK

logger = logging.getLogger(__name__)
logger.propagate = False

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY', force=True)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

LONG_RUNNING_END_AFTER_SECONDS = 1_800 - 120


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task(bind=True, name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT)
def update_public_transport_pois(self):
    logger.info(f"Starting initial public transport POI import")
    import_efa_stops_as_pois(settings.PUBLIC_TRANSPORT_EFA_ENDPOINT, settings.PUBLIC_TRANSPORT_EFA_POI_TYPE)
    logger.info(f"Finished initial public transport POI import")


@app.task(bind=True, name=TASK_NAME_SEND_SMS)
def send_sms(self, phone_number: str, text: str):
    logger.info(f"Starting SMS send to {phone_number} for text: {text}")
    self.update_state(state='STARTED', meta={'progress': 0})
    for k in range(10):
        time.sleep(2)
        self.update_state(state='PROGRESS', meta={'progress': k + 1})
    logger.info(f"Finished SMS send to {phone_number} for text: {text}")


@app.task(bind=True, name=TASK_RRIVE_HEALTHCHECK)
def rrive_healthcheck(self):
    from backend import rrive
    from backend.rrive import RRiveStatusCodeEnum

    status_message = rrive.healthcheck()
    logger.info(
        f"RRive healthcheck status {status_message.statusCode}, Result: {status_message!r} (Sucess value: {RRiveStatusCodeEnum.SUCCESS!r})")
    assert status_message.statusCode == RRiveStatusCodeEnum.SUCCESS.value


@app.task(bind=True, name=TASK_USER_SCORE_UPDATE_SCHEDULER)
def user_score_update_scheduler(self):
    from backend.models import BackendUser
    logger.info(f"Updating all user accounts with recalculated scores")
    count_updated = 0
    count_failed = 0
    users = BackendUser.objects.all()
    for bu in users:
        # noinspection PyBroadException
        try:
            if bu.update_score():
                count_updated += 1
                bu.save()
        except:
            count_failed += 1
            logger.exception(f"Failed updating user {bu}")
    logger.info(f"Updating {len(users)} users finished. {count_updated} changed. {count_failed} failed.")


@app.task(bind=True, name=TASK_CELERY_BEAT_CHECK)
def celery_beat_heartbeat(self):
    from backend.models import BackendSyncProgress
    logger.debug(f"Setting celery beat heartbeat in database")
    BackendSyncProgress.objects.update_or_create(
        sync_key=TASK_CELERY_BEAT_CHECK,
        defaults={
            'sync_value_timestamp': datetime.datetime.now(tz=datetime.timezone.utc),
        }
    )

@app.task(bind=True, name=TASK_NEWS_EXTERNAL_SYNC)
def user_score_update_scheduler(self):
    if not settings.NEWS_EXTERNAL_SYNC_URL:
        logger.warning(f"Set NEWS_EXTERNAL_SYNC_URL to enable news synchronization")
        return
    from backend.news_sync import news_sync
    logger.info(f"Syncing external news")
    news_sync(settings.NEWS_EXTERNAL_SYNC_URL)
    logger.info(f"Syncing external finished")


@worker_ready.connect
def at_start(sender, **k):
    if settings.TESTING_IN_PROGRESS:
        logger.info("NOT scheduling update_public_transport_pois because testing is underway")
    else:
        logging_tree.printout()
        with sender.app.connection() as conn:
            logger.info(f"Scheduling update_public_transport_pois 240s into the future")
            sender.app.send_task(TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT, countdown=240, connection=conn)
            logger.info(f"Scheduling RRive health check 10s into the future")
            sender.app.send_task(TASK_RRIVE_HEALTHCHECK, countdown=10, connection=conn)
        # logger.warning(f"Scheduling {TASK_PUSH_NOTIFICATIONS} to run every minute")
        # sender.app.add_periodic_task(
        #     crontab(minute="*"),
        #     long_running_push_notification_handler.s('Long-running: Handle push notifications'),
        # )


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, CrontabSchedule

    if not PeriodicTask.objects.filter(name=TASK_USER_SCORE_UPDATE_SCHEDULER).exists():
        cs, _ = CrontabSchedule.objects.get_or_create(
            hour='4',
            minute='0',
        )
        pt, _ = PeriodicTask.objects.get_or_create(
            name=TASK_USER_SCORE_UPDATE_SCHEDULER,
            defaults={
                'task': TASK_USER_SCORE_UPDATE_SCHEDULER,
                'crontab': cs,
            }
        )

    if not PeriodicTask.objects.filter(name=TASK_NEWS_EXTERNAL_SYNC).exists():
        cs, _ = CrontabSchedule.objects.get_or_create(
            minute='*/5',
        )
        pt, _ = PeriodicTask.objects.get_or_create(
            name=TASK_NEWS_EXTERNAL_SYNC,
            defaults={
                'task': TASK_NEWS_EXTERNAL_SYNC,
                'crontab': cs,
            }
        )

    if not PeriodicTask.objects.filter(name=TASK_CELERY_BEAT_CHECK).exists():
        cs, _ = CrontabSchedule.objects.get_or_create(
            minute='*',
        )
        pt, _ = PeriodicTask.objects.get_or_create(
            name=TASK_CELERY_BEAT_CHECK,
            defaults={
                'task': TASK_CELERY_BEAT_CHECK,
                'crontab': cs,
            }
        )



# Avoid Celery hijacking the root logger
@celery.signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass
