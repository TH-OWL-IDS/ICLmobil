# SPDX-FileCopyrightText: 2025 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from backend.utils import RE_PATTERN_MOBILE_PHONE_NUMBER


def test_phone_number():
    assert RE_PATTERN_MOBILE_PHONE_NUMBER.match('+491711234567890')
    assert RE_PATTERN_MOBILE_PHONE_NUMBER.match('00491711234567890')
    assert not RE_PATTERN_MOBILE_PHONE_NUMBER.match('0491711234567890'), 'Not a mobile number'
    assert not RE_PATTERN_MOBILE_PHONE_NUMBER.match('004952112345678'), 'Not a mobile number'
    assert not RE_PATTERN_MOBILE_PHONE_NUMBER.match('+4952112345678'), 'Not a mobile number'
    assert RE_PATTERN_MOBILE_PHONE_NUMBER.match('+919825212345'), 'international number should be accepted'
