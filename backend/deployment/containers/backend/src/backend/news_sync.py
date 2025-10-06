# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import logging

import requests
from django.db import transaction

from backend.api_v1.schemas import ExternalNews
from backend.enum import NewsType
from backend.models import NewsEntry

logger = logging.getLogger(__name__)

def news_sync(url: str):
    r = requests.get(url)
    assert r.ok, f"{r.status_code} {r.reason} {r.content} (URL: {url})"
    try:
        data = ExternalNews.model_validate_json(r.content)
    except:
        logger.exception(f"Failed to validate to ExternalNews: {repr(r.content)[:1000]}")
        raise
    for category in data.categories:
        category_id = category.category_id
        if category_id == 'iclmobil':
            category_id = 'icl_news'
        entries = category.entries
        try:
            NewsType(category_id)
        except ValueError:
            logger.warning(f"Ignoring unknown category '{category_id}' with {len(entries)} entries from: {url}")
            continue
        with transaction.atomic():
            NewsEntry.objects.filter(external_source=url, news_type=category_id).delete()
            for k, entry in enumerate(entries):
                data = {
                    'external_source': url,
                    'external_id': entry.id,
                    'external_url': entry.url,
                    'news_type': category_id,
                    'image_url': entry.icon_image_url,
                    'sort_order': k + 1,
                }
                # if category_id == 'events':
                #     mapping = (
                #         ('header', entry.header),
                #         ('sub_header', entry.title),
                #         ('text', entry.text),
                #     )
                # else:
                mapping = (
                    ('header', entry.title),
                    ('sub_header', entry.header),
                    ('sub_header2', entry.sub_header),
                    ('text', entry.text),
                )
                try:
                    for stem, translated_string in mapping:
                        try:
                            if translated_string:
                                items = translated_string.root.items()
                            else:
                                items = ()
                            for lang, text in items:
                                data[stem+'_'+lang] = text
                            data[stem] = data.get(stem+'_de')
                        except AttributeError:
                            logger.warning(f"Failed for stem='{stem}' translated_string='{translated_string}'")
                            raise
                except:
                    logger.warning(f"Entry was: {entry}")
                    raise
                # logger.debug(f"Adding NewsEntry {data}")
                NewsEntry.objects.create(**data)

