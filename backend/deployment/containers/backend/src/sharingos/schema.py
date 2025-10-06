# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
from enum import Enum
from typing import List, Annotated

import pytz
from pydantic import BaseModel, AfterValidator, Field


class VehicleType(Enum):
    EKICK = 2
    EBIKE = 3


class LockState(Enum):
    CLOSE = 0
    OPEN = 1


class VehicleStatus(Enum):
    LOST_FOREVER = -11
    LOST_STOLEN = -12
    REPAIR_NOT_URGENT = -10
    REPAIR_VAN = -9
    REPAIR_WORKSHOP = -8
    REPAIR_WAREHOUSE = -7
    REPAIR_URGENT = -6
    NORMAL_1 = -1
    NORMAL = 0
    NORMAL_FOLLOW_UP = 1


def int_to_vehicle_type(value: int) -> VehicleType:
    return VehicleType(value)


def int_to_lock_state(value: int) -> VehicleType:
    return VehicleType(value)


def unix_epoch_to_datetime(value: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(value, tz=pytz.UTC)


class VehicleInfo(BaseModel):
    id: int | None = None
    lock_id: str
    latitude: float
    longitude: float
#    msg_time_ts: Annotated[datetime.datetime, AfterValidator(unix_epoch_to_datetime)]
    msg_time_ts: datetime.datetime
    plate_no: str
    qr_code: str
    status: VehicleStatus
    battery: int
    lock_state: LockState
    vehicle_type: VehicleType
    firmware_version: str | None = None
    meters: int | None = None

    class Config:
        use_enum_values = True


error_codes = {
    0: 'Request successful',
    100001: 'The input parameter is incorrect or missing',
    100002: 'Wrong mobile number entered',
    100004: 'The signature parameter(sign) is lost or the verification of signature failed',
    100006: 'Operation (update) failed, please try again later',
    100017: 'An error occurred, please try again later',
    100029: 'Client request rejected',
    210011: 'The information is incomplete',
    210012: 'An error occurred',
    210061: 'Timestamp error (parameter "ts" is valid for more than 5 minutes)',
}


class VehicleListByTypeResponse(BaseModel):
    message: str
    errcode: int
    data: List[VehicleInfo]


class VehicleUnLockResponse(BaseModel):
    message: str
    errcode: int
    data: bool | None = None
