# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import logging
from dataclasses import dataclass

from django.http import HttpResponse
from ninja import NinjaAPI, Swagger
from ninja.errors import ValidationError
from ninja.renderers import BaseRenderer

from backend.file_v1.user import router
from backend.file_v1.utils import BinaryRenderer

logger = logging.getLogger(__name__)

api = NinjaAPI(
    title="ICLMobil Files API",
    version='1.0.0',
    docs=Swagger(),
    urls_namespace='file-1.0.0',
    renderer=BinaryRenderer(),
)

api.add_router('/user/', router)

# @api.exception_handler(ValidationError)
# def validation_errors(request, exc: ValidationError):
#     logger.warning(f"Validation errors: {exc.errors}")
#     return HttpResponse(f"Validation of input failed. Errors: {exc.errors}", status=422)
