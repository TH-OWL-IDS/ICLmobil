# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from backend.models import UserCategory, NewsEntry, Vehicle, SupportTextEntry, SupportTextCategory, NewsCategory


@register(UserCategory)
class UserCategoryTranslation(TranslationOptions):
    fields = ('name', 'description')

@register(NewsCategory)
class NewsCategoryTranslation(TranslationOptions):
    fields = ('more_link_label',)

@register(NewsEntry)
class NewsEntryTranslation(TranslationOptions):
    fields = ('header', 'sub_header', 'sub_header2', 'text')

@register(Vehicle)
class VehicleTranslation(TranslationOptions):
    fields = ('unlock_secret_user_hint', 'user_hint_start', 'user_hint_end')

@register(SupportTextCategory)
class SupportTextCategoryTranslation(TranslationOptions):
    fields = ('title', 'description')

@register(SupportTextEntry)
class SupportTextEntryTranslation(TranslationOptions):
    fields = ('title', 'text', 'content')

