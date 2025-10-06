# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import json
import os
import random
import string
import sys
import tempfile
from pathlib import Path

import corsheaders.defaults
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from backend.utils import unquoted_env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    print("WARNING: SECRET_KEY was not set and is now randomly chosen!")
    SECRET_KEY = "".join(random.choices(string.ascii_lowercase, k=50))
else:
    print(f"SECRET_KEY first/last char: {SECRET_KEY[0]}...{SECRET_KEY[-1]}")
assert len(SECRET_KEY) > 20

# SECURITY WARNING: don't run with debug turned on in production!
# WARNING: Running with DEBUG=no requires serving STATIC_ROOT and MEDIA_ROOT using e.g. Nginx which is not implemented yet.
DEBUG = os.environ.get('DEBUG', 'yes') == 'yes'
DEBUG_HEADERS = os.environ.get('DEBUG_HEADERS', 'no') == 'yes'

# Application definition

INSTALLED_APPS = [
    # "unfold",  # before django.contrib.admin
    # "unfold.contrib.filters",  # optional, if special filters are needed
    # "unfold.contrib.inlines",  # optional, if special inlines are needed
    # "unfold.contrib.import_export",  # optional, if django-import-export package is used
    # "unfold.contrib.guardian",  # optional, if django-guardian package is used
    # "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    'modeltranslation',
    'unfold.apps.BasicAppConfig',
    "unfold.contrib.forms",  # optional, if special form elements are needed
    'unfold.contrib.import_export',
    'import_export',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django_celery_beat',
    'django_celery_results',
    'django_extensions',
    'django_htmx',
    "crispy_forms",
    "crispy_bootstrap5",
    "django_bootstrap5",
    "corsheaders",
    'easy_thumbnails',
    'filer',
    'tinymce',
    'backend',
]


THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)
FILER_DEBUG = False
FILER_ENABLE_LOGGING = True
FILER_CANONICAL_URL = 'backend/filer/canonical/'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'backend.middleware.HeaderSessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    "backend.middleware.CurrentRequestMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]
if DEBUG_HEADERS:
    MIDDLEWARE.insert(0, "backend.middleware.global_request_middleware")


ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        # 'APP_DIRS': True,
        'OPTIONS': {
            "loaders": [
                "backend.loaders.UnfoldAdminLoader",
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)- 5s %(asctime)s %(process) 3d %(threadName)s %(name)s %(message)s'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,

        },
        'backend': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'services': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'efa_client': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'efa': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'sharingos': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}


WSGI_APPLICATION = 'backend.wsgi.application'

if 'DB_FILENAME' in os.environ:
    print("WARNING: DB_FILENAME not used!")

POSTGRES_BACKEND_USERNAME = os.environ.get('POSTGRES_BACKEND_USERNAME')
POSTGRES_BACKEND_PASSWORD = os.environ.get('POSTGRES_BACKEND_PASSWORD')
if not POSTGRES_BACKEND_PASSWORD or not POSTGRES_BACKEND_USERNAME:
    print("WARNING: Missing POSTGRES_BACKEND_PASSWORD and/or POSTGRES_BACKEND_USERNAME")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        "ENGINE": "django.contrib.gis.db.backends.postgis",  # "django.db.backends.postgresql",
        "NAME": 'backend',
        "USER": POSTGRES_BACKEND_USERNAME,
        "PASSWORD": POSTGRES_BACKEND_PASSWORD,
        "HOST": os.environ.get('BACKEND_DB_HOSTNAME_OVERRIDE', 'db'),  # used for manual testing
        "PORT": "5432",
        "TIME_ZONE": 'UTC',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': DB_FILENAME,
    # }
}

MEMCACHE_HOSTNAME = 'memcached'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
        "LOCATION": f"{MEMCACHE_HOSTNAME}:11211",
        "KEY_PREFIX": "backend-django-",
        "OPTIONS": {
        }
    }
}

TESTING_IN_PROGRESS = os.environ.get('TESTING_IN_PROGRESS')

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 9,
        },
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

