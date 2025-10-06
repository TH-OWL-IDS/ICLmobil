# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import json
import logging
import typing
from typing import Optional, Union, Dict, List, Literal, Any, Tuple

from django.contrib.auth.models import Group
from django.http import HttpRequest
from ninja import Schema
from pydantic import EmailStr, constr, Field, field_validator, ConfigDict, RootModel
from pydantic_extra_types.coordinate import Latitude, Longitude
from typing_extensions import Annotated

from backend.api_v1.utils import api_efa_client
from backend.enum import PoiType, OptionType, BookingState, VehicleType, NewsType, RideIcon
from backend.models import BackendUser, BackendRole, GroupMetadata, BackendPoi, Booking, UserCategory, NewsEntry, \
    Message, Vehicle, WalletEntry
from backend.twilio import VerifyCodeResult
from backend.utils import TranslatedString
from efa.models import PTJourney

logger = logging.getLogger(__name__)


class APIStatus(Schema):
    status: str


class ErrorResponse(Schema):
    error: str


class TranslatedErrorResponse(Schema):
    error: TranslatedString


class TokenNotValidResponse(Schema):
    error: str
    isValid: bool = Field(default=False)


class TokenValidResponse(Schema):
    msg: str = Field(default="OK")
    isValid: bool = Field(default=True)


class UserCategorySchema(Schema):
    id: str
    name: TranslatedString
    description: TranslatedString

    @classmethod
    def from_django(cls, category: UserCategory):
        return UserCategorySchema(
            id=str(category.id),
            name=TranslatedString.from_modeltranslation_field(category, 'name'),
            description=TranslatedString.from_modeltranslation_field(category, 'description'),
        )


class UserMetadata(Schema):
    userid: str
    active: bool
    category: UserCategorySchema
    name: str | None
    email: EmailStr | None | None = Field(
        description="Email address used for logging in. This is replaced by email_next when verification succeeds.")
    email_next: EmailStr | None = Field(
        description="When changing the email address, the new one is stored here until verification is successful")
    email_is_verified: bool = Field(description="If true, the address in 'email' has been verified by the user.")
    mobile_number_unverified: str | None = Field(
        description="When changing the mobile number, the new one is stored here until verification is successful")
    mobile_number_verified: str | None = Field(
        description="Filled once the number in 'mobile_number_unverified' has been verified.")
    mobile_number_is_verified: bool
    pooling_is_linked: bool
    auth_key_external_service: str = Field(description="Per-user random key used to authenticate calls from third party services to backend APIs")

    @staticmethod
    def from_django_user(user: BackendUser) -> "UserMetadata":
        return UserMetadata(
            userid=str(user.id),
            name=user.last_name,
            active=user.is_active,
            category=UserCategorySchema.from_django(user.category),
            email=user.email or None,
            email_next=user.email_next or None,
            email_is_verified=user.email_is_verified or False,
            mobile_number_unverified=user.mobile_number_unverified or None,
            mobile_number_verified=user.mobile_number_verified or None,
            mobile_number_is_verified=user.mobile_number_is_verified or False,
            pooling_is_linked=user.pooling_is_linked,
            auth_key_external_service=user.auth_key_external_service,
        )

    @staticmethod
    def from_user_id(user_id: Union[int, str]) -> Optional["UserMetadata"]:
        if type(user_id) == str:
            try:
                user_id = int(user_id)
            except ValueError:
                logger.debug(f"'{user_id:r}' is not a valid integer")
                return None
        try:
            user = BackendUser.objects.get(id=user_id)
        except BackendUser.DoesNotExist:
            return None
        return UserMetadata.from_django_user(user)


class LoginCredentials(Schema):
    email: EmailStr
    password: constr(min_length=1)


class CheckPasswordRequest(Schema):
    password: str


class RegisterUser(Schema):
    password: constr(min_length=1)
    name: str | None
    email: EmailStr | None
    mobile_phone_number: str | None
    category_id: str | None
    pooling_is_linked: bool | None = Field(default=None)


class LoginResponseSuccess(Schema):
    token: str
    user: UserMetadata


class LoginResponseFailure(ErrorResponse):
    reason: Literal['unknown_email', 'wrong_password']


class RegisterResponseSuccess(Schema):
    msg: str
    userID: str


class BitPermission(Schema):
    bit: int = Field(description="Value is 2^N with N in 1..63")
    permissionName: str


