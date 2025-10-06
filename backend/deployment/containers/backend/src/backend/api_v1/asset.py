# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.http import HttpRequest
from ninja import Router

from backend.api_v1.schemas import ErrorResponse, MsgResponse, TranslatedErrorResponse, AssetUnlockRequest, \
    AssetLockRequest
from backend.models import Booking, BackendUser
from backend.utils import TranslatedString

router = Router()

logger = logging.getLogger(__name__)



@router.post(
    "/unlock",
    response={
        200: MsgResponse,
        400: TranslatedErrorResponse,
        401: ErrorResponse,
        404: ErrorResponse,
        504: TranslatedErrorResponse,
    },
    summary="Unlock an asset like a vehicle",
    description="""
Returns 200 if the asset was successfully unlocked.
Returns 400 if a) the unlock secret is needed for this asset but was either omitted or wrong,
b) the booking does not belong to the user,
c) the booking is not in an appriopriate state (e.g. not planned or already finished) or
d) the booking is not for the current point in time or
e) the asset does not support locking/unlocking.
The response contains a user-appropriate message in the response body in these cases.
Returns 401 if user is not authenticated (e.g. missing Header/Cookie).
Returns 404 if the booking was not found.
Returns 404 if the booking does not contain an asset to unlock.
Returns 504 if unlocking was attempted but failed in an unexpected way (e.g. due to connection problems).
The response will be a user-appropriate message in the response body. 
""",
    tags=['asset'],
)
def post_unlock(request: HttpRequest, unlock_request: AssetUnlockRequest):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    # noinspection PyTypeChecker
    user: BackendUser = request.user
    try:
        booking = Booking.objects.get(id=int(unlock_request.booking_id))
        if booking.user != user:
            return 404, ErrorResponse(error="Not authenticated for this booking")
    except (ValueError, Booking.DoesNotExist):
        return 404, ErrorResponse(error=f"Booking with ID '{unlock_request.booking_id}' not found")

    if not booking.vehicle:
        return 404, ErrorResponse(error="No asset associated with booking")

    ok, message = booking.can_be_unlocked(user)
    if not ok:
        return 400, TranslatedErrorResponse(error=message)

    ok, message = booking.vehicle.can_be_unlocked(unlock_request.unlock_secret)
    if not ok:
        return 400, TranslatedErrorResponse(error=message)

    # Trigger unlock
    # noinspection PyBroadException
    try:
        booking.vehicle.unlock(user, booking)
    except:
        return 504, TranslatedErrorResponse(error=TranslatedString.from_gettext("Der Entsperrversuch ist aus unbekannten Gründen fehlgeschlagen."))

    return 200, MsgResponse(msg="OK")


@router.post(
    "/lock",
    response={
        200: MsgResponse,
        400: TranslatedErrorResponse,
        401: ErrorResponse,
        404: ErrorResponse,
        504: TranslatedErrorResponse,
    },
    summary="Lock an asset like a vehicle",
    description="""
Returns 200 if the asset was successfully unlocked.
Returns 400 if the booking is not valid (anymore) and the (now invalid/expired) booking was not the last booking for this asset.
Returns 401 if user is not authenticated (e.g. missing Header/Cookie).
Returns 404 if the booking was not found.
Returns 404 if the booking does not contain an asset to unlock.
Returns 504 if unlocking was attempted but failed in an unexpected way (e.g. due to connection problems).
The response will be a user-appropriate message in the response body. 
""",
    tags=['asset'],
)
def post_lock(request: HttpRequest, unlock_request: AssetLockRequest):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    # noinspection PyTypeChecker
    user: BackendUser = request.user
    try:
        booking = Booking.objects.get(id=int(unlock_request.booking_id))
        if booking.user != user:
            return 404, ErrorResponse(error="Not authenticated for this booking")
    except (ValueError, Booking.DoesNotExist):
        return 404, ErrorResponse(error=f"Booking with ID '{unlock_request.booking_id}' not found")

    if not booking.vehicle:
        return 404, ErrorResponse(error="No asset associated with booking")

    ok, message = booking.can_be_locked(user)
    if not ok:
        return 400, TranslatedErrorResponse(error=message)

    # Trigger lock
    # noinspection PyBroadException
    try:
        booking.vehicle.lock(user)
    except:
        return 504, TranslatedErrorResponse(error=TranslatedString.from_gettext("Der Sperrversuch ist aus unbekannten Gründen fehlgeschlagen."))

    return 200, MsgResponse(msg="OK")

