# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import dataclasses
import datetime
import hashlib
import json
import logging
import random
import re
import string
from collections import defaultdict
from typing import Dict, List, Tuple, Union, Literal, Callable
import itertools
from urllib.parse import urlencode

import pytz
from dateutil.relativedelta import relativedelta
from dirtyfields import DirtyFieldsMixin
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db.models.functions import Distance
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.gis.db.models import PointField, LineStringField
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q, CheckConstraint, Count, Index
from django.http import HttpRequest
from django.urls import reverse
from django.utils.text import slugify
from filer.fields.image import FilerImageField
from pydantic import ValidationError as PydanticValidationError
from tinymce.models import HTMLField

from backend.enum import PoiType, OptionType, BookingState, VehicleType, NewsType, VehicleLockState, MessagePurpose, \
    UserImageFeedbackType, VehicleAvailabilityEnum
from backend.translate import get_translator
from backend.utils import generate_verification_code, get_distance_meter, geod_wgs84, TranslatedString, \
    RE_PATTERN_MOBILE_PHONE_NUMBER, send_email_template, load_class_from_dotted_path

logger = logging.getLogger(__name__)

_ = get_translator()

translate_me = lambda x: x

backend_permissions = {
    0: 'readDashboard       ',
    1: 'readProjects        ',
    2: 'readUsers           ',
    3: 'readDevices         ',
    4: 'readStatistics      ',
    5: 'readHelp            ',
    6: 'addProject          ',
    7: 'addUser             ',
    8: 'addRole             ',
    9: 'addGroup  ',
    10: 'addWorksheet        ',
    11: 'addWorkspace        ',
    12: 'editProject         ',
    13: 'editUser            ',
    14: 'editRole            ',
    15: 'editGroup           ',
    16: 'editWorksheet       ',
    17: 'editWorkspace       ',
    18: 'deleteProject       ',
    19: 'deleteUser          ',
    20: 'deleteRole          ',
    21: 'deleteGroup         ',
    22: 'deleteWorksheet     ',
    23: 'deleteWorkspace     ',
    24: 'readWorkflows       ',
    25: 'deleteWorkflows     ',
    26: 'readTemplates       ',
    27: 'deleteTemplates     ',
    28: 'addWorkflows        ',
    29: 'addTemplates        ',
    30: 'editWorkflows       ',
    31: 'editTemplates       ',
    32: 'editWorkflowProps   ',
    33: 'editTemplateProps   ',
    34: 'NA                  ',
    35: 'NA                  ',
    36: 'NA                  '
}


class BackendRole(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField("Role", max_length=100, unique=True)
    description = models.TextField("Description")
    permissions = models.BigIntegerField()

    def get_permission_bits(self) -> Dict[int, str]:
        return {k: v
                for k, v in backend_permissions.items()
                if self.permissions & 2 ** k
                }


class GroupMetadata(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField("Description")


class UserCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(translate_me("Kategorie"), max_length=100, unique=True)
    description = models.TextField(translate_me("Beschreibung"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)

def get_random_string_32() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))

class BackendUser(DirtyFieldsMixin, AbstractUser):
    class ImageFormats(models.TextChoices):
        PNG = "PNG", "image/png"
        JPEG = "JPEG", "image/jpeg"

    email = models.EmailField(translate_me("email address"), unique=True)

    roles = models.ManyToManyField(BackendRole)
    password_reset_secret = models.CharField(max_length=100, null=True, blank=True)
    password_reset_validity = models.DateTimeField(null=True, blank=True)
    profile_image_data = models.BinaryField(max_length=10 * 1024 * 1024, null=True, blank=True)
    profile_image_mimetype = models.CharField(choices=ImageFormats.choices, null=True, blank=True, default=None,
                                              max_length=20)
    category = models.ForeignKey(UserCategory, on_delete=models.SET_DEFAULT, null=True, blank=True, default=0)

    phone_regex = RegexValidator(regex=r'^\+[1-9]\d{1,14}$',
                                 message="Phone number must be entered in the format: '+49170999999999'. Up to 15 digits allowed.")
    mobile_number_unverified = models.CharField(validators=[phone_regex], max_length=17, default="", blank=True,
                                                help_text="")
    mobile_number_verified = models.CharField(validators=[phone_regex], max_length=17, default="", blank=True)
    mobile_number_is_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=32, null=True, blank=True, default=None)
    email_verification_valid_until = models.DateTimeField(null=True, blank=True, default=None)
    email_next = models.EmailField(translate_me("Neue, noch nicht verifizierte E-Mail-Adresse"), unique=True,
                                   default=None, blank=True, null=True)
    email_is_verified = models.BooleanField(default=False)

    score_experience = models.FloatField(default=0.0,
                                         help_text="Score from 0 to 5 that rises with experience in the app")
    score_points = models.IntegerField(default=0,
                                       help_text="Different actions in the app lead to an increase in points")

    pooling_is_linked = models.BooleanField(default=False)

    auth_key_external_service = models.CharField(max_length=32, default=get_random_string_32)

    @classmethod
    def normalize_mobile_phone_number(cls, number: str):
        if not number:
            raise ValueError("No number provided")
        # Strip out everything but non-number and non-plus
        number = re.sub(r'[^+0-9]', '', number)
        if number.startswith('00'):
            # e.g. 0049...
            number = '+' + number[2:]
        elif number.startswith('0'):
            # e.g. 0171...
            number = '+49' + number[1:]
        if not RE_PATTERN_MOBILE_PHONE_NUMBER.match(number):
            raise ValueError("Only german mobile phone numbers (of form +491567890123 or 01567890123) or international numbers are allowed")
        return number

    @classmethod
    def email_to_username(cls, email: str):
        return ('fe_' + hashlib.sha256(email.encode('utf-8')).hexdigest().upper()[:6] + '_' + slugify(email))[:140]

    def start_email_verification(self, save=True, test_mode=False, request: HttpRequest | None = None) -> Tuple[
        str, str]:
        assert self.email_next, f"Set email_next before starting verification!"
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        grace_period = datetime.timedelta(minutes=30)
        if not self.email_verification_valid_until or self.email_verification_valid_until < now:
            self.email_verification_code = generate_verification_code()
            logger.debug(
                f"Setting new email verification code '{self.email_verification_code}' for '{self.email_next}'")
        else:
            logger.debug(
                f"Keeping email verification code '{self.email_verification_code}' for '{self.email_next}'. Valid until: {self.email_verification_valid_until} (extending by {grace_period})")
        self.email_verification_valid_until = now + grace_period
        if save:
            self.save()
        url = reverse('backend-email-verify') + '?' + urlencode(
            {'email': self.email_next, 'code': self.email_verification_code})
        if request is not None:
            url = request.build_absolute_uri(url)
        metadata =  {
            "code": self.email_verification_code,
            "url": url,
        }
        if not test_mode:
            send_email_template(settings.EMAIL_FROM_ADDRESS, [self.email_next], 'VERIFY_EMAIL', metadata)

        return self.email_verification_code, url

    def process_email_verification_code(self, code: str):
        if not self.email_verification_valid_until or not self.email_verification_code:
            verify_code_result = 'unknown'
        elif self.email_verification_valid_until < datetime.datetime.now(tz=datetime.timezone.utc):
            verify_code_result = 'expired'
        elif self.email_verification_code == code:
            verify_code_result = 'approved'
        else:
            verify_code_result = 'failed'
        if verify_code_result == 'approved':
            logger.debug(
                f"User {self}: Setting user.email_verified = True (verify_code_result = {verify_code_result}) email={self.email} email_next={self.email_next}")
            self.email = self.email_next
            self.email_is_verified = True
            self.save()
        return verify_code_result

    def get_scores(self, when: datetime.datetime | None = None) -> Tuple[float, int, List[str], List[str], List[str]]:
        experience = 0.0
        points = 0
        points_reasons = []
        reasons = []
        rules = []

        when = when or datetime.datetime.now(tz=datetime.timezone.utc)

        mode_counts = {ot: 0 for ot in OptionType}
        mode_counts.update({
            OptionType(e['trip_mode']): e['total'] for e in
            self.booking_set.filter(
                state__in={BookingState.finished}
            ).all().values('trip_mode').annotate(total=Count('trip_mode'))
        })
        bookings = self.booking_set.filter(state__in={BookingState.finished}).all()
        distances_all = {}
        distances_in_campus_range = {}
        last_booking_at = None
        rules.append("Points per km distance are only awarded for 'finished' cookings (not those canceled or in timeout).")
        rules.append("Points per km distance are only awarded if start or end point are on campus.")
        rules.append("Points per km distance are (proportionally) reduced if actual duration is shorter than planned duration (duration ratio < 1).")
        rules.append("1 point per km distance for car bookings")
        rules.append("2 points per km distance for public transport")
        rules.append("4 points per km distance for sharing bookings")
        bookings_without_campus_end = 0
        for b in bookings:
            distance = b.get_distance()[1] or 0.0
            distance_km = distance / 1000
            distances_all[b] = distance
            in_range = b.is_in_campus_range()
            if last_booking_at is None or last_booking_at < b.start_time:
                last_booking_at = b.start_time
            if in_range:
                distances_in_campus_range[b] = distances_all[b]
                factor = {
                    OptionType.car: 1,
                    OptionType.rriveOffer: 1,
                    OptionType.rriveUse: 1,
                    OptionType.pt: 2,
                    OptionType.sharing: 4,
                    OptionType.walk: 7,
                    OptionType.own_bike: 4,
                    OptionType.own_scooter: 4,
                }[OptionType(b.trip_mode)]
                ratio_actual_to_planned = 1.0
                if b.planned_start_time and b.planned_end_time and b.start_time and b.end_time:
                    ratio_actual_to_planned = (b.end_time - b.start_time) / (b.planned_end_time - b.planned_start_time)
                    if ratio_actual_to_planned > 0.9:
                        ratio_actual_to_planned = 1.0
                p = factor * distance_km * ratio_actual_to_planned
                points_reasons.append(f"{factor} (mode) * {ratio_actual_to_planned:0.2f} (duration ratio) * {distance_km:0.1f}km = {p:0.1f} points for {b}")
                points += p
            else:
                points_reasons.append(f"0 points (neither end was in range of campus) for {b}")
                bookings_without_campus_end += 1
        # points_reasons.append(f"{bookings_without_campus_end} not counted because neither end was in range of campus")



        distance_by_trip_mode = defaultdict(float)
        for b, distance in distances_in_campus_range.items():
            distance_by_trip_mode[OptionType(b.trip_mode)] += distance / 1000.0
        booking_count = len(distances_in_campus_range)
        distance_km = sum(distances_in_campus_range.values())

        reason = "0.5 experience points for having a booking of type walk or own_bike or own_scooter"
        rules.append(reason)
        if mode_counts[OptionType.walk] or mode_counts[OptionType.own_bike] or mode_counts[OptionType.own_scooter]:
            experience += 0.5
            reasons.append(reason)

        reason = "0.5 experience points for having a booking of type public transport"
        rules.append(reason)
        if mode_counts[OptionType.pt]:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for having a booking of type sharing"
        rules.append(reason)
        if mode_counts[OptionType.sharing]:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for having a booking of type car pooling"
        rules.append(reason)
        if mode_counts[OptionType.rriveOffer] or mode_counts[OptionType.rriveUse]:
            experience += 0.5
            reasons.append(reason)

        reason = "0.5 experience points for bookings >= 5km (to or from campus only)"
        rules.append(reason)
        if distance_km >= 5:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for bookings >= 25km (to or from campus only)"
        rules.append(reason)
        if distance_km >= 25:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for bookings >= 200km (to or from campus only)"
        rules.append(reason)
        if distance_km >= 200:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for having >= 1 booking (to or from campus only)"
        rules.append(reason)
        if booking_count >= 1:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for having >= 5 bookings (to or from campus only)"
        rules.append(reason)
        if booking_count >= 5:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for having >= 15 bookings (to or from campus only)"
        rules.append(reason)
        if booking_count >= 15:
            experience += 0.5
            reasons.append(reason)
        reason = "0.5 experience points for having >= 50 bookings (to or from campus only)"
        rules.append(reason)
        if booking_count >= 50:
            experience += 0.5
            reasons.append(reason)

        reason = "-1 experience points for last booking >=1 month ago (only if >1 point left)"
        rules.append(reason)
        if last_booking_at and last_booking_at + relativedelta(months=1) < when and experience >= 2.0:
            experience -= 1.0
            reasons.append(reason)
        reason = "-1 experience points for last booking >=2 month ago (only if >1 point left)"
        rules.append(reason)
        if last_booking_at and last_booking_at + relativedelta(months=2) < when and experience >= 2.0:
            experience -= 1.0
            reasons.append(reason)
        reason = "-1 experience points for last booking >=3 month ago (only if >1 point left)"
        rules.append(reason)
        if last_booking_at and last_booking_at + relativedelta(months=3) < when and experience >= 2.0:
            experience -= 1.0
            reasons.append(reason)
        reason = "-1 experience points for last booking >=4 month ago (only if >1 point left)"
        rules.append(reason)
        if last_booking_at and last_booking_at + relativedelta(months=4) < when and experience >= 2.0:
            experience -= 1.0
            reasons.append(reason)

        experience = min(experience, 5.0)

        return experience, points, points_reasons, reasons, rules

    def update_score(self) -> bool:
        """Sets values if changed but does not save. Returns True if any value changed."""
        experience, points, points_reasons, reasons, rules = self.get_scores()
        logger.debug(f"User {self} updated to experience {experience}, points {points}, reasons: {reasons}")
        old_points, self.score_points = self.score_points, points
        old_experience, self.score_experience = self.score_experience, experience
        return old_points != self.score_points or old_experience != self.score_experience

    def save(self, *args, **kwargs):
        # dirty = self.get_dirty_fields()
        # old_mobile_number_verified = dirty.get('mobile_number_verified', None)
        # old_mobile_number_is_verified = dirty.get('mobile_number_is_verified', None)
        # if old_mobile_number_verified != self.mobile_number_unverified and self.mobile_number_unverified is not None:
        #     self.mobile_number_is_verified = False
        #     logger.debug(f"User {self}: New unverified mobile number ({self.mobile_number_unverified}) differs from verified number ({old_mobile_number_verified}). mobile_number_is_verified {old_mobile_number_is_verified} -> {self.mobile_number_is_verified}")

        # noinspection PyArgumentList
        super().save(*args, **kwargs)