class Role(Schema):
    id: str
    name: str
    description: str
    permissions: str
    options: Dict = Field(default={"editable": True, "deletable": True})

    @staticmethod
    def from_backend_role(br: BackendRole) -> "Role":
        return Role(id=str(br.id), name=br.name, description=br.description, permissions=str(br.permissions))


class BackendGroup(Schema):
    id: str
    name: str
    description: str

    @staticmethod
    def from_django_group(group: Group) -> "BackendGroup":
        try:
            metadata = GroupMetadata.objects.get(group=group)
            description = metadata.description
        except GroupMetadata.DoesNotExist:
            description = ""
        return BackendGroup(id=str(group.id), name=group.name, description=description)


class ValidateResponseSuccess(Schema):
    resp: str = Field(default="OK")


class Email(Schema):
    email: EmailStr


class Username(Schema):
    username: constr(min_length=1)


# def resolve_permissions(v):
#     if type(v) == list:
#         v = v[0]
#     try:
#         data = json.loads(v)
#         return [BitPermission.parse_obj(e) for e in data]
#     except:
#         raise ValueError(f"Failed converting: {v}")


# class BitPermissionFromJson(list):
#     @classmethod
#     def __get_validators__(cls):
#         # one or more validators may be yielded which will be called in the
#         # order to validate the input, each validator will receive as an input
#         # the value returned from the previous validator
#         yield cls.validate
#
#     @classmethod
#     def __get_pydantic_core_schema__(
#             cls, source_type: Any, handler: GetCoreSchemaHandler
#     ) -> core_schema.CoreSchema:
#         return core_schema.typed_dict_schema(
#             {
#                 'name': core_schema.typed_dict_field(core_schema.str_schema()),
#                 'age': core_schema.typed_dict_field(core_schema.int_schema()),
#             },
#         )
#
#     @classmethod
#     def __get_pydantic_json_schema__(
#             cls, cs: core_schema.CoreSchema, handler: GetJsonSchemaHandler
#     ) -> JsonSchemaValue:
#         json_schema = handler(cs)
#         json_schema = handler.resolve_ref_schema(json_schema)
#         json_schema['examples'] = [
#             {
#                 'name': 'John Doe',
#                 'age': 25,
#             }
#         ]
#         json_schema['title'] = 'Person'
#         return json_schema
#
#     @classmethod
#     def validate(cls, v):
#         if type(v) == list:
#             v = v[0]
#         try:
#             data = json.loads(v)
#             return cls(*[BitPermission.parse_obj(e) for e in data])
#         except:
#             raise ValueError(f"Failed converting: {v}")
#
#     def __repr__(self):
#         return f'BitPermissionFromJson({super().__repr__()})'


# BitPermissionFromJson = Annotated[
#     List[BitPermission], PlainValidator(resolve_permissions)
# ]

def parse_permissions(cls, value):
    if isinstance(value, str):
        value = json.loads(value)
        value = [BitPermission.model_validate(e) for e in value]
    return value


class CreateRoleRequest(Schema):
    name: str
    description: str
    permissions: List[BitPermission]  # BitPermissionFromJson

    deserialize_permissions = field_validator('permissions', mode='before')(parse_permissions)

    # @classmethod
    # def validate(cls, value: Any) -> "CreateRoleRequest":
    #     if isinstance(value, dict) and isinstance(value.get('permissions'), list):
    #         value['permissions'] = json.loads(value['permissions'])
    #     return super().validate(value)


class UpdateRoleRequest(Schema):
    roleID: str
    name: str
    description: str
    permissions: List[BitPermission]

    deserialize_permissions = field_validator('permissions', mode='before')(parse_permissions)


class DeleteRoleRequest(Schema):
    roleID: str


class MsgResponse(Schema):
    msg: str

class CreateSuccessResponse(MsgResponse):
    created_id: str


class CreateGroupRequest(Schema):
    name: str
    description: str


class UpdateGroupRequest(Schema):
    groupID: str
    name: str
    description: str


class DeleteGroupRequest(Schema):
    groupID: str


desc_repl = "Replace field value with this. If not set/null, keep existing value."


class UpdateUserRequest(Schema):
    name: str | None = Field(description=desc_repl, default=None)
    password: str | None = Field(description=desc_repl, default=None)
    email: EmailStr | None = Field(description=desc_repl, default=None)
    category_id: str | None = Field(description=desc_repl, default=None)
    mobile_number: str | None = Field(description=desc_repl, default=None)
    pooling_is_linked: bool | None = Field(description=desc_repl, default=None)


