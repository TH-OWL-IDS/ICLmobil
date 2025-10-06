from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmptyMessage(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatusMessage(_message.Message):
    __slots__ = ("statusCode",)
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    statusCode: int
    def __init__(self, statusCode: _Optional[int] = ...) -> None: ...

class RideRequestMessage(_message.Message):
    __slots__ = ("fromLat", "fromLng", "toLat", "toLng", "startingEarliest", "startingLatest", "userId")
    FROMLAT_FIELD_NUMBER: _ClassVar[int]
    FROMLNG_FIELD_NUMBER: _ClassVar[int]
    TOLAT_FIELD_NUMBER: _ClassVar[int]
    TOLNG_FIELD_NUMBER: _ClassVar[int]
    STARTINGEARLIEST_FIELD_NUMBER: _ClassVar[int]
    STARTINGLATEST_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    fromLat: float
    fromLng: float
    toLat: float
    toLng: float
    startingEarliest: int
    startingLatest: int
    userId: str
    def __init__(self, fromLat: _Optional[float] = ..., fromLng: _Optional[float] = ..., toLat: _Optional[float] = ..., toLng: _Optional[float] = ..., startingEarliest: _Optional[int] = ..., startingLatest: _Optional[int] = ..., userId: _Optional[str] = ...) -> None: ...

class MatchMessage(_message.Message):
    __slots__ = ("offerId", "meetingLat", "meetingLng", "dropoffLat", "dropoffLng", "driverAtMeetingPoint", "driverAtDropoffPoint")
    OFFERID_FIELD_NUMBER: _ClassVar[int]
    MEETINGLAT_FIELD_NUMBER: _ClassVar[int]
    MEETINGLNG_FIELD_NUMBER: _ClassVar[int]
    DROPOFFLAT_FIELD_NUMBER: _ClassVar[int]
    DROPOFFLNG_FIELD_NUMBER: _ClassVar[int]
    DRIVERATMEETINGPOINT_FIELD_NUMBER: _ClassVar[int]
    DRIVERATDROPOFFPOINT_FIELD_NUMBER: _ClassVar[int]
    offerId: int
    meetingLat: float
    meetingLng: float
    dropoffLat: float
    dropoffLng: float
    driverAtMeetingPoint: int
    driverAtDropoffPoint: int
    def __init__(self, offerId: _Optional[int] = ..., meetingLat: _Optional[float] = ..., meetingLng: _Optional[float] = ..., dropoffLat: _Optional[float] = ..., dropoffLng: _Optional[float] = ..., driverAtMeetingPoint: _Optional[int] = ..., driverAtDropoffPoint: _Optional[int] = ...) -> None: ...

class MatchesStatusMessage(_message.Message):
    __slots__ = ("statusCode", "matches")
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    MATCHES_FIELD_NUMBER: _ClassVar[int]
    statusCode: int
    matches: _containers.RepeatedCompositeFieldContainer[MatchMessage]
    def __init__(self, statusCode: _Optional[int] = ..., matches: _Optional[_Iterable[_Union[MatchMessage, _Mapping]]] = ...) -> None: ...

class PollRideReportsMessage(_message.Message):
    __slots__ = ("startingTimeTicksOffers", "startingTimeTicksBookings")
    STARTINGTIMETICKSOFFERS_FIELD_NUMBER: _ClassVar[int]
    STARTINGTIMETICKSBOOKINGS_FIELD_NUMBER: _ClassVar[int]
    startingTimeTicksOffers: int
    startingTimeTicksBookings: int
    def __init__(self, startingTimeTicksOffers: _Optional[int] = ..., startingTimeTicksBookings: _Optional[int] = ...) -> None: ...

class RideReportsStatusMessage(_message.Message):
    __slots__ = ("statusCode", "bookingReports", "bookingReportsEndingTimeTicks", "offerReports", "offerReportsEndingTimeTicks")
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    BOOKINGREPORTS_FIELD_NUMBER: _ClassVar[int]
    BOOKINGREPORTSENDINGTIMETICKS_FIELD_NUMBER: _ClassVar[int]
    OFFERREPORTS_FIELD_NUMBER: _ClassVar[int]
    OFFERREPORTSENDINGTIMETICKS_FIELD_NUMBER: _ClassVar[int]
    statusCode: int
    bookingReports: _containers.RepeatedCompositeFieldContainer[RideReportBookingMessage]
    bookingReportsEndingTimeTicks: int
    offerReports: _containers.RepeatedCompositeFieldContainer[RideReportOfferMessage]
    offerReportsEndingTimeTicks: int
    def __init__(self, statusCode: _Optional[int] = ..., bookingReports: _Optional[_Iterable[_Union[RideReportBookingMessage, _Mapping]]] = ..., bookingReportsEndingTimeTicks: _Optional[int] = ..., offerReports: _Optional[_Iterable[_Union[RideReportOfferMessage, _Mapping]]] = ..., offerReportsEndingTimeTicks: _Optional[int] = ...) -> None: ...

class RideReportBookingMessage(_message.Message):
    __slots__ = ("bookingId", "rideBookingStatusCode", "fromLat", "fromLng", "toLat", "toLng", "distanceMeters", "savedCo2", "gotinTime", "droppedOffTime")
    BOOKINGID_FIELD_NUMBER: _ClassVar[int]
    RIDEBOOKINGSTATUSCODE_FIELD_NUMBER: _ClassVar[int]
    FROMLAT_FIELD_NUMBER: _ClassVar[int]
    FROMLNG_FIELD_NUMBER: _ClassVar[int]
    TOLAT_FIELD_NUMBER: _ClassVar[int]
    TOLNG_FIELD_NUMBER: _ClassVar[int]
    DISTANCEMETERS_FIELD_NUMBER: _ClassVar[int]
    SAVEDCO2_FIELD_NUMBER: _ClassVar[int]
    GOTINTIME_FIELD_NUMBER: _ClassVar[int]
    DROPPEDOFFTIME_FIELD_NUMBER: _ClassVar[int]
    bookingId: int
    rideBookingStatusCode: int
    fromLat: float
    fromLng: float
    toLat: float
    toLng: float
    distanceMeters: int
    savedCo2: int
    gotinTime: int
    droppedOffTime: int
    def __init__(self, bookingId: _Optional[int] = ..., rideBookingStatusCode: _Optional[int] = ..., fromLat: _Optional[float] = ..., fromLng: _Optional[float] = ..., toLat: _Optional[float] = ..., toLng: _Optional[float] = ..., distanceMeters: _Optional[int] = ..., savedCo2: _Optional[int] = ..., gotinTime: _Optional[int] = ..., droppedOffTime: _Optional[int] = ...) -> None: ...

class RideReportOfferMessage(_message.Message):
    __slots__ = ("offerId", "fromLat", "fromLng", "toLat", "toLng", "startingAt", "eta")
    OFFERID_FIELD_NUMBER: _ClassVar[int]
    FROMLAT_FIELD_NUMBER: _ClassVar[int]
    FROMLNG_FIELD_NUMBER: _ClassVar[int]
    TOLAT_FIELD_NUMBER: _ClassVar[int]
    TOLNG_FIELD_NUMBER: _ClassVar[int]
    STARTINGAT_FIELD_NUMBER: _ClassVar[int]
    ETA_FIELD_NUMBER: _ClassVar[int]
    offerId: int
    fromLat: float
    fromLng: float
    toLat: float
    toLng: float
    startingAt: int
    eta: int
    def __init__(self, offerId: _Optional[int] = ..., fromLat: _Optional[float] = ..., fromLng: _Optional[float] = ..., toLat: _Optional[float] = ..., toLng: _Optional[float] = ..., startingAt: _Optional[int] = ..., eta: _Optional[int] = ...) -> None: ...

class PollActiveBookingsMessage(_message.Message):
    __slots__ = ("startingTimeTicks",)
    STARTINGTIMETICKS_FIELD_NUMBER: _ClassVar[int]
    startingTimeTicks: int
    def __init__(self, startingTimeTicks: _Optional[int] = ...) -> None: ...

class ActiveBookingsStatusMessage(_message.Message):
    __slots__ = ("statusCode", "activeBookings")
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    ACTIVEBOOKINGS_FIELD_NUMBER: _ClassVar[int]
    statusCode: int
    activeBookings: _containers.RepeatedCompositeFieldContainer[ActiveBookingMessage]
    def __init__(self, statusCode: _Optional[int] = ..., activeBookings: _Optional[_Iterable[_Union[ActiveBookingMessage, _Mapping]]] = ...) -> None: ...

class ActiveBookingMessage(_message.Message):
    __slots__ = ("bookingId", "passengerIclId", "driverToMeetingPointTimestamp", "driverToDropoffPointTimestamp", "rideBookingStatus", "price", "passengerStartString", "passengerDestString", "maxUpdatedAtTimestamp", "meetingPointLat", "meetingPointLng", "dropoffPointLat", "dropoffPointLng")
    BOOKINGID_FIELD_NUMBER: _ClassVar[int]
    PASSENGERICLID_FIELD_NUMBER: _ClassVar[int]
    DRIVERTOMEETINGPOINTTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DRIVERTODROPOFFPOINTTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RIDEBOOKINGSTATUS_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PASSENGERSTARTSTRING_FIELD_NUMBER: _ClassVar[int]
    PASSENGERDESTSTRING_FIELD_NUMBER: _ClassVar[int]
    MAXUPDATEDATTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MEETINGPOINTLAT_FIELD_NUMBER: _ClassVar[int]
    MEETINGPOINTLNG_FIELD_NUMBER: _ClassVar[int]
    DROPOFFPOINTLAT_FIELD_NUMBER: _ClassVar[int]
    DROPOFFPOINTLNG_FIELD_NUMBER: _ClassVar[int]
    bookingId: int
    passengerIclId: int
    driverToMeetingPointTimestamp: int
    driverToDropoffPointTimestamp: int
    rideBookingStatus: int
    price: int
    passengerStartString: str
    passengerDestString: str
    maxUpdatedAtTimestamp: int
    meetingPointLat: float
    meetingPointLng: float
    dropoffPointLat: float
    dropoffPointLng: float
    def __init__(self, bookingId: _Optional[int] = ..., passengerIclId: _Optional[int] = ..., driverToMeetingPointTimestamp: _Optional[int] = ..., driverToDropoffPointTimestamp: _Optional[int] = ..., rideBookingStatus: _Optional[int] = ..., price: _Optional[int] = ..., passengerStartString: _Optional[str] = ..., passengerDestString: _Optional[str] = ..., maxUpdatedAtTimestamp: _Optional[int] = ..., meetingPointLat: _Optional[float] = ..., meetingPointLng: _Optional[float] = ..., dropoffPointLat: _Optional[float] = ..., dropoffPointLng: _Optional[float] = ...) -> None: ...
