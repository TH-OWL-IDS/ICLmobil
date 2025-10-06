# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

import datetime
import logging
from typing import List

from django.contrib.gis.geos import Point
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpRequest
from ninja import Router

from backend.api_v1.schemas import ErrorResponse, MsgResponse, BookingSchema, BookingCreateSchema, BookingUpdateSchema, \
    BookingFrontendResponse, \
    BookingFrontendSchema, TranslatedErrorResponse, CreateSuccessResponse, PointsEstimateRequest, PointsEstimateResponse
from backend.enum import OptionType, BookingState
from backend.models import Booking, Vehicle
from backend.utils import TranslatedString

router = Router()

logger = logging.getLogger(__name__)



@router.get(
    "/list",
    response={
        200: List[BookingSchema],
        401: ErrorResponse,
    },
    summary="Get all bookings of this user",
    description=""" """,
    tags=['booking'],
)
def get_list_me(request: HttpRequest):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    return 200, [BookingSchema.from_django(b) for b in Booking.objects.filter(user=request.user).all()]


@router.get(
    "/list/frontend",
    response={
        200: BookingFrontendResponse,
        401: ErrorResponse,
    },
    summary="All bookings of this user in a format that is easier to work with for the frontend",
    description=""" """,
    tags=['booking'],
)
def get_list_frontend(request: HttpRequest):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return 200, BookingFrontendResponse(
        previousRides=[BookingFrontendSchema.from_django(b) for b in Booking.queryset_previous(request.user, now).order_by('-start_time').all()],
        nextRides=[BookingFrontendSchema.from_django(b) for b in Booking.queryset_next(request.user, now).order_by('-start_time').all()],
    )


@router.get(
    "/{booking_id}/frontend",
    response={
        200: BookingFrontendSchema,
        401: ErrorResponse,
        404: ErrorResponse,
    },
    summary="One booking of this user in a format for the frontend",
    description=""" """,
    tags=['booking'],
)
def get_booking_frontend(request: HttpRequest, booking_id: str):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    try:
        booking = Booking.objects.get(id=int(booking_id))
        if booking.user != request.user:
            return 404, ErrorResponse(error="Not authenticated")
        return 200, BookingFrontendSchema.from_django(booking)
    except (ValueError, Booking.DoesNotExist):
        return 404, ErrorResponse(error="No booking found")



@router.delete(
    "/delete/{bookingID}",
    response={
        200: MsgResponse,
        401: ErrorResponse,
        404: ErrorResponse,
    },
    summary="Delete the booking",
    description=""" """,
    tags=['booking'],
)
def delete(request: HttpRequest, bookingID: str):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    try:
        booking = Booking.objects.get(id=int(bookingID))
        if booking.user != request.user:
            return 404, ErrorResponse(error="Not authenticated")
        booking.delete()
    except (ValueError, Booking.DoesNotExist):
        return 404, ErrorResponse(error="No booking found")
    return 200, MsgResponse(msg="OK")


@router.post(
    "/create",
    response={
        200: CreateSuccessResponse,
        400: ErrorResponse,
        401: ErrorResponse,
        409: TranslatedErrorResponse,
    },
    summary="Create new booking for this user",
    description="""
If the booking to be created would conflict with another booking that has an overlapping time range and the same vehicle,
409 is returned.
""",
    tags=['booking'],
)
def create(request: HttpRequest, booking: BookingCreateSchema):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    state = BookingState[booking.state] if booking.state else BookingState.created
    if state not in {BookingState.created, BookingState.planned, BookingState.started}:
        return 400, ErrorResponse(error="Invalid initial state")
    if booking.start_time is not None and booking.end_time is not None and booking.start_time > booking.end_time:
        return 400, ErrorResponse(error="Start time must be before end time")
    vehicle = None
    if booking.vehicle_id:
        try:
            vehicle = Vehicle.objects.get(id=int(booking.vehicle_id))
        except (ValueError, Vehicle.DoesNotExist):
            return 400, ErrorResponse(error=f"Vehicle with ID '{booking.vehicle_id}' not found")

    params = {}
    if booking.from_location_latitude and booking.from_location_longitude:
        params['from_location'] = Point(booking.from_location_longitude, booking.from_location_latitude)
        params['from_description'] = booking.from_description
    if booking.to_location_latitude and booking.to_location_longitude:
        params['to_location'] = Point(booking.to_location_longitude, booking.to_location_latitude)
        params['to_description'] = booking.to_description

    try:
        with transaction.atomic():
            b = Booking.objects.create(
                user=request.user,
                trip_mode=OptionType[booking.trip_mode],
                state=state,
                start_time=booking.start_time,
                end_time=booking.end_time,
                vehicle=vehicle,
                provider_id=booking.provider_id,
                **params,
            )
    except IntegrityError:
        return 409, TranslatedErrorResponse(error=TranslatedString.from_gettext("Buchung nicht möglich, weil sie mit einer bestehenden Buchung kollidiert."))

    return 200, CreateSuccessResponse(msg="OK", created_id=str(b.pk))


