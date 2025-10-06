# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import io
import logging
from typing import Optional, Callable, List, Union, Sequence, Dict, Any

from PIL.Image import Image
from django.http import HttpResponse, HttpRequest
from ninja import NinjaAPI, Swagger, Router
from ninja.constants import NOT_SET_TYPE, NOT_SET
from ninja.errors import ValidationError
from ninja.openapi.docs import DocsBase
from ninja.openapi.schema import OpenAPISchema
from ninja.parser import Parser
from ninja.renderers import BaseRenderer, JSONRenderer
from ninja.throttling import BaseThrottle
from ninja.types import DictStrAny, TCallable

from backend.api_v1 import system, user, poi, trip, booking, news, asset

logger = logging.getLogger(__name__)


class PatchedNinjaAPI(NinjaAPI):

    def get_openapi_schema(self, *, path_prefix: Optional[str] = None,
                           path_params: Optional[DictStrAny] = None) -> OpenAPISchema:
        schema = super().get_openapi_schema(path_prefix=path_prefix, path_params=path_params)
        schema['components']['securitySchemes'] = {
            'bearerAuth': {  # arbitrary name for the security scheme
                'type': 'http',
                'scheme': 'bearer',
                'description': 'We allow the session cookie value (which is the session key) to be delivered ' +
                               'as a base64-encoded "Authorization: Bearer ..." token, too. This is comparable to RFC6750. ' +
                               'If present, it takes precedence over the "backendsession" cookie.',
                'bearerFormat': 'base64-encoded session key',  # optional, arbitrary value for documentation purposes
            },
            'cookie': {
                'type': 'apiKey',
                'name': 'backendsession',
                'in': 'cookie',
                'description': 'Same value as the base64-encoded bearer token: session key received after login (but not base64-encoded here)'
            }
        }
        return schema


api = PatchedNinjaAPI(
    title="ICLMobil Backend API",
    version='1.1.44',
    docs=Swagger(),
    urls_namespace='api-1.1.44',
    description="""
Please note that APIs serving non-JSON data are in a parallel namespace /file/v1/. See /file/v1/docs for details.
""",
    openapi_extra={
        "tags": [
            {
                "name": "poi",
                "description": """POI are Points of Interest. They are used for showing "special" places on the map.
POIs can be manually added for "well-known" places like a Mensa or a plaza (`PoiType TYPE_WELL_KNOWN`). 
POIs for public transport stops (ÖPNV Haltestellen) are also automatically managed by the public transport
module (`PoiType TYPE_STOP_*`).

Automatically provisioned POIs are identified by a common `source_type` in the database (not visible through the API).
""",
            },
            {
                "name": "user_public",
                "description": """
Endpoints that are typically used from the frontend for users that are not yet logged in.
                """
            },
            {
                "name": "user",
                "description": """
Endpoints used by regular and administrative users, typically from the frontend and after authentication.
Authorization rules are enforced.
""",
                "externalDocs": {"url": "/documentation/architecture/authorization.md"},
            },
        ]
    }
)

api.add_router('/system/', system.router)
api.add_router('/user/', user.router)
api.add_router('/poi/', poi.router)
api.add_router('/trip/', trip.router)
api.add_router('/booking/', booking.router)
api.add_router('/news/', news.router)
api.add_router('/assets/', asset.router)


@api.exception_handler(ValidationError)
def validation_errors(request, exc: ValidationError):
    logger.warning(f"Validation errors: {exc.errors}")
    return HttpResponse(f"Validation of input failed. Errors: {exc.errors}", status=400)