class CreateAssignedGroupsRequest(Schema):
    userID: str
    groups: List[Dict[str, str]]


class CreateAssignedRolesRequest(Schema):
    userID: str
    roles: List[Dict[str, str]]


class UploadProfileImageRequest(Schema):
    profileImage: str

class UploadImageProofRequest(Schema):
    image: str
    latitude: float | None
    longitude: float | None
    booking_id: str | None

class PasswordResetRequest(Schema):
    email: str
    code: str
    newPassword: constr(min_length=1)


class CreatePoiRequest(Schema):
    name: str
    description: Optional[str] = Field(default=None)
    latitude: Latitude = Field(description="WGS84 latitude -90..90°")
    longitude: Longitude = Field(description="WGS84 longitude -180..180°")


class Poi(Schema):
    poiID: str
    poiType: PoiType
    name: str
    description: Optional[str] = Field(default=None)
    latitude: Latitude = Field(description="WGS84 latitude -90..90°")
    longitude: Longitude = Field(description="WGS84 longitude -180..180°")
    distance_meter: float | None = Field(default=None, description="Calculacted distance from query location in meters")
    osm_data: Dict | None = Field(default=None, description="For OpenStreetMap data, the metadata returned")

    @staticmethod
    def from_django(poi: BackendPoi) -> "Poi":
        distance = getattr(poi, "distance", None)
        distance = distance.m if distance else None
        return Poi(
            poiID=str(poi.id),
            poiType=PoiType(poi.poi_type),
            name=poi.name,
            description=poi.description,
            latitude=Latitude(poi.location[1]),
            longitude=Longitude(poi.location[0]),
            distance_meter=distance,
        )


# class OrderElement(Schema):
#     optionType: OptionType
#     optionID: str


class OptionPT(Schema):
    """Public transport (ÖPNV)"""
    optionType: Literal[OptionType.pt] = OptionType.pt
    optionID: str
    rideOption: str = Field(description="Short text describing the option")
    rideTimestamp: datetime.datetime = Field(description="Start timestamp of option")
    rideIcon: RideIcon
    approxTimeOfArrival: datetime.datetime = Field(description="Calculated or estimated end timestamp of option")
    journey: PTJourney


class OptionWalk(Schema):
    """Walk"""
    optionType: Literal[OptionType.walk] = OptionType.walk
    optionID: str
    rideOption: str = Field(description="Short text describing the option")
    rideTimestamp: datetime.datetime = Field(description="Start timestamp of option")
    rideIcon: RideIcon
    approxTimeOfArrival: datetime.datetime = Field(description="Calculated or estimated end timestamp of option")
    distanceM: float | None = Field(description='Distance to walk in meter')


# SharingVehicleType = Literal['scooter', 'bike']


class OptionSharing(Schema):
    optionType: Literal[OptionType.sharing] = OptionType.sharing
    optionID: str
    rideOption: str = Field(description="Short text describing the option")
    rideTimestamp: datetime.datetime = Field(description="Start timestamp of option")
    rideIcon: RideIcon
    approxTimeOfArrival: datetime.datetime = Field(description="Calculated or estimated end timestamp of option")
    maximumDurationH: float | None = Field(description="Maximum duration in hours that this option can be booked (because of follow-on booking or global maximum duration).", default=None)
    vehicleId: str
    vehicleType: VehicleType
    vehicleModel: str | None = Field(description="Model of the vehicle")
    vehicleNumber: str | None = Field(description="Identification of vehicle, e.g. ID visible on the vehicle")
    vehicleProviderName: str | None = Field(description="Name of the provider (e.g. ICL e.V.)")
    vehicleProviderId: str | None = Field(description="ID defined by provider for the vehicle")
    stateOfCharge: float | None = Field(description='State of charge in percent (0...100)')
    remainingRangeKm: float | None = Field(description='Remaining range in kilometer')
    distanceM: float | None = Field(description='How far away the vehicle currently is in meter')
    pickup_latitude: Latitude | None = Field(description="Current location of vehicle if available, WGS84 latitude -90..90°")
    pickup_longitude: Longitude | None = Field(description="Current location of vehicle if available, WGS84 longitude -180..180°")
    valid: bool = Field(description='Is this a valid option regarding distance and remaining range?')
    invalid_reasons: List[TranslatedString] | None = Field(default=None)


