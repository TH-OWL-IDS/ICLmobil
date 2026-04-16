from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field
from datetime import datetime


class ServerInfo(BaseModel):
    controllerVersion: str
    serverID: str
    virtDir: str
    serverTime: str
    calcTime: float


class SystemMessage(BaseModel):
    type: str
    module: str
    code: int
    text: str
    subType: str


class Parent(BaseModel):
    id: str
    type: str
    name: Optional[str] = None
    isGlobalId: Optional[bool] = None
    disassembledName: Optional[str] = None
    parent: Optional[Parent] = None
    properties: Optional[Properties] = None
    coord: Optional[List[float]] = None
    niveau: Optional[int] = None


class Download(BaseModel):
    type: str
    url: str


class Properties(BaseModel):
    riderCategoryName: Optional[str] = None
    displayGroup: Optional[str] = None
    ticketType: Optional[str] = None
    productID: Optional[str] = None
    validity_start_date: Optional[str] = None
    validity_start_time: Optional[str] = None
    validity_end_date: Optional[str] = None
    validity_end_time: Optional[str] = None
    distExact: Optional[int] = None
    distRounded: Optional[int] = None
    pricePerKM: Optional[float] = None
    priceBasic: Optional[float] = None
    workingPrice: Optional[float] = None
    tariffProductDefault: Optional[List] = None
    tariffProductOption: Optional[List] = None
    journeyDetail: Optional[str] = None
    ticket_available_from: Optional[str] = None
    EAV_Kode: Optional[str] = Field(None, alias="EAV Kode")
    MeldeCode: Optional[str] = None
    WTB_SORTKEY: Optional[str] = None
    GBR_K_TG: Optional[str] = Field(None, alias="GBR-K-TG")
    validity_minutes: Optional[str] = None
    priceLevelCode: Optional[str] = None
    priceLevelPrintText: Optional[str] = None
    priceLevelPublished: Optional[str] = None
    units_per_trip: Optional[str] = None
    number_units: Optional[str] = None
    validityCondition: Optional[ValidityCondition] = None
    numberOfUnits: Optional[int] = None
    totalUnits: Optional[int] = None
    Mitnahme: Optional[str] = None
    travellers_individuals: Optional[str] = None
    GBR_R: Optional[str] = Field(None, alias="GBR-R")
    maxPriceRestrictionDayLimit: Optional[str] = None
    maxPriceRestrictionName: Optional[str] = None
    maxPriceRestrictionPriceLimit: Optional[str] = None
    validityDuration: Optional[str] = None
    stopId: Optional[str] = None
    AREA_NIVEAU_DIVA: Optional[str] = None
    TRACK_ILLUMINATED: Optional[str] = None
    OUTDOOR_TYPE: Optional[Union[str,List[str]]] = None
    FLOOR_LEVEL_CHANGE_DIRECTION: Optional[str] = None
    INDOOR_TYPE: Optional[str] = None
    areaGid: Optional[str] = None
    area: Optional[int] = None  # int? was str
    platform: Optional[Union[str, int]] = None
    zone: Optional[str] = None
    stoppingPointPlanned: Optional[str] = None
    platformName: Optional[str] = None
    georef: Optional[str] = None
    trainName: Optional[str] = None
    trainType: Optional[str] = None
    trainNumber: Optional[str] = None
    mtSubcode: Optional[str] = None
    timetablePeriod: Optional[str] = None
    tripCode: Optional[int] = None
    lineDisplay: Optional[str] = None
    isSTT: Optional[bool] = None
    stopId: Optional[str] = None
    downloads: Optional[List[Download]] = None
    subnet: Optional[str] = None


class Origin(BaseModel):
    isGlobalId: Optional[bool] = None
    id: str
    name: Optional[str] = None
    disassembledName: Optional[str] = None
    type: str
    coord: List[float]
    parent: Optional[Parent] = None
    departureTimePlanned: Optional[datetime] = None
    departureTimeEstimated: Optional[datetime] = None
    properties: Properties
    niveau: Optional[int] = None
    productClasses: Optional[List[int]] = None
    pointType: Optional[str] = None


class Destination(BaseModel):
    name: str
    type: str
    id:  Optional[str] = None
    disassembledName: Optional[str] = None
    coord: List[float]
    niveau: Optional[int] = None
    parent: Optional[Parent] = None
    productClasses: Optional[List[int]] = None
    arrivalTimePlanned: Optional[datetime] = None
    arrivalTimeEstimated: Optional[datetime] = None
    pointType: Optional[str] = None
    isGlobalId: Optional[bool] = None
    coord: Optional[List[float]] = None
    properties: Optional[Properties] = None
    name: Optional[str] = None


class Product(BaseModel):
    class_: Optional[int] = Field(None, alias="class")
    name: str
    iconId: int
    id: Optional[int] = None


class Operator(BaseModel):
    code: Optional[str] = None
    id: str
    name: str


