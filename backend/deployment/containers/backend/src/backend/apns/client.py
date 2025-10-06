# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import json
import logging
import ssl
import tempfile
from enum import Enum
from typing import Optional, Tuple

import httpx

from .payload import Payload, NotificationType, NotificationPriority, DEFAULT_APNS_PRIORITY

# openssl pkcs12 -legacy -out Certificates.pem -password pass:123456 -nodes < Certificates.p12
# openssl pkcs12 -legacy -nocerts -out Certificates.pwprotected.key -password pass:123456 -passin pass:123456 -passout:TempPassword -nodes < Certificates.p12
# openssl rsa -in Certificates.pwprotected.key -out Certificates.key -passin pass:TempPassword
token_hex = '3c93a0c175278a9a6ce9d9b10b2a55aa8b3164871b3bc0d4136055652a185ae5'
payload = Payload(alert="Hello World!", sound="default", badge=1)

SANDBOX_SERVER = 'api.development.push.apple.com'
LIVE_SERVER = 'api.push.apple.com'

logger = logging.getLogger()


class ApnsResponse(Enum):
    SUCCESS = 'success'
    AUTH_ERROR = 'auth_error'
    DEVICE_TOKEN_INACTIVE_ERROR = 'device_token_inactive_error'
    OTHER_ERROR = 'other_error'
    BAD_DEVICE_TOKEN = 'bad_device_token'


class ApnsCertificateError(Exception):
    pass


class ApnsPushClient:
    def __init__(self, certificate_with_key_filename: str | None = None,
                 certificate_with_key_content: str | None = None, use_sandbox=False):
        assert certificate_with_key_filename or certificate_with_key_content, "Must specify one way to get certificate"

        ctx = ssl.create_default_context()
        if certificate_with_key_content:
            try:
                with tempfile.NamedTemporaryFile() as cert_file:
                    cert_file.write(certificate_with_key_content.encode('utf-8'))
                    cert_file.seek(0)
                    ctx.load_cert_chain(certfile=cert_file.name)
            except ssl.SSLError as e:
                logger.exception(f"Failed with SSLError when loading: {certificate_with_key_content[:100]}...")
                raise ApnsCertificateError(e)
        else:
            try:
                ctx.load_cert_chain(certfile=certificate_with_key_filename)
            except ssl.SSLError as e:
                logger.exception(f"Failed with SSLError when loading: {certificate_with_key_filename}")
                raise ApnsCertificateError(e)
        self.client = httpx.Client(verify=ctx, http2=True)
        self.host = SANDBOX_SERVER if use_sandbox else LIVE_SERVER

    def send_notification(self, token_hex: str, notification: Payload, topic: Optional[str] = None,
                          priority: NotificationPriority = NotificationPriority.Immediate,
                          expiration: Optional[int] = None, collapse_id: Optional[str] = None,
                          push_type: Optional[NotificationType] = None) -> Tuple[ApnsResponse, str]:
        # method inspired by PyAPNs2

        # see Apple's simple example using curl as a starter:
        # https://developer.apple.com/documentation/usernotifications/sending-push-notifications-using-command-line-tools?language=objc#Send-a-push-notification-using-a-certificate

        __json_encoder = None
        json_str = json.dumps(notification.dict(), ensure_ascii=False, separators=(',', ':'))
        json_payload = json_str.encode('utf-8')

        headers = {}

        inferred_push_type = None  # type: Optional[str]
        if topic is not None:
            headers['apns-topic'] = topic
            if topic.endswith('.voip'):
                inferred_push_type = NotificationType.VoIP.value
            elif topic.endswith('.complication'):
                inferred_push_type = NotificationType.Complication.value
            elif topic.endswith('.pushkit.fileprovider'):
                inferred_push_type = NotificationType.FileProvider.value
            elif any([
                notification.alert is not None,
                notification.badge is not None,
                notification.sound is not None,
            ]):
                inferred_push_type = NotificationType.Alert.value
            else:
                inferred_push_type = NotificationType.Background.value

        if push_type:
            inferred_push_type = push_type.value

        if inferred_push_type:
            headers['apns-push-type'] = inferred_push_type

        if priority != DEFAULT_APNS_PRIORITY:
            headers['apns-priority'] = priority.value

        if expiration is not None:
            headers['apns-expiration'] = '%d' % expiration

        # This would be the place for token based auth:
        # headers['authorization'] = auth_header

        if collapse_id is not None:
            headers['apns-collapse-id'] = collapse_id

        url = f'https://{self.host}/3/device/{token_hex}'

        def __try_extract_reason(content: bytes) -> str:
            if not content:
                return ''
            # noinspection PyBroadException
            try:
                data = json.loads(content)
                return data['reason']
            except:
                logger.debug(f"Failed to decode: {content!r}")
                return ''

        try:
            response = self.client.post(url, content=json_payload, headers=headers)
            logger.debug(
                f"Response: HTTP/{response.http_version} {response.status_code} {response.reason_phrase} {response.content}")
        except Exception as e:
            logger.exception(f"Failed POST to '{url}' with payload '{json_payload}' and headers: {headers}")
            return ApnsResponse.OTHER_ERROR, str(e)
        reason = __try_extract_reason(response.content)
        # Responses: https://developer.apple.com/documentation/usernotifications/handling-notification-responses-from-apns?language=objc
        if response.status_code == 200:
            return ApnsResponse.SUCCESS, 'OK'
        elif response.status_code == 403:
            return ApnsResponse.AUTH_ERROR, reason
        elif response.status_code == 410:
            return ApnsResponse.DEVICE_TOKEN_INACTIVE_ERROR, reason
        elif 'BadDeviceToken' in reason:
            return ApnsResponse.BAD_DEVICE_TOKEN, reason
        else:
            return ApnsResponse.OTHER_ERROR, reason
