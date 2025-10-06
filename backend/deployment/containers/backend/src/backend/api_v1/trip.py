# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import concurrent.futures
import datetime
import logging

from django.conf import settings
from django.contrib.gis.geos import Point
from django.http import HttpRequest
from ninja import Router

from backend.api_v1.schemas import ErrorResponse, TripSearchResponse, TripSearchRequest, \
    OptionPT, OptionSharing, TripSearchFrontendResponse, OptionAllFields, OptionRriveUse, OptionWalk
from backend.api_v1.utils import api_efa_client
from backend.enum import PoiType, VehicleType, RideIcon
from backend.models import Vehicle
from backend.rrive import find_offers_for_request, datetime_to_ticks, RRiveStatusCodeEnum, ticks_to_datetime
from backend.translate import get_translator
from backend.utils import TranslatedString, get_distance_meter, get_subrequest_threadpool
from efa.models import EfaModeOfTransport
from protos.rrive_pb2 import RideRequestMessage, MatchesStatusMessage

_ = get_translator()

router = Router()

logger = logging.getLogger(__name__)




trip_search_openapi_extra = {
    "requestBody": {
        "content": {
            "application/json": {
                "examples": {
                    "Vom Fraunhofer IOSB-INA zur Berufsschule": {
                        "summary": "Vom Fraunhofer IOSB-INA zur Berufsschule",
                        "value": {
                            "start_timestamp": "2024-09-16T08:00:00+02:00",
                            "location_from_latitude": 52.0172726,
                            "location_from_longitude": 8.9008242,
                            "location_to_latitude": 52.0175167,
                            "location_to_longitude": 8.9081392,
                            "user_location_latitude": None,
                            "user_location_longitude": None
                        }
                    },
                    "Vom Rathaus Lemgo zur Berufsschule": {
                        "summary": "Vom Rathaus Lemgo zur Berufsschule",
                        "value": {
                            "start_timestamp": "2024-09-16T08:00:00+02:00",
                            "location_from_latitude": 52.0281672,
                            "location_from_longitude": 8.9008364,
                            "location_to_latitude": 52.0175167,
                            "location_to_longitude": 8.9081392,
                            "user_location_latitude": None,
                            "user_location_longitude": None
                        }
                    },
                    "Bielefeld Jahnplatz zum Innovation Spin": {
                        "summary": "Bielefeld Jahnplatz zum Innovation Spin",
                        "value": {
                            "start_timestamp": "2024-09-16T08:00:00+02:00",
                            "location_from_latitude": 52.0234109,
                            "location_from_longitude": 8.532586,
                            "location_to_latitude": 52.0175792,
                            "location_to_longitude": 8.9018994,
                            "user_location_latitude": None,
                            "user_location_longitude": None
                        }
                    },
                }
            }
        }
    }
}


@router.post(
    "/search",
    response={
        200: TripSearchResponse,
        400: ErrorResponse,
    },
    summary="Search for trip options",
    description="""
The "from" and "to" locations need to be WGS84 latitude/longitude location.
"from" can be replaced by the user device's location in `user_location_latitude`/`user_location_longitude`.
`start_timestamp` is optional. If not specified, the current time is used, e.g. "as soon as possible".
`include_invalid_trips` can be set to `true` to also see invalid trips, e.g. vehicles too far away or with
too low a remaining range for the planned trip.
""",
    tags=['trip'],
    openapi_extra=trip_search_openapi_extra,
)
def post_trip_search(request: HttpRequest, data: TripSearchRequest):
    return _search(request, data)


@router.post(
    "/search/frontend",
    response={
        200: TripSearchFrontendResponse,
        400: ErrorResponse,
    },
    summary="Search for trip options and return specialized results with dummy data in all but used fields",
    description="""See /search for details.
""",
    tags=['trip'],
    openapi_extra=trip_search_openapi_extra,
)
def post_trip_search_frontend(request: HttpRequest, data: TripSearchRequest):
    status, result = _search(request, data)
    if status != 200:
        return status, result

    result: TripSearchResponse
    return status, TripSearchFrontendResponse(warnings=result.warnings,
                                              options=[OptionAllFields.from_option(o) for o in result.options])


