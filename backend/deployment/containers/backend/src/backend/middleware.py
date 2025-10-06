# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import base64
import logging
import threading
from typing import Union

from asgiref.sync import iscoroutinefunction
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest
from django.utils.decorators import sync_and_async_middleware
from django.utils.deprecation import MiddlewareMixin
import _thread as thread
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class HeaderSessionMiddleware(SessionMiddleware):
    """Alternative to SessionMiddleware which also (prefrentially) uses a session key served
    in the "Authorization" header with scheme "Bearer". This is not validated to confirm to
    RFC6750 even though it uses the same scheme.
    """

    def process_request(self, request):
        session_key: str | None = None
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        if authorization_header and authorization_header.startswith('Bearer '):
            _, token = authorization_header.split('Bearer ', maxsplit=1)
            # noinspection PyBroadException
            try:
                session_key = base64.b64decode(token).decode('utf-8')
            except:
                # logger.debug(f"Failed decoding bearer token: {token}")
                # We also allow non-encoded tokens for easier working in Swagger - even though this is very unusual
                session_key = token
        if not session_key:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.session = self.SessionStore(session_key)


_thread_data = threading.local()


class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_data.request = request
        response = self.get_response(request)
        return response

@sync_and_async_middleware
def global_request_middleware(get_response):
    grm_logger = logging.getLogger(__name__+'.global_request_middleware')


    def __is_path_excluded(request: Union[ASGIRequest, WSGIRequest]):
        # noinspection PyBroadException
        try:
            if request.path.endswith('getAPIStatus'):
                return True
        except:
            pass
        return False

    def process_request(request: Union[ASGIRequest, WSGIRequest]):
        grm_logger.debug(f"Request cookies: {request.COOKIES}")
        if hasattr(request, 'headers'):
            grm_logger.debug(f"Request headers: {request.headers}")
        if hasattr(request, 'META'):
            grm_logger.debug(f"Request META: {request.META}")

    def process_response(request: Union[ASGIRequest, WSGIRequest], response: HttpResponse):
        grm_logger.debug(f"Request cookies: {request.COOKIES}")
        if hasattr(request, 'headers'):
            grm_logger.debug(f"Request headers: {request.headers}")
        if hasattr(request, 'META'):
            grm_logger.debug(f"Request META: {request.META}")

        grm_logger.debug(f"Response headers: {getattr(response, 'headers', None)}")
        # noinspection PyBroadException
        try:
            if isinstance(getattr(request, 'session', None), ASGIRequest):
                grm_logger.debug(f"Response->request {request} session: "+repr({k:v for k,v in request.session.items()}))
        except:
            grm_logger.exception(f"Failed to dump session {request!r} {type(request)}")

    # One-time configuration and initialization goes here.
    if iscoroutinefunction(get_response):

        async def middleware(request):
            # noinspection PyBroadException
            try:
                if not __is_path_excluded(request):
                    process_request(request)
            except:
                grm_logger.exception("Failed processing request")
            response = await get_response(request)
            # noinspection PyBroadException
            try:
                if not __is_path_excluded(request):
                    process_response(request, response)
            except:
                grm_logger.exception("Failed processing response")

            return response

    else:

        def middleware(request):
            # noinspection PyBroadException
            try:
                if not __is_path_excluded(request):
                    process_request(request)
            except:
                grm_logger.exception("Failed processing request")
            response = get_response(request)
            # noinspection PyBroadException
            try:
                if not __is_path_excluded(request):
                    process_response(request, response)
            except:
                grm_logger.exception("Failed processing response")
            return response

    return middleware
