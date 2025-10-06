# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import enum
from typing import Callable, List, Tuple, Literal
from django.utils.translation import gettext_lazy as _

RideIcon = Literal['unknown', 'pt', 'scooter', 'bike', 'car', 'walk']


class StrDescriptionEnum(str, enum.Enum):
    def __new__(cls, value: str, description: str):
        obj = super().__new__(cls, value)
        obj._value_ = value
        # obj = enum.Enum.__new__(cls, value)
        obj.description = description
        return obj

    @classmethod
    def get_choices(cls: enum.Enum) -> List[Tuple[str, str]]:
        # noinspection PyTypeChecker
        return [(e.value, e.description) for e in cls]


class PoiType(enum.IntEnum):
    """
    TYPE_UNBEKANNT          = 0
    TYPE_STOP_BUS           = 1
    TYPE_STOP_STRASSENBAHN  = 2
    TYPE_STOP_ZUG           = 3
    TYPE_STOP_AST           = 4
    TYPE_WELL_KNOWN         = 5
    TYPE_OPENSTREETMAP      = 6
    """
    TYPE_UNBEKANNT = 0
    TYPE_STOP_BUS = 1
    TYPE_STOP_STRASSENBAHN = 2
    TYPE_STOP_ZUG = 3
    TYPE_STOP_AST = 4
    TYPE_WELL_KNOWN = 5
    TYPE_OPENSTREETMAP = 6

    @classmethod
    def is_public_transport(cls, poi_type: 'PoiType') -> bool:
        return poi_type in {
            PoiType.TYPE_STOP_BUS,
            PoiType.TYPE_STOP_STRASSENBAHN,
            PoiType.TYPE_UNBEKANNT,
            PoiType.TYPE_STOP_AST,
        }


class OptionType(StrDescriptionEnum):
    """
    pt = 'pt', _('ÖPNV')
    sharing = 'sharing', _('Sharing')
    rriveUse = 'rriveUse', _('RRive als Mitfahrer')
    rriveOffer = 'rriveOffer', _('RRive Mitfahrt anbieten')
    static = 'static', _('Statisches Angebot')
    car = 'car', _('Auto')
    walk = 'walk', _('Fußweg')
    own_bike = 'own_bike', _('Fahrrad')
    own_scooter = 'own_scooter', _('Scooter')
    """
    pt = 'pt', _('ÖPNV')
    sharing = 'sharing', _('Sharing')
    rriveUse = 'rriveUse', _('RRive als Mitfahrer')
    rriveOffer = 'rriveOffer', _('RRive Mitfahrt anbieten')
    static = 'static', _('Statisches Angebot')
    car = 'car', _('Auto')
    walk = 'walk', _('Fußweg')
    own_bike = 'own_bike', _('Fahrrad')
    own_scooter = 'own_scooter', _('Scooter')

    def get_description(self, N_: Callable[[str], str] | None = None) -> str:
        if not N_:
            N_ = lambda x: x
        return N_(self.description)
        # match self.name:
        #     case OptionType.pt.name:
        #         return N_("ÖPNV")
        #     case OptionType.sharing.name:
        #         return N_("Sharing")
        #     case OptionType.rriveUse.name:
        #         return N_("RRive als Mitfahrer")
        #     case OptionType.rriveOffer.name:
        #         return N_("RRive Mitfahrt anbieten")
        #     case OptionType.static.name:
        #         return N_("Statisches Angebot")
        #     case OptionType.car.name:
        #         return N_("Auto")
        #     case _:
        #         return N_("Unbekannt")


class BookingState(StrDescriptionEnum):
    """Expected order of states in the life of a Booking: created -> planned -> started -> finished/timeout/canceled"""
    created = 'created', _("Erzeugt")
    planned = 'planned', _("Geplant")
    started = 'started', _("Gestartet")
    finished = 'finished', _("Abgeschlossen")
    timeout = 'timeout', _("Timeout")
    canceled = 'canceled', _("Storniert")


class VehicleType(StrDescriptionEnum):
    unknown = 'unknown', _("-"),
    bike = 'bike', _('Fahrrad')
    scooter = 'scooter', _('E-Scooter')

    def get_ride_icon(self) -> RideIcon:
        if self == VehicleType.bike:
            return 'bike'
        elif self == VehicleType.scooter:
            return 'scooter'
        else:
            return 'unknown'


class VehicleAvailabilityEnum(StrDescriptionEnum):
    normal = 'normal', _("Normal (sichtbar in Suchen)"),
    hidden = 'hidden', _('Unsichtbar (nicht sichtbar in Suchen)'),


class VehicleLockState(StrDescriptionEnum):
    unknown = 'unknown', _("Unbekannt"),
    locked = 'locked', _('Verriegelt')
    unlocked = 'unlocked', _('Entriegelt')
    failure = 'failure', _("Fehler")


class NewsType(StrDescriptionEnum):
    unknown = 'unknown', _("-"),
    icl_news = 'icl_news', _('ICL News')
    campus_news = 'campus_news', _('Campus News')
    events = 'events', _('Events')
    food_and_drinks = 'food_and_drinks', _('Food & Drinks')


class MessagePurpose(StrDescriptionEnum):
    booking_start_reminder = 'booking_start_reminder', _('Erinnerung an bevorstehende Buchung')


class UserImageFeedbackType(StrDescriptionEnum):
    image_proof = 'image_proof', _('Nachweis über zurückgegebenes Fahrzeug')