class OptionStatic(Schema):
    optionType: Literal[OptionType.static] = OptionType.static
    optionID: str
    rideOption: str = Field(description="Short text describing the option")
    rideIcon: RideIcon
    rideTimestamp: datetime.datetime = Field(description="Start timestamp of option")
    approxTimeOfArrival: datetime.datetime = Field(description="Calculated or estimated end timestamp of option")
    description: str


class OptionRriveUse(Schema):
    optionType: Literal[OptionType.rriveUse] = OptionType.rriveUse
    optionID: str
    rideOption: str = Field(description="Short text describing the option")
    rideTimestamp: datetime.datetime = Field(description="Start timestamp of option")
    rideIcon: RideIcon
    providerId: str
    approxTimeOfArrival: datetime.datetime = Field(description="Calculated or estimated end timestamp of option")
    from_latitude: Latitude = Field(description="Start location location, WGS84 latitude -90..90°")
    from_longitude: Longitude = Field(description="Start location, WGS84 longitude -180..180°")
    pickup_latitude: Latitude = Field(description="Pickup location, WGS84 latitude -90..90°")
    pickup_longitude: Longitude = Field(description="Pickup location, WGS84 longitude -180..180°")
    dropoff_latitude: Latitude = Field(description="Dropoff location, WGS84 latitude -90..90°")
    dropoff_longitude: Longitude = Field(description="Dropoff location, WGS84 longitude -180..180°")
    to_latitude: Latitude = Field(description="Destination location, WGS84 latitude -90..90°")
    to_longitude: Longitude = Field(description="Destination location, WGS84 longitude -180..180°")
    distanceM: float | None = Field(description="Distance from start to pickup location")
    distanceDropOffM: float | None = Field(description="Distance from dropoff to target location")


# class OptionRriveOffer(Schema):
#     optionType: Literal[OptionType.rriveOffer] = OptionType.rriveOffer
#     optionID: str
#     rideOption: str = Field(description="Short text describing the option")
#     rideIcon: RideIcon
#     rideTimestamp: datetime.datetime = Field(description="Start timestamp of option")
#     approxTimeOfArrival: datetime.datetime = Field(description="Calculated or estimated end timestamp of option")
#     todo: Any


class TripSearchRequest(Schema):
    start_timestamp: datetime.datetime
    location_from_latitude: Latitude | None = Field(default=None)
    location_from_longitude: Longitude | None = Field(default=None)
    location_to_latitude: Latitude | None = Field(default=None)
    location_to_longitude: Longitude | None = Field(default=None)
    user_location_latitude: Latitude | None = Field(default=None)
    user_location_longitude: Longitude | None = Field(default=None)
    include_invalid_trips: bool | None = Field(default=None)


TripOptionUnion = Union[
    OptionPT,
    OptionSharing,
    OptionRriveUse,
#    OptionRriveOffer,
    OptionStatic,
    OptionWalk,
]
TripOption = Annotated[
    TripOptionUnion,
    Field(discriminator="optionType")
]


class OptionAllFields(Schema):
    approxTimeOfArrival: datetime.datetime
    description: str = ""
    distanceM: float | None = None
    distanceDropOffM: float | None = None
    invalid_reasons: List[TranslatedString] | None = Field(default=[])
    journey: PTJourney = Field(default_factory=lambda: PTJourney(legs=[]))
    optionID: str
    optionType: str
    remainingRangeKm: float | None = None
    rideIcon: RideIcon
    rideOption: str
    rideTimestamp: datetime.datetime
    maximumDurationH: float | None = None
    providerId: str | None = None
    stateOfCharge: float | None = Field(default=None)
    todo: Any = Field(default={})
    valid: bool = True
    vehicleId: str = ""
    vehicleModel: str | None = None
    vehicleNumber: str | None = None
    vehicleProviderId: str | None = None
    vehicleProviderName: str | None = None
    vehicleType: VehicleType = VehicleType.unknown
    from_latitude: float | None = None
    from_longitude: float | None = None
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None
    dropoff_latitude: float | None = None
    dropoff_longitude: float | None = None
    to_latitude: float | None = None
    to_longitude: float | None = None

    @classmethod
    def from_option(cls, option: TripOptionUnion) -> "OptionAllFields":
        logger.debug(f"FROM_OPTION: {option.model_dump()}")
        if isinstance(option, OptionPT):
            logger.debug(f"LEGS: {option.journey.legs} {[l.model_dump() for l in option.journey.legs]}")

        return OptionAllFields.model_validate(option.model_dump())


