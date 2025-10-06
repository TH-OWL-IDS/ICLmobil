# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import dataclasses
from typing import Any

import ninja.errors
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from ninja.renderers import BaseRenderer

from efa.client import EfaClient


class HttpErrorNotImplemented(ninja.errors.HttpError):
    def __init__(self):
        super().__init__(501, 'Not implemented')

api_efa_client = EfaClient(efa_endpoint=settings.PUBLIC_TRANSPORT_EFA_ENDPOINT, cache=cache,
                           trip_endpoint=settings.PUBLIC_TRANSPORT_TRIP_ENDPOINT)