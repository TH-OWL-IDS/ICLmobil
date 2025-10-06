# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import json
import logging
import random
import time
import traceback
from abc import ABC, abstractmethod
from typing import List, Dict

import firebase_admin
from django.conf import settings
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
from ninja import Schema

from backend.apns.client import ApnsPushClient, ApnsCertificateError, ApnsResponse
from backend.apns.payload import Payload
from backend.constants import TASK_PUSH_NOTIFICATIONS
from backend.models import Message, PushNotificationDevice

logger = logging.getLogger(__name__)


class PushAttemptResult(Schema):
    timestamp: datetime.datetime
    successful: bool
    invalidate_device: bool
    notes: str


class PushTokenState(Schema):
    attempts: List[PushAttemptResult]
    done: bool
    notes: str


class PushState(Schema):
    tokens: Dict[str, PushTokenState]


def get_apns_push_setup_problems() -> List[str]:
    problems = []
    if not settings.PUSH_APNS_CERTIFICATE_KEY_PEM:
        problems.append(f"Missing APNS_CERTIFICATE_WITH_KEY_PEM environment variable")
    # noinspection PyPackageRequirements
    try:
        try:
            ApnsPushClient(certificate_with_key_content=settings.PUSH_APNS_CERTIFICATE_KEY_PEM)
        except ApnsCertificateError:
            problems.append(
                f"APNs (iOS) push certificate failed to load. Check certificate/key in APNS_CERTIFICATE_WITH_KEY_PEM.")
            raise
    except:
        problems.append(f"Exception was: {traceback.format_exc()}")
    # TODO check certificate age before it's too late.
    return problems


MAX_PUSH_ATTEMPTS = 5


class AbstractPushHandler(ABC):
    @abstractmethod
    def push_attempt(self, message: Message, device: PushNotificationDevice) -> PushAttemptResult:
        pass

    @abstractmethod
    def send_push(self, title: str, device: PushNotificationDevice) -> PushAttemptResult:
        pass


class ApplePushHandler(AbstractPushHandler):

    def __init__(self):
        super().__init__()
        self.client = None
        try:
            self.client = ApnsPushClient(certificate_with_key_content=settings.PUSH_APNS_CERTIFICATE_KEY_PEM)
        except ApnsCertificateError:
            logger.exception(f"APNs push client could not be initialized")
            self.client = None

    def send_push(self, title: str, device: PushNotificationDevice) -> PushAttemptResult:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        payload = Payload(alert=title, sound="default")
        result, reason = self.client.send_notification(device.token, payload, topic=settings.PUSH_APNS_TOPIC)
        if result == ApnsResponse.SUCCESS:
            return PushAttemptResult(timestamp=now, successful=True, invalidate_device=False,
                                     notes='OK')
        elif result == ApnsResponse.DEVICE_TOKEN_INACTIVE_ERROR:
            return PushAttemptResult(timestamp=now, successful=False, invalidate_device=True,
                                     notes=reason)
        elif result == ApnsResponse.BAD_DEVICE_TOKEN:
            return PushAttemptResult(timestamp=now, successful=False, invalidate_device=True,
                                     notes=reason)
        else:
            return PushAttemptResult(timestamp=now, successful=False, invalidate_device=False,
                                     notes=f"{result.value}/{reason}")

    def push_attempt(self, message: Message, device: PushNotificationDevice) -> PushAttemptResult:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if self.client:
            logger.info(f"Apple push attempt for '{message}' to '{device}'")
            return self.send_push(message.title, device)
        else:
            logger.warning(f"Apple push attempt not made '{message}' to '{device}': Client could not be initialized")
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            return PushAttemptResult(timestamp=now, successful=False, invalidate_device=False,
                                     notes='Client failed to initialize')


