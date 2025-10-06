# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import logging
import traceback
from typing import Any, Dict

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.gis import forms as gis_forms
from django import forms, setup
from django.forms import TextInput
from django.forms.utils import ErrorList
from django.urls import reverse
from django.views.generic import TemplateView
from django_celery_beat.models import PeriodicTask
from django_celery_results.models import TaskResult
from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin
from unfold.widgets import UnfoldAdminSelectWidget

from backend.constants import TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT
from backend.models import BackendPoi, BackendUser
from backend.push import get_apns_push_setup_problems
from backend.twilio import get_balance
from backend.utils import twilio_setup_problems, email_setup_problems

logger = logging.getLogger(__name__)


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        # noinspection PyUnresolvedReferences
        return self.request.user.is_superuser


class PoiForm(forms.Form):
    near = gis_forms.PointField(srid=4326,
                                help_text="Get POIs near this point",
                                widget=gis_forms.OSMWidget(attrs={
                                    # "display_raw": True,
                                    "default_lat": 52.017460729788304,
                                    "default_lon": 8.903475808038054,
                                }))
    poi_type = forms.ChoiceField(choices=[(-1, "---")] + list(BackendPoi.POI_TYPE_CHOICES),
                                 # widget=UnfoldAdminSelectWidget(),
                                 label="Limit results to POIs of this type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-poi'),
            "hx-target": "#diagnostics-poi-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Search for POIs near',
                'near',
                'poi_type',
            ),
            Submit('submit', 'Search', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-poi-result"></div>'),
        )


class TripSearchForm(forms.Form):
    from_location = gis_forms.PointField(srid=4326,
                                         help_text="Search for trips from this location",
                                         widget=gis_forms.OSMWidget(attrs={
                                             # "display_raw": True,
                                             "default_lat": 52.017460729788304,
                                             "default_lon": 8.903475808038054,
                                         }))
    to_location = gis_forms.PointField(srid=4326,
                                       help_text="to this location",
                                       widget=gis_forms.OSMWidget(attrs={
                                           # "display_raw": True,
                                           "default_lat": 52.017460729788304,
                                           "default_lon": 8.903475808038054,
                                       }))
    start_timestamp = forms.DateTimeField(label="Departure date and time (UTC)",
                                          initial=datetime.datetime.now(tz=datetime.timezone.utc),
                                          # widget=forms.widgets.DateTimeInput() #attrs={'type': 'datetime-local'})
                                          )
    include_invalid_trips = forms.BooleanField(label="Include invalid trips", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-trip'),
            "hx-target": "#diagnostics-trip-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Find trips',
                'from_location',
                'to_location',
                'start_timestamp',
                'include_invalid_trips',
            ),
            Submit('submit', 'Search', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-trip-result"></div>'),
        )


class PTDiagnosticsView(SuperUserRequiredMixin, UnfoldModelAdminViewMixin, TemplateView):
    title = "Diagnostics: Public transport"  # required: custom page header title
    permission_required = ()  # required: tuple of permissions
    template_name = "admin/backend/diagnostics-pt.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['last_task_result'] = TaskResult.objects.filter(
            task_name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT).order_by('-date_done').first()
        context['periodic_task'] = PeriodicTask.objects.filter(name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT).first()
        context['poi_form'] = PoiForm()
        context['trip_search_form'] = TripSearchForm()
        return context


class UserScoreView(SuperUserRequiredMixin, UnfoldModelAdminViewMixin, TemplateView):
    title = "Diagnostics: User score"  # required: custom page header title
    permission_required = ()  # required: tuple of permissions
    template_name = "admin/backend/diagnostics-user-score.html"

    def get_context_data(self, user_id=None, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        try:
            user = BackendUser.objects.get(id=user_id)
            experience, points, points_reasons, reasons, rules = user.get_scores()
            context.update(
                {
                    'experience': experience,
                    'points': points,
                    'points_reasons': points_reasons,
                    'reasons': reasons,
                    'rules': rules,
                })
        except BackendUser.DoesNotExist:
            logger.exception(f"Failed for user_id {user_id}")
        return context


class SharingOSCheckForm(forms.Form):
    dummy = forms.HiddenInput()

    # phone_number = forms.RegexField(label="Phone number in E.164 format (e.g. +49 160 ...)", regex=r"\+[0-9 ]{9,30}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-sharingos-check'),
            "hx-target": "#diagnostics-sharingos-check-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Request data from SharingOS',
                'dummy'
            ),
            Submit('submit', 'Request', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-sharingos-check-result"></div>'),
        )


class RriveCheckForm(forms.Form):
    dummy = forms.HiddenInput()

    # phone_number = forms.RegexField(label="Phone number in E.164 format (e.g. +49 160 ...)", regex=r"\+[0-9 ]{9,30}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-rrive-check'),
            "hx-target": "#diagnostics-rrive-check-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Request data from Rrive',
                'dummy'
                #     'Send SMS verification',
                #     'phone_number',
            ),
            Submit('submit', 'Request', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-rrive-check-result"></div>'),
        )


class RriveUseForm(forms.Form):
    from_location = gis_forms.PointField(srid=4326,
                                         help_text="Search for trips from this location",
                                         widget=gis_forms.OSMWidget(attrs={
                                             # "display_raw": True,
                                             "default_lat": 52.017460729788304,
                                             "default_lon": 8.903475808038054,
                                         }))
    to_location = gis_forms.PointField(srid=4326,
                                       help_text="to this location",
                                       widget=gis_forms.OSMWidget(attrs={
                                           # "display_raw": True,
                                           "default_lat": 52.017460729788304,
                                           "default_lon": 8.903475808038054,
                                       }))
    start_earliest = forms.DateTimeField(label="Earliest departure date and time (UTC)",
                                         initial=datetime.datetime.now(tz=datetime.timezone.utc),
                                         # widget=forms.widgets.DateTimeInput() #attrs={'type': 'datetime-local'})
                                         )
    start_latest = forms.DateTimeField(label="Latest departure date and time (UTC)",
                                       initial=datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                                           hours=12),
                                       # widget=forms.widgets.DateTimeInput() #attrs={'type': 'datetime-local'})
                                       )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-rrive-use'),
            "hx-target": "#diagnostics-rrive-use-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Request ride offers from Rrive',
                'from_location', 'to_location', 'start_earliest', 'start_latest',
                #     'Send SMS verification',
                #     'phone_number',
            ),
            Submit('submit', 'Submit request', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-rrive-use-result"></div>'),
        )


class RRiveDiagnosticsView(SuperUserRequiredMixin, UnfoldModelAdminViewMixin, TemplateView):
    title = "Diagnostics: RRive"  # required: custom page header title
    permission_required = ()  # required: tuple of permissions
    template_name = "admin/backend/diagnostics-rrive.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['rrive_check_form'] = RriveCheckForm()
        context['rrive_use_form'] = RriveUseForm()
        context['RRIVE_GRPC_ENDPOINT'] = settings.RRIVE_GRPC_ENDPOINT
        # context['last_task_result'] = TaskResult.objects.filter(
        #     task_name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT).order_by('-date_done').first()
        # context['periodic_task'] = PeriodicTask.objects.filter(name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT).first()
        # context['poi_form'] = PoiForm()
        # context['trip_search_form'] = TripSearchForm()
        return context


class SharingOSDiagnosticsView(SuperUserRequiredMixin, UnfoldModelAdminViewMixin, TemplateView):
    title = "Diagnostics: SharingOS"  # required: custom page header title
    permission_required = ()  # required: tuple of permissions
    template_name = "admin/backend/diagnostics-sharingos.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['sharingos_check_form'] = SharingOSCheckForm()
        return context


class MessagingDiagnosticsView(SuperUserRequiredMixin, UnfoldModelAdminViewMixin, TemplateView):
    title = "Diagnostics: Messaging"  # required: custom page header title
    permission_required = ()  # required: tuple of permissions
    template_name = "admin/backend/diagnostics-messaging.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # context['last_task_result'] = TaskResult.objects.filter(
        #    task_name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT).order_by('-date_done').first()
        # context['periodic_task'] = PeriodicTask.objects.filter(name=TASK_NAME_PUBLIC_TRANSPORT_POI_IMPORT).first()
        sms_setup_problems = twilio_setup_problems()
        # noinspection PyBroadException
        try:
            context['balance'] = get_balance()
            if context['balance'][0] < 5.0:
                sms_setup_problems.append(f"Account balance at Twilio is very low. SMS verification will fail!")
        except:
            logger.exception("Failed getting balance")
            context['balance'] = 0.0, "FAILED GETTING BALANCE"
            sms_setup_problems.append(f"Failed getting account balance: " + traceback.format_exc())
        context['sms_setup_errors'] = sms_setup_problems
        context['sms_form'] = SendSMSForm()
        context['email_provider'] = settings.EMAIL_PROVIDER
        context['email_setup_errors'] = email_setup_problems()
        context['email_verified_from_address'] = settings.EMAIL_FROM_ADDRESS
        context['check_verify_form'] = CheckVerifyForm()
        context['push_notification_form'] = PushNotificationForm()
        context['push_setup_errors'] = get_apns_push_setup_problems()
        return context


class PushNotificationForm(forms.Form):
    message = forms.CharField(label="Message")

    def __init__(self, *args, **kwargs):
        choices = [(bu.id, bu.username) for bu in BackendUser.objects.all()]
        super().__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(
            label="User who gets a push notification on all their registered devices", choices=choices)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-send-push'),
            "hx-target": "#diagnostics-send-push-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Send Push notification',
                'user',
                'message'
            ),
            HTML('<p>Note that sending diagnostic push notifications will not invalid device tokens even if the service indicates an invalid device token.</p>'),
            Submit('submit', 'Send', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-send-push-result"></div>'),
        )


class SendSMSForm(forms.Form):
    phone_number = forms.RegexField(label="Phone number in E.164 format (e.g. +49 160 ...)", regex=r"\+[0-9 ]{9,30}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-send-sms'),
            "hx-target": "#diagnostics-send-sms-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Send SMS verification',
                'phone_number',
            ),
            Submit('submit', 'Send', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-send-sms-result"></div>'),
        )


class CheckVerifyForm(forms.Form):
    sid = forms.CharField(label="Twilio SID from verification attempt",
                          widget=TextInput(attrs={'id': 'twilio-verify-sid'}))
    code = forms.CharField(label="Security code",
                           help_text="Check if the code is valid if specified. Get verify status as it is if empty.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            "hx-post": reverse('diagnostics-check-verify'),
            "hx-target": "#diagnostics-verify-result",
        }
        self.helper.layout = Layout(
            Fieldset(
                'Send verification code / Look up verification result',
                'sid',
                'code',
            ),
            Submit('submit', 'Send', css_class="btn-primary"),
            # , css_class='border font-medium hidden px-3 py-2 rounded-md transition-all w-full hover:bg-gray-50 lg:block lg:w-auto dark:border-gray-700  dark:hover:text-gray-200 dark:hover:bg-gray-900')
            HTML('<div id="diagnostics-verify-result"></div>'),
        )