trip_option_union_fields = set()
for member in typing.get_args(TripOptionUnion):
    member: Schema
    trip_option_union_fields.update(member.model_fields.keys())
    for field in ('optionType', 'optionID', 'rideTimestamp', 'approxTimeOfArrival', 'rideOption', 'rideIcon'):
        assert field in member.model_fields, f"Missing field '{field}' in {member}"

for field_name in trip_option_union_fields:
    assert field_name in OptionAllFields.model_fields, f"OptionAllFields missing field '{field_name}'"


class TripSearchResponse(Schema):
    """Option IDs are only unique in one response and will differ even for equivalent options on later requests."""
    options: List[TripOption]
    warnings: List[TranslatedString] = Field(default_factory=lambda: list())


class TripSearchFrontendResponse(Schema):
    """Option IDs are only unique in one response and will differ even for equivalent options on later requests."""
    options: List[OptionAllFields]
    warnings: List[TranslatedString] = Field(default_factory=lambda: list())


class BookingSchema(Schema):
    # Cannot use ModelSchema since PointField is not supported by Django Ninja
    id: str
    userID: str
    trip_mode: OptionType
    state: BookingState
    from_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°")
    from_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°")
    from_description: str | None = Field(default=None)
    to_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°")
    to_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°")
    to_description: str | None = Field(default=None)
    start_time: datetime.datetime | None
    end_time: datetime.datetime | None
    provider_id: str | None

    vehicle_id: str | None = Field(default=None)
    vehicle_type: TranslatedString | None = Field(default=None)
    vehicle_model: str | None = Field(default=None)
    vehicle_number: str | None = Field(default=None)
    vehicle_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°", default=None)
    vehicle_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°", default=None)
    vehicle_unlock_secret_needed: bool | None = Field(
        description="If true, an unlocks secret needs to be sent along with the unlock request", default=None)
    vehicle_unlock_secret_user_hint: TranslatedString | None = Field(default=None)

    vehicle_user_hint_start: TranslatedString | None = Field(
        description="A hint for the user that is displayed when the booking is started. Example usage would be to indicate where a helmet can be found.",
        default=None,
    )
    vehicle_user_hint_end: TranslatedString | None = Field(
        description="A hint for the user that is displayed when the booking is finished. Example usage would be to indicate where a helmet should be placed.",
        default=None,
    )

    @staticmethod
    def get_vehicle_params(booking: Booking) -> Dict[str, Any]:
        v: Vehicle | None = booking.vehicle
        if v:
            vehicle_unlock_secret_needed = bool(v.unlock_secret)
            if vehicle_unlock_secret_needed:
                vehicle_unlock_secret_user_hint = TranslatedString.from_modeltranslation_field(v,
                                                                                               'unlock_secret_user_hint')
                if not all(bool(v) for v in vehicle_unlock_secret_user_hint.values()):
                    logger.warning(f"Incomplete translation for unlock_secret_user_hint in vehicle ID {v.id}: {v}")
                    vehicle_unlock_secret_user_hint = None
            else:
                vehicle_unlock_secret_user_hint = None
            vehicle_user_hint_start = TranslatedString.from_modeltranslation_field(v,'user_hint_start')
            vehicle_user_hint_end = TranslatedString.from_modeltranslation_field(v, 'user_hint_end')
            vehicle_params = {
                'vehicle_id': str(v.id),
                'vehicle_type': TranslatedString.from_gettext(VehicleType(v.vehicle_type).description),
                'vehicle_model': v.vehicle_model,
                'vehicle_number': v.vehicle_number,
                'vehicle_location_latitude': v.location[1] if v.location else None,
                'vehicle_location_longitude': v.location[0] if v.location else None,
                'vehicle_unlock_secret_needed': vehicle_unlock_secret_needed,
                'vehicle_unlock_secret_user_hint': vehicle_unlock_secret_user_hint,
                'vehicle_user_hint_start': vehicle_user_hint_start if any([bool(h) for h in vehicle_user_hint_start.values()]) else None,
                'vehicle_user_hint_end': vehicle_user_hint_end if any([bool(h) for h in vehicle_user_hint_end.values()]) else None,
            }
        else:
            vehicle_params = {}
        return vehicle_params

    @staticmethod
    def from_django(booking: Booking) -> "BookingSchema":
        return BookingSchema(
            id=str(booking.id),
            userID=str(booking.user.id),
            trip_mode=OptionType(booking.trip_mode),
            state=BookingState(booking.state),
            from_location_latitude=Latitude(booking.from_location[1]) if booking.from_location else None,
            from_location_longitude=Longitude(booking.from_location[0]) if booking.from_location else None,
            from_description=booking.from_description,
            to_location_latitude=Latitude(booking.to_location[1]) if booking.to_location else None,
            to_location_longitude=Longitude(booking.to_location[0]) if booking.to_location else None,
            to_description=booking.to_description,
            start_time=booking.start_time,
            end_time=booking.end_time,
            provider_id=booking.provider_id,
            **BookingSchema.get_vehicle_params(booking),
        )