__firebase_initialized = False
def ensure_firebase_initialized():
    global __firebase_initialized
    if not __firebase_initialized:
        # noinspection PyBroadException
        try:
            certificate_data = json.loads(settings.PUSH_ANDROID_GCM_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(certificate_data)
            firebase_admin.initialize_app(cred)
            __firebase_initialized = True
        except json.decoder.JSONDecodeError:
            logger.exception(
                f"Failed to decode GCM service account JSON from: {settings.PUSH_ANDROID_GCM_SERVICE_ACCOUNT_JSON[:100]}...")
        except:
            logger.exception(
                f"GCM initialization failed for GCM service account JSON from: {settings.PUSH_ANDROID_GCM_SERVICE_ACCOUNT_JSON[:100]}...")


def is_firebase_initialized():
    global __firebase_initialized
    return __firebase_initialized


class AndroidPushHandler(AbstractPushHandler):

    def __init__(self):
        super().__init__()
        ensure_firebase_initialized()

    def send_push(self, title: str, device: PushNotificationDevice) -> PushAttemptResult:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        message = messaging.Message(
            notification=messaging.Notification(
                title=settings.PUSH_ANDROID_TITLE,
                body=title
            ),
            token=device.token
        )

        # noinspection PyBroadException
        try:
            response = messaging.send(message)
            logger.debug(f"Successfully sent message: {response}")
            return PushAttemptResult(timestamp=now, successful=True, invalidate_device=False,
                                     notes='OK')

        except FirebaseError as e:
            msg = f"Failed to push '{title}' to '{device}' with '{e.code} {e.http_response} {e.cause}'"
            logger.exception(msg)
            return PushAttemptResult(timestamp=now, successful=False, invalidate_device=False,
                                     notes=msg)
        except:
            msg = f"Failed to push '{title}' to '{device}' " + traceback.format_exc()
            logger.exception(msg)
            return PushAttemptResult(timestamp=now, successful=False, invalidate_device=False,
                                     notes=msg)

    def push_attempt(self, message: Message, device: PushNotificationDevice) -> PushAttemptResult:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if is_firebase_initialized():
            logger.info(f"Android push attempt for '{message}' to '{device}'")
            return self.send_push(message.title, device)
        else:
            logger.warning(f"Android push attempt not made '{message}' to '{device}': Library could not be initialized")
            return PushAttemptResult(timestamp=now, successful=False, invalidate_device=False,
                                     notes='Library failed to initialize')


def push_loop_iteration(until_monotonic: float | None = None):
    _start_time = time.monotonic()
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    messages = Message.objects.filter(
        push_notification_requested=True,
        push_notification_done=False,
    ).exclude(
        publish_after__gt=now,
    ).exclude(
        # do not send out scheduled messages that have been sitting for too long
        publish_after__lt=now - datetime.timedelta(minutes=10),
    ).all()
    logger.debug(f"{TASK_PUSH_NOTIFICATIONS}: {len(messages)} outstanding messages")
    for message in messages:
        if until_monotonic and time.monotonic() > until_monotonic:
            logger.warning(f"Did not complete processing in {until_monotonic - _start_time:0.1f}s")
            break
        if now > message.push_notification_no_later_than:
            logger.warning(f"Push for '{message}' did not successfully complete in time")
            message.push_notification_done = True

        if message.push_notification_state:
            state = PushState.model_validate_json(str(message.push_notification_state))
        else:
            state = PushState(tokens={})
        # Try to deliver message to all of user's valid PushNotificationDevices
        # except those that have been marked as done before.
        tokens_done = {token_id for token_id, pts in state.tokens.items() if pts.done}
        pnds = PushNotificationDevice.objects.filter(user=message.user, state__in={'valid', 'invalid'}).exclude(
            token__in=tokens_done).all()
        for pnd in pnds:
            pnd: PushNotificationDevice
            if pnd.token not in state.tokens:
                state.tokens[pnd.token] = PushTokenState(attempts=[], done=False, notes="")
            if len(state.tokens[pnd.token].attempts) >= MAX_PUSH_ATTEMPTS:
                logger.warning(f"Push for '{message}' to '{pnd}' failed too many times. Giving up.")
                message.push_notification_done = True
            else:
                # Make another/first attempt to deliver push notification
                if pnd.push_system == 'apple':
                    result = ApplePushHandler().push_attempt(message, pnd)
                elif pnd.push_system == 'android':
                    result = AndroidPushHandler().push_attempt(message, pnd)
                else:
                    logger.error(f"Unknown push system '{pnd.push_system}'")
                    result = PushAttemptResult(timestamp=now, successful=False, invalidate_device=False,
                                               notes='Unknown push system')
                logger.info(f"Push for '{message}' result: {result}")
                pnd.last_push_attempt_at = now
                state.tokens[pnd.token].attempts.append(result)
                if result.successful or result.invalidate_device:
                    state.tokens[pnd.token].done = True
                delete_pnd = False
                if result.invalidate_device:
                    if pnd.state == 'invalid':
                        logger.info(f"Already invalid '{pnd}' will be deleted (after result: {result})")
                        delete_pnd = True
                    else:
                        logger.info(f"Invalidating '{pnd}' after result: {result}")
                        pnd.state = 'invalid'
                if delete_pnd:
                    LogEntry.objects.log_action(
                        user_id=pnd.user.id,
                        content_type_id=ContentType.objects.get_for_model(pnd.user).id,
                        object_id=pnd.user.id,
                        object_repr=repr(pnd.user),
                        action_flag=CHANGE,
                        change_message=f"Push device {pnd.push_system} {pnd.device_model} {pnd.token} removed after second invalid attempt")
                    pnd.delete()
                else:
                    pnd.save()

        pnds_tokens = {pnd.token for pnd in pnds}
        if all([pnd_token in state and state[pnd_token].done for pnd_token in pnds_tokens]):
            logger.info(f"All device tokens are done for '{message}': {state!r}")
            message.push_notification_done = True
        logger.debug(f"Push state for '{message}': {state!r}")
        message.push_notification_state = state.model_dump_json()
        message.save()
