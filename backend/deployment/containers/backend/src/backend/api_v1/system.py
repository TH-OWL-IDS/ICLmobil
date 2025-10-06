# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import logging
from typing import Iterable

from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from ninja import Router
from pydantic import ValidationError as PydanticValidationError

from backend.api_v1 import schemas
from backend.api_v1.schemas import SupportTextResponse, SupportText, FrontendAppConfig, ErrorResponse
from backend.models import SupportTextEntry, Configuration
from backend.translate import get_translator
from backend.utils import load_class_from_dotted_path

router = Router()

_ = get_translator()

logger = logging.getLogger(__name__)

@router.get("/getAPIStatus", response={200: schemas.APIStatus}, tags=['system'],
            description="Simple test that can be used to see if backend is ready")
def health(request):
    return {"status": "ok"}


def get_supporttext_response(entries: Iterable[SupportTextEntry]) -> SupportTextResponse:
    data = {}
    for language, _ in settings.LANGUAGES:
        data[language] = [
            SupportText(
                title=getattr(st, 'title_'+language) or "",
                text=getattr(st, 'text_'+language) or "",
                content=getattr(st, 'content_'+language) or "",
                category=getattr(st.category, 'title_'+language) or "",
                description=getattr(st.category, 'description_'+language) or "",
                entry_name=st.entry_name,
            )
            for st in entries
        ]
    return SupportTextResponse(by_language=data)

@router.get("/supportTexts", response={200: SupportTextResponse}, tags=['system'],
            summary="Get the list of support texts along with their category information")
def get_support_texts(request: HttpRequest):
    entries = SupportTextEntry.objects.filter(Q(entry_name__isnull=True) | Q(entry_name='')).order_by('category__sort_order', 'category__title', 'sort_order', 'id').all()
    return 200, get_supporttext_response(entries)

@router.get("/specialPages", response={200: SupportTextResponse}, tags=['system'],
            summary="Get the list of special pages. Use field 'entry_name' to distinguish them.")
def get_special_pages(request: HttpRequest):
    entries = SupportTextEntry.objects.exclude(entry_name__isnull=True).exclude(entry_name='').order_by('sort_order', 'id').all()
    return 200, get_supporttext_response(entries)

@router.get("/appConfig", response={200: FrontendAppConfig, 400: ErrorResponse}, tags=['system'],
            summary="Get app config")
def get_app_config(request: HttpRequest):
    config = Configuration.objects.get(key='AppConfig')
    # noinspection PyBroadException
    try:
        obj = FrontendAppConfig.model_validate(config.value)
    except PydanticValidationError as pve:
        logger.exception(f"Failed validation for FrontendAppConfig: {config.value!r}")
        return 400, ErrorResponse(error=_("Validierung der Daten anhand des Schemas fehlgeschlagen"))
    return 200, obj