class BackendPoi(models.Model):
    POI_TYPE_CHOICES = (
        (PoiType.TYPE_UNBEKANNT.value, translate_me("Unbekannt")),
        (PoiType.TYPE_STOP_BUS.value, translate_me("Bushaltestelle")),
        (PoiType.TYPE_STOP_STRASSENBAHN.value, translate_me("Straßenbahn")),
        (PoiType.TYPE_STOP_ZUG.value, translate_me("Zug")),
        (PoiType.TYPE_WELL_KNOWN.value, translate_me("Well-known")),
    )
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    poi_type = models.IntegerField(choices=POI_TYPE_CHOICES, default=PoiType.TYPE_UNBEKANNT.value)
    location = PointField(srid=4326, geography=True)  # WGS84
    source_type = models.CharField(max_length=100, null=True, blank=True,
                                   help_text="Only relevant for automatic POI sync: Distinguishes between different sync sources")
    source_id = models.CharField(max_length=40, null=True, blank=True,
                                 help_text="Only relevant for automatic POI sync: Distinguishes between POIs of one sync source")
    source_properties = models.JSONField(default=dict, encoder=DjangoJSONEncoder, blank=True, null=True,
                                         help_text="Only relevant for automatic POI sync: Metadata from POI source for this ID")
    source_acquired_at = models.DateTimeField(null=True, blank=True, auto_now_add=True,
                                              help_text="Only relevant for automatic POI sync: When was this POI acquired")

    @staticmethod
    def bulk_update_or_create(objects: List['BackendPoi']):
        # Note: keep update_fields in sync with all fields above!
        result = BackendPoi.objects.bulk_create(objects, update_conflicts=True, update_fields=[
            'name',
            'description',
            'poi_type',
            'location',
            'source_properties',
        ], unique_fields=['source_type', 'source_id'])

    def poi_type_name(self):
        names = [c[1] for c in self.POI_TYPE_CHOICES if c[0] == self.poi_type]
        return names[0] if names else None

    def list_get_location_coordinates(self):
        return f"Lat/Lon {self.location[1]}, {self.location[0]}"

    def __str__(self):
        return f"POI '{self.name}' type '{PoiType(self.poi_type).name}={self.poi_type}' at '{self.location}'"

    class Meta:
        verbose_name = "POI"
        verbose_name_plural = "POIs"

        indexes = [
            models.Index(fields=['source_type', 'source_id'])
        ]
        constraints = [
            models.UniqueConstraint(fields=['source_type', 'source_id'], name='unique_source_type_source_id'),
        ]


__sharingos_client = None


def get_sharingos_client():
    global __sharingos_client
    if not __sharingos_client:
        from sharingos.client import SharingOSClient
        __sharingos_client = SharingOSClient()
    return __sharingos_client


@dataclasses.dataclass
class VehicleAvailability:
    vehicle: 'Vehicle'
    hidden_by_availability: bool
    near_enough: bool
    range_ok: bool
    busy_in_timerange: bool
    distance_m: float
    maximum_booking_duration_s: float
    reasons: List[TranslatedString]


