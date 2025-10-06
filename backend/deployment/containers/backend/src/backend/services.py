# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import faulthandler
import logging
import os
import signal
import sys
import threading
import time
from typing import Callable, Set

import django
import logging_tree

from backend.constants import TASK_PUSH_NOTIFICATIONS, TASK_SHARINGOS_SYNC, TASK_BOOKING_AUTOMATION, \
    TASK_USER_SCORE_UPDATER, TASK_RRIVE_POLL_REPORTS

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()

from backend.models import Booking, BackendUser

logger = logging.getLogger('services')
logger.propagate = False

MAX_LOOP_UPDATE_DELAY = 60


class ServiceThread(threading.Thread):
    def __init__(self, name: str, loop_function: Callable, delay_initial=1.0, delay_loop=1.0):
        super().__init__()
        self.name = name
        self.loop_function = loop_function
        self.last_loop_timestamp = time.monotonic()
        self._shutdown = False
        self.delay_initial = delay_initial
        self.delay_loop = delay_loop

    def update_loop_timestamp(self):
        self.last_loop_timestamp = time.monotonic()

    def run(self):
        self.update_loop_timestamp()
        logger.info(f"Thread '{self.name}': Starting")
        time.sleep(self.delay_initial)
        loop_count = 0
        try:
            while not self._shutdown:
                loop_count += 1
                logger.debug(f"Thread '{self.name}': Loop iteration {loop_count}")
                try:
                    self.loop_function()
                    self.update_loop_timestamp()
                except:
                    logger.exception(f"Thread '{self.name}': Loop iteration {loop_count} exception")
                    raise

                time.sleep(self.delay_loop)
        finally:
            logger.info(f"Thread '{self.name}': Ending")

    def shutdown(self):
        logger.info(f"Thread '{self.name}': Shutdown initiated")
        self._shutdown = True

def user_score_updater():
    to_be_updated = Booking.objects.filter(score_needs_update=True).all()
    logger.debug(f"{TASK_USER_SCORE_UPDATER}: About to update users for {len(to_be_updated)} bookings: {to_be_updated}")
    user_id_updated = set()
    for b in to_be_updated:
        if b.user and b.user.id not in to_be_updated:
            b.user.update_score()
            b.user.save()
            user_id_updated.add(b.user.id)
        b.score_needs_update = False
        b.save()


def main():
    """Used for permanently running services that don't fit celery's task model well"""
    faulthandler.enable(all_threads=True)
    faulthandler.register(signal.SIGUSR1)
    faulthandler.dump_traceback_later(30, exit=True)

    logger.info("Starting")
    logger.warning('Logging tree: '+logging_tree.format.build_description())

    services = []

    from sharingos.client import SharingOSClient  # Needs to be after app.config_from_object
    sharingos_client = SharingOSClient()
    from backend.push import push_loop_iteration  # Needs to be after app.config_from_object
    from backend.booking_automation import BookingAutomation  # Needs to be after app.config_from_object
    ba = BookingAutomation()

    from backend.rrive import RriveRequestPoller
    rrp = RriveRequestPoller(TASK_RRIVE_POLL_REPORTS)

    for delay_loop_s, task_name, func in [
        (5, TASK_PUSH_NOTIFICATIONS, push_loop_iteration),
        (30, TASK_SHARINGOS_SYNC, sharingos_client.sync_loop_iteration),
        (30, TASK_BOOKING_AUTOMATION, ba.loop_iteration),
        (20, TASK_USER_SCORE_UPDATER, user_score_updater),
        (5, TASK_RRIVE_POLL_REPORTS, rrp.poll)
    ]:
        st = ServiceThread(task_name, func, delay_loop=delay_loop_s)
        services.append(st)
        logger.info(f"Starting thread '{task_name}' with function '{func}'")
        st.start()

    logging.info(f"Starting to monitor {len(services)} threads")
    try:
        while True:
            time.sleep(1)
            now = time.monotonic()
            all_ok = True
            for st in services:
                if not st.is_alive():
                    logger.warning(f"Thread '{st.name}' ended")
                    all_ok = False
                loop_update_delay = now - st.last_loop_timestamp
                if loop_update_delay > MAX_LOOP_UPDATE_DELAY:
                    logger.warning(
                        f"Thread '{st.name} did not complete a loop in {loop_update_delay:0.1f}s>{MAX_LOOP_UPDATE_DELAY:0.1f}s")
                    all_ok = False
            if all_ok:
                faulthandler.dump_traceback_later(MAX_LOOP_UPDATE_DELAY + 10, exit=True)
            else:
                break
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Shutting down")
        faulthandler.dump_traceback_later(30, exit=True)
        for st in services:
            if st.is_alive():
                st.shutdown()
    logger.info("Waiting for threads to end")
    while True:
        time.sleep(1)
        if not any([st.is_alive() for st in services]):
            break
    logger.info("Threads ended - exiting")
    sys.exit(0)


if __name__ == '__main__':
    main()