@router.patch(
    "/update/{bookingID}",
    response={
        200: MsgResponse,
        400: ErrorResponse,
        401: ErrorResponse,
        404: ErrorResponse,
        409: TranslatedErrorResponse,
    },
    summary="Update a booking of this user",
    description="""
`start_time` is the planned point in time until the state is `started` or later. Then it is the actual time the trip was started.
`end_time` is the planned point of time of arrival in the states before `finished`.
If the new state is `started` and no `start_time` is given, the current time is recorded as `start_time`.
The same is true for state `finished` and `end_time`.

If the updated booking would conflict with another booking that has an overlapping time range and the same vehicle,
409 is returned.
""",
    tags=['booking'],
)
def update(request: HttpRequest, bookingID: str, booking: BookingUpdateSchema):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    try:
        b = Booking.objects.get(id=int(bookingID))
        if b.user != request.user:
            return 404, ErrorResponse(error="Not a booking of this user")
    except (ValueError, Booking.DoesNotExist):
        return 404, ErrorResponse(error="No booking found")
    if booking.start_time is not None and booking.end_time is not None and booking.start_time > booking.end_time:
        return 400, ErrorResponse(error="Start time must be before end time")
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    # noinspection PyBroadException
    try:
        with transaction.atomic():
            state = BookingState[booking.state] if booking.state else None
            if booking.from_location_latitude and booking.from_location_longitude:
                b.from_location = Point(booking.from_location_longitude, booking.from_location_latitude)
                b.from_description = booking.from_description
            if booking.to_location_latitude and booking.to_location_longitude:
                b.to_location = Point(booking.to_location_longitude, booking.to_location_latitude)
                b.to_description = booking.to_description
            if booking.trip_mode:
                b.trip_mode = OptionType[booking.trip_mode]
            if booking.state:
                b.state = state
            if booking.start_time:
                b.start_time = booking.start_time
            if booking.end_time:
                b.end_time = booking.end_time
            if booking.provider_id:
                b.provider_id = booking.provider_id
            if booking.vehicle_id:
                try:
                    vehicle = Vehicle.objects.get(id=int(booking.vehicle_id))
                    b.vehicle = vehicle
                except (ValueError, Vehicle.DoesNotExist):
                    return 400, ErrorResponse(error=f"Vehicle with ID '{booking.vehicle_id}' not found")

            b.save()
    except IntegrityError:
        logger.exception(f"Failed updating '{b}' from: {booking}")
        return 409, TranslatedErrorResponse(error=TranslatedString.from_gettext(
            "Änderung nicht möglich, weil sie mit einer bestehenden Buchung kollidiert."))
    except:
        logger.exception(f"Failed updating '{b}' from: {booking}")
        return 400, ErrorResponse(error="Invalid request")
    return 200, MsgResponse(msg="OK")


@router.post(
    "/points/estimate",
    response={
        200: PointsEstimateResponse,
        401: ErrorResponse,
    },
    summary="Get the estimated points for a finished booking given distance and trip mode",
    description=""" """,
    tags=['booking'],
)
def post_points_estimate(request: HttpRequest, per: PointsEstimateRequest):
    if request.user.is_anonymous:
        return 401, ErrorResponse(error="Not authenticated")
    spr = Booking.get_score_points_static(
        BookingState.finished,
        per.distance_m,
        per.trip_mode,
        True,
        None, None, None, None,
        None
    )
    return 200, PointsEstimateResponse(
        trip_mode=per.trip_mode,
        distance_m=per.distance_m,
        points_estimate=spr.points,
        reasons=spr.reasons,
    )