def _search(request: HttpRequest, data: TripSearchRequest):
    if data.include_invalid_trips is None:
        invalid_trips = request.POST.get('include_invalid_trips') == 'on'
    else:
        invalid_trips = data.include_invalid_trips

    warnings = []

    logger.debug(f"Trip _search start_timestamp {type(data.start_timestamp)} {data.start_timestamp} {data.start_timestamp!r}")

    search_params = {
        "start_timestamp": data.start_timestamp,
    }
    for end in ('from', 'to'):
        lat = getattr(data, f'location_{end}_latitude')
        lon = getattr(data, f'location_{end}_longitude')
        if not (lat and lon) and end == 'from':
            lat = data['user_location_latitude']
            lon = data['user_location_longitude']
        if lat and lon:
            search_params[f'{end}_latitude'] = lat
            search_params[f'{end}_longitude'] = lon
        else:
            return 400, ErrorResponse(error=f"Need either POI id or location for '{end}")

    max_option_id = 1
    logger.debug(f"Starting EFA trip search with params: {search_params}")
    options = []
    mot_in_title = {mot for mot in EfaModeOfTransport if
                    mot.value.poi_type_mapping in {PoiType.TYPE_STOP_ZUG, PoiType.TYPE_STOP_STRASSENBAHN,
                                                   PoiType.TYPE_STOP_BUS, PoiType.TYPE_STOP_AST}}
    logger.debug(f"Will use in rideOption: {mot_in_title}")
    mot_efa_id_in_title = {mot.value.efa_id for mot in mot_in_title}

    # Prepare RideRequestMessage for RRive
    params = dict(
        fromLat=search_params['from_latitude'], fromLng=search_params['from_longitude'],
        toLat=search_params['to_latitude'], toLng=search_params['to_longitude'],
        startingEarliest=datetime_to_ticks(data.start_timestamp - datetime.timedelta(hours=4)),
        startingLatest=datetime_to_ticks(data.start_timestamp + datetime.timedelta(hours=4)),
        userId=request.user.username if request.user.is_authenticated else "unknown",
    )
    # noinspection PyBroadException
    logger.info(f"Getting RRive offers for {params}")
    rrive_rrm = RideRequestMessage(**params)

    tp = get_subrequest_threadpool()
    future_pt = tp.submit(api_efa_client.get_trips, **search_params)
    future_rrive = tp.submit(find_offers_for_request, rrive_rrm)

    p_from = Point(search_params['from_longitude'], search_params['from_latitude'], srid=4326)
    p_to = Point(search_params['to_longitude'], search_params['to_latitude'], srid=4326)
    distance_m = get_distance_meter(p_from, p_to)

    walk_found = False
    # Process PT result
    # noinspection PyBroadException
    try:
        journeys = future_pt.result(timeout=5)
        for j in journeys:
            if not j.legs:
                continue
            if j.air_distance_legs_m > settings.GLOBAL_LIMIT_METER:
                logger.debug(f"Rejecting PT result because distance {j.air_distance_legs_m}m>{settings.GLOBAL_LIMIT_METER}m")
                continue
            if len(j.legs) == 1 and EfaModeOfTransport.is_footway(j.legs[0].mode_of_transport.efa_id):
                ride_option = "Fußweg"
                walk_found = True
                # noinspection PyTypeChecker
                pt = OptionWalk(
                    optionID=f'walk_{max_option_id}',
                    rideTimestamp=j.legs[0].from_timestamp,
                    rideIcon='walk',
                    approxTimeOfArrival=j.legs[-1].to_timestamp,
                    rideOption=ride_option,
                    distanceM=j.legs[0].distance_m,
                )
            else:
                pt_name_legs = [l for l in j.legs if l.mode_of_transport.efa_id in mot_efa_id_in_title]
                ride_option = " - ".join(leg.pt_name for leg in pt_name_legs if leg.pt_name)

                # noinspection PyTypeChecker
                pt = OptionPT(
                    optionID=f'PT_{max_option_id}',
                    rideTimestamp=j.legs[0].from_timestamp,
                    rideIcon='pt',
                    approxTimeOfArrival=j.legs[-1].to_timestamp,
                    rideOption=ride_option,
                    journey=j
                )
            max_option_id += 1
            options.append(pt)
    except:
        logger.exception(f"PT request failed for {search_params}")
        warnings.append(TranslatedString.from_gettext("Fehler beim Abruf von ÖPNV Angeboten"))
    if not walk_found:
        # Add a manual walk option if PT did not deliver one and the distance is not too large
        if distance_m < settings.WALK_LIMIT_METER and distance_m < settings.GLOBAL_LIMIT_METER:
            option = OptionWalk(
                optionID=f'walk_{max_option_id}',
                rideTimestamp=data.start_timestamp,
                rideIcon='walk',
                approxTimeOfArrival=data.start_timestamp+datetime.timedelta(hours=distance_m/1000/settings.WALK_SPEED_KMH),
                rideOption=_("Fußweg"),
                distanceM=distance_m,
            )
            logger.debug(f"Added no-PT walk option: {option}")
            options.append(option)
            max_option_id += 1
        else:
            logger.debug(f"Not adding non-PT walk option since distance is {distance_m:0.1f}m")

    # Process RRive result
    # noinspection PyBroadException
    try:
        msm: MatchesStatusMessage = future_rrive.result(timeout=5)
        logger.debug(f"RRive result: {msm}")

        if msm.statusCode != RRiveStatusCodeEnum.SUCCESS.value:
            warnings.append(TranslatedString.from_gettext(
                "Fehler beim Abruf von RRive Angeboten: Status Code={statuscode_value} {statuscode_name}",
                statuscode_value=msm.statusCode, statuscode_name=RRiveStatusCodeEnum(msm.statusCode).name))
        else:
            if len(msm.matches) == 0:
                logger.debug(f"RRive no matches returned")
            for match in msm.matches:
                logger.debug(f"RRive Match: {match}")
                logger.debug(f"RRive Pmeeting={match.meetingLng}/{match.meetingLat} from={search_params['from_longitude']}/{search_params['from_latitude']}")
                distance_pickup = get_distance_meter(
                    Point(match.meetingLng, match.meetingLat, srid=4326),
                    Point(search_params['from_longitude'], search_params['from_latitude'], srid=4326),
                )
                logger.debug(f"RRive Pmeeting={match.dropoffLng}/{match.dropoffLat} to={search_params['to_longitude']}/{search_params['to_latitude']}")
                distance_dropoff = get_distance_meter(
                    Point(match.dropoffLng, match.dropoffLat, srid=4326),
                    Point(search_params['to_longitude'], search_params['to_latitude'], srid=4326),
                )
                rideOption = "RRive"
                extras = []
                if distance_pickup > 10:
                    extras += f"{distance_pickup:0.0f}m"
                if distance_dropoff > 10:
                    extras += f"{distance_dropoff:0.0f}m"
                if extras:
                    rideOption += " "
                    rideOption += "+".join(extras)
                # noinspection PyTypeChecker
                pt = OptionRriveUse(
                    optionID=f'RRive_{max_option_id}_{match.offerId}',
                    rideTimestamp=ticks_to_datetime(match.driverAtMeetingPoint),
                    rideIcon='car',
                    providerId=str(match.offerId),
                    approxTimeOfArrival=ticks_to_datetime(match.driverAtDropoffPoint),
                    rideOption=rideOption,
                    from_latitude=search_params['from_latitude'],
                    from_longitude=search_params['from_longitude'],
                    pickup_latitude=match.meetingLat,
                    pickup_longitude=match.meetingLng,
                    dropoff_latitude=match.dropoffLat,
                    dropoff_longitude=match.dropoffLng,
                    to_latitude=search_params['to_latitude'],
                    to_longitude=search_params['to_longitude'],
                    distanceM=distance_pickup,
                    distanceDropOffM=distance_dropoff,
                )
                max_option_id += 1
                options.append(pt)
    except:
        logger.exception(f"RRive request failed for {search_params}")
        warnings.append(TranslatedString.from_gettext("Fehler beim Abruf von RRive Angeboten"))

    # Find sharing vehicles
    point_from = Point(data.location_from_longitude, data.location_from_latitude, srid=4326)
    point_to = Point(data.location_to_longitude, data.location_to_latitude, srid=4326)
    distance_to_travel_m = get_distance_meter(point_from, point_to)
    if distance_to_travel_m >= settings.GLOBAL_LIMIT_METER:
        logger.debug(f"Not looking for sharing vehicle since distance to travel is {distance_to_travel_m:0.1f}m > {settings.GLOBAL_LIMIT_METER}m")
    else:
        speed_kmh = 10
        duration_s = distance_to_travel_m / 1000.0 / speed_kmh * 3600.0
        vehicles = Vehicle.get_available_vehicles(
            point_from,
            point_to,
            distance_cutoff_meter=settings.SHARING_IGNORE_VEHICLE_FARTHER_THAN_METER,
            timerange_from=data.start_timestamp,
            timerange_to=data.start_timestamp + datetime.timedelta(seconds=settings.SHARING_DEFAULT_DURATION_SECONDS),
        )
        for va in vehicles[:15]:
            valid = True
            if va.busy_in_timerange or not va.near_enough or not va.range_ok:
                valid = False
                if invalid_trips:
                    logger.debug(f"Marking vehicle '{va.vehicle}' invalid: {va.reasons}")
                else:
                    logger.debug(f"Dismissing potential vehicle '{va.vehicle}': {va.reasons}")
                    continue
            if va.hidden_by_availability:
                valid = False
                logger.debug(f"Hidden by availability '{va.vehicle}': {va.reasons}")
            rideOption = va.vehicle.vehicle_number
            if va.vehicle.vehicle_model:
                rideOption = rideOption + f' ({va.vehicle.vehicle_model})'
            if va.vehicle.location:
                pickup_latitude, pickup_longitude = va.vehicle.location[1], va.vehicle.location[0]
            else:
                pickup_latitude, pickup_longitude = None, None
            pt = OptionSharing(
                optionID=f'sharing_{max_option_id}',
                rideTimestamp=data.start_timestamp,
                approxTimeOfArrival=data.start_timestamp + datetime.timedelta(seconds=duration_s),
                maximumDurationH=min(va.maximum_booking_duration_s or settings.SHARING_MAXIMUM_DURATION_SECONDS, settings.SHARING_MAXIMUM_DURATION_SECONDS)/3600,
                rideOption=rideOption,
                rideIcon=VehicleType(va.vehicle.vehicle_type).get_ride_icon(),
                vehicleId=str(va.vehicle.id),
                vehicleProviderName=va.vehicle.provider_name,
                vehicleProviderId=va.vehicle.provider_id,
                vehicleType=VehicleType[va.vehicle.vehicle_type].value,
                vehicleModel=va.vehicle.vehicle_model,
                vehicleNumber=va.vehicle.vehicle_number,
                distanceM=va.distance_m,
                stateOfCharge=va.vehicle.battery_level_percent,
                remainingRangeKm=va.vehicle.remaining_range_km,
                pickup_latitude=pickup_latitude,
                pickup_longitude=pickup_longitude,
                valid=valid,
                invalid_reasons=va.reasons,
            )
            max_option_id += 1
            options.append(pt)

    tsr = TripSearchResponse(options=options, warnings=warnings)

    return 200, tsr