class BookingFrontendSchema(Schema):
    id: str
    state: BookingState
    type: OptionType
    rideIcon: RideIcon
    rideDestinationLatitude: Latitude | None = Field(description="WGS84 latitude -90..90°")
    rideDestinationLongitude: Longitude | None = Field(description="WGS84 longitude -180..180°")
    rideDestination: str | None = Field(default=None)
    rideStartLatitude: Latitude | None = Field(description="WGS84 latitude -90..90°")
    rideStartLongitude: Longitude | None = Field(description="WGS84 longitude -180..180°")
    rideStart: str | None = Field(default=None)
    rideStartTimestamp: datetime.datetime | None
    rideEndTimestamp: datetime.datetime | None
    provider_id: str | None

    vehicle_id: str | None = Field(default=None)
    vehicle_type: TranslatedString | None = Field(default=None)
    vehicle_model: str | None = Field(default=None)
    vehicle_number: str | None = Field(default=None)
    vehicle_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°", default=None)
    vehicle_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°", default=None)
    vehicle_unlock_secret_needed: bool | None = Field(
        description="If true, an unlocks secret needs to be sent along with the unlock request", default=None)
    vehicle_unlock_secret_user_hint: TranslatedString | None = Field(default=None)

    vehicle_user_hint_start: TranslatedString | None = Field(
        description="A hint for the user that is displayed when the booking is started. Example usage would be to indicate where a helmet can be found.",
        default=None,
    )
    vehicle_user_hint_end: TranslatedString | None = Field(
        description="A hint for the user that is displayed when the booking is finished. Example usage would be to indicate where a helmet should be placed.",
        default=None,
    )

    source_link_more_information: str | None = Field(description="Link to public transport operator with more information like ticket options", default=None)

    score_points: float = Field(
        default=None,
        description="Points awarded for this booking"
    )
    score_points_reason: List[str] = Field(
        default=[],
        description="Reasons why the points calculated as they were"
    )

    @staticmethod
    def from_django(booking: Booking) -> "BookingFrontendSchema":
        source_link_more_information = None
        icon: RideIcon
        icon = 'unknown'
        if booking.trip_mode == 'pt':
            icon = 'pt'
            if booking.from_location and booking.to_location and booking.start_time:
                source_link_more_information = api_efa_client.build_source_link(
                    booking.from_location[0], booking.from_location[1],
                    booking.to_location[0], booking.to_location[1],
                    booking.start_time,
                )
        elif booking.trip_mode in {'car', 'rriveUse', 'rriveOffer'}:
            icon = 'car'
        elif booking.trip_mode == 'walk':
            icon = 'walk'
        elif booking.trip_mode == 'own_bike':
            icon = 'bike'
        elif booking.trip_mode == 'own_scooter':
            icon = 'scooter'
        elif booking.trip_mode == 'sharing' and booking.vehicle:
            if booking.vehicle.vehicle_type == 'bike':
                icon = 'bike'
            elif booking.vehicle.vehicle_type == 'scooter':
                icon = 'scooter'
        points_response = booking.get_score_points()
        return BookingFrontendSchema(
            id=str(booking.id),
            state=BookingState(booking.state),
            type=OptionType(booking.trip_mode),
            rideIcon=icon,
            rideStartLatitude=Latitude(booking.from_location[1]) if booking.from_location else None,
            rideStartLongitude=Longitude(booking.from_location[0]) if booking.from_location else None,
            rideStart=booking.from_description,
            rideDestinationLatitude=Latitude(booking.to_location[1]) if booking.to_location else None,
            rideDestinationLongitude=Longitude(booking.to_location[0]) if booking.to_location else None,
            rideDestination=booking.to_description,
            rideStartTimestamp=booking.start_time,
            rideEndTimestamp=booking.end_time,
            provider_id=booking.provider_id,
            source_link_more_information=source_link_more_information,
            score_points=points_response.points,
            score_points_reason=points_response.reasons,
            **BookingSchema.get_vehicle_params(booking),
        )