class Vehicle(DirtyFieldsMixin, models.Model):
    id = models.BigAutoField(primary_key=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.get_choices(), default='unknown')
    vehicle_model = models.CharField(max_length=50)
    vehicle_number = models.CharField(max_length=20)
    provider_name = models.CharField(max_length=20)
    provider_id = models.CharField(max_length=50)
    availability = models.CharField(max_length=30, choices=VehicleAvailabilityEnum.get_choices(), default='normal')
    battery_level_percent = models.FloatField(help_text="Battery level in percent (0-100)", null=True, blank=True)
    remaining_range_km = models.FloatField(help_text="Remaining range in kilometers with current battery charge",
                                           null=True, blank=True)
    location = PointField(srid=4326, geography=True, null=True, blank=True)  # WGS84
    lock_state = models.CharField(max_length=20, choices=VehicleLockState.get_choices(), default='unknown',
                                  help_text="Last known lock state (if supported by device)")
    unlock_secret = models.CharField(max_length=20, null=True, blank=True, default=None,
                                     help_text="If the user needs to enter something to unlock the vehicle, it must be stored here.")
    unlock_secret_user_hint = models.TextField(null=True, blank=True, default=None,
                                               help_text="A hint for the user where the unlock secret is found. Is shown to the user before they need to enter the unlock secret.")
    last_unlock_at = models.DateTimeField(null=True, blank=True, default=None)
    last_unlock_by = models.ForeignKey(BackendUser, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    last_unlock_for_booking = models.ForeignKey('Booking', related_name='+', on_delete=models.SET_NULL, null=True,
                                                blank=True, default=None)

    user_hint_start = models.TextField(null=True, blank=True, default=None,
                                       help_text="A hint for the user that is displayed when the booking is started. Example usage would be to indicate where a helmet can be found.")
    user_hint_end = models.TextField(null=True, blank=True, default=None,
                                       help_text="A hint for the user that is displayed when the booking is finished. Example usage would be to indicate where a helmet should be placed.")


    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle_type} {self.vehicle_model} {self.vehicle_number}"

    @classmethod
    def get_available_vehicles(cls, from_location: Point, to_location: Point, distance_cutoff_meter: float,
                               timerange_from: datetime.datetime, timerange_to: datetime.datetime) -> List[
        VehicleAvailability]:
        distance_one_way = get_distance_meter(from_location, to_location)

        vehicles = Vehicle.objects \
            .annotate(distance=Distance('location', from_location, spheroid=True)) \
            .order_by('distance') \
            .all()
        vehicle_ids = {v.id for v in vehicles}
        # Find planned and started Bookings that overlap with timerange
        bookings = Booking.objects.filter(
            vehicle__in=vehicle_ids,
            state__in={BookingState.planned, BookingState.started},
        ).filter(Q(start_time__gte=timerange_from, start_time__lte=timerange_to) | Q(end_time__gte=timerange_from,
                                                                                     end_time__lte=timerange_to))
        bookings_by_vehicle_ids = defaultdict(list)
        [bookings_by_vehicle_ids[b.vehicle.id].append(b) for b in bookings]
        result = []
        for v in vehicles:
            reasons = []
            near_enough = True
            range_ok = True
            busy_in_timerange = False
            hidden_by_availability = v.availability != VehicleAvailabilityEnum.normal.name
            if hidden_by_availability:
                reasons.append(TranslatedString.from_gettext("Fahrzeug ist als nicht verfügbar markiert"))
            # noinspection PyUnresolvedReferences
            distance_vehicle_from_location_meter = v.distance.m
            if v.battery_level_percent is not None and v.battery_level_percent < 0.01:
                range_ok = False
                reasons.append(TranslatedString.from_gettext("Ladezustand ist zu gering"))
            if v.id in bookings_by_vehicle_ids:
                busy_in_timerange = True
                reasons.extend(
                    [TranslatedString.from_gettext("Fahrzeug ist belegt") for b in bookings_by_vehicle_ids[v.id]])
            if distance_vehicle_from_location_meter > distance_cutoff_meter:
                near_enough = False
                reasons.append(TranslatedString.from_gettext(
                    "Fahrzeug ist {distance_m}m, entfernt, was weiter entfernt ist als {distance_cutoff_meter}m.",
                    distance_m=distance_vehicle_from_location_meter,
                    distance_cutoff_meter=distance_cutoff_meter)
                )
            if distance_one_way * 2 > settings.GLOBAL_LIMIT_METER:
                range_ok = False
                reasons.append(TranslatedString.from_gettext(
                    "Distanz des Trips ist mindestens {distance}m und damit mehr als die globale Obergrenze von {limit_km}km.",
                    distance=int(distance_one_way * 2),
                    limit_km=int(settings.GLOBAL_LIMIT_METER / 1000.0)
                ))
            if v.vehicle_type == VehicleType.bike and distance_one_way * 2 > settings.BIKE_LIMIT_METER:
                range_ok = False
                reasons.append(TranslatedString.from_gettext(
                    "Distanz des Trips ist mindestens {distance}m und damit mehr als die Obergrenze von {limit_km}km.",
                    distance=int(distance_one_way * 2),
                    limit_km=int(settings.BIKE_LIMIT_METER / 1000.0)
                ))
            elif v.vehicle_type == VehicleType.scooter and distance_one_way * 2 > settings.SCOOTER_LIMIT_METER:
                range_ok = False
                reasons.append(TranslatedString.from_gettext(
                    "Distanz des Trips ist mindestens {distance}m und damit mehr als die Obergrenze von {limit_km}km.",
                    distance=int(distance_one_way * 2),
                    limit_km=int(settings.SCOOTER_LIMIT_METER / 1000.0)
                ))
            if v.remaining_range_km is not None:
                # Rule out if 2* distance to travel is larger than remaining range

                # logger.debug(
                #     f"VEHICLE {v}: Distance to travel is {distance_one_way*2}m settings.SHARING_DISTANCE_TO_RANGE_PERCENT={settings.SHARING_DISTANCE_TO_RANGE_PERCENT}")
                if distance_one_way*2 > settings.SHARING_DISTANCE_TO_RANGE_PERCENT / 100.0 * v.remaining_range_km * 1000.0:
                    range_ok = False
                    reasons.append(TranslatedString.from_gettext(
                        "Distanz des Trips ist mindestens {distance}m und damit mehr als {percent}% der verbleibenden Reichweite von {range_m}m.",
                        distance=int(distance_one_way*2),
                        percent=int(settings.SHARING_DISTANCE_TO_RANGE_PERCENT),
                        range_m=int(v.remaining_range_km * 1000.0)
                    ))
            maximum_booking_duration_s = None
            # Look for next booking after this time range
            bookings_next = Booking.objects.filter(
                vehicle=v,
                state__in={BookingState.planned, BookingState.started},
                start_time__gte=timerange_from,
            ).order_by('start_time').first()

            if bookings_next:
                maximum_booking_duration_s = (bookings_next.start_time - timerange_from).total_seconds()

            result.append(VehicleAvailability(vehicle=v, near_enough=near_enough, busy_in_timerange=busy_in_timerange,
                                              range_ok=range_ok,
                                              reasons=reasons, distance_m=distance_vehicle_from_location_meter,
                                              maximum_booking_duration_s=maximum_booking_duration_s,
                                              hidden_by_availability=hidden_by_availability))
        return result

    def can_be_unlocked(self, secret: str | None) -> Tuple[bool, TranslatedString]:
        if self.unlock_secret:
            if not secret or secret.strip() != self.unlock_secret:
                return False, TranslatedString.from_gettext("Falscher Entsperr-Code")
        return True, TranslatedString.from_gettext("OK")

    def get_sharingos_vehicle_type(self) -> Literal['ebike', 'ekick'] | None:
        if self.vehicle_type == VehicleType.bike.name:
            return 'ebike'
        elif self.vehicle_type == VehicleType.scooter.name:
            return 'ekick'
        else:
            logger.warning(f"Invalid request for SharingOS vehicle type in: {self}")
            return None

    def unlock(self, user: BackendUser, booking):
        """Caller beware: This will not catch exceptions from underlying functionality! """
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        try:
            if self.provider_name == 'SharingOS':
                client = get_sharingos_client()
                client.unlock(self.provider_id, vehicle_type=self.get_sharingos_vehicle_type())
            elif self.provider_name == 'ICL' and 'Dummy' in self.vehicle_model:
                if 'fail' in self.vehicle_model.lower():
                    logger.info(f"Dummy vehicle '{self}': Simulated FAILURE TO UNLOCK")
                    raise RuntimeError(f"Dummy vehicle '{self}' simulated failure")
                logger.info(f"Dummy vehicle '{self}': Simulated UNLOCKED")
            else:
                raise NotImplementedError(f"Function not implemented for {self.provider_name}/{self.provider_id}")
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(self).id,
                object_id=self.id,
                object_repr=repr(self),
                action_flag=CHANGE,
                change_message=f"Successfully unlocked vehicle {self.vehicle_number} (ID {self.id}) '{self.provider_name}'/'{self.provider_id}'")
            self.last_unlock_at = now
            self.last_unlock_by = user
            self.last_unlock_for_booking = booking
            self.lock_state = VehicleLockState.unlocked
            self.save()
        except:
            logger.exception(
                f"Failed to unlock vehicle ID {self.id} '{self.provider_name}'/'{self.provider_id}'")
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(self).id,
                object_id=self.id,
                object_repr=repr(self),
                action_flag=CHANGE,
                change_message=f"Failed to unlock vehicle {self.vehicle_number} (ID {self.id}) '{self.provider_name}'/'{self.provider_id}'")
            self.lock_state = VehicleLockState.unknown
            self.save()
            raise

    def lock(self, user: BackendUser):
        """Caller beware: This will not catch exceptions from underlying functionality! """
        try:
            if self.provider_name == 'SharingOS':
                client = get_sharingos_client()
                client.lock(self.provider_id, vehicle_type=self.get_sharingos_vehicle_type())
            elif self.provider_name == 'ICL' and 'Dummy' in self.vehicle_model:
                if 'fail' in self.vehicle_model.lower():
                    logger.info(f"Dummy vehicle '{self}': Simulated FAILURE TO LOCK")
                    raise RuntimeError(f"Dummy vehicle '{self}' simulated failure")
                logger.info(f"Dummy vehicle '{self}': Simulated LOCKED")
            else:
                raise NotImplementedError(f"Function not implemented for {self.provider_name}/{self.provider_id}")
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(self).id,
                object_id=self.id,
                object_repr=repr(self),
                action_flag=CHANGE,
                change_message=f"Successfully locked vehicle ID {self.id} '{self.provider_name}'/'{self.provider_id}'")
            self.lock_state = VehicleLockState.locked
            self.save()
        except:
            logger.exception(
                f"Failed to lock vehicle ID {self.id} '{self.provider_name}'/'{self.provider_id}'")
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(self).id,
                object_id=self.id,
                object_repr=repr(self),
                action_flag=CHANGE,
                change_message=f"Failed to lock vehicle ID {self.id} '{self.provider_name}'/'{self.provider_id}'")
            self.lock_state = VehicleLockState.unknown
            self.save()
            raise

