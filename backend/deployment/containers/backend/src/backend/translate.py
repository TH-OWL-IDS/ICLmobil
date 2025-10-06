# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

import gettext
import logging
import os
from typing import Callable, Optional

logger = logging.getLogger(__name__)

localedir = os.path.join(os.path.dirname(__file__), 'locale')

__translators = {}

LANGUAGE_TO_GETTEXT_LOCALE = {
    'en': 'en_US',
    'de': 'de_DE',
    None: 'en_US',
}

LANGUAGE_TO_SYSTEM_LOCALE = {
    'en': 'en_US.UTF8',
    'de': 'de_DE.UTF8',
    None: 'en_US.UTF8',
}

_reported_translation_hit = set()
_reported_translation_miss = set()


class TranslationFallback(gettext.NullTranslations):
    def gettext(self, msg):
        global _reported_translation_miss
        if msg not in _reported_translation_miss:
            _reported_translation_miss.add(msg)
            logger.info(f"No translation for '{msg}'")
        return msg


class ReportingGNUTranslations(gettext.GNUTranslations, object):
    def __init__(self, *args, **kwargs):
        super(ReportingGNUTranslations, self).__init__(*args, **kwargs)
        self.add_fallback(TranslationFallback())

    def gettext(self, message):
        global _reported_translation_hit
        result = super(ReportingGNUTranslations, self).gettext(message)
        # noinspection PyUnresolvedReferences
        if message in self._catalog and message not in _reported_translation_hit:
            _reported_translation_hit.add(message)
        return result


def get_translator(language: Optional[str] = None) -> Callable[[str], str]:
    lang = LANGUAGE_TO_GETTEXT_LOCALE.get(language, 'de_DE')
    if lang not in __translators:
        __translators[lang] = gettext.translation("messages", localedir=localedir, languages=(lang,), fallback=True,
                                                  class_=ReportingGNUTranslations)
    return __translators[lang].gettext
