# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import logging
import re
from enum import Enum
from typing import NamedTuple, List, Any

from django.contrib.gis.geos import Point
from pydantic import BaseModel, Field, model_validator, ConfigDict, field_serializer, BeforeValidator
from pydantic_extra_types.coordinate import Coordinate
from typing_extensions import Annotated

from backend.enum import PoiType
from backend.translate import get_translator
from backend.utils import get_distance_meter

logger = logging.getLogger(__name__)

_ = get_translator()

class EfaPointTypes(Enum):
    ANY = "Alle Punkte"
    BUS_POINT = "Steige"
    ENTRANCE = "Eingänge"
    GIS_AREA = "GIS-Gebiet"
    GIS_POINT = "GIS-Punkt"
    INFRASTRUCTURE = "Infrastrukturelemente"
    LINE = "Linien, die über das Straßensegment der übergebenen Koordinate coord fahren"
    POI_AREA = "Flächen-POIs (wichtige Flächen-Punkte)"
    POI_POINT = "Punkt-POIs (wichtige Punkte)"
    STOP = "Haltestellen"
    STREET = "Straßen"


class EfaModeOfTransportValue(BaseModel):
    efa_id: int
    description: str
    poi_type_mapping: PoiType

efa_mot_cache = {}

class EfaModeOfTransport(Enum):
    # (enum value, text, Backend PoiType mapping
    TT_0 = EfaModeOfTransportValue(efa_id=0, description=_("Zug"), poi_type_mapping=PoiType.TYPE_STOP_ZUG)
    TT_1 = EfaModeOfTransportValue(efa_id=1, description=_("S-Bahn"), poi_type_mapping=PoiType.TYPE_STOP_STRASSENBAHN)
    TT_2 = EfaModeOfTransportValue(efa_id=2, description=_("U-Bahn"), poi_type_mapping=PoiType.TYPE_STOP_STRASSENBAHN)
    TT_3 = EfaModeOfTransportValue(efa_id=3, description=_("Stadtbahn"), poi_type_mapping=PoiType.TYPE_STOP_STRASSENBAHN)
    TT_4 = EfaModeOfTransportValue(efa_id=4, description=_("Straßenbahn"), poi_type_mapping=PoiType.TYPE_STOP_STRASSENBAHN)
    TT_5 = EfaModeOfTransportValue(efa_id=5, description=_("Stadtbus"), poi_type_mapping=PoiType.TYPE_STOP_BUS)
    TT_6 = EfaModeOfTransportValue(efa_id=6, description=_("Regionalbus"), poi_type_mapping=PoiType.TYPE_STOP_BUS)
    TT_7 = EfaModeOfTransportValue(efa_id=7, description=_("Schnellbus"), poi_type_mapping=PoiType.TYPE_STOP_BUS)
    TT_8 = EfaModeOfTransportValue(efa_id=8, description=_("Seil-/Zahnradbahn"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)
    TT_10 = EfaModeOfTransportValue(efa_id=10, description=_("AST/Rufbus"), poi_type_mapping=PoiType.TYPE_STOP_AST)
    TT_11 = EfaModeOfTransportValue(efa_id=11, description=_("Schwebebahn"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)
    TT_12 = EfaModeOfTransportValue(efa_id=12, description=_("Flugzeug"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)
    TT_13 = EfaModeOfTransportValue(efa_id=13, description=_("Regionalzug"), poi_type_mapping=PoiType.TYPE_STOP_ZUG)
    TT_14 = EfaModeOfTransportValue(efa_id=14, description=_("Nationaler Zug"), poi_type_mapping=PoiType.TYPE_STOP_ZUG)
    TT_15 = EfaModeOfTransportValue(efa_id=15, description=_("Internationale Zug"), poi_type_mapping=PoiType.TYPE_STOP_ZUG)
    TT_16 = EfaModeOfTransportValue(efa_id=16, description=_("Hochgeschwindigkeitszüge"), poi_type_mapping=PoiType.TYPE_STOP_ZUG)
    TT_17 = EfaModeOfTransportValue(efa_id=17, description=_("Schienenersatzverkehr"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)
    TT_18 = EfaModeOfTransportValue(efa_id=18, description=_("Shuttlezug"), poi_type_mapping=PoiType.TYPE_STOP_ZUG)
    TT_19 = EfaModeOfTransportValue(efa_id=19, description=_("Bürgerbus"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)
    TT_99 = EfaModeOfTransportValue(efa_id=99, description=_("Fußweg"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)
    TT_100 = EfaModeOfTransportValue(efa_id=100, description=_("Fußweg"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)
    TT_UNKNOWN = EfaModeOfTransportValue(efa_id=-1, description=_("Unbekannt"), poi_type_mapping=PoiType.TYPE_UNBEKANNT)

    @staticmethod
    def from_number(efa_id: int) -> 'EfaModeOfTransport':
        global efa_mot_cache
        if not efa_mot_cache:
            efa_mot_cache = {e.value.efa_id: e for e in EfaModeOfTransport}
        return efa_mot_cache.get(efa_id, EfaModeOfTransport.TT_UNKNOWN)

    @staticmethod
    def is_footway(efa_id: int) -> bool:
        return efa_id in {EfaModeOfTransport.TT_99.value.efa_id, EfaModeOfTransport.TT_100.value.efa_id}

EfaModeOfTransport.from_number(0)

class PTLegPointTypeValue(NamedTuple):
    efa_name: str
    name: str


efa_leg_point_type = {}

class PTLegPointType(Enum):
    PT_ADDRESS = PTLegPointTypeValue('address', _("Adresse"))
    PT_PLATFORM = PTLegPointTypeValue('platform', _("Gleis"))
    PT_STOP = PTLegPointTypeValue('stop', _("Haltstelle"))

    @staticmethod
    def from_efa_type(efa_name: str) -> 'PTLegPointTypeValue | None':
        global efa_leg_point_type
        if not efa_leg_point_type:
            efa_leg_point_type = {e.value[0]: e for e in PTLegPointType}
        return efa_leg_point_type.get(efa_name, None)

class PTStop(BaseModel):
    id: str
    name: str
    parent_name: str
    location: Coordinate
    properties: dict
    main_mode_of_transport: EfaModeOfTransport | None = Field(default=None)

    def __str__(self):
        return f"<PTStop {self.id} {self.name} at {self.location} MOT {self.main_mode_of_transport.value if self.main_mode_of_transport else self.main_mode_of_transport    }>"

    @model_validator(mode='before')
    def coord(cls, values):
        # means (of transport), siehe EfaMeansOfTransport
        # Example
        # {'id': 'de:05766:3680', 'isGlobalId': True, 'name': 'Schlingfeld', 'type': 'stop',
        #           'coord': [52.050231, 8.880664],
        #           'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'},
        #           'productClasses': [5, 6, 10], 'properties': {'distance': 581, 'STOP_GLOBAL_ID': 'de:05766:3680',
        #                                                        'STOP_NAME_WITH_PLACE': 'Le-Entrup, Schlingfeld',
        #                                                        'STOP_MAJOR_MEANS': '3',
        #                                                        'STOP_MEANS_LIST': '3,8,105,107,100,104',
        #                                                        'STOP_MOT_LIST': '5,6,10', 'STOP_TARIFF_ZONES:owl': '66011'}}
        values['location'] = Coordinate(latitude=values['coord'][0], longitude=values['coord'][1])
        del values['coord']
        values['parent_name'] = values['parent']['name']
        try:
            mots = values['properties']['STOP_MOT_LIST'].split(',')
            if not mots[0]:
                logger.warning(f"No STOP_MOT_LIST in '{values['properties']}'.")
            else:
                values['main_mode_of_transport'] = EfaModeOfTransport.from_number(int(mots[0]))
        except (KeyError, ValueError):
            logger.warning(f"Unexpected format in: {values}")
        return values

    model_config = ConfigDict(extra='ignore')

    def to_backend_poi(self, source_type: str | None = None) -> 'BackendPoi':
        from backend.models import BackendPoi
        if self.main_mode_of_transport:
            mot_value: EfaModeOfTransportValue = self.main_mode_of_transport.value
            poi_type: PoiType | None = mot_value.poi_type_mapping
        else:
            logger.warning(f"No poi_type: {self} {self.properties}")
            poi_type = None
        return BackendPoi(
            source_type=source_type,
            source_id=self.id,
            name=self.name,
            description=(self.parent_name + ', ' if self.parent_name else "") + self.name,
            poi_type=poi_type,
            location=Point(self.location.longitude, self.location.latitude, srid=4326),
            source_properties=self.properties
        )
        # return BackendPoi.objects.update_or_create(
        #     source_type=source_type,
        #     source_id=self.id,
        #     defaults={
        #         'name': self.name,
        #         'description': (self.parent_name + ', ' if self.parent_name else "") + self.name,
        #         'poi_type': poi_type,
        #         'location': Point(self.location.longitude, self.location.latitude, srid=4326),
        #         'source_properties': self.properties,
        #     }
        # )

def leg_type_serializer(end_type: PTLegPointTypeValue|None) -> str | None:
    if not end_type:
        return end_type
    return end_type.efa_name

def bv_pt_leg_point_type(value: Any) -> Any:
    if isinstance(value, str):
        point_type = PTLegPointType.from_efa_type(value)
        if point_type is not None:
            return point_type
    return value

RE_EFA_NAME_SUFFIXES = re.compile(r', (coord.*|\$[^$]+\$)$') # strip ", coord:8.5311" or ", $UNKNOWN_POINT%$"
class PTLeg(BaseModel):
    mode_of_transport: EfaModeOfTransportValue
    distance_m: int | None = Field(default=None, description="Distance in meters for footpaths")
    pt_line: str | None = Field(default=None, description="Number of PT line only, without mode of transport designation.")
    pt_name: str | None = Field(default=None, description="Name and number of PT line")
    pt_direction: str | None = Field(default=None, description="On PT lines, the direction of the line, typically the last stop in this direction.")

    from_timestamp: datetime.datetime = Field(description="Leg start time")
    to_timestamp: datetime.datetime = Field(description="Leg arrival time")
    duration_s: int = Field(description="Duration in seconds")

    from_type: Annotated[PTLegPointType, BeforeValidator(bv_pt_leg_point_type)]
    from_location: Coordinate
    from_name: str

    to_type: Annotated[PTLegPointType, BeforeValidator(bv_pt_leg_point_type)]
    to_location: Coordinate
    to_name: str

    serializer_from_type = field_serializer('from_type')(leg_type_serializer)
    serializer_to_type = field_serializer('to_type')(leg_type_serializer)

    model_config = ConfigDict(use_enum_values=True)


    @model_validator(mode='before')
    def coord(cls, values):
        def __coord(c: List[float]) -> Coordinate|None:
            if type(c) != list:
                return None
            try:
                # noinspection PyTypeChecker
                return Coordinate(latitude=c[0], longitude=c[1])
            except IndexError:
                return None

        def __clean_name(name: str|None) -> str|None:
            if not name:
                return name
            return RE_EFA_NAME_SUFFIXES.sub('', name)

        if all([e in values for e in ('origin', 'destination', 'transportation')]):
            # EFA XML_TRIP_REQUEST2 rapidJSON format
            values['distance_m'] = values.pop('distance', 0)
            values['duration_s'] = values.pop('duration', 0)
            transportation = values['transportation']
            # noinspection PyBroadException
            try:
                product_class = transportation.get('product', {}).get('class')
                if product_class:
                    values['mode_of_transport'] = EfaModeOfTransport.from_number(product_class).value
                else:
                    values['mode_of_transport'] = EfaModeOfTransport.TT_UNKNOWN.value
            except:
                logger.exception(f"Failed to decode mode_of_transport from: {values}")
                values['mode_of_transport'] = EfaModeOfTransport.TT_UNKNOWN.value
            if values['mode_of_transport'] == EfaModeOfTransport.TT_100.value:
                # footpath
                values['pt_line'] = None
                values['pt_name'] = None
                values['pt_direction'] = None
            else:
                values['pt_line'] = transportation.get('number')
                values['pt_name'] = transportation.get('name')
                values['pt_direction'] = transportation.get('destination', {}).get('name')
            values['from_type'] = PTLegPointType.from_efa_type(values['origin']['type'])
            values['from_location'] = __coord(values['origin']['coord'])
            values['from_name'] = __clean_name(values['origin'].get('name'))
            values['from_timestamp'] = values['origin']['departureTimePlanned']

            values['to_type'] = PTLegPointType.from_efa_type(values['destination']['type'])
            values['to_location'] = __coord(values['destination']['coord'])
            values['to_name'] = __clean_name(values['destination'].get('name'))
            values['to_timestamp'] = values['destination']['arrivalTimePlanned']
        else:
            pass

        return values

class PTJourney(BaseModel):
    duration_s: int = Field(description="Duration in seconds", default=0)
    air_distance_legs_m: float = Field(description="Sum of all air distances between the legs in meters", default=0.0)
    source_link_more_information: str | None = Field(description="Link to source with more information like ticketing", default=None)

    legs: List[PTLeg]

    @model_validator(mode='after')
    def duration_from_legs(self):
        if self.legs:
            self.duration_s = int(round((self.legs[-1].to_timestamp-self.legs[0].from_timestamp).total_seconds()))
        return self

    @model_validator(mode='after')
    def air_distance(self):
        if self.legs:
            distances = []
            for leg in self.legs:
                if leg.from_location and leg.to_location:
                    distance = get_distance_meter(
                        Point(leg.from_location.longitude, leg.from_location.latitude, srid=4326),
                        Point(leg.to_location.longitude, leg.to_location.latitude, srid=4326)
                    )
                    distances.append(distance)
            self.air_distance_legs_m = sum(distances)
        return self