@dataclasses.dataclass
class ScorePointResult:
    distance_meter: float
    in_range: bool
    reasons: List[str]
    points: float

class Booking(DirtyFieldsMixin, models.Model):
    # class State(models.TextChoices):
    #     created = 'created', translate_me("Created")
    #     planned = 'planned', translate_me("Planned")
    #     started = 'started', translate_me("Started")
    #     finished = 'finished', translate_me("Finished")
    #     timeout = 'timeout', translate_me("Timeout")

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(BackendUser, on_delete=models.CASCADE)
    trip_mode = models.CharField(max_length=20, choices=OptionType.get_choices())

    state = models.CharField(max_length=20, choices=BookingState.get_choices(), default=BookingState.created)

    from_location = PointField(srid=4326, geography=True, null=True, blank=True)  # WGS84
    from_description = models.CharField(max_length=250, null=True, blank=True)
    to_location = PointField(srid=4326, geography=True, null=True, blank=True)  # WGS84
    to_description = models.CharField(max_length=250, null=True, blank=True)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    planned_start_time = models.DateTimeField(null=True, blank=True)
    planned_end_time = models.DateTimeField(null=True, blank=True)

    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.SET_NULL)
    provider_id = models.CharField(max_length=250, null=True, blank=True,
                                   help_text="Used to store a provider-specific ID usually returned by an earlier trip search")

    trace = LineStringField(srid=4326, null=True, blank=True)

    external_distance_m = models.FloatField(_("Externe Distanz"), help_text=_("Distanz in Metern gemeldet von externer Quelle"),
                                          null=True, blank=True, default=None)
    external_co2e = models.FloatField(_("Externes CO2e"), help_text=_("CO₂e Emissionen gemeldet von externer Quelle"),
                                      null=True,
                                      blank=True)
    score_needs_update = models.BooleanField(_("Set on save to trigger background recalculation of user score"),
                                             default=False)

    class Meta:
        indexes = [
            Index(name='booking_snuu', fields=['score_needs_update'], include=['user'])
        ]
        constraints = [
            CheckConstraint(
                check=Q(start_time__isnull=True) | Q(end_time__isnull=True) | Q(start_time__lte=models.F("end_time")),
                name="start_time_before_end_time",
            )
        ]

    states_force_previous = {
        BookingState.timeout,
        BookingState.canceled,
        BookingState.finished,
    }

    @classmethod
    def queryset_previous(cls, user: BackendUser, when: datetime.datetime):
        return Booking.objects.filter(user=user).filter(Q(start_time__lt=when) | Q(state__in=Booking.states_force_previous))

    @classmethod
    def queryset_next(cls, user: BackendUser, when: datetime.datetime):
        return Booking.objects.filter(user=user).filter(Q(start_time__gte=when) | Q(start_time=None)).exclude(state__in=Booking.states_force_previous)

    def __str__(self):
        return f"Booking {self.id} '{self.trip_mode}' ({self.state}) by '{self.user}' from {self.start_time} to {self.end_time}{' with vehicle ' + str(self.vehicle) if self.vehicle else ''}"

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        dirty = self.get_dirty_fields()
        # NB: On inserts (rather than updates) dirty will contain the initial value - which makes it the same as the model instance value
        is_insert = self.id is None

        # Set marker iff this save does not include changing the marker
        old_score_needs_update = dirty.get('score_needs_update', None)
        if old_score_needs_update is None or old_score_needs_update == False:
            self.score_needs_update = True

        old_state = dirty.get('state', None)
        old_start_time = dirty.get('start_time', None)
        if old_state != self.state or old_start_time != self.start_time or is_insert:
            logger.debug(f"Booking save: state {old_state} -> {self.state}, start_time {old_start_time} -> {self.start_time}")
            # State or start_time changed (or insert is happening)
            if old_state != self.state or is_insert:
                # State changed
                if self.state in {BookingState.started, BookingState.finished, BookingState.timeout, BookingState.canceled}:
                    if not self.start_time:
                        logger.warning(f"Repairing missing start_time to {now} in: {self}")
                        self.start_time = now
                if self.state == BookingState.started:
                    self.start_time = now
                    if self.end_time < self.start_time:
                        self.end_time = self.start_time
                    if is_insert:  # Quick start -> no run through state started
                        self.planned_start_time = self.start_time
                        self.planned_end_time = self.end_time
                elif self.state == BookingState.planned:
                    self.planned_start_time = self.start_time
                    self.planned_end_time = self.end_time
                elif self.state == BookingState.finished:
                    self.end_time = max(now, self.start_time)
                elif self.state in {BookingState.timeout, BookingState.canceled}:
                    self.end_time = self.start_time

        if self.trip_mode != OptionType.sharing:
            self.vehicle = None

        # noinspection PyArgumentList
        super().save(*args, force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

        # to support inserts, save() needs to happen first (to assign PK)
        if old_state != self.state or old_start_time != self.start_time or is_insert:
            if self.state == BookingState.planned and self.start_time:
                # Setup or update start reminder
                m, created = Message.objects.update_or_create(
                    booking=self,
                    purpose=MessagePurpose.booking_start_reminder,
                    defaults={
                        'user': self.user,
                        'title': _("Deine Buchung startet jetzt!"),
                        'sub_title': '',
                        'content': _("Deine Buchung startet jetzt!"),
                        'push_notification_requested': True,
                        'publish_after': self.start_time - datetime.timedelta(minutes=1),
                    }
                )
                if created:
                    logger.debug(f"Setting up start reminder for booking '{self}'")
                else:
                    logger.debug(f"Updating start reminder for booking '{self}'")
            if self.state in {BookingState.created, BookingState.finished, BookingState.timeout, BookingState.canceled}:
                # Remove reminder if it is in the future
                count, deleted_objects = Message.objects.filter(
                    booking=self,
                    purpose=MessagePurpose.booking_start_reminder,
                    publish_after__gt=now,
                ).delete()
                if count:
                    logger.debug(f"Removed start reminder for booking '{self}'")

            if self.state in {BookingState.finished, BookingState.canceled, BookingState.timeout}:
                self.update_wallet()

    @staticmethod
    def get_score_points_static(state: BookingState, distance: float, trip_mode: str, in_range: bool,
                         planned_start_time, planned_end_time, start_time, end_time,
                         description: str|None) -> ScorePointResult:
        distance_km = distance / 1000

        reasons = []

        if state in {BookingState.finished, BookingState.timeout}:

            if in_range:
                factor = {
                    OptionType.car: 1,
                    OptionType.rriveOffer: 1,
                    OptionType.rriveUse: 1,
                    OptionType.pt: 2,
                    OptionType.sharing: 4,
                    OptionType.walk: 7,
                    OptionType.own_bike: 4,
                    OptionType.own_scooter: 4,
                }[OptionType(trip_mode)]
                ratio_actual_to_planned = 1.0
                if planned_start_time and planned_end_time and start_time and end_time:
                    ratio_actual_to_planned = (end_time - start_time) / (planned_end_time - planned_start_time)
                    if ratio_actual_to_planned > 0.9:
                        ratio_actual_to_planned = 1.0
                p = factor * distance_km * ratio_actual_to_planned
                reasons.append(f"{factor} (mode) * {ratio_actual_to_planned:0.2f} (duration ratio) * {distance_km:0.1f}km = {p:0.1f} points"+(f" for {description}" if description else ''))
            else:
                p = 0.0
                reasons.append(f"0 points (neither end was in range of campus)"+(f" for {description}" if description else ''))
        else:
            p = 0.0
            reasons.append(f"0 points (booking not finished or timed out)")
        return ScorePointResult(distance_meter=distance, in_range=in_range, reasons=reasons, points=p)

    def get_score_points(self) -> ScorePointResult:
        return Booking.get_score_points_static(
            BookingState(self.state),
            self.get_distance()[1] or 0.0,
            self.trip_mode,
            self.is_in_campus_range(),
            self.planned_start_time,
            self.planned_end_time,
            self.start_time,
            self.end_time,
            str(self)
        )

    def update_wallet(self):
        unit = WalletEntry.Units.g_CO2e
        if self.state in {BookingState.finished, BookingState.timeout}:
            if self.external_co2e:
                source = 'External source'
                quantity = self.external_co2e
                distance = 0.0
            else:
                source, distance = self.get_distance()
                match source:
                    case 'trace':
                        source = 'Recorded trace'
                    case 'endpoints':
                        source = 'From/to location'
                    case 'external':
                        source = 'External'
                if not distance:
                    source = 'No known distance'
                    quantity = 0
                else:
                    try:
                        if self.trip_mode == 'rriveUse':
                            # We assume riding as a passenger via RRive accounts for half of a solo car ride in emissions.
                            emission = CO2eEmission.objects.get(mode_of_transport='car', per_unit='g/Pkm')
                            quantity = emission.quantity * distance / 1000
                            quantity /= 2
                        else:
                            emission = CO2eEmission.objects.get(mode_of_transport=self.trip_mode, per_unit='g/Pkm')
                            quantity = emission.quantity * distance / 1000
                    except CO2eEmission.DoesNotExist:
                        source = f"No CO2e for mode of transport '{self.trip_mode}' found"
                        quantity = 0

            defaults = {
                'user': self.user,
                'quantity': quantity,
                'source_information': source,
                'booking_state': self.state,
                'trip_mode': self.trip_mode,
                'trip_distance_m': distance,
                'vehicle_type': self.vehicle.vehicle_type if self.vehicle else None,
                'vehicle_model': self.vehicle.vehicle_model if self.vehicle else None,
                'vehicle_number': self.vehicle.vehicle_number if self.vehicle else None,
            }
            logger.info(f"Creating/updating WalletEntry with {defaults}")
            we, created = WalletEntry.objects.update_or_create(
                booking=self,
                wallet=WalletEntry.Wallets.CO2e,
                unit=unit,
                defaults=defaults,
            )
        elif self.state == BookingState.canceled:
            wes = list(WalletEntry.objects.filter(
                booking=self,
                wallet=WalletEntry.Wallets.CO2e,
                unit=unit,
            ))
            for we in wes:
                if wes:
                    logger.info(f"Removing WalletEntry '{we}' since Booking '{self}' has been canceled")
                    we.delete()

    def get_distance(self) -> Tuple[Union[Literal['trace'], Literal['endpoints'], Literal['external'], Literal['none']], float | None]:
        """Returns source as string and distance in meters in a tuple"""
        if self.trace and len(self.trace.coords) >= 2:
            distance = 0.0
            for from_coords, to_coords in itertools.pairwise(self.trace):
                _, _, distance_pair = geod_wgs84.inv(*from_coords, *to_coords)
                distance += distance_pair
            return 'trace', distance
        elif self.external_distance_m is not None:
            return 'external', self.external_distance_m
        elif self.from_location and self.to_location:
            _, _, distance = geod_wgs84.inv(*self.from_location, *self.to_location)
            return 'endpoints', distance
        else:
            return 'none', None

    def is_in_campus_range(self) -> bool:
        """Returns True iff start or destination location is within CAMPUS_RADIUS_METER range of LOCATION_DEFAULT_*"""
        campus = Point(settings.LOCATION_DEFAULT_LON, settings.LOCATION_DEFAULT_LAT, srid=4326)
        if self.from_location and get_distance_meter(self.from_location, campus) <= settings.CAMPUS_RADIUS_METER:
            return True
        if self.to_location and get_distance_meter(self.to_location, campus) <= settings.CAMPUS_RADIUS_METER:
            return True
        return False

    def can_be_unlocked(self, user: BackendUser, when: datetime.datetime | None = None) -> Tuple[
        bool, TranslatedString]:
        if self.user != user:
            return False, TranslatedString.from_gettext("Diese Buchung gehört zu einem anderen Benutzer.")
        if self.state == BookingState.created:
            return False, TranslatedString.from_gettext("Buchung ist zwar angelegt, aber nicht eingeplant worden.")
        elif self.state in {BookingState.finished, BookingState.timeout}:
            return False, TranslatedString.from_gettext("Diese Buchung ist schon abgelaufen.")
        elif self.state not in {BookingState.planned, BookingState.started}:
            return False, TranslatedString.from_gettext("Unerwarteter Buchungsstatus")

        if not when:
            when = datetime.datetime.now(tz=datetime.timezone.utc)
        if when < self.start_time - settings.SHARING_UNLOCK_ALLOWED_BEFORE_START_TIME:
            return False, TranslatedString.from_gettext(
                "Diese Buchung gilt erst ab {start_time}.",
                start_time=self.start_time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %H:%M %z"))
        if when > self.end_time + datetime.timedelta(minutes=60):
            return False, TranslatedString.from_gettext(
                "Diese Buchung gilt nur bis {end_time}.",
                end_time=self.end_time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %H:%M %z"))

        return True, TranslatedString.from_gettext("OK")

    def can_be_locked(self, user: BackendUser, when: datetime.datetime | None = None) -> Tuple[bool, TranslatedString]:
        if not when:
            when = datetime.datetime.now(tz=datetime.timezone.utc)

        if self.user != user:
            return False, TranslatedString.from_gettext("Diese Buchung gehört zu einem anderen Benutzer.")
        current_booking = True
        if self.state not in {BookingState.planned, BookingState.started}:
            current_booking = False

        if when < self.start_time - settings.SHARING_UNLOCK_ALLOWED_BEFORE_START_TIME:
            current_booking = False
        if when > self.end_time + datetime.timedelta(minutes=60):
            current_booking = False

        if current_booking:
            return True, TranslatedString.from_gettext("OK")
        else:
            # Check if last (valid) booking for this vehicle was for user asking to lock
            bookings = Booking.objects.filter(
                vehicle=self.vehicle,
                state__in=[BookingState.planned, BookingState.finished, BookingState.started, BookingState.timeout],
                start_time__lt=when,
            ).order_by('-start_time').all()
            if bookings and bookings[0].user == user:
                return True, TranslatedString.from_gettext("OK")
            else:
                return False, TranslatedString.from_gettext(
                    "Buchung ist abgelaufen und ein anderer Benutzer hatte in der Zwischenzeit eine Buchung.")


class CO2eEmission(models.Model):
    """Calculatory emission of CO2-equivalents (according to AR5 (5. Sachstandsbericht des IPCC))"""
    id = models.BigAutoField(primary_key=True)
    mode_of_transport = models.CharField(max_length=20, choices=OptionType.get_choices())
    per_unit = models.CharField(max_length=20, choices=[('g/Pkm', 'g per person per km')], default='g/Pkm')
    quantity = models.FloatField()

    def __repr__(self):
        return f"<CO2eEmission mode_of_transport='{OptionType[self.mode_of_transport].value}' {self.quantity:0.0f} {self.per_unit}>"

    def __str__(self):
        return f"CO2e emission '{OptionType[self.mode_of_transport].value}'"

    class Meta:
        verbose_name = "CO₂e emission"
        constraints = [
            models.UniqueConstraint(fields=['mode_of_transport', 'per_unit'], name='unique_mp')
        ]


class WalletEntry(models.Model):
    class Wallets(models.TextChoices):
        CO2e = "CO2e", translate_me("CO₂ äquivalent")

    class Units(models.TextChoices):
        g_CO2e = "g CO2e", translate_me("g CO₂ äquivalent")

    id = models.BigAutoField(primary_key=True)
    wallet = models.CharField(_("Wallet"), max_length=20, choices=Wallets.choices, default=Wallets.CO2e)
    user = models.ForeignKey(BackendUser, on_delete=models.SET_NULL, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    booking_state = models.CharField(max_length=20, choices=BookingState.get_choices(), null=True, blank=True,
                                     default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    unit = models.CharField(_("Einheit"), max_length=20, choices=Units.choices, default=Units.g_CO2e)
    quantity = models.FloatField()
    source_information = models.TextField(null=True, blank=True)
    external_co2e = models.FloatField(_("Externes CO₂e"), help_text=_("CO₂e Emissionen gemeldet von externer Quelle"),
                                      null=True, blank=True)
    trip_mode = models.CharField(max_length=20, choices=OptionType.get_choices(), null=True, blank=True, default=None)
    trip_distance_m = models.FloatField(null=True, blank=True, default=None)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.get_choices(), null=True, blank=True,
                                    default=None)
    vehicle_model = models.CharField(max_length=50, null=True, blank=True, default=None)
    vehicle_number = models.CharField(max_length=20, null=True, blank=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['wallet', 'user', 'booking', 'unit'], name='unique_wubu')
        ]

    def get_co2e_reduction_g(self) -> float:
        if self.wallet != WalletEntry.Wallets.CO2e.value:
            return 0.0
        if self.unit != WalletEntry.Units.g_CO2e.value:
            return 0.0
        if not self.trip_distance_m or self.trip_distance_m < 2_000:
            return 0.0
        car_co2e_g_per_km = cache.get('car_co2e_g')
        if car_co2e_g_per_km is None:
            try:
                car_co2e_g_per_km = CO2eEmission.objects.get(mode_of_transport=OptionType.car,
                                                             per_unit='g/Pkm').quantity
                cache.set('car_co2e_g', car_co2e_g_per_km, timeout=60)
            except CO2eEmission.DoesNotExist:
                logger.error(f"Please set CO2eEmission value for 'car' and per_unit 'g/Pkm'.")
                return 0.0
        difference = car_co2e_g_per_km * self.trip_distance_m / 1000.0 - self.quantity
        return max(0.0, difference)

    def __str__(self):
        return f"<WalletEntry id={self.id} wallet={self.wallet} user={self.user} booking={self.booking} unit={self.unit} quantity={self.quantity} source_information={self.source_information}>"


class NewsCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    news_type = models.CharField(max_length=20, choices=NewsType.get_choices(), unique=True)
    more_link_url = models.CharField(_("Link zu einer Webseite mit weiteren oder den gleichen News"), max_length=255, null=True, blank=True)
    more_link_label = models.CharField(_("Beschriftung des Buttons in der App"), max_length=255, null=True, blank=True)


class NewsEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    news_type = models.CharField(max_length=20, choices=NewsType.get_choices(), default=NewsType.campus_news.value)
    sort_order = models.PositiveIntegerField(null=True, blank=True)

    header = models.CharField(translate_me("Überschrift"), max_length=500)
    sub_header = models.CharField(translate_me("Anriss"), max_length=500)
    sub_header2 = models.CharField(translate_me("Anriss")+' 2', max_length=500, default="")
    text = HTMLField()
    image = FilerImageField(verbose_name=translate_me("Bild"), on_delete=models.SET_NULL, null=True, blank=True)
    image_url = models.URLField(help_text=translate_me(
        "URL als Ersatz für das Bild. Wird verwendet, wenn das Bild-Feld leer ist."
    ), blank=True, null=True, max_length=500,)

    publish_from = models.DateTimeField(translate_me("Sichtbar ab"), null=True, blank=True,
                                        help_text=translate_me(
                                            "Eintrag erst ab diesem Zeitpunkt zeigen oder ab sofort, wenn nicht gesetzt"))
    publish_until = models.DateTimeField(translate_me("Sichtbar bis"), null=True, blank=True,
                                         help_text=translate_me(
                                             "Eintrag bis zu diesem Zeitpunkt zeigen oder für immer, wenn nicht gesetzt"))

    external_source = models.CharField(translate_me("Bezeichnung einer externen News-Quelle"), null=True, blank=True, max_length=500)
    external_id = models.CharField(
        translate_me("Externe ID"),
        max_length=100,
        help_text=translate_me("ID des Eintrags bei extern synchronisierten News"),
        blank=True, null=True, db_index=True,
    )
    external_url = models.URLField(
        translate_me("Externe URL"),
        max_length=500,
        help_text=translate_me("URL, unter dem der Artikel außerhalb eingesehen werden kann. Wird bei extern synchronisierten News verwendet."),
        blank=True, null=True, db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"News Entry id={self.id} header={self.header}"

    class Meta:
        ordering = ('-created_at', 'id')


class SupportTextCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    sort_order = models.PositiveIntegerField(blank=True, null=True)
    title = models.CharField(translate_me("Titel"), max_length=200)
    description = models.CharField(translate_me("Beschreibung"), max_length=600, blank=True)

    def __str__(self):
        return f"SupportTextCategory {self.sort_order}: '{self.title}' (id {self.id})"

    class Meta:
        ordering = ('sort_order', 'id')


class SupportTextEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(SupportTextCategory, on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField(db_index=True)
    title = models.CharField(translate_me("Titel"), max_length=200)
    text = models.CharField(translate_me("Untertitel"), max_length=200)
    content = HTMLField(translate_me("Inhalt"))

    entry_name = models.CharField(
        translate_me("Name des Eintrags"),
        max_length=50,
        null=True, blank=True,
        help_text=translate_me("(Technischer) Name für einen Eintrag, der eine spezielle Bedeutung im Frontend hat. Z.B. 'about', 'AGB' usw. Bitte nur bei diesen Einträgen benutzen und sonst leer lassen."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Support text '{self.title}' ({self.id})"

    class Meta:
        ordering = ('category__sort_order', 'category__title', 'sort_order', 'id')


class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(BackendUser, on_delete=models.CASCADE)
    title = models.CharField(translate_me("Titel"), max_length=200)
    sub_title = models.CharField(translate_me("Untertitel"), max_length=200)
    content = models.TextField(translate_me("Inhalt"))
    push_notification_requested = models.BooleanField(default=False,
                                                      help_text=_("Push Notification an registrierte Geräte senden"))
    push_notification_done = models.BooleanField(default=False, help_text=_(
        "Wird gesetzt, nachdem alle registrierten Device Tokens bedient wurden"))
    push_notification_no_later_than = models.DateTimeField(null=True, blank=True, help_text=_(
        "Erstes oder wiederholtes senden von Push Notifications nicht nach diesem Zeitpunkt"))
    push_notification_state = models.JSONField(null=True, blank=True)
    soft_delete = models.BooleanField(default=False, help_text=_("Wird gesetzt, wenn der Benutzer die Message löscht"))
    created_at = models.DateTimeField(auto_now_add=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, default=True)
    purpose = models.CharField(max_length=50, null=True, blank=True, default=None, choices=MessagePurpose.get_choices())
    publish_after = models.DateTimeField(null=True, blank=True, default=None)

    def save(self, *args, **kwargs):
        # dirty = self.get_dirty_fields()
        # old_mobile_number_verified = dirty.get('mobile_number_verified', None)
        # old_mobile_number_is_verified = dirty.get('mobile_number_is_verified', None)
        # if old_mobile_number_verified != self.mobile_number_unverified and self.mobile_number_unverified is not None:
        #     self.mobile_number_is_verified = False
        #     logger.debug(f"User {self}: New unverified mobile number ({self.mobile_number_unverified}) differs from verified number ({old_mobile_number_verified}). mobile_number_is_verified {old_mobile_number_is_verified} -> {self.mobile_number_is_verified}")
        if self.push_notification_requested:
            if self.publish_after:
                self.push_notification_no_later_than = self.publish_after + datetime.timedelta(minutes=5)
            elif not self.push_notification_no_later_than:
                self.push_notification_no_later_than = datetime.datetime.now(
                    tz=datetime.timezone.utc) + datetime.timedelta(minutes=5)
        else:
            self.push_notification_no_later_than = None

        # noinspection PyArgumentList
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message {self.id}: Title '{self.title}' to '{self.user}' created at {self.created_at}"

    class Meta:
        indexes = [
            models.Index(fields=['push_notification_requested', 'push_notification_done'], name='pnr_pnd'),
        ]


class PushNotificationDevice(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(BackendUser, on_delete=models.CASCADE)
    device_model = models.CharField(translate_me("Gerätetyp"), max_length=200, null=True, blank=True)
    push_system = models.CharField(max_length=20, choices=(("apple", "Apple APNS"), ("android", "Android")))
    token = models.CharField("Token", max_length=200)
    state = models.CharField(max_length=20, choices=(
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
    ), default='valid', help_text="""
Tokens are considered valid until sending a notification produces a (permanent) error that indicates the token is
not usable for push notification anymore. Then it is marked as invalid for later removal from the database.
""")
    created_at = models.DateTimeField(auto_now_add=True)
    last_push_attempt_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PushNotificationDevice {self.id} model '{self.device_model}' of user '{self.user.username}'"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'token'], name='user_token'),
        ]


class UserFeedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(BackendUser, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    vote = models.CharField(max_length=20, choices=(
        ('up', 'Up'),
        ('down', 'Down'),
        ('neutral', 'Neutral'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)


class UserImageFeedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    feedback_type = models.CharField(max_length=20, choices=UserImageFeedbackType.get_choices(), default=UserImageFeedbackType.image_proof.value)
    user = models.ForeignKey(BackendUser, on_delete=models.CASCADE)
    image = FilerImageField(verbose_name=translate_me("Bild"), on_delete=models.SET_NULL, null=True, blank=True)
    location = PointField(srid=4326, geography=True, null=True, blank=True)  # WGS84
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User feedback '{self.feedback_type}' id={self.id}"

    class Meta:
        ordering = ('-created_at', '-id')

USER_IMAGE_FEEDBACK_FOLDER_NAME = 'User Image Feedback'


class BackendSyncProgress(models.Model):
    id = models.BigAutoField(primary_key=True)
    sync_key = models.CharField(max_length=50, unique=True)
    sync_value_int = models.BigIntegerField(blank=True, null=True)
    sync_value_timestamp = models.DateTimeField(blank=True, null=True)

class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)

class Configuration(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=50, unique=True)
    value = models.JSONField(encoder=PrettyJSONEncoder)
    schema = models.CharField(
        null=True, blank=True,
        help_text="If set, the dot-delimited python module and class name of the schema to check the value against"
    )

    def __str__(self):
        return f"Configuration '{self.key}'"

    def clean(self):
        if self.schema:
            try:
                schema_class = load_class_from_dotted_path(self.schema)
            except:
                logger.exception(f"Failed loading schema from: {self.schema!r}")
                raise DjangoValidationError(_("Keine passende Klasse gefunden"))
            try:
                schema_class.model_validate(self.value)
            except PydanticValidationError as pve:
                logger.exception(f"Failed validation for {schema_class}: {self.value!r}")
                raise DjangoValidationError(_("Validierung der Daten anhand des Schemas fehlgeschlagen"+': '+str(pve)))

