# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import concurrent.futures
import hashlib
import importlib
import inspect
import keyword
import logging
import os
import random
import re
import traceback
from typing import List, Dict

import filelock
import pylibmc
import sib_api_v3_sdk
import sib_api_v3_sdk.rest
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.mail import EmailMessage
from django.utils.text import slugify
from pydantic import RootModel, BaseModel
from pyproj import Geod

from google.protobuf import message as protobuf_message

from backend.translate import get_translator

regexp = re.compile('^[\'"]?(.*)[\'"]$')

logger = logging.getLogger(__name__)

def unquoted_env(variable_name, default=""):
    return regexp.sub('\\1', os.environ.get(variable_name, default))

__mc_client = None
def get_mc_client():
    global __mc_client
    if __mc_client is None:
        __mc_client = pylibmc.Client(['memcached'], binary=True)  # settings.MEMCACHE_HOSTNAME
    return __mc_client

def get_lock(name: str, **kwargs) -> filelock.BaseFileLock:
    lock_filename = os.path.join(os.environ['LOCK_DIR'], slugify(name)[:100]+'_'+hashlib.md5(name.encode('utf-8')).hexdigest()+'.lock')
    return filelock.FileLock(lock_filename, **kwargs)

def twilio_setup_problems() -> List[str]:
    problems = []
    for key in 'TWILIO_API_SID', 'TWILIO_API_SECRET', 'TWILIO_VERIFY_SERVICE_SID':
        value = getattr(settings, key)
        if not value and not value == False:
            problems.append(f"Expected setting '{key}' missing. Check environment variables from .env file!")
    return problems

def email_setup_problems() -> List[str]:
    problems = []
    expected_settings = ['EMAIL_FROM_ADDRESS', 'EMAIL_OPERATOR_ADDRESSES']
    if settings.EMAIL_PROVIDER == 'sendgrid':
        expected_settings.extend([key for key in dir(settings) if key.startswith("SENDGRID_")])
    elif settings.EMAIL_PROVIDER == 'brevo':
        expected_settings.extend([key for key in dir(settings) if key.startswith("BREVO_")])
    else:
        problems.append(f"Unknown EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
    logger.debug(f"Considering these settings keys for setup check: {expected_settings}")
    for key in expected_settings:
        if not hasattr(settings, key):
            problems.append(f"Missing setting {key}")
            continue
        value = getattr(settings, key)
        if not value:
            problems.append(f"Expected setting '{key}' missing. Check environment variables from .env file!")
    if settings.EMAIL_PROVIDER == 'brevo':
        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = settings.BREVO_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            result: sib_api_v3_sdk.GetSmtpTemplateOverview = api_instance.get_smtp_template(settings.BREVO_TEMPLATE_ID_RESET_PASSWORD)
            logger.info(f"Brevo diagnostics returned template name: {result.name}")
        except Exception as e:
            problems.append(f"Testing Brevo API access failed: {traceback.format_exception(e)}")

    return problems

def generate_verification_code() -> str:
    return ''.join(random.choice('0123456789') for _ in range(6))

def get_distance_meter(from_location_srid4326: Point, to_location_srid4326: Point) -> float:
    assert from_location_srid4326.srid == 4326, "Point SRID must be 4326"
    assert to_location_srid4326.srid == 4326, "Point SRID must be 4326"
    _, _, distance = geod_wgs84.inv(
        from_location_srid4326[0],
        from_location_srid4326[1],
        to_location_srid4326[0],
        to_location_srid4326[1]
    ) # lon/lat
    return distance


geod_wgs84 = Geod(ellps="WGS84")


class TranslatedString(RootModel[Dict[str, str]]):
    """
    Keys are ISO 639-1 language codes (e.g. 'de', 'en'), values are translated strings in that language
    """
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def values(self):
        return self.root.values()


    @classmethod
    def from_modeltranslation_field(cls, model_instance, field_basename: str, strip_html_tags=False):
        data = {
            language: getattr(model_instance, field_basename + '_' + language) or ''
            for language, _ in settings.LANGUAGES
        }
        # Default missing translations to default (first) language
        data = {k: v if v else data.get(settings.LANGUAGES[0][0], '') for k, v in data.items()}
        if strip_html_tags:
            data = {k: html_get_text(v) for k, v in data.items()}
        return TranslatedString.model_validate(data)

    @classmethod
    def from_gettext(cls, text: str, **format_args)-> 'TranslatedString':
        languages = [l[0] for l in settings.LANGUAGES]
        translators = {l: get_translator(l) for l in languages}
        result = {}
        for language in languages:
            result[language] = str(translators[language](text))  # explicit str() to not end up with a lazy object
            if format_args:
                result[language] = result[language].format(**format_args)

        return TranslatedString.model_validate(result)

def html_get_text(text: str, block_elements=True, normalize_to_single_space=True):
    strings = []
    last_block_container = None
    soup = BeautifulSoup(text, 'html.parser')
    for element in soup.descendants:
        # determine if we have entered a new string context or not
        if isinstance(element, NavigableString):
            if block_elements is True:
                # separate *every* string (current behavior)
                new_container = True
            elif block_elements:
                # must be a list; use block-element semantics
                try:
                    this_block_container = next(
                        parent
                        for parent in element.parents
                        if parent.name in block_elements
                    )
                except StopIteration:
                    this_block_container = None
                new_container = this_block_container is not last_block_container
                last_block_container = this_block_container
            else:
                # return one big string
                new_container = False

            if new_container or not strings:
                # start a new string
                strings.append("")

            strings[-1] += element.text

    text = "\n".join(strings)
    text = re.sub(r"^\n+|\n(?=\n)|\n+$", "", text)
    if normalize_to_single_space:
        text = re.sub(r'[ \n\r]+', ' ', text)
    return text

__threadpool = None


def get_subrequest_threadpool() -> concurrent.futures.ThreadPoolExecutor:
    global __threadpool
    if __threadpool is None:
        __threadpool = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="subrequest")
    return __threadpool

