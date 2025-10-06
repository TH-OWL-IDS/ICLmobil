# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import logging
from collections import defaultdict

from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from ninja import Router

from backend.api_v1.schemas import NewsListResponse, NewsEntryTranslatedSchema, NewsListResponse2, NewsListCategory
from backend.models import NewsEntry, NewsCategory
from backend.translate import get_translator
from backend.utils import TranslatedString

_ = get_translator()

router = Router()

logger = logging.getLogger(__name__)


@router.get(
    "/list/frontend",
    response={
        200: NewsListResponse,
    },
    summary="DEPRECATED: Please use /list/frontend2 instead. (was: Return list of news entries)",
    description=""" """,
    tags=['news'],
    deprecated=True,
)
def get_news_list(request: HttpRequest):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    data = defaultdict(list)
    # Frontend expects these keys to always be there - empty if no data available
    data['EVENTS'] = []
    data['FOOD_AND_DRINKS'] = []
    data['ICL_NEWS'] = []
    data['CAMPUS_NEWS'] = []

    for entry in NewsEntry.objects \
            .filter(Q(publish_from=None) | Q(publish_from__lte=now)) \
            .filter(Q(publish_until=None) | Q(publish_until__gte=now)) \
            .order_by('sort_order') \
            .all():
        key = entry.news_type.upper()
        if len(data[key]) < settings.NEWS_MAX_ARTICLES_PER_CATEGORY:
            data[key].append(NewsEntryTranslatedSchema.from_news_entry(entry, request))
    return 200, NewsListResponse(root=data)

@router.get(
    "/list/frontend2",
    response={
        200: NewsListResponse2,
    },
    summary="Return list of news entries with additional metdata",
    description=""" """,
    tags=['news'],
)
def get_news_list2(request: HttpRequest):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    entries = defaultdict(list)
    # Frontend expects these keys to always be there - empty if no data available
    entries['EVENTS'] = []
    entries['FOOD_AND_DRINKS'] = []
    entries['ICL_NEWS'] = []
    entries['CAMPUS_NEWS'] = []

    news_category_metadata = {
        nc.news_type.upper(): nc
        for nc in NewsCategory.objects.all()
    }

    for entry in NewsEntry.objects \
            .filter(Q(publish_from=None) | Q(publish_from__lte=now)) \
            .filter(Q(publish_until=None) | Q(publish_until__gte=now)) \
            .order_by('sort_order') \
            .all():
        key = entry.news_type.upper()
        if len(entries[key]) < settings.NEWS_MAX_ARTICLES_PER_CATEGORY:
            entries[key].append(NewsEntryTranslatedSchema.from_news_entry(entry, request))
    nlcs = {}
    for k, e in entries.items():
        metadata = news_category_metadata.get(k)
        nlcs[k] = NewsListCategory(
            entries=e,
            more_link_url=metadata.more_link_url if metadata else None,
            more_link_label=TranslatedString.from_modeltranslation_field(metadata, 'more_link_label') if metadata else None,
        )
    return 200, NewsListResponse2(root=nlcs)