class BookingFrontendResponse(Schema):
    nextRides: List[BookingFrontendSchema]
    previousRides: List[BookingFrontendSchema]


class BookingCreateSchema(Schema):
    trip_mode: OptionType
    state: BookingState | None = Field(default=None)
    from_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°", default=None)
    from_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°", default=None)
    from_description: str | None = Field(default=None)
    to_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°", default=None)
    to_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°", default=None)
    to_description: str | None = Field(default=None)
    start_time: datetime.datetime | None = Field(default=None)
    end_time: datetime.datetime | None = Field(default=None)
    vehicle_id: str | None = Field(default=None)
    provider_id: str | None = Field(default=None)


class BookingUpdateSchema(Schema):
    trip_mode: OptionType | None = Field(default=None)
    state: BookingState | None = Field(default=None)
    from_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°", default=None)
    from_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°", default=None)
    from_description: str | None = Field(default=None)
    to_location_latitude: Latitude | None = Field(description="WGS84 latitude -90..90°", default=None)
    to_location_longitude: Longitude | None = Field(description="WGS84 longitude -180..180°", default=None)
    to_description: str | None = Field(default=None)
    start_time: datetime.datetime | None = Field(default=None)
    end_time: datetime.datetime | None = Field(default=None)
    vehicle_id: str | None = Field(default=None)
    provider_id: str | None = Field(default=None)


class UserCategoryResponse(Schema):
    categories: List[UserCategorySchema]


class CheckVerificationCodeRequest(Schema):
    code: str


class CheckVerificationCodeResponse(Schema):
    verified: bool
    status: VerifyCodeResult


class NewsEntryTranslatedSchema(Schema):
    id: str
    title: TranslatedString
    image: str | None
    header: TranslatedString
    subHeader: TranslatedString
    subHeader2: TranslatedString
    previewText: TranslatedString
    text: TranslatedString
    source_url: str | None = Field(description="Link to the source of the news entry if given be synced news source")

    @classmethod
    def from_news_entry(cls, news_entry: NewsEntry, request: HttpRequest | None = None):
        if news_entry.image_url:
            image_url = news_entry.image_url
        else:
            if news_entry.image:
                image_url = news_entry.image.canonical_url
                if request:
                    image_url = request.build_absolute_uri(image_url)
            else:
                image_url = None
        return NewsEntryTranslatedSchema(
            id=str(news_entry.id),
            title=TranslatedString.from_gettext(NewsType[news_entry.news_type].description),
            image=image_url,
            header=TranslatedString.from_modeltranslation_field(news_entry, 'header'),
            subHeader=TranslatedString.from_modeltranslation_field(news_entry, 'sub_header'),
            subHeader2=TranslatedString.from_modeltranslation_field(news_entry, 'sub_header2'),
            previewText=TranslatedString.from_modeltranslation_field(news_entry, 'text', strip_html_tags=True),
            text=TranslatedString.from_modeltranslation_field(news_entry, 'text'),
            source_url=news_entry.external_url,
        )


class NewsListResponse(RootModel):
    root: Dict[str, List[NewsEntryTranslatedSchema]]

class NewsListCategory(Schema):
    entries: List[NewsEntryTranslatedSchema]
    more_link_url: str | None
    more_link_label: TranslatedString | None

class NewsListResponse2(RootModel):
    root: Dict[str, NewsListCategory]

class MessageSchema(Schema):
    id: str
    title: str
    subTitle: str
    content: str
    createdAt: datetime.datetime

    @classmethod
    def from_model(cls, message: Message):
        return MessageSchema(
            id=str(message.id),
            title=message.title,
            subTitle=message.sub_title,
            content=message.content,
            createdAt=message.created_at,
        )


class RegisterPushTokenRequest(Schema):
    push_system: Literal['apple', 'android']
    device_model: Optional[str] = Field(default=None, description="""A user-readable description of the device this is from.
Only used for human administrative purposes to identify a device.""")
    token: str


class PoiSearchResponse(Schema):
    pois: List[Poi]
    warnings: List[TranslatedString] = Field(default_factory=lambda: list())


