# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import hashlib
import json
import logging
import os
import urllib.parse
from contextlib import nullcontext
from typing import ContextManager, Tuple, List, Set

import pytz
import requests
from django.db import transaction
from pydantic import ValidationError
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from backend.translate import get_translator
from backend.utils import get_lock
from efa.models import PTStop, EfaPointTypes, PTJourney
from django.core.cache import ConnectionProxy

logger = logging.getLogger(__name__)

_ = get_translator()


class EfaClient:
    def __init__(self, efa_endpoint: str, lock: ContextManager | None = None,
                 local_timezone=pytz.timezone('Europe/Berlin'), cache=None,
                 trip_endpoint: str | None=None):
        self.efa_endpoint = efa_endpoint
        self.trip_endpoint = trip_endpoint
        self.cache: ConnectionProxy | None = cache
        self.lock = lock or get_lock('EfaClient', timeout=30)  # We want to avoid hammering on the server by accident
        self.session = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.local_timezone = local_timezone

    def get_trips(self,
                  start_timestamp: datetime.datetime | None = None,
                  from_ptstop_id: str | None = None,
                  from_latitude: float | None = None,
                  from_longitude: float | None = None,
                  to_ptstop_id: str | None = None,
                  to_latitude: float | None = None,
                  to_longitude: float | None = None,
                  static_data_filename: str | None = None,
                  dump_json=False):
        params = {
            "allInterchangesAsLegs": 1,
            "coordOutputDistance": 1,
            "language": "de",
            "coordOutputFormat": "WGS84[dd.ddddd]",
            "outputFormat": "rapidJSON",
            "calcOneDirection": 1,
            "locationServerActive": 1,
            "useRealtime": 0,
            "genC": 0,  # don't generate coordinates
            "genP": 0,  # don't generate paths
            "genMaps": 0,
            "imparedOptionsActive": 1,

            "itOptionsActive": 1,
            "itdTripDateTimeDepArr": "dep",  # dep(arture), arr(ival)
            # "nwlTripMacro": 1,
            "ptOptionsActive": 1,
            "routeType": "LEASTTIME",  # leastinterchange, leastwalking
            "sl3plusTripMacro": 1,
            "trITMOTvalue100": 10,
            "type_destination": 'any',
            "type_notVia": 'any',
            "type_origin": 'any',
            "type_via": 'any',
            "useProxFootSearch": True,
            "useUT": 0,  # unified tickets
        }
        if start_timestamp:
            local_timestamp = start_timestamp.astimezone(self.local_timezone)
            params.update({
                'itdDateDayMonthYear': local_timestamp.strftime('%d.%m.%Y'),
                'itdTime': local_timestamp.strftime('%H:%M'),
            })
        # Coordinate request (MRCV is an MDV-internal coordinate system that does not seem to quite match EPSG:3857)
        # params.update({
        #     "name_destination": "coord:8.89802:52.02568:WGS84[dd.ddddd]",
        #     "name_origin": "coord:8.9040021:52.0193822:WGS84[dd.ddddd]"
        # })
        # BI -> Innovation Spin
        if from_ptstop_id:
            params.update({
                "name_origin": from_ptstop_id
            })
        else:
            params.update({
                "name_origin": f"coord:{from_longitude}:{from_latitude}:WGS84[dd.ddddd]"
            })
        if to_ptstop_id:
            params.update({
                "name_destination": to_ptstop_id
            })
        else:
            params.update({
                "name_destination": f"coord:{to_longitude}:{to_latitude}:WGS84[dd.ddddd]"
            })
        # params.update({
        #     "name_destination": "coord:991331:5194515:MRCV:Lemgo, $UNKNOWN_POINT$:0",
        #     "name_origin": "coord:949182:5194964:MRCV:Bielefeld, $UNKNOWN_POINT$:0"
        # })

        # Geokoordinaten:
        #   https://westfalenfahrplan.de/nwl-efa/XML_TRIP_REQUEST2
        #   ?allInterchangesAsLegs=1
        #   &coordOutputDistance=1
        #   &coordOutputFormat=WGS84[dd.ddddd]
        #   &language=de
        #   &name_destination=coord:991331:5194515:MRCV:Lemgo, $UNKNOWN_POINT$:0
        #   &name_origin=coord:949182:5194964:MRCV:Bielefeld, $UNKNOWN_POINT$:0
        #   &calcOneDirection=1
        #   &locationServerActive=1
        #   &outputFormat=rapidJSON

        #   &convertAddressesITKernel2LocationServer=1
        #   &convertCoord2LocationServer=1
        #   &convertCrossingsITKernel2LocationServer=1
        #   &convertPOIsITKernel2LocationServer=1
        #   &convertStopsPTKernel2LocationServer=1
        #   &genC=1
        #   &genMaps=0
        #   &imparedOptionsActive=1
        #   &inclMOT_10=true
        #   &inclMOT_11=true
        #   &inclMOT_13=true
        #   &inclMOT_14=true
        #   &inclMOT_15=true
        #   &inclMOT_16=true
        #   &inclMOT_17=true
        #   &inclMOT_18=true
        #   &inclMOT_19=true
        #   &inclMOT_1=true
        #   &inclMOT_2=true
        #   &inclMOT_3=true
        #   &inclMOT_4=true
        #   &inclMOT_5=true
        #   &inclMOT_6=true
        #   &inclMOT_7=true
        #   &inclMOT_8=true
        #   &inclMOT_9=true
        #   &includedMeans=checkbox
        #   &itOptionsActive=1
        #   &itdTripDateTimeDepArr=dep
        #   &lineRestriction=400
        #   &nwlTripMacro=1
        #   &ptOptionsActive=1
        #   &routeType=LEASTTIME
        #   &serverInfo=1
        #   &sl3plusTripMacro=1
        #   &trITMOTvalue100=10
        #   &type_destination=any
        #   &type_notVia=any
        #   &type_origin=any
        #   &type_via=any
        #   &useProxFootSearch=true
        #   &useRealtime=1
        #   &useUT=1
        #   &version=10.5.17.3
        if static_data_filename:
            with open(static_data_filename, mode='r') as f:
                data = json.load(f)
        else:
            assert from_ptstop_id or (
                    from_longitude and from_latitude), "Specify either ptstop_id or latitude and longitude"
            assert to_ptstop_id or (to_longitude and to_latitude), "Specify either ptstop_id or latitude and longitude"

            url = self.efa_endpoint + 'XML_TRIP_REQUEST2'
            cache_key = 'efa_client-'+hashlib.md5(
                ('v1-'+repr(url)+repr(params)).encode('utf-8'), usedforsecurity=False
            ).hexdigest()
            if self.cache and self.cache.get(cache_key):
                logger.debug(f"Cache hit for {url}")
                data = json.loads(self.cache.get(cache_key))
            else:
                logger.debug(f"Cache miss for {url}")
                with self.lock:
                    logger.debug(f"Request to '{url}', params: {params}")
                    r = requests.get(url, params=params)
                    r.raise_for_status()
                    data = r.json()
                if self.cache:
                    data_json = json.dumps(data)
                    # noinspection PyBroadException
                    try:
                        self.cache.set(cache_key, data_json)
                    except:
                        logger.exception(f"Failed setting key '{cache_key}' to data length {len(data_json)} Byte starting with: {data_json[:200]}")
                if dump_json:
                    logger.debug("Received JSON: " + json.dumps(data, indent=None))
        try:
            journeys_raw = data.get('journeys', [])
        except:
            logger.exception(f"Failed decoding data for params '{params}' starting with: {repr(data)[:1000]}")
            raise
        journeys = []
        for i, j in enumerate(journeys_raw):
            try:
                journey = PTJourney.model_validate(j)
                journey.source_link_more_information = self.get_source_link(journey, i)
                journeys.append(journey)
            except ValidationError:
                logger.exception(f"Deserialization to PTJourney failed for: {j!r}")

        return journeys

    def get_stops(self, bb_left_upper_lat_lon: Tuple[float, float], bb_right_lower_lat_lon: Tuple[float, float]) -> \
            List[
                PTStop]:
        with self.lock:
            # Alternative Bounding Box: http://server:port/virtuellesVerzeichnis/XML_COORD_REQUEST?XML_COORD_REQUEST?outputFormat=rapidJSON&hideBannerInfo=1&vehSM=BB&vehBB=BB&vehBBLU=11.1:48.6:WGS84[dd.ddddd]&vehBBRL=12.1:47.6:WGS84[dd.ddddd]&vehPId1=1006&vehOpArId1=1
            params = {
                "inclFilter": "1",
                "boundingBox": "",
                "boundingBoxLU": f"{bb_left_upper_lat_lon[1]}:{bb_left_upper_lat_lon[0]}:WGS84[DD.DDDDD]",
                "boundingBoxRL": f"{bb_right_lower_lat_lon[1]}:{bb_right_lower_lat_lon[0]}:WGS84[DD.DDDDD]",
                "coordOutputFormat": "WGS84[dd.ddddd]",
                #                "coord": "8.89802:52.02568:WGS84[DD.DDDDD]",  # center of area to search in
                # "radius": "3000",  # maximum distance in meter
                "type_1": EfaPointTypes.STOP.name,
                # "type_1": "POI_AREA",
                # "type_2": "POI_POINT",
                # "inclPOIH_1": "NK",
                # "inclPOIH_2": "NK",

                "language": "de",
                "outputFormat": "rapidJSON",
            }
            r = requests.get(self.efa_endpoint + 'XML_COORD_REQUEST', params=params)
            ## XML_COORD_REQUEST?=&jsonp=jsonpFn1&boundingBox=&boundingBoxLU=8.613281:52.160455:WGS84[DD.DDDDD]&boundingBoxRL=9.140625:51.944265:WGS84[DD.DDDDD]&language=de&coordOutputFormat=WGS84[DD.DDDDD]&outputFormat=rapidJSON&inclFilter=1&type_1=POI_AREA&type_2=POI_POINT&inclPOIH_1=NK&inclPOIH_2=NK
            r.raise_for_status()
            data = r.json()
            try:
                return [PTStop.model_validate(e) for e in data['locations']]
            except:
                logger.exception(f"Unexpected response format: {repr(data)[:2000]}")
                raise

        # {'version': '10.6.14.22', 'locations': [
        #     {'id': 'de:05766:3680', 'isGlobalId': True, 'name': 'Schlingfeld', 'type': 'stop',
        #      'coord': [5190787.0, 988591.0],
        #      'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'},
        #      'productClasses': [5, 6, 10], 'properties': {'distance': 581, 'STOP_GLOBAL_ID': 'de:05766:3680',
        #                                                   'STOP_NAME_WITH_PLACE': 'Le-Entrup, Schlingfeld',
        #                                                   'STOP_MAJOR_MEANS': '3',
        #                                                   'STOP_MEANS_LIST': '3,8,105,107,100,104',
        #                                                   'STOP_MOT_LIST': '5,6,10', 'STOP_TARIFF_ZONES:owl': '66011'}},
        #     {'id': 'de:05766:2050', 'isGlobalId': True, 'name': 'Entrup', 'type': 'stop',
        #      'coord': [5190444.0, 988808.0],
        #      'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'},
        #      'productClasses': [5, 10],
        #      'properties': {'distance': 633, 'STOP_GLOBAL_ID': 'de:05766:2050', 'STOP_NAME_WITH_PLACE': 'Le-Entrup',
        #                     'STOP_MAJOR_MEANS': '3', 'STOP_MEANS_LIST': '3,8,105,107,100,104', 'STOP_MOT_LIST': '5,10',
        #                     'STOP_TARIFF_ZONES:owl': '66011'}},
        #     {'id': 'de:05766:3668', 'isGlobalId': True, 'name': 'Entruper Krug', 'type': 'stop',
        #      'coord': [5190620.0, 988880.0],
        #      'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'}, 'productClasses': [6],
        #      'properties': {'distance': 743, 'STOP_GLOBAL_ID': 'de:05766:3668',
        #                     'STOP_NAME_WITH_PLACE': 'Le-Entrup, Entruper Krug', 'STOP_MAJOR_MEANS': '3',
        #                     'STOP_MEANS_LIST': '3,105,107,100,104', 'STOP_MOT_LIST': '6',
        #                     'STOP_TARIFF_ZONES:owl': '66011'}},
        #     {'id': 'de:05766:2154', 'isGlobalId': True, 'name': 'Am Kurzen Land', 'type': 'stop',
        #      'coord': [5190899.0, 988885.0],
        #      'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'},
        #      'productClasses': [5, 6, 10], 'properties': {'distance': 878, 'STOP_GLOBAL_ID': 'de:05766:2154',
        #                                                   'STOP_NAME_WITH_PLACE': 'Le-Entrup, Am Kurzen Land',
        #                                                   'STOP_MAJOR_MEANS': '3',
        #                                                   'STOP_MEANS_LIST': '3,8,105,107,100,104',
        #                                                   'STOP_MOT_LIST': '5,6,10',
        #                                                   'STOP_TARIFF_ZONES:owl': '66011'}}]}

    def get_source_link(self, journey: PTJourney, ordinal: int | None) -> str | None:
        if not self.trip_endpoint:
            return None
        return self.build_source_link(
            journey.legs[0].from_location.longitude,
            journey.legs[0].from_location.latitude,
            journey.legs[-1].to_location.longitude,
            journey.legs[-1].to_location.latitude,
            journey.legs[0].from_timestamp,
        )

    def build_source_link(self,
                          from_longitude: float, from_latitude: float,
                          to_longitude: float, to_latitude: float,
                          from_timestamp: datetime.datetime,
                          ):
        formik = {
            'origin': f"coord:{from_longitude}:{from_latitude}:WGS84[dd.ddddd]",
            'destination': f"coord:{to_longitude}:{to_latitude}:WGS84[dd.ddddd]",
        }
        local_timestamp = from_timestamp.astimezone(self.local_timezone)
        local_timestamp -= datetime.timedelta(minutes=5)
        formik.update({
            'itdDateDayMonthYear': local_timestamp.strftime('%d%m%Y'),
            'itdTime': local_timestamp.strftime('%H%M'),
        })

        params = {
            'formik': urllib.parse.urlencode(formik, quote_via=urllib.parse.quote),
            'trip': urllib.parse.quote('multiModalitySelected=bike'),
            'lng': 'de',
            'sharedLink': 'true',
        }
        # Note: Using the ordinal of the search result in the link (e.g. /trip/0 for the first entry)
        # presumably works if the link we construct here yields the same order of results we are coming from.
        # This is evidently not the case even if we ignore the start_time so we don't use the ordinal to avoid
        # linking to a different trip than the one we are coming from.
        #return f"{self.trip_endpoint}{ordinal}?"+urllib.parse.urlencode(params)
        return f"{self.trip_endpoint}?"+urllib.parse.urlencode(params)


