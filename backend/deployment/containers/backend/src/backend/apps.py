# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
from django.apps import AppConfig
class BackendAppConfig(AppConfig):
    name = 'backend'
    verbose_name = "ICLMobil Backend"

    # noinspection PyUnresolvedReferences
    def ready(self):
        from backend.celery import app as celery_app
        import backend.signals.handlers