class Transportation(BaseModel):
    product: Product
    properties: Properties
    id: Optional[str] = None
    name: Optional[str] = None
    disassembledName: Optional[str] = None
    number: Optional[str] = None
    description: Optional[str] = None
    operator: Optional[Operator] = None
    destination: Optional[Destination] = None


class StopSequenceItem(BaseModel):
    isGlobalId: Optional[bool] = None
    id: str
    name: str
    type: str
    coord: List[float]
    parent: Parent
    properties: Properties
    departureTimePlanned: Optional[str] = None
    disassembledName: Optional[str] = None
    niveau: Optional[int] = None
    productClasses: Optional[List[int]] = None
    arrivalTimePlanned: Optional[str] = None
    departureTimeEstimated: Optional[str] = None
    pointType: Optional[str] = None
    arrivalTimeEstimated: Optional[str] = None


class Coords(BaseModel):
    d: Optional[float] = None
    z: Optional[int] = None


class PathDescription(BaseModel):
    turnDirection: str
    manoeuvre: str
    name: str
    coord: List[float]
    duration: int
    cumDuration: int
    distance: int
    cumDistance: int
    fromCoordsIndex: int
    toCoordsIndex: int
    skyDirection: Optional[int] = None
    properties: Optional[Properties] = None
    distanceUp: Optional[int] = None
    distanceDown: Optional[int] = None


class Hint(BaseModel):
    content: str
    providerCode: str
    type: str
    properties: Properties


class Zone(BaseModel):
    net: str
    toLeg: int
    fromLeg: int
    neutralZone: str
    zones: Optional[List[List[str]]] = None
    zonesUnited: Optional[List[List[str]]] = None


class Fare(BaseModel):
    tickets: Optional[List[Ticket]] = None
    zones: Optional[List[Zone]] = None


class ElevationSummary(BaseModel):
    minAlt: int
    maxAlt: int
    maxGrad: int
    maxSlope: int
    altDiffUp: int
    distUp: int
    altDiffDw: int
    distDw: int


class FootPathElemItem(BaseModel):
    description: str
    type: str
    levelFrom: int
    levelTo: int
    level: str
    origin: Origin
    destination: Destination


class FootPathInfoItem(BaseModel):
    position: str
    duration: int
    footPathElem: Optional[List[FootPathElemItem]] = None


class Leg(BaseModel):
    duration: Optional[int] = None
    distance: Optional[int] = None
    origin: Origin
    destination: Destination
    transportation: Transportation
    stopSequence: List[StopSequenceItem]
    stopSequence: Optional[List[StopSequenceItem]] = None
    infos: List
    coords: Optional[List[List[Union[float, Coords]]]] = None
    pathDescriptions: Optional[List[PathDescription]] = None
    hints: Optional[List[Hint]] = None
    fare: Optional[Fare] = None
    elevationSummary: Optional[ElevationSummary] = None
    footPathInfo: Optional[List[FootPathInfoItem]] = None


class Area(BaseModel):
    id: int
    name: Optional[str] = None


class RelationKey(BaseModel):
    id: str
    code: str
    name: str
    areas: Optional[List[Area]] = None
    scopeAreas: Optional[List[int]] = None


class ValidityCondition(BaseModel):
    type: str


class Accompany(BaseModel):
    adults: int
    children: int
    animals: int
    bicycles: int
    startTime: int
    endTime: int


class Ticket(BaseModel):
    id: str
    name: str
    comment: str
    URL: str
    currency: str
    priceLevel: str
    priceBrutto: float
    priceNetto: float
    taxPercent: float
    fromLeg: int
    toLeg: int
    net: str
    person: str
    travellerClass: str
    timeValidity: str
    validMinutes: int
    isShortHaul: str
    returnsAllowed: str
    validForOneJourneyOnly: str
    validForOneOperatorOnly: str
    numberOfChanges: int
    nameValidityArea: str
    relationKeys: Optional[List[RelationKey]] = None
    validFrom: Optional[str] = None
    validTo: Optional[str] = None
    properties: Properties
    targetGroups: Optional[List[str]] = None
    accompany: Optional[Accompany] = None


class DaysOfService(BaseModel):
    rvb: str


class Journey(BaseModel):
    rating: Optional[int] = None
    isAdditional: bool
    interchanges: int
    legs: List[Leg]
    fare: Fare
    daysOfService: DaysOfService

    def getDurationMin(self)->float:
        departure = self.legs[0].origin.departureTimePlanned
        arrival = self.legs[-1].destination.arrivalTimePlanned

        duration = arrival - departure
        return duration.total_seconds()/60


class TripResponse(BaseModel):
    serverInfo: ServerInfo
    version: str
    systemMessages: List[SystemMessage]
    journeys:  Optional[List[Journey]] = None


import json

if __name__ == "__main__":

    # file_name = "route-response.json"
    file_name = "latest_trip_response.json"
    with open(file_name) as f:
        data = json.load(f)

    response = TripResponse(**data)
    print(response)