class UserStatisticsResponse(Schema):
    completed_bookings_count: int = Field(description="How many bookings has the user completed?")
    completed_bookings_distance_km: float = Field(
        description="Sum of the distance of all completed bookings in kilometers")
    completed_bookings_duration_hour: float = Field(
        description="Sum of the duration of all completed bookings in hours")
    completed_bookings_co2e_reduction_g: float = Field(
        description="Sum of the CO2e reduced by the completed bookings in grams")
    experience: float = Field(description="value 0..5")
    points: int = Field()
    rank: int | None = Field(description="Among users of the platform, ranking in the leaderboard of points")
    booking_percentage_per_mode: Dict[str, float] = Field(
        description="Keys are 'pt', 'sharing', 'rrive', 'car', 'walk'. Values are percentage of completed bookings for this key. Sums to 100.")
    leaderboard: List[Tuple[str, float, int]] = Field(
        description="Leaderboard of users' points. Each list entry is the user's name, the experience (0..5) and the number of points. Ordered by points descreasing.")


class AssetUnlockRequest(Schema):
    booking_id: str = Field(description="Booking of the user that contains the asset")
    unlock_secret: str | None = Field(description="Unlock secret entered by the user (if needed by asset)",
                                      default=None)


class AssetLockRequest(Schema):
    booking_id: str = Field(description="Booking of the user that contains the asset")


class FeedbackRequest(Schema):
    feedbackText: str
    rideData: Dict | None
    vote: Literal['up', 'down', 'neutral']
    model_config = ConfigDict(extra="allow")

class SupportText(Schema):
    title: str
    text: str
    content: str
    category: str
    description: str
    entry_name: str | None

class SupportTextResponse(Schema):
    by_language: Dict[str, List[SupportText]]

class ExternalNewsEntry(Schema):
    id: str
    title: TranslatedString
    icon_image_url: str
    header: TranslatedString
    sub_header: TranslatedString = Field(default={})
    preview_text: TranslatedString
    text: TranslatedString
    url: str

class ExternalNewsCategory(Schema):
    category_id: str
    entries: List[ExternalNewsEntry]

class ExternalNews(Schema):
    categories: List[ExternalNewsCategory]

class PoolingLinkResultRequest(Schema):
    is_linked: bool = Field(description="true if linking was successful; false to report the link as broken or removed")
    user_id: str
    key: str

SimpleHttpUrl = Annotated[str, Field(pattern="^https?://")]

class FrontendUrlPerEnvironment(Schema):
    development: SimpleHttpUrl
    production: SimpleHttpUrl


class FrontendAppConfig(Schema):
    MAPBOX_API: SimpleHttpUrl = Field(default='https://api.mapbox.com')
    MAPBOX_BBOX_COORDS: List[float] = Field(description="Mapbox bounding box ", min_length=4, max_length=4)
    MAPBOX_CYCLING_URI: str = Field(description='path only (should start with /)', default="/directions/v5/mapbox/cycling/")
    MAPBOX_DRIVING_URI: str = Field(description='path only (should start with /)', default="/directions/v5/mapbox/driving/")
    MAPBOX_PLACES_URI: str = Field(description='path only (should start with /)', default="/geocoding/v5/mapbox.places/")
    MAPBOX_STYLE: str = Field(default="mapbox://styles/mapbox/streets-v12")
    MAPBOX_TOKEN: str = Field(min_length=10)
    MAPBOX_WALKING_URI: str = Field(description='path only (should start with /)', default="/directions/v5/mapbox/walking/")
    POOLING_DOWNLOAD_URLS: FrontendUrlPerEnvironment
    POOLING_PLANNED_DRIVER: str = Field(description='path only (should start with /)', default="/tab/2/trips/planned/offer/")
    POOLING_PLANNED_PASSENGER: str = Field(description='path only (should start with /)', default="/tab/2/trips/planned/booking/")
    POOLING_PREVIOUS_DRIVER: str = Field(description='path only (should start with /)', default="/tab/2/trips/past/offer/")
    POOLING_PREVIOUS_PASSENGER: str = Field(description='path only (should start with /)', default="/tab/2/trips/past/booking/")
    POOLING_REGISTER: str = Field(description='path only (should start with /)', default="")
    POOLING_RIDE_OFFER: str = Field(description='path only (should start with /)', default="/tab/1/rideoffer/")
    POOLING_URLS: FrontendUrlPerEnvironment

class PointsEstimateRequest(Schema):
    trip_mode: OptionType
    distance_m: float

class PointsEstimateResponse(PointsEstimateRequest):
    points_estimate: float
    reasons: List[str]