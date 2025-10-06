# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import enum
import logging
import threading

import grpc
import pytz
from django.conf import settings
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point

from backend.enum import BookingState, OptionType
from backend.models import BackendSyncProgress, Booking, BackendUser
from backend.utils import proto_to_str
from protos import rrive_pb2_grpc
from protos.rrive_pb2 import EmptyMessage, StatusMessage, PollRideReportsMessage, RideReportsStatusMessage, \
    RideRequestMessage, MatchesStatusMessage, PollActiveBookingsMessage, ActiveBookingsStatusMessage

logger = logging.getLogger(__name__)


# rideBookingStatus and rideBookingStatusCode are the same

class RRiveRideBookingStatusCode(enum.Enum):
    UNKNOWN = 0
    REQUESTED = 1
    CANCELLED = 2
    ACCEPTED = 3
    GOTIN = 4
    COMPLETED = 5
    DECLINED = 6
    ACCEPTEDBUTCANCELLEDBYDRIVER = 7
    ACCEPTEDBUTCANCELLEDBYPASSENGER = 8
    RESPONSETIMEOUTDRIVER = 9
    PARTCOMPLETEDBUTCANCELLEDBYDRIVER = 10
    PARTCOMPLETEDBUTCANCELLEDBYPASSENGER = 11
    PAYMENTPENDING = 12
    PAYMENTCOMPLETED = 13
    PAYMENTFAILED = 14
    REFUNDCOMPLETED = 15

# Information from Jan Loescher 2025-05-12:
"""
enum rideBookingStatus: Int32 {
    case UNKNOWN                                = 0     //Unknown State
    case REQUESTED                              = 1     //Booking Requested but no response so far
    case CANCELLED                              = 2     //Booking canceled by passenger before driver could respond to it
    case ACCEPTED                               = 3     //Driver accepted request and is heading to the meeting point
    case GOTIN                                  = 4     //Driver reached meeting point and passenger got in the car and scanned the qr code.
    case COMPLETED                              = 5     //Trip ended correctly, the passenger destination was reached
    case DECLINED                               = 6     //Booking declined by driver
    case ACCEPTEDBUTCANCELLEDBYDRIVER           = 7     //Booking was accepted by the driver but he canceled the carpool before he reached the meeting point
    case ACCEPTEDBUTCANCELLEDBYPASSENGER        = 8     //Booking was accepted by the driver but the passenger canceled the carpool before he reached the meeting point
    case RESPONSETIMEOUTDRIVER                  = 9     //Driver did not respond to request
    case PARTCOMPLETEDBUTCANCELLEDBYDRIVER      = 10    //Passenger was inside the car but the driver canceled the carpool before he reached the dropoff point. Trip never was fully completed
    case PARTCOMPLETEDBUTCANCELLEDBYPASSENGER   = 11    //Passenger was inside the car but he canceled the carpool before they reached the dropoff point. Trip never was fully completed
    case PAYMENTPENDING                         = 12    //Booking was created and payment has been requested. Once approved, the Booking will switch to Requested and will be found by the driver
    case PAYMENTCOMPLETED                       = 13    //Booking is completed and the payment has been successful.
    case PAYMENTFAILED                          = 14    //Booking was created but payment has been declined. End State
    case REFUNDCOMPLETED                        = 15    //Booking has been refunded
}
 """

def rideBookingStatusCode_to_booking_state(rrive_status: RRiveRideBookingStatusCode) -> BookingState | None:
    return {
        RRiveRideBookingStatusCode.UNKNOWN: None,
        RRiveRideBookingStatusCode.REQUESTED: BookingState.planned,
        RRiveRideBookingStatusCode.CANCELLED: BookingState.canceled,
        RRiveRideBookingStatusCode.ACCEPTED: BookingState.planned,
        RRiveRideBookingStatusCode.GOTIN: BookingState.started,
        RRiveRideBookingStatusCode.COMPLETED: BookingState.finished,
        RRiveRideBookingStatusCode.DECLINED: BookingState.canceled,
        RRiveRideBookingStatusCode.ACCEPTEDBUTCANCELLEDBYDRIVER: BookingState.canceled,
        RRiveRideBookingStatusCode.ACCEPTEDBUTCANCELLEDBYPASSENGER: BookingState.canceled,
        RRiveRideBookingStatusCode.RESPONSETIMEOUTDRIVER: BookingState.finished,
        RRiveRideBookingStatusCode.PARTCOMPLETEDBUTCANCELLEDBYDRIVER: BookingState.finished,
        RRiveRideBookingStatusCode.PARTCOMPLETEDBUTCANCELLEDBYPASSENGER: BookingState.finished,
        RRiveRideBookingStatusCode.PAYMENTPENDING: None,
        RRiveRideBookingStatusCode.PAYMENTCOMPLETED: None,
        RRiveRideBookingStatusCode.PAYMENTFAILED: None,
        RRiveRideBookingStatusCode.REFUNDCOMPLETED: BookingState.finished,
    }.get(rrive_status, None)

assert rideBookingStatusCode_to_booking_state(RRiveRideBookingStatusCode(4)) == BookingState.started

class RRiveStatusCodeEnum(enum.Enum):
    FOUND = 0
    MAILADDRESSUNKNOWN = 1
    PARSEERROR = 2
    UNKNOWNERROR = 3
    PHONENUMBERUNKNOWN = 4
    MORETHANONE = 5
    NOTFOUND = 6
    IDINVALID = 7
    ARGUMENTNULL = 8
    NOTALLOWED = 9
    INVALIDPARAMETERS = 10
    INSERTED = 11
    ALREADYKNOWN = 12
    DATABASEERROR = 13
    UPDATED = 14
    SUCCESS = 15
    ALREADYVALIDATED = 16
    UNKNOWN = 17
    NOTVALIDATED = 18
    VALIDATED = 19
    ACTIVEOFFEREXISTING = 20
    REACTIVATED = 21
    ACTIVE = 22
    INACTIVE = 23
    INCONSISTENT = 24
    OFFERINACTIVE = 25
    UNCHANGED = 26
    EXCEPTIONCAUGHT = 27
    REGIONNOTENABLED = 28
    TWILIOEXCEPTION = 29
    PAYMENTERROR = 30
    PASSENGERMONEYNOTSUFFICIENT = 31
    INVALIDLICENSEKEY = 32
    ITINERONOTAVAILABLE = 33


def datetime_to_ticks(dt: datetime.datetime) -> int:
    assert dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None, "Can only process TZ aware datetimes"
    return int((dt - datetime.datetime(1, 1, 1, tzinfo=pytz.UTC)).total_seconds() * 10000000)


def ticks_to_datetime(ticks: int) -> datetime.datetime:
    # constant is the number of seconds between
    # DotNet Ticks start 0001-01-01 12:00:00+00:00 and
    # Unix epoch start 1970-01-01 00:00:00+00:00
    # according to https://stackoverflow.com/a/1628018
    unix_epoch = (ticks / 10_000_000) - 62_135_596_800
    return datetime.datetime.fromtimestamp(unix_epoch, tz=pytz.UTC)


assert datetime_to_ticks(datetime.datetime(2025, 2, 13, 16, 7, 7, tzinfo=pytz.UTC)) == 638750596270000000
assert ticks_to_datetime(638750596270000000) - datetime.datetime(2025, 2, 13, 16, 7, 7,
                                                                 tzinfo=pytz.UTC) < datetime.timedelta(seconds=1)


def get_per_thread_channel():
    if not settings.RRIVE_GRPC_ENDPOINT:
        raise RuntimeError(f"RRIVE_GRPC_ENDPOINT not set")
    thread_locals = threading.local()
    if not hasattr(thread_locals, 'channel'):
        thread_locals.grpc_channel_credentials = grpc.ssl_channel_credentials()
        thread_locals.channel = grpc.secure_channel(settings.RRIVE_GRPC_ENDPOINT,
                                                    credentials=thread_locals.grpc_channel_credentials)
    return thread_locals.channel


def healthcheck() -> StatusMessage:
    with get_per_thread_channel() as channel:
        stub = rrive_pb2_grpc.RRiveServiceStub(channel)
        empty_message = EmptyMessage()
        status_message: StatusMessage = stub.HealthCheck(empty_message)
    return status_message


def poll_ride_reports(starting_timestamp: datetime.datetime | None = None) -> RideReportsStatusMessage:
    if not starting_timestamp:
        starting_timestamp = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=1)
    with get_per_thread_channel() as channel:
        stub = rrive_pb2_grpc.RRiveServiceStub(channel)
        prrm = PollRideReportsMessage(startingTimeTicksBookings=datetime_to_ticks(starting_timestamp), startingTimeTicksOffers=datetime_to_ticks(starting_timestamp))
        prsm: RideReportsStatusMessage = stub.PollRideReports(prrm)
    return prsm


def find_offers_for_request(rrm: RideRequestMessage) -> MatchesStatusMessage:
    with get_per_thread_channel() as channel:
        stub = rrive_pb2_grpc.RRiveServiceStub(channel)
        msm: MatchesStatusMessage = stub.FindOffersForRequest(rrm)
    return msm

class RriveRequestPoller:
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.last_ride_report_ticks_offers = 0
        self.last_ride_report_ticks_bookings = 0
        self.sync_key_ride_report_offers = self.task_name+'_ride_report_time_ticks_offers'
        self.sync_key_ride_report_bookings = self.task_name+'_ride_report_time_ticks_bookings'
        self.sync_key_active_bookings = self.task_name+'_active_bookings_time_ticks'
        try:
            bsp = BackendSyncProgress.objects.get(sync_key=self.sync_key_ride_report_offers)
            self.last_ride_report_ticks_offers = bsp.sync_value_int
        except BackendSyncProgress.DoesNotExist:
            pass
        try:
            bsp = BackendSyncProgress.objects.get(sync_key=self.sync_key_ride_report_bookings)
            self.last_ride_report_ticks_bookings = bsp.sync_value_int
        except BackendSyncProgress.DoesNotExist:
            pass
        logger.info(f"{self.task_name} starting with ride_report_time_ticks_offers={self.last_ride_report_ticks_offers} ({ticks_to_datetime(self.last_ride_report_ticks_offers)}) ride_report_ticks_bookings={self.last_ride_report_ticks_bookings} ({ticks_to_datetime(self.last_ride_report_ticks_bookings)})")

        self.last_active_bookings_ticks = 0
        try:
            bsp = BackendSyncProgress.objects.get(sync_key=self.sync_key_active_bookings)
            self.last_active_bookings_ticks = bsp.sync_value_int
        except BackendSyncProgress.DoesNotExist:
            pass
        logger.info(f"{self.task_name} starting with last_active_bookings_ticks={self.last_active_bookings_ticks} ({ticks_to_datetime(self.last_active_bookings_ticks)})")

        self.fail_count = 0
        self.max_fail_count = 5

        self.user_id = BackendUser.objects.get(username="admin").id


    def poll(self):
        pabm: PollActiveBookingsMessage | None = None
        # noinspection PyBroadException
        try:
            with get_per_thread_channel() as channel:
                stub = rrive_pb2_grpc.RRiveServiceStub(channel)

                # We process ActiveBookingMessage first because creating a Booking from RideReportBookingMessage is not possible since it misses the IclId/username.
                startingTimeTicks = self.last_active_bookings_ticks+1
                logger.debug(f"{self.task_name} polling PollActiveBookings from {startingTimeTicks}")
                pabm = PollActiveBookingsMessage(startingTimeTicks=startingTimeTicks)
                absm: ActiveBookingsStatusMessage = stub.PollActiveBookings(pabm)
                absm_status = RRiveStatusCodeEnum(absm.statusCode)
                if absm_status != RRiveStatusCodeEnum.SUCCESS:
                    raise RuntimeError(f"PollRideReportsMessage returned statusCode {absm_status}")
                logger.debug(f"{self.task_name} Number of activeBookings: {len(absm.activeBookings)}")
                for ab in absm.activeBookings:
                    logger.debug(f"{self.task_name} Processing activeBooking {proto_to_str(ab)}")
                    self.last_active_bookings_ticks = max(self.last_active_bookings_ticks, ab.maxUpdatedAtTimestamp)
                    bookings = Booking.objects.filter(trip_mode='rriveUse', provider_id=ab.bookingId).all()
                    if len(bookings) == 0:
                        # New booking!
                        try:
                            user = BackendUser.objects.filter(id=ab.passengerIclId)[0]
                        except (IndexError, ValueError):
                            logger.warning(f"{self.task_name} Ignoring RRive active booking message since user with user ID '{ab.passengerIclId}' is unknown: {proto_to_str(ab)}")
                            continue

                        booking = Booking.objects.create(
                            user=user,
                            trip_mode=OptionType.rriveUse.value,
                            state=BookingState.planned.value,
                            from_location=Point(ab.meetingPointLng, ab.meetingPointLat),
                            from_description=ab.passengerStartString,
                            to_description=ab.passengerDestString,
                            to_location=Point(ab.dropoffPointLng, ab.dropoffPointLat),
                            start_time=ticks_to_datetime(ab.driverToMeetingPointTimestamp),
                            end_time=ticks_to_datetime(ab.driverToDropoffPointTimestamp),
                            provider_id=ab.bookingId,
                        )
                        logger.info(f"{self.task_name} RRive active booking message resulted in new booking: {proto_to_str(ab)} -> {booking}")
                        LogEntry.objects.log_action(
                            user_id=self.user_id,
                            content_type_id=ContentType.objects.get_for_model(Booking).id,
                            object_id=booking.id,
                            object_repr=repr(booking),
                            action_flag=ADDITION,
                            change_message=f"New booking from RRive")
                    elif len(bookings) > 1:
                        logger.warning(f"{self.task_name} Ignoring RRive active booking message since bookingId '{ab.bookingId}' is not unique: {proto_to_str(ab)}")
                        continue
                    else:
                        # We found the one booking
                        booking = bookings[0]
                        if booking.user.id != ab.passengerIclId:
                            logger.warning(f"{self.task_name} Ignoring RRive active booking message since corresponding Booking is for user '{booking.user}' but RRive shows passengerIclId '{ab.passengerIclId}': {proto_to_str(ab)}")
                            continue
                        logger.debug(f"{self.task_name} activeBooking {proto_to_str(ab)} found backend booking: {booking}")
                    updates = []
                    start_time = ticks_to_datetime(ab.driverToMeetingPointTimestamp)
                    if abs((start_time-booking.start_time).total_seconds()) > 1:
                        updates.append(f"start_time {booking.start_time} -> {start_time}")
                        booking.start_time = start_time
                    end_time = ticks_to_datetime(ab.driverToDropoffPointTimestamp)
                    if abs((end_time-booking.end_time).total_seconds()) > 1:
                        updates.append(f"end_time {booking.end_time} -> {end_time}")
                        booking.end_time = end_time
                    booking_state = rideBookingStatusCode_to_booking_state(RRiveRideBookingStatusCode(ab.rideBookingStatus))
                    if booking_state is None:
                        logger.debug(f"booking_state is None - coming from rideBookingStatus={ab.rideBookingStatus}")
                    if booking_state is not None and booking.state != booking_state.value:
                        updates.append(f"state {booking.state} -> {booking_state.value}")
                        booking.state = booking_state.value
                    if booking.from_description != ab.passengerStartString:
                        updates.append(f"from_description {booking.from_description} -> {booking_state.value}")
                        booking.from_description = ab.passengerStartString
                    if booking.to_description != ab.passengerDestString:
                        updates.append(f"to_description {booking.to_description} -> {booking_state.value}")
                        booking.to_description = ab.passengerDestString
                    if abs(ab.meetingPointLng-booking.from_location[0])+abs(ab.meetingPointLat-booking.from_location[1]) > 0.01:
                        updates.append(f"from_location {booking.from_location[1]}/{booking.from_location[0]} -> {ab.meetingPointLat}/{ab.meetingPointLng}")
                        booking.from_location = Point(ab.meetingPointLng, ab.meetingPointLat)
                    if abs(ab.dropoffPointLng-booking.to_location[0])+abs(ab.dropoffPointLat-booking.to_location[1]) > 0.01:
                        updates.append(f"to_location {booking.to_location[1]}/{booking.to_location[0]} -> {ab.dropoffPointLat}/{ab.dropoffPointLng}")
                        booking.to_location = Point(ab.dropoffPointLng, ab.dropoffPointLat)
                    if updates:
                        logger.debug(f"{self.task_name} activeBooking {proto_to_str(ab)} found updates to backend booking: {updates}")
                        booking.score_needs_update = True
                        booking.save()
                        LogEntry.objects.log_action(
                            user_id=self.user_id,
                            content_type_id=ContentType.objects.get_for_model(Booking).id,
                            object_id=booking.id,
                            object_repr=repr(booking),
                            action_flag=CHANGE,
                            change_message=f"Changes from RRive: "+', '.join(updates))
                    else:
                        logger.debug(f"{self.task_name} activeBooking {proto_to_str(ab)} found no updates to backend booking")


                BackendSyncProgress.objects.update_or_create(
                    sync_key=self.sync_key_active_bookings,
                    defaults={"sync_value_int": self.last_active_bookings_ticks},
                )

                # Process RideReportBookingMessages
                logger.debug(f"{self.task_name} polling PollRideReportsMessage from offers={self.last_ride_report_ticks_offers} bookings={self.last_ride_report_ticks_bookings}")
                prrm = PollRideReportsMessage(
                    startingTimeTicksOffers=self.last_ride_report_ticks_offers,
                    startingTimeTicksBookings=self.last_ride_report_ticks_bookings,
                )
                rrsm: RideReportsStatusMessage = stub.PollRideReports(prrm)
                rrsm_status = RRiveStatusCodeEnum(rrsm.statusCode)
                if rrsm_status != RRiveStatusCodeEnum.SUCCESS:
                    raise RuntimeError(f"PollRideReportsMessage returned statusCode {proto_to_str(rrsm_status)}")
                logger.debug(f"{self.task_name} Number of bookingReports: {len(rrsm.bookingReports)}")
                for br in rrsm.bookingReports:
                    logger.debug(f"{self.task_name} BookingReport: {proto_to_str(br)}")
                    bookings = Booking.objects.filter(trip_mode='rriveUse', provider_id=br.bookingId).all()
                    if len(bookings) == 0:
                        logger.warning(f"{self.task_name} Ignoring RRive booking report since we don't know bookingId '{br.bookingId}': {br}")
                        continue
                    elif len(bookings) > 1:
                        logger.warning(f"{self.task_name} Ignoring RRive booking report since bookingId '{br.bookingId}' is not unique: {br}")
                        continue
                    booking = bookings[0]
                    updates = []
                    booking_state = rideBookingStatusCode_to_booking_state(RRiveRideBookingStatusCode(br.rideBookingStatusCode))
                    if booking_state is not None and booking.state != booking_state.value:
                        updates.append(f"state {booking.state} -> {booking_state.value}")
                        booking.state = booking_state.value
                    if abs(br.fromLng-booking.from_location[0])+abs(br.fromLat-booking.from_location[1]) > 0.01:
                        updates.append(f"from_location {booking.from_location[1]}/{booking.from_location[0]} -> {br.fromLat}/{br.fromLng}")
                        booking.from_location = Point(br.fromLng, br.fromLat)
                    if abs(br.toLng-booking.to_location[0])+abs(br.toLat-booking.to_location[1]) > 0.01:
                        updates.append(f"to_location {booking.to_location[1]}/{booking.to_location[0]} -> {br.toLat}/{br.toLng}")
                        booking.to_location = Point(br.toLng, br.toLat)
                    if abs(br.distanceMeters - (booking.external_distance_m or 0.0)) > 0.01:
                        updates.append(f"external_distance_m {booking.external_distance_m} -> {br.distanceMeters}")
                        booking.external_distance_m = br.distanceMeters
                    # We don't use RRives savedCo2 but rely on Booking.update_wallet() using the external_distance_m.
                    if updates:
                        booking.score_needs_update = True
                        booking.save()
                        booking.update_wallet()
                        LogEntry.objects.log_action(
                            user_id=self.user_id,
                            content_type_id=ContentType.objects.get_for_model(Booking).id,
                            object_id=booking.id,
                            object_repr=repr(booking),
                            action_flag=CHANGE,
                            change_message=f"Changes from RRive: "+', '.join(updates))
                        logger.debug(f"{self.task_name} Updates from BookingReport '{proto_to_str(br)}': {updates}")
                    else:
                        logger.debug(f"{self.task_name} No updates from BookingReport '{proto_to_str(br)}'")

                self.last_ride_report_ticks_bookings = max(self.last_ride_report_ticks_bookings, rrsm.bookingReportsEndingTimeTicks)
                BackendSyncProgress.objects.update_or_create(
                    sync_key=self.sync_key_ride_report_bookings,
                    defaults={"sync_value_int": self.last_ride_report_ticks_bookings}
                )
                self.last_ride_report_ticks_offers = max(self.last_ride_report_ticks_offers, rrsm.offerReportsEndingTimeTicks)
                BackendSyncProgress.objects.update_or_create(
                    sync_key=self.sync_key_ride_report_offers,
                    defaults={"sync_value_int": self.last_ride_report_ticks_offers}
                )

            self.fail_count = 0

        except:
            if self.fail_count >= self.max_fail_count:
                raise
            else:
                self.fail_count += 1
                logger.exception(f"Temporarily ignoring failure ({self.fail_count} of {self.max_fail_count})")