AUTH_USER_MODEL = 'backend.BackendUser'

LOGIN_URL = '/admin-backend/login/'

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'de-DE'  # http://www.i18nguy.com/unicode/language-identifiers.html
gettext = lambda s: s
LANGUAGES = (
    ('de', gettext('Deutsch')),
    ('en', gettext('Englisch')),
)

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'backend/static/'

# PA: This is where manage.py collectstatic will copy all our */static/** stuff
# for the web server to pick up and serve. So
# DO NOT put original files in backend/src/static/ but
# DO put original files in e.g. backend/src/backend/static/ !
STATIC_ROOT = os.path.join(BASE_DIR, "static")
print("DEBUG", DEBUG, "DEBUG_HEADERS", DEBUG_HEADERS, "BASE_DIR", BASE_DIR, "STATIC_ROOT", STATIC_ROOT, "STATIC_URL", STATIC_URL)

MEDIA_ROOT = os.path.join(os.environ.get('STORAGE_DIR', '/tmp'), 'media_root')
if 'STORAGE_DIR' not in os.environ:
    print("WARNING: STORAGE_DIR not set! Uploads will vanish on restart!")

MEDIA_URL = '/backend/media/'

FILER_STORAGES = {
    'public': {
        'main': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(MEDIA_ROOT, 'media', 'public', 'filer'),
                'base_url': MEDIA_URL+'public/filer/',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': 'filer_public',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(MEDIA_ROOT, 'media', 'public', 'filer_thumbnails'),
                'base_url': MEDIA_URL+'public/filer_thumbnails/',
            },
        },
    },
    'private': {
        'main': {
            'ENGINE': 'filer.storage.PrivateFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(MEDIA_ROOT, 'media', 'private', 'filer'),
                'base_url': '/smedia/filer/',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': 'filer_public',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PrivateFileSystemStorage',
            'OPTIONS': {
                'location': os.path.join(MEDIA_ROOT, 'media', 'private', 'filer_thumbnails'),
                'base_url': '/smedia/filer_thumbnails/',
            },
        },
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_NAME = 'backendsession'
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = (unquoted_env('CLUSTER_WITH_CERTIFICATES', 'yes') == 'yes')
SESSION_HEADER_NAME = 'Authentication'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

ICON_SVG_LIGHT = os.environ.get('ICON_SVG_LIGHT', 'icon-light.svg')
ICON_SVG_DARK = os.environ.get('ICON_SVG_DARK', 'icon-dark.svg')

#lazy_link =
UNFOLD = {
    "STYLES": [
        lambda request: static("css/unfold-admin.css"),
        "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css",
        #        "https://cdn.jsdelivr.net/npm/ol@v7.2.2/ol.css",
        #        lambda request: static("gis/css/ol3.css"),
    ],
    "SCRIPTS": [
        # "https://cdn.tailwindcss.com?plugins=forms,typography,aspect-ratio,line-clamp,container-queries",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js",
        #        "https://cdn.jsdelivr.net/npm/ol@v7.2.2/dist/ol.js",
        #        lambda request: static("gis/js/OLMapWidget.js"),
    ],
    "SITE_ICON": {
        "light": lambda request: static(ICON_SVG_LIGHT),  # light mode
        "dark": lambda request: static(ICON_SVG_DARK),  # dark mode
    },
    "SIDEBAR": {
        "show_search": False,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Administration"),
                "separator": False,  # Top border
                "collapsible": False,
                "items": [
                    # {
                    #     "title": _("Dashboard"),
                    #     "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                    #     "link": reverse_lazy("backend_admin_site:index"),
                    #     #"badge": "sample_app.badge_callback",
                    #     "permission": lambda request: request.user.is_superuser,
                    # },
                    {
                        "title": _("Benutzer"),
                        "icon": "people",
                        "link": reverse_lazy("backend_admin_site:backend_backenduser_changelist"),
                    },
                    {
                        "title": _("Feedback"),
                        "icon": "communication",
                        "link": reverse_lazy("backend_admin_site:backend_userfeedback_changelist"),
                    },
                    {
                        "title": _("Benutzer Kategorien"),
                        "icon": "groups",
                        "link": reverse_lazy("backend_admin_site:backend_usercategory_changelist"),
                    },
                    {
                        "title": _("News"),
                        "icon": "newspaper",
                        "link": reverse_lazy("backend_admin_site:backend_newsentry_changelist"),
                    },
                    {
                        "title": _("Support-Texte"),
                        "icon": "unknown_document",
                        "link": reverse_lazy("backend_admin_site:backend_supporttextentry_changelist"),
                    },
                    {
                        "title": _("Messages"),
                        "icon": "chat",
                        "link": reverse_lazy("backend_admin_site:backend_message_changelist"),
                    },
                    # {
                    #     "title": _("Bilder"),
                    #     "icon": "photo_library",
                    #     "link": lazy(lambda _: 'javascript:void(window.open('+json.dumps(reverse("admin:filer_folder_changelist"))+', "_blank"));', str),
                    # },
                    {
                        "title": _("POI"),
                        "icon": "location_on",
                        "link": reverse_lazy("backend_admin_site:backend_backendpoi_changelist"),
                    },
                    {
                        "title": _("CO₂e Emissions-Einstellungen"),
                        "icon": "co2",
                        "link": reverse_lazy("backend_admin_site:backend_co2eemission_changelist"),
                    },
                    {
                        "title": _("Buchungen"),
                        "icon": "trip",
                        "link": reverse_lazy("backend_admin_site:backend_booking_changelist"),
                    },
                    {
                        "title": _("Wallet"),
                        "icon": "receipt_long",
                        "link": reverse_lazy("backend_admin_site:backend_walletentry_changelist"),
                    },
                    {
                        "title": _("Fahrzeuge"),
                        "icon": "transportation",
                        "link": reverse_lazy("backend_admin_site:backend_vehicle_changelist"),
                    },
                    {
                        "title": _("Konfiguration"),
                        "icon": "construction",
                        "link": reverse_lazy("backend_admin_site:backend_configuration_changelist"),
                    },
                ],
            },
            {
                "title": _("Diagnose"),
                "separator": True,  # Top border
                "collapsible": False,
                "items": [
                    {
                        "title": _("POI"),
                        "icon": "location_on",  # Supported icon set: https://fonts.google.com/icons
                        "link": lambda _: reverse_lazy("backend_admin_site:diagnostics-public-transport") + '#poi',
                        # "badge": "sample_app.badge_callback",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("SMS/E-Mail/Push Versand"),
                        "icon": "sms",  # Supported icon set: https://fonts.google.com/icons
                        "link": lambda _: reverse_lazy("backend_admin_site:diagnostics-messaging"),  # +'#poi',
                        # "badge": "sample_app.badge_callback",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Trip Suche"),
                        "icon": "manage_search",  # Supported icon set: https://fonts.google.com/icons
                        "link": lambda _: reverse_lazy("backend_admin_site:diagnostics-public-transport") + '#trip',
                        # "badge": "sample_app.badge_callback",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Periodische Tasks"),
                        "icon": "task_alt",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("backend_admin_site:django_celery_beat_periodictask_changelist"),
                        # "badge": "sample_app.badge_callback",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    # {
                    #     "title": _("Crontab"),
                    #     "icon": "schedule",  # Supported icon set: https://fonts.google.com/icons
                    #     "link": reverse_lazy("backend_admin_site:django_celery_beat_crontabschedule_changelist"),
                    #     # "badge": "sample_app.badge_callback",
                    #     "permission": lambda request: request.user.is_superuser,
                    # },
                    {
                        "title": _("RRive"),
                        "icon": "swap_driving_apps",
                        "link": reverse_lazy("backend_admin_site:diagnostics-rrive"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("SharingOS"),
                        "icon": "bike_scooter",
                        "link": reverse_lazy("backend_admin_site:diagnostics-sharingos"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Ergebnisse Hintergrund tasks"),
                        "icon": "task_alt",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("backend_admin_site:django_celery_results_taskresult_changelist"),
                        # "badge": "sample_app.badge_callback",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    # {
                    #     "title": _("Users"),
                    #     "icon": "people",
                    #     "link": reverse_lazy("admin:users_user_changelist"),
                    # },
                ],
            },
        ],
    },
}

CSRF_TRUSTED_ORIGINS = []
ALLOWED_HOSTS = ["127.0.0.1", "127.0.0.1:8000", "localhost", "https://localhost", "localhost:8000", "localhost:5173", "app://localhost"]
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_METHODS = corsheaders.defaults.default_methods

def __add_trusted(name):
    global CSRF_TRUSTED_ORIGINS, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, CORS_ALLOW_ALL_ORIGINS
    if '://' in name:
        schema, name = name.split('://', maxsplit=1)
    else:
        schema = ''
    for part in name, name.split(':', maxsplit=1)[0]:
        if not part in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(part)
    if schema:
        origins = [schema+'://'+name]
    else:
        origins = ['http://' + name]
        if 'HTTPS_PORT' in os.environ and not ':' in name and os.environ['HTTPS_PORT'] != '443':  # noqa
            origins.append('https://' + name + ':' + os.environ['HTTPS_PORT'])
        else:
            origins.append('https://' + name)
    for origin in origins:
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)
        if origin not in CORS_ALLOWED_ORIGINS:
            CORS_ALLOWED_ORIGINS.append(origin)


cto = os.environ.get('CLUSTER_FQDN', 'localhost')  # noqa
__add_trusted(cto)
for to in os.environ.get('ADDITIONAL_TRUSTED_ORIGINS', '').split(','):  # noqa
    if not to:
        continue
    __add_trusted(to)
for host in ALLOWED_HOSTS:
    __add_trusted(host)

CSRF_TRUSTED_ORIGINS = sorted(list(set(CSRF_TRUSTED_ORIGINS)))
CORS_ALLOWED_ORIGINS = sorted(list(set(CORS_ALLOWED_ORIGINS)))

print("CSRF_TRUSTED_ORIGINS", CSRF_TRUSTED_ORIGINS)
print("ALLOWED_HOSTS", ALLOWED_HOSTS)
print("CORS_ALLOWED_ORIGINS", CORS_ALLOWED_ORIGINS)
print("CORS_ALLOW_ALL_ORIGINS", CORS_ALLOW_ALL_ORIGINS)
print("CORS_ALLOW_METHODS", CORS_ALLOW_METHODS)

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = False
CELERY_BROKER_URL = "amqp://guest:guest@rabbitmq:5672/"
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT = False
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "Etc/UTC"

PUBLIC_TRANSPORT_EFA_ENDPOINT = os.environ.get('PUBLIC_TRANSPORT_EFA_ENDPOINT')
PUBLIC_TRANSPORT_TRIP_ENDPOINT = os.environ.get('PUBLIC_TRANSPORT_TRIP_ENDPOINT')
PUBLIC_TRANSPORT_EFA_POI_TYPE = f"EFA_{PUBLIC_TRANSPORT_EFA_ENDPOINT}"

PHOTON_HOST = 'https://photon.komoot.io'

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_API_SID = os.environ.get('TWILIO_API_SID')
TWILIO_API_SECRET = os.environ.get('TWILIO_API_SECRET')
TWILIO_VERIFY_SERVICE_SID = os.environ.get('TWILIO_VERIFY_SERVICE_SID')

SHARING_IGNORE_VEHICLE_FARTHER_THAN_METER = 2000.0
SHARING_DEFAULT_DURATION_SECONDS = 1 * 3600  # only show sharing assets that are available this long after search start time
SHARING_MAXIMUM_DURATION_SECONDS = 4 * 3600
SHARING_DISTANCE_TO_RANGE_PERCENT = 80.0
SHARING_UNLOCK_ALLOWED_BEFORE_START_TIME = datetime.timedelta(minutes=5)

SHARINGOS_ENDPOINT = os.environ.get('SHARINGOS_ENDPOINT', 'https://open-api.sharingos.com')
SHARINGOS_AUTH_PRIVATE_KEY = os.environ.get('SHARINGOS_AUTH_PRIVATE_KEY', '')
SHARINGOS_AUTH_AK = os.environ.get('SHARINGOS_AUTH_AK', '')

LOCATION_DEFAULT_LON = 8.905524
LOCATION_DEFAULT_LAT = 52.016519
CAMPUS_RADIUS_METER = 1_000
WALK_LIMIT_METER = int(os.environ.get('WALK_LIMIT_METER', '15000'))
WALK_SPEED_KMH = 4.5
BIKE_LIMIT_METER = 100_000
SCOOTER_LIMIT_METER = 100_000
GLOBAL_LIMIT_METER = 300_000

APP_NAME = os.environ.get('APP_NAME', 'App name undefined')

EMAIL_FROM_ADDRESS = os.environ.get("EMAIL_FROM_ADDRESS")
EMAIL_OPERATOR_ADDRESSES = [e.strip() for e in os.environ.get("EMAIL_OPERATOR_ADDRESSES", '').split(',')]
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_ECHO_TO_STDOUT = True
SENDGRID_TRACK_CLICKS_HTML = False
SENDGRID_TRACK_CLICKS_PLAIN = False
SENDGRID_TEMPLATE_ID_VERIFY_EMAIL = os.environ.get("SENDGRID_TEMPLATE_ID_VERIFY_EMAIL")
SENDGRID_TEMPLATE_ID_RESET_PASSWORD = os.environ.get("SENDGRID_TEMPLATE_ID_RESET_PASSWORD")
SENDGRID_TEMPLATE_ID_FEEDBACK = os.environ.get("SENDGRID_TEMPLATE_ID_FEEDBACK")

BREVO_API_KEY=os.environ.get("BREVO_API_KEY")
BREVO_TEMPLATE_ID_FEEDBACK=int(os.environ.get("BREVO_TEMPLATE_ID_FEEDBACK") or '-1')
BREVO_TEMPLATE_ID_RESET_PASSWORD=int(os.environ.get("BREVO_TEMPLATE_ID_RESET_PASSWORD") or '-1')
BREVO_TEMPLATE_ID_VERIFY_EMAIL=int(os.environ.get("BREVO_TEMPLATE_ID_VERIFY_EMAIL") or '-1')
# EMAIL_PROVIDER options: brevo, sendgrid
EMAIL_PROVIDER=os.environ.get("EMAIL_PROVIDER", 'brevo')
if EMAIL_PROVIDER == 'sendgrid':
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
EMAIL_SUPPRESS = False  # overridden by tests


PUSH_APNS_TOPIC='de.iclowl.iclmobile'
PUSH_APNS_CERTIFICATE_KEY_PEM=os.environ.get('APNS_CERTIFICATE_WITH_KEY_PEM', '').strip()
PUSH_ANDROID_TITLE='ICL Mobile'
PUSH_ANDROID_PACKAGE_NAME='de.iclowl.iclmobile'
PUSH_ANDROID_GCM_SERVICE_ACCOUNT_JSON=os.environ.get('ANDROID_GCM_SERVICE_ACCOUNT_JSON', '').strip()

RRIVE_GRPC_ENDPOINT = os.environ.get('RRIVE_GRPC_ENDPOINT')

NEWS_EXTERNAL_SYNC_URL = os.environ.get('NEWS_EXTERNAL_SYNC_URL')
NEWS_MAX_ARTICLES_PER_CATEGORY = 100
ROOT_REDIRECT_URL = os.environ.get('ROOT_REDIRECT_URL')


DATA_UPLOAD_MAX_MEMORY_SIZE = 50*1024*1024