RE_PATTERN_MOBILE_PHONE_NUMBER = re.compile(r'(\+|00)(491[567][0-9]{3,15}|(?!49)[0-9]{8,15})')

def proto_to_str(m: protobuf_message) -> str:
    # noinspection PyBroadException
    try:
        if not m:
            return ""
        return m.__class__.__name__+"("+", ".join([f"{fd.name}={value}" for fd, value in m.ListFields()])+")"
    except:
        return f"Failed formatting: '{m}'"

def send_email_template(email_from: str, emails_to: List[str], template_name: str, metadata: Dict):
    if settings.EMAIL_SUPPRESS:
        logger.info(f"Email sending suppressed: email_from={email_from} emails_to={emails_to} template_name={template_name} metadata={metadata}")
        return
    if settings.EMAIL_PROVIDER == 'sendgrid':
        msg = EmailMessage(
            from_email=email_from,
            to=emails_to,
        )
        msg.template_id = getattr(settings, 'SENDGRID_TEMPLATE_ID_'+template_name)
        msg.dynamic_template_data = metadata
        msg.send(fail_silently=False)
    elif settings.EMAIL_PROVIDER == 'brevo':
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY

        template_id = getattr(settings, 'BREVO_TEMPLATE_ID_'+template_name)

        # create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sib_api_v3_sdk.SendSmtpEmailSender(email=email_from),
            to=[sib_api_v3_sdk.SendSmtpEmailTo(email=e) for e in emails_to],
            template_id=template_id,
            params=metadata,
        )

        try:
            api_response: sib_api_v3_sdk.CreateSmtpEmail = api_instance.send_transac_email(send_smtp_email)
            logger.debug(f"Brevo CreateSmtpEmail result: {api_response}")

        except sib_api_v3_sdk.rest.ApiException as e:
            raise RuntimeError(f"Exception when sending email: from='{emails_to}' to='{emails_to}' template_name='{template_name}' template_id='{template_id!r}' metadata='{metadata}'")

    else:
        raise RuntimeError(f"Unknown email provider: {settings.EMAIL_PROVIDER}")

def _is_valid_identifier(name: str) -> bool:
    """Return True iff *name* is a valid Python identifier and not a keyword."""
    return name.isidentifier() and not keyword.iskeyword(name)

def load_class_from_dotted_path(path: str) -> type[BaseModel]:
    """
    Given a string like 'pkg.mod.ClassName', import the module part and
    return the class object.  On any error (bad format, import failure,
    attribute missing, attribute not a class) raise Exception.
    """
    if not isinstance(path, str) or not path:
        raise Exception("Did not get a non-empty string")

    parts = path.split(".")
    if any([len(e) == 0 for e in parts]):
        raise Exception(f"Contained empty part: {path}")

    if any(not part or not _is_valid_identifier(part) for part in parts):
        raise Exception(f"Contained invalid identifier: {path}")

    mod_path = ".".join(parts[:-1])
    class_name = parts[-1]

    try:
        module = importlib.import_module(mod_path)
    except ImportError:
        raise Exception(f"Could not import module '{mod_path}'")

    try:
        obj = getattr(module, class_name)
    except AttributeError:
        raise Exception(f"Could not import class '{class_name}' in '{module}'")

    # --- final sanity check -------------------------------------------------
    if not inspect.isclass(obj):
        raise Exception(f"Not a class: {obj!r}")
    if not issubclass(obj, BaseModel):
        raise Exception(f"Not a subclass of BaseModel: {obj!r}")
    return obj


# from backend.utils import send_email_template; from django.conf import settings
# send_email_template(settings.EMAIL_FROM_ADDRESS, ['pa@iplus1.de'], 'VERIFY_EMAIL', {'code': '12345', 'url': 'https://google.com'})