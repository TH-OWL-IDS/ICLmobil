# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import json
import logging
from dataclasses import dataclass
from typing import Union, Any, Dict

from celery.bin.control import status
from ninja import Schema
from ninja.renderers import BaseRenderer, JSONRenderer
from ninja.responses import NinjaJSONEncoder

logger = logging.getLogger()

class BinaryDataResponse(Schema):
    data: bytes
    mime_type: str


class BinaryRenderer(BaseRenderer):
    def render(self, request, data: Union[Dict, Any], *args, response_status):
        if type(data) == dict and response_status == 200:
            result = data['data']
        else:
            # noinspection PyBroadException
            try:
                result =  json.dumps(data, cls=NinjaJSONEncoder)
            except:
                logger.exception("JSON encoding failed")
                result = repr(data)
        return result
