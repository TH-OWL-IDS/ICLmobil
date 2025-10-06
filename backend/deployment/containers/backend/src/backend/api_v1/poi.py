# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import hashlib
import logging
import pprint
from typing import List, Tuple

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Q
from django.http import HttpRequest
from ninja import Router
from pyphoton import Photon
from pyphoton.models import Location

from backend.api_v1.authz import can_administer_poi
from backend.api_v1.schemas import TokenNotValidResponse, ErrorResponse, MsgResponse, Poi, CreatePoiRequest, \
    PoiSearchResponse
from backend.enum import PoiType
from backend.models import BackendUser, BackendPoi
from backend.utils import TranslatedString, get_subrequest_threadpool, get_distance_meter

router = Router()

logger = logging.getLogger(__name__)


@router.post("/create", response={
    200: Poi,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             tags=['poi'])
def post_poi_create(request: HttpRequest, data: CreatePoiRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_poi(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    poi = BackendPoi(name=data.name, description=data.description,
                     location=Point(data.longitude, data.latitude))
    poi.save()

    return 200, Poi.from_django(poi)


@router.post("/update", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             tags=['poi'])
def post_poi_update(request: HttpRequest, data: Poi):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_poi(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        poi = BackendPoi.objects.get(id=int(data.poiID))
    except (ValueError, BackendUser.DoesNotExist):
        return 404, ErrorResponse(error=f"No POI with ID '{data.poiID}'")
    poi.name = data.name
    poi.description = data.description
    poi.location = Point(data.longitude, data.latitude)
    poi.save()

    return 200, MsgResponse(msg='OK')


@router.get("/list",
            response={200: List[Poi], },
            tags=['poi'],
            summary="Returns a list of local POIs sorted by distance to the `near_latitude`/`near_longitude` parameters with shortest distance first.")
def get_poi_list(request: HttpRequest,
                 near_latitude: float = 52.0177405,
                 near_longitude: float = 8.9045151,
                 limit: int = 100,
                 offset: int = 0,
                 # exclude_poi_types: List[PoiType] | None = None,
                 # only_poi_types: List[PoiType] | None = None
                 ):
    query = BackendPoi.objects
    # if only_poi_types:
    #     query = query.filter(poi_type__in=only_poi_types)
    # if exclude_poi_types:
    #     query = query.exclude(poi_type__in=exclude_poi_types)
    query = query.annotate(
        distance=Distance('location', Point(near_longitude, near_latitude, srid=4326), spheroid=True))
    query = query.order_by('distance')
    query = query.all()[offset:offset + limit]

    return 200, [Poi.from_django(p) for p in query]


@router.delete("/delete", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
               tags=['poi'])
def delete_poi_(request: HttpRequest, poiID: str):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_poi(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        poi = BackendPoi.objects.get(id=int(poiID))
    except (ValueError, BackendUser.DoesNotExist):
        return 404, ErrorResponse(error=f"No POI with ID '{poiID}'")
    poi.delete()

    return 200, MsgResponse(msg='OK')


@router.get("/search",
            response={200: PoiSearchResponse},
            tags=['poi'],
            summary="Searches a) the local POIs and b) an external Photon geocoder for POIs matching a search string. "
                    "Search string must be at least 3 characters long - otherwise an empty result is returned. "
                    "Returns list of local POIs sorted by distance to the `near_latitude`/`near_longitude` parameters with shortest distance first.")
def get_poi_search(request: HttpRequest,
                   near_latitude: float = 52.0177405,
                   near_longitude: float = 8.9045151,
                   search_query: str = None,
                   limit: int = 100,
                   # exclude_poi_types: List[PoiType] | None = None,
                   # only_poi_types: List[PoiType] | None = None
                   ):
    language = request.LANGUAGE_CODE or 'de'
    return _poi_search(near_latitude, near_longitude, search_query, language, limit)


def _poi_search(near_latitude: float, near_longitude: float, search_query: str, language: str, limit: int) -> Tuple[
    int, PoiSearchResponse]:
    if not search_query or len(search_query) < 3:
        return 200, PoiSearchResponse(pois=[], warnings=[
            TranslatedString.from_gettext("Suchbegriff ist zu kurz")
        ])
    warnings = []

    tp = get_subrequest_threadpool()
    photon = Photon(host=settings.PHOTON_HOST)
    args = (search_query,)
    near = Point(near_longitude, near_latitude, srid=4326)
    kwargs = {
        'limit': limit,
        'language': language,
        'latitude': near_latitude,
        'longitude': near_longitude,
        # 'osm_tags', [], # https://github.com/komoot/photon#filter-results-by-tags-and-values
    }
    future_photon = tp.submit(photon.query, *args, **kwargs)

    offset = 0
    query = BackendPoi.objects
    # if only_poi_types:
    #     query = query.filter(poi_type__in=only_poi_types)
    # if exclude_poi_types:
    #     query = query.exclude(poi_type__in=exclude_poi_types)
    query = query.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    query = query.annotate(
        distance=Distance('location', Point(near_longitude, near_latitude, srid=4326), spheroid=True))
    query = query.order_by('distance')
    query = query.all()[offset:offset + limit]
    from_django = [Poi.from_django(p) for p in query]

    # from django.contrib.gis.geos import Point

    from_osm: List[Poi] = []
    # noinspection PyBroadException
    try:
        result: List[Location] = future_photon.result(timeout=5)
        for l in result:
            if 'osm_id' in l.__dict__:
                # noinspection PyUnresolvedReferences
                poi_id = 'OSM_'+str(l.osm_id)
            else:
                # noinspection PyUnresolvedReferences
                poi_id = 'OSM_' + hashlib.md5(f"{l.longitude}_{l.latitude}_{l.name}".encode('utf-8')).hexdigest()
            # noinspection PyUnresolvedReferences
            description = [getattr(l, 'osm_value', '').replace(';', ', ').title(), getattr(l, 'city', '')]
            description = [d for d in description if d]
            # noinspection PyUnresolvedReferences
            from_osm.append(Poi(
                poiID=poi_id,
                poiType=PoiType.TYPE_OPENSTREETMAP,
                name=l.name,
                description=", ".join(description),
                latitude=l.latitude,
                longitude=l.longitude,
                distance_meter=get_distance_meter(near, Point(l.longitude, l.latitude, srid=4326)),
                osm_data={k: str(v) for k, v in l.__dict__.items()},
            ))
    except:
        logger.exception(f"Photon request failed for {args} {kwargs}")
        warnings.append(TranslatedString.from_gettext("Fehler beim Abruf von OpenStreetMap-POIs"))

    merged = sorted(from_osm + from_django, key=lambda x: x.distance_meter)[:limit]

    return 200, PoiSearchResponse(pois=merged, warnings=warnings)
