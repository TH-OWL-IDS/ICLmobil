# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import time
import datetime
import logging

from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType

from backend.enum import OptionType, BookingState
from backend.models import Booking

logger = logging.getLogger(__name__)

class BookingAutomation:
    def loop_iteration(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        # Automatically start bookings that don't require manual starting
        for b in Booking.objects.exclude(
            trip_mode__in={
                OptionType.sharing,
                OptionType.rriveOffer,
                OptionType.rriveUse,
            },
        ).filter(
            state__in={BookingState.planned},
            # Don't start bookings that have been sitting for too long
            start_time__gt=now - datetime.timedelta(minutes=5),
            start_time__lte=now,
        ):
            # noinspection PyBroadException
            try:
                b.state = BookingState.started
                b.save()
                LogEntry.objects.log_action(
                    user_id=b.user.id,
                    content_type_id=ContentType.objects.get_for_model(b).id, object_id=b.id,
                    object_repr=repr(b),
                    action_flag=CHANGE,
                    change_message=f"Booking ID {b.id} started automatically (start: {b.start_time} end {b.end_time})")
            except:
                logger.exception(f"Failed to update booking {b.id} to state started")
                time.sleep(10)
        # Time out bookings that have not been finished for a while
        for b in Booking.objects.filter(
            state__in={BookingState.started, BookingState.planned},
            end_time__lt=now-datetime.timedelta(hours=24),
        ):
            # noinspection PyBroadException
            try:
                b.state = BookingState.timeout
                b.save()
                LogEntry.objects.log_action(
                    user_id=b.user.id,
                    content_type_id=ContentType.objects.get_for_model(b).id,
                    object_id=b.id,
                    object_repr=repr(b),
                    action_flag=CHANGE,
                    change_message=f"Booking ID {b.id} set from 'started' to 'timeout' automatically")
            except:
                logger.exception(f"Failed to update booking {b.id} to state timeout")
                time.sleep(10)
