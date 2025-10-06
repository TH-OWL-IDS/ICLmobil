# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import concurrent.futures
import datetime
import sys
import hashlib
import json
import logging
from contextlib import nullcontext
from enum import Enum
from typing import ContextManager, Dict, Iterable, List, Literal
import time

import urllib.parse

import pytz
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.cache import ConnectionProxy
from requests.adapters import HTTPAdapter
import urllib3

from backend.models import Vehicle
from backend.models import VehicleType as ModelVehicleType, VehicleLockState as ModelVehicleLockState
from backend.translate import get_translator
from sharingos.schema import VehicleListByTypeResponse, VehicleType, VehicleInfo, LockState, VehicleUnLockResponse

logger = logging.getLogger(__name__)

_ = get_translator()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__threadpool = None

PROVIDER_NAME = "SharingOS"


def get_threadpool() -> concurrent.futures.ThreadPoolExecutor:
    global __threadpool
    if __threadpool is None:
        __threadpool = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="sharingos")
    return __threadpool


class SharingOSClient:
    # Docs: (links received 2025-03-04 via WeChat)
    #   Ebike: https://www.showdoc.com.cn/sharingosebike
    #   Ekick: https://www.showdoc.com.cn/sharingosekick
    def __init__(self, endpoint: str | None = None,
                 private_key: str | None = None, ak: str | None = None,
                 local_timezone=pytz.timezone('Europe/Berlin'), cache=None,
                 vehicle_types: Iterable[VehicleType] | None = None,
                 verify_tls=True,
                 test_mode=False):
        self.endpoint = endpoint or settings.SHARINGOS_ENDPOINT
        self.private_key = private_key or settings.SHARINGOS_AUTH_PRIVATE_KEY
        self.ak = ak or settings.SHARINGOS_AUTH_AK
        self.cache: ConnectionProxy | None = cache
        self.session = requests.Session()
        retries = urllib3.Retry(total=5,
                                backoff_factor=0.1,
                                status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.local_timezone = local_timezone
        self.verify_tls = verify_tls
        self.vehicle_types = vehicle_types or {VehicleType.EKICK, VehicleType.EBIKE}
        self.page_size = 1000
        self.test_mode = test_mode
        self.last_vehicle_lock_state_by_sim_id = {}

    def sign_data(self, data: Dict) -> hashlib.md5:
        # PHP example
        # public function  getSignature (array $allParams): string
        # {
        #     sort($allParams, SORT_STRING);
        #     return md5(implode($allParams)."private_key");
        # }
        # JS example

        # var getSignature = function (postData) {
        #     // Value to array
        #     var postArr = [];
        #     var valueStr = "";
        #     for (var key in postData) {
        #         valueStr = postData[key];
        #         postArr.push(valueStr);
        #     }
        #     // Array sorting
        #     postArr.sort();
        #     // Array to string
        #     var str = "";
        #     for (var key in postArr) {
        #         str += postArr[key];
        #     }
        #     // Add the string
        #     str += "private_key";
        #     // Md5
        #     var md5Str = md5(str);
        #     return md5Str;
        # };

        values_str = [urllib.parse.quote_plus(str(v)) for v in data.values()]
        try:
            values = sorted([str(v).encode('ascii') for v in values_str]) + [self.private_key.encode('ascii')]
        except UnicodeEncodeError:
            logger.warning(
                f"At least one element is not encodable to pure ASCII. Going to assume UTF-8 encoding in the API. This might be wrong and lead to seemingly incorrect signatures! Values were: {values_str!r}")
            values = sorted([str(v).encode('utf-8') for v in values_str]) + [self.private_key.encode('ascii')]
        to_be_hashed = b''.join(values)
        return hashlib.md5(to_be_hashed)

    def lock(self, vehicle_id: str, vehicle_type: Literal['ebike', 'ekick'] | None='ebike'):
        if not vehicle_type:
            logger.warning(f"Defaulting to ekick for vehicle id {vehicle_id}")
            vehicle_type = 'ekick'

        params = {
            't': 'close',
            'ak': self.ak,
            'lang': 'en-US',
            'ts': int(round(time.time())),  # assumed to be unix seconds since the epoch
            'open_id': 'not specified',
            'sim_id': vehicle_id,
            'lng':  1.0,
            'lat': 1.0,
        }
        params['sign'] = self.sign_data(params).hexdigest()
        url = f'{self.endpoint}/open_api/{vehicle_type}.ashx?' + urllib.parse.urlencode(params)
        logger.debug(f"vehicle_lock Request to {url}")
        r = requests.post(url, verify=False)
        assert r.status_code == 200, (r.status_code, r.reason, r.content)

        content = r.content

        try:
            response = VehicleUnLockResponse.model_validate_json(content)
        except:
            logger.exception(f"Decoding response failed: {content}")
            raise
        if response.errcode != 0:
            raise RuntimeError(f"Request was not successful (errcode {response.errcode}). Message: {response.message}")

        if not response.data:
            raise RuntimeError(
                f"Send command failed on remote backend (errcode {response.errcode}). Message: {response.message} Data: {response.data} Body content: {content}")

        logger.debug(f"Lock command to {vehicle_id} was successful")

    def unlock(self, vehicle_id: str, vehicle_type: Literal['ebike', 'ekick'] | None='ebike'):
        if not vehicle_type:
            logger.warning(f"Defaulting to ekick for vehicle id {vehicle_id}")
            vehicle_type = 'ekick'
        params = {
            't': 'open',
            'ak': self.ak,
            'lang': 'en-US',
            'ts': int(round(time.time())),  # assumed to be unix seconds since the epoch
            'open_id': 'not specified',
            'sim_id': vehicle_id,
            'lng':  1.0,
            'lat': 1.0,
        }
        params['sign'] = self.sign_data(params).hexdigest()
        url = f'{self.endpoint}/open_api/{vehicle_type}.ashx?' + urllib.parse.urlencode(params)
        logger.debug(f"vehicle_unlock Request to {url}")
        r = requests.post(url, verify=False)
        assert r.status_code == 200, (r.status_code, r.reason, r.content)

        content = r.content

        try:
            response = VehicleUnLockResponse.model_validate_json(content)
        except:
            logger.exception(f"Decoding response failed: {content}")
            raise
        if response.errcode != 0:
            raise RuntimeError(f"Request was not successful (errcode {response.errcode}). Message: {response.message}")

        if not response.data:
            raise RuntimeError(f"Send command failed on remote backend (errcode {response.errcode}). Message: {response.message} Data: {response.data}")

        logger.debug(f"Unlock command to {vehicle_id} was successful")


    def request_vehicle_info_list_by_type(self, vehicle_type: VehicleType, **global_params) -> List[VehicleInfo]:
        params = global_params.copy()
        params.update({
            'vehicle_type': vehicle_type.value,
        })
        params['sign'] = self.sign_data(params).hexdigest()
        url = f'{self.endpoint}/open_api/vehicle.ashx?' + urllib.parse.urlencode(params)
        # logger.debug(f"vehicle_lock_list Request to {url}")
        r = requests.post(url, verify=False)
        assert r.status_code == 200, (r.status_code, r.reason, r.content)

        content = r.content

        if self.test_mode:
            if vehicle_type == VehicleType.EKICK:
                content = """{
                    "errcode": 0,
                    "message": "ok",
                    "data": [
                        {
                            "lock_id": "867255073020705",
                            "latitude": 47.925454,
                            "longitude": 106.887375,
                            "msg_time_ts": 1720504270,
                            "plate_no": "S0DCC2413C0010",
                            "qr_code": "QR777935",
                            "status": -1,
                            "battery": 0,
                            "lock_state": 0,
                            "vehicle_type": 2,
                            "firmware_version": "",
                            "meters": 1777422
                        },
                        {
                            "id": 1045469,
                            "lock_id": "860470069869364",
                            "latitude": 31.299139,
                            "longitude": 121.515282,
                            "msg_time_ts": 1710485240,
                            "plate_no": "860470069869364",
                            "qr_code": "QR305783",
                            "status": 0,
                            "battery": 41,
                            "lock_state": 0,
                            "vehicle_type": 2
                        }
                    ]
                }"""
            elif vehicle_type == VehicleType.EBIKE:
                content = """{
                    "errcode": 0,
                    "message": "ok",
                    "data": [
                        {
                            "id": 1045247,
                            "lock_id": "88810050030",
                            "latitude": 22.645107,
                            "longitude": 114.083321,
                            "msg_time_ts": 1675057756,
                            "plate_no": "88810050030",
                            "qr_code": "QR910006",
                            "status": 0,
                            "battery": 55,
                            "lock_state": 0,
                            "vehicle_type": 3
                        }
                    ]
                }"""

        response = VehicleListByTypeResponse.model_validate_json(content)
        return response.data

    def get_vehicle_list(self) -> List[VehicleInfo]:
        global_params = {
            'ak': self.ak,
            'lang': 'en-US',
            'time_zone': 'GMT+01',
            'ts': int(round(time.time())),  # assumed to be unix seconds since the epoch
            't': 'vehicle_info_list_by_type',
            'page_size': self.page_size,
        }

        tp = get_threadpool()

        futures = {
            vt: tp.submit(self.request_vehicle_info_list_by_type, vt, **global_params)
            for vt in self.vehicle_types
        }
        vehicles = sum([f.result(timeout=5) for f in futures.values()], [])
        logger.debug(f"SharingOS returned vehicles: {vehicles}")
        return vehicles

    def sync_loop_iteration(self):
        vehicles = self.get_vehicle_list()
        db_vehicles = {
            v.provider_id: v
            for v in
            Vehicle.objects.filter(provider_name=PROVIDER_NAME, provider_id__in=[v.lock_id for v in vehicles]).all()
        }
        for v in vehicles:
            update_parameters = dict(
                battery_level_percent=v.battery,
                location=Point(v.longitude, v.latitude, srid=4326),
                lock_state={
                    LockState.CLOSE.value: ModelVehicleLockState.locked,
                    LockState.OPEN.value: ModelVehicleLockState.unlocked,
                }.get(v.lock_state, ModelVehicleLockState.unknown),
            )
            if v.meters:
                update_parameters['remaining_range_km'] = v.meters / 1000

            if v.lock_id in self.last_vehicle_lock_state_by_sim_id and v.lock_id in db_vehicles:
                if update_parameters['lock_state'] == ModelVehicleLockState.locked:
                    if db_vehicles[v.lock_id].lock_state == ModelVehicleLockState.unlocked:
                        logger.warning(f"SharingOS sync revealed that vehicle '{v.lock_id}' is locked in SharingOS backend but unlocked in our backend")
            self.last_vehicle_lock_state_by_sim_id[v.lock_id] = update_parameters['lock_state']


            if v.lock_id not in db_vehicles:
                db_vehicle = Vehicle.objects.create(
                    vehicle_type={
                        VehicleType.EBIKE.value: ModelVehicleType.bike,
                        VehicleType.EKICK.value: ModelVehicleType.scooter,
                    }.get(v.vehicle_type, ModelVehicleType.unknown),
                    vehicle_model="please update",
                    vehicle_number=v.plate_no or "please update",
                    provider_name=PROVIDER_NAME,
                    provider_id=v.lock_id,
                    **update_parameters,
                )
                logger.info(f"New vehicle from SharingOS: {v} -> {db_vehicle}")
                # db_vehicle.save()
            else:
                db_vehicle = db_vehicles[v.lock_id]
                changed = {}
                for key, value in update_parameters.items():
                    old = getattr(db_vehicle, key, None)
                    if key == 'location':
                        update = abs(old[0] - value[0]) > 0.00001 or abs(old[1] - value[1]) > 0.00001
                    else:
                        update = value != old
                    if update:
                        changed[key] = (old, value)
                        setattr(db_vehicle, key, value)

                if changed:
                    db_vehicle.save()
                    logger.debug(f"Vehicle ID '{db_vehicle.id}' updated: {changed}")



def main():
    client = SharingOSClient()
    print(client.get_vehicle_list())


if __name__ == '__main__':
    main()
