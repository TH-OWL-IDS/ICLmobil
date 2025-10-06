# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import logging
from typing import Literal, Optional, get_args, Tuple

from django.conf import settings
from twilio.rest import Client
from twilio.rest.verify.v2.service import VerificationList
from twilio.rest.verify.v2.service.verification import VerificationInstance
from twilio.rest.verify.v2.service.verification_check import VerificationCheckInstance

logger = logging.getLogger(__name__)

__twilio_client = None
def get_twilio_client():
    global __twilio_client
    if not __twilio_client:
        assert settings.TWILIO_API_SID, "Missing settings.TWILIO_API_SID"
        assert settings.TWILIO_API_SECRET, "Missing settings.TWILIO_API_SECRET"
        __twilio_client = Client(settings.TWILIO_API_SID, settings.TWILIO_API_SECRET, account_sid=settings.TWILIO_ACCOUNT_SID)
    return __twilio_client

def get_verify_service() -> VerificationList:
    client = get_twilio_client()
    verify = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications
    return verify

def create_verification(phone_number: str) -> VerificationInstance:
    result = get_verify_service().create(to=phone_number, channel='sms')
    logger.debug(f"Verification creation result for '{phone_number}': SID={result.sid} status={result.status} valid={result.valid}")
    return result

def get_balance() -> Tuple[float, str]:
    client = get_twilio_client()
    balance_data = client.api.account.balance.fetch()
    return float(balance_data.balance), balance_data.currency

VerifyCodeResult = Literal['unknown', 'pending', 'approved', 'canceled', 'max_attempts_reached', 'deleted', 'failed', 'expired']
def check_verify_code(verification_sid: Optional[str], phone_number: Optional[str], code: str) -> Tuple[VerifyCodeResult, VerificationCheckInstance]:
    assert verification_sid or phone_number, "Specify either phone_number or verification_id"
    client = get_twilio_client()
    params = {
        'code': code,
    }
    if verification_sid:
        params['verification_sid'] = verification_sid
    if phone_number:
        params['to'] = phone_number
    verify = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(**params)
    return (verify.status if verify.status in get_args(VerifyCodeResult) else 'unknown'), verify
    # Wrong code
    # {"status": "pending", "payee": null, "date_updated": "2024-10-30T16:47:00Z", "account_sid": "AC02...b", "to": "+49171...", "amount": null, "valid": false, "sid": "VE4...9", "date_created": "2024-10-30T16:46:39Z", "service_sid": "VAe...8", "channel": "sms"}
    # Good code

    #Expired -> 404

    # {"status": "approved", "payee": null, "date_updated": "2024-10-30T16:48:13Z", "account_sid": "AC0...b", "to": "+49171...", "amount": null, "valid": true, "sid": "VE4...9", "date_created": "2024-10-30T16:46:39Z", "service_sid": "VAe...8", "channel": "sms"}
