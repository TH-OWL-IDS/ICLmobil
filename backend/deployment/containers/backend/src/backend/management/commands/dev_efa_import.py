# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from django.conf import settings
from django.core.management import BaseCommand

from efa.client import import_efa_stops_as_pois


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_efa_stops_as_pois(settings.PUBLIC_TRANSPORT_EFA_ENDPOINT, settings.PUBLIC_TRANSPORT_EFA_POI_TYPE)