def import_efa_stops_as_pois(endpoint, source_type: str, lock: ContextManager | None = None):
    client = EfaClient(efa_endpoint=endpoint, lock=lock)
    # stops = client.get_stops(bb_left_upper_lat_lon=(52.160455, 8.613281), bb_right_lower_lat_lon=(51.944265, 9.140625)) #
    # stops = client.get_stops(bb_left_upper_lat_lon=(52.076130, 8.654480), bb_right_lower_lat_lon=(51.955268, 8.389435))
    stops = client.get_stops(bb_left_upper_lat_lon=(52.266477, 9.555359), bb_right_lower_lat_lon=(51.611195, 7.978821))

    from backend.models import BackendPoi
    identifiers_seen: Set[str] = set()
    db_source_ids_before = set(
        BackendPoi.objects.filter(source_type=source_type).values_list('source_id', flat=True).distinct())
    created_count = 0
    with transaction.atomic():
        pois = [s.to_backend_poi(source_type=source_type) for s in stops]
        BackendPoi.bulk_update_or_create(pois)
        identifiers_seen = set(p.source_id for p in pois)
        # precache_db = BackendPoi.objects.filter(source_type=source_type).all()
        # for s in stops:
        #     poi, created = s.to_backend_poi(source_type=source_type)
        #     if created:
        #         created_count += 1
        #     poi: BackendPoi
        #     identifiers_seen.add(poi.source_id)
        #     poi.save()
        to_be_deleted = db_source_ids_before - identifiers_seen
        # del precache_db
        BackendPoi.objects.filter(source_type=source_type, source_id__in=list(to_be_deleted)).delete()
    db_source_ids_after = set(
        BackendPoi.objects.filter(source_type=source_type).values_list('source_id', flat=True).distinct())
    new_ids = db_source_ids_after - db_source_ids_before
    logger.info(
        f"New set for source_type '{source_type}' has {len(db_source_ids_after)} entries, {len(new_ids)} of those new. {len(to_be_deleted)} from DB not found anymore.")

    # data = {'locations': [{'id': 'de:05766:3680', 'isGlobalId': True, 'name': 'Schlingfeld', 'type': 'stop',
    #                        'coord': [52.050231, 8.880664],
    #                        'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'},
    #                        'productClasses': [5, 6, 10],
    #                        'properties': {'distance': 581, 'STOP_GLOBAL_ID': 'de:05766:3680',
    #                                       'STOP_NAME_WITH_PLACE': 'Le-Entrup, Schlingfeld',
    #                                       'STOP_MAJOR_MEANS': '3',
    #                                       'STOP_MEANS_LIST': '3,8,105,107,100,104',
    #                                       'STOP_MOT_LIST': '5,6,10', 'STOP_TARIFF_ZONES:owl': '66011'}},
    #                       {'id': 'de:05766:2050', 'isGlobalId': True, 'name': 'Entrup', 'type': 'stop',
    #                        'coord': [52.052126, 8.882613],
    #                        'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'},
    #                        'productClasses': [5, 10],
    #                        'properties': {'distance': 633, 'STOP_GLOBAL_ID': 'de:05766:2050',
    #                                       'STOP_NAME_WITH_PLACE': 'Le-Entrup',
    #                                       'STOP_MAJOR_MEANS': '3', 'STOP_MEANS_LIST': '3,8,105,107,100,104',
    #                                       'STOP_MOT_LIST': '5,10',
    #                                       'STOP_TARIFF_ZONES:owl': '66011'}},
    #                       {'id': 'de:05766:3668', 'isGlobalId': True, 'name': 'Entruper Krug', 'type': 'stop',
    #                        'coord': [52.051154, 8.88326],
    #                        'parent': {'id': 'placeID:5766044:5', 'name': 'Entrup (Lemgo)', 'type': 'locality'},
    #                        'productClasses': [6],
    #                        'properties': {'distance': 743, 'STOP_GLOBAL_ID': 'de:05766:3668',
    #                                       'STOP_NAME_WITH_PLACE': 'Le-Entrup, Entruper Krug',
    #                                       'STOP_MAJOR_MEANS': '3',
    #                                       'STOP_MEANS_LIST': '3,105,107,100,104', 'SOP_MOT_LIST': '6',
    #                                       'STOP_TARIFF_ZONES:owl': '66011'}}]}
    # stops = [PTStop.model_validate(d) for d in data['locations']]


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname).1s PID %(process)d  %(pathname)s:%(lineno)d  %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    main_endpoint = 'https://westfalenfahrplan.de/nwl-efa/'
    client = EfaClient(efa_endpoint=main_endpoint, lock=nullcontext())
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    print(client.get_trips(
        static_data_filename=os.path.join(os.path.dirname(__file__), 'xml_trip_request2_example1.json')))
    print(client.get_trips(
        static_data_filename=os.path.join(os.path.dirname(__file__), 'xml_trip_request2_example2.json')))
    # Stop->Stop, Now
    # print(client.get_trips(from_ptstop_id="de:05711:5667", # Mergenthaler Weg, Bielefeld
    #     to_ptstop_id="de:05766:20016", # Lemgo-Lüttfeld
    #     dump_json=True,
    # ))
    print(client.get_trips(
        static_data_filename=os.path.join(os.path.dirname(__file__), 'xml_trip_request2_example3.json')))
    # Now
    print(client.get_trips(
        from_ptstop_id="de:05711:5667",  # Mergenthaler Weg, Bielefeld
        to_ptstop_id="de:05766:20016",  # Lemgo-Lüttfeld
        dump_json=True,
    ))
    pass
    ## This call will only work until first contact with Django models is made. So this is only useful in interactive debugging.
    # import_efa_stops_as_pois(main_endpoint, f"EFA_{main_endpoint}", lock=contextlib.nullcontext())
