# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from django import template

from backend.enum import OptionType

register = template.Library()

@register.filter
def get_type(value):
    """Returns variable type as a string."""
    return type(value).__name__

@register.filter
def option_type_description(option_type: OptionType):
    return option_type.get_description()

