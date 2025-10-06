# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

from backend.models import Booking

logger = logging.getLogger(__name__)
