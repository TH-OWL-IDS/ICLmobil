# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

import filer.urls
from filer import views as filer_views
from .settings import FILER_CANONICAL_URL
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin as contrib_admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

from backend import admin as backend_admin
from backend import views
from backend.api_v1.api import api as api_v1
from backend.file_v1 import api as file_v1

urlpatterns = ([
    path("", RedirectView.as_view(url=settings.ROOT_REDIRECT_URL or '/api/v1/docs')),
    path("api/v1/", api_v1.urls),
    path("file/v1/", file_v1.urls),
    path("diagnostics/poi/", views.poi, name="diagnostics-poi"),
    path("diagnostics/trip/", views.trip, name="diagnostics-trip"),
    path("diagnostics/send-sms/", views.send_sms, name="diagnostics-send-sms"),
    path("diagnostics/send-push/", views.send_push, name="diagnostics-send-push"),
    path("diagnostics/rrive-check/", views.rrive_check, name="diagnostics-rrive-check"),
    path("diagnostics/rrive-use/", views.rrive_use, name="diagnostics-rrive-use"),
    path("diagnostics/check-verify/", views.check_verify, name="diagnostics-check-verify"),
    path("diagnostics/sharingos-vehicles/", views.sharingos_vehicles, name="diagnostics-sharingos-check"),
    path("diagnostics/vehicle-timeline/<int:vehicle_id>", views.vehicle_timeline, name="diagnostics-vehicle-timeline"),

    path('default-admin/', contrib_admin.site.urls),
    path('admin-backend/', backend_admin.backend_site.urls),
    re_path(r'^'+FILER_CANONICAL_URL+r'(?P<uploaded_at>[0-9]+)/(?P<file_id>[0-9]+)/$',
      filer_views.canonical,
      name='canonical'),
    path('backend/filer/', include('filer.urls')),
    path('user/email/verify/', views.email_verify, name="backend-email-verify"),
    path('user/account/deletion-request/', views.account_deletion_request, name="backend-user-deletion-request"),
    path('tinymce/', include('tinymce.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
  + static(settings.MEDIA_URL+'public/', document_root=os.path.join(settings.MEDIA_ROOT, 'media', 'public'))
)
