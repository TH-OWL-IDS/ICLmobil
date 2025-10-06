# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import traceback
from copy import deepcopy
from typing import List, Dict, Any

import django_celery_results.models
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.gis.admin.options import GeoModelAdminMixin
from django.db.models import TextField
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse, reverse_lazy
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _, gettext, get_language
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin, TaskSelectWidget, PeriodicTaskForm, \
    CrontabScheduleAdmin
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from filer.admin import FolderAdmin
from filer.models import Folder
from import_export.admin import ExportActionModelAdmin
from import_export.fields import Field
from import_export.resources import ModelResource
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.import_export.forms import ExportForm
from unfold.decorators import action
from unfold.forms import UserCreationForm, AdminPasswordChangeForm, UserChangeForm
from unfold.sites import UnfoldAdminSite
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

from backend import twilio
from backend.diagnostics import PTDiagnosticsView, MessagingDiagnosticsView, RRiveDiagnosticsView, \
    SharingOSDiagnosticsView, UserScoreView
from backend.models import BackendPoi, BackendUser, CO2eEmission, Booking, WalletEntry, UserCategory, Vehicle, \
    NewsEntry, Message, PushNotificationDevice, UserFeedback, SupportTextEntry, SupportTextCategory, UserImageFeedback, \
    NewsCategory, Configuration
from backend.translate import get_translator
from tinymce import widgets as tinymce_widgets


class BackendAdminSite(UnfoldAdminSite):
    site_header = f"{settings.APP_NAME} Backend"

    def __init__(self, *args, **kwargs):
        super(BackendAdminSite, self).__init__(*args, **kwargs)
        # noinspection PyProtectedMember

        # self._registry.update(contrib_admin_site._registry)

    def get_sidebar_list(self, request: HttpRequest) -> List[Dict[str, Any]]:
        t = get_translator(get_language())
        result = deepcopy(super().get_sidebar_list(request))

        def __translate_title(item: Dict) -> Dict:
            if 'title' in item:
                item['title'] = t(str(item['title']))
            if 'items' in item:
                item['items'] = [__translate_title(k) for k in item['items']]
            return item

        result = [__translate_title(i) for i in result]
        return result


class BackendPoiAdmin(GeoModelAdminMixin, ModelAdmin):  # GISModelAdmin):
    list_display = ("name", "poi_type", "description", "list_get_location_coordinates")
    list_filter = ('poi_type',)
    search_fields = ('name', 'description',)

    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lon': settings.LOCATION_DEFAULT_LON,
            'default_lat': settings.LOCATION_DEFAULT_LAT,
        },
    }

    def get_urls(self):
        return super().get_urls() + [
            path(
                "diagnostics-public-transport",
                PTDiagnosticsView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="diagnostics-public-transport"
            ),
            path(
                "diagnostics-messaging",
                MessagingDiagnosticsView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="diagnostics-messaging"
            ),
            path(
                "diagnostics-rrive",
                RRiveDiagnosticsView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="diagnostics-rrive"
            ),
            path(
                "diagnostics-sharingos",
                SharingOSDiagnosticsView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="diagnostics-sharingos"
            ),
        ]


class GroupAdmin(ModelAdmin):
    filter_horizontal = ('permissions',)


class GroupNewMeta:
    proxy = True
    app_label = 'backend'  # BackendUser._meta.app_label


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()


class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    form = UnfoldPeriodicTaskForm


class UnfoldTaskResultAdmin(ModelAdmin):
    # Copy with different superclass of: django_celery_beat.admin.TaskResultAdmin

    model = django_celery_results.models.TaskResult
    date_hierarchy = 'date_done'
    list_display = ('task_id', 'periodic_task_name', 'task_name', 'date_done',
                    'status', 'worker')
    list_filter = ('status', 'date_done', 'periodic_task_name', 'task_name',
                   'worker')
    readonly_fields = ('date_created', 'date_done', 'result', 'meta')
    search_fields = ('task_name', 'task_id', 'status', 'task_args',
                     'task_kwargs')
    fieldsets = (
        (None, {
            'fields': (
                'task_id',
                'task_name',
                'periodic_task_name',
                'status',
                'worker',
                'content_type',
                'content_encoding',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Parameter'), {
            'fields': (
                'task_args',
                'task_kwargs',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Ergebnis'), {
            'fields': (
                'result',
                'date_created',
                'date_done',
                'traceback',
                'meta',
            ),
            'classes': ('extrapretty', 'wide')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        return list({
            field.name for field in self.opts.local_fields
        })


class CO2eAdmin(GeoModelAdminMixin, ModelAdmin):  # GISModelAdmin):
    list_display = ("mode_of_transport", "quantity", "per_unit")
    list_display_links = list_display
    # change_list_template = "admin/backend/coe2/change_list.html"

    actions_list = ["documentation"]

    @action(description="Click to jump to documentation")
    def documentation(self, request: HttpRequest):  # queryset: QuerySet
        return HttpResponseRedirect('/documentation/concepts/co2/#emission-intensities')


class UserCategoryAdmin(TranslationAdmin, ModelAdmin):
    list_display = ('name', 'description')


class UserImageFeedbackAdmin(GeoModelAdminMixin, ModelAdmin):
    list_display = ('id', 'created_at', 'user', 'booking')
    list_display_links = ("id", "created_at")
    readonly_fields = ("feedback_type", "user", "booking", "created_at")


class BookingAdmin(GeoModelAdminMixin, ModelAdmin):  # GISModelAdmin):
    list_display = ("id", "user", "state", "trip_mode", "start_time", "end_time", "from_location", "to_location",
                    'get_vehicle')
    list_display_links = ("id", "user", "state", "trip_mode")
    list_filter = ('user', 'state', 'trip_mode', 'start_time')
    # readonly_fields = ('start_time', 'end_time')
    search_fields = ('user__username', 'user__email', 'user__last_name', 'trip_mode', 'state')

    actions_list = ["documentation"]

    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lon': settings.LOCATION_DEFAULT_LON,
            'default_lat': settings.LOCATION_DEFAULT_LAT,
        },
    }

    def get_vehicle(self, b: Booking):
        if b.vehicle:
            return f"{b.vehicle.vehicle_model} {b.vehicle.vehicle_number} ({b.vehicle.provider_name})"

    get_vehicle.short_description = _("Fahrzeug")

    @action(description="Click to jump to documentation")
    def documentation(self, request: HttpRequest):  # queryset: QuerySet
        return HttpResponseRedirect('/documentation/concepts/bookings/')


class SupportTextEntryResource(ModelResource):
    id = Field()
    category_name = Field()
    category_sort_order = Field()
    entry_sort_order = Field()
    title_de = Field()
    title_en = Field()
    text_de = Field()
    text_en = Field()
    content_de = Field()
    content_en = Field()
    content_text_de = Field()
    content_text_en = Field()

    class Meta:
        model = SupportTextEntry
        fields = ('id', 'category_name', 'category_sort_order', 'entry_sort_order', 'title_de', 'title_en', 'text_de', 'text_en', 'content_de', 'content_en', 'content_text_de', 'content_text_en')

    def get_queryset(self):
        return self._meta.model.objects.order_by('category.sort_order', 'sort_order')

    def dehydrate_entry_sort_order(self, ste: SupportTextEntry):
        return str(ste.sort_order)

    def dehydrate_category_sort_order(self, ste: SupportTextEntry):
        return str(ste.category.sort_order)

    def dehydrate_id(self, ste: SupportTextEntry):
        return str(ste.id)

    def dehydrate_category_name(self, ste: SupportTextEntry):
        if not ste.category:
            return ""
        return ste.category.title_de

    def dehydrate_title_de(self, ste: SupportTextEntry):
        if not ste.title_de:
            return ""
        return ste.title_de

    def dehydrate_title_en(self, ste: SupportTextEntry):
        if not ste.title_en:
            return ""
        return ste.title_en

    def dehydrate_text_de(self, ste: SupportTextEntry):
        if not ste.text_de:
            return ""
        return ste.text_de

    def dehydrate_text_en(self, ste: SupportTextEntry):
        if not ste.text_en:
            return ""
        return ste.text_en

    def dehydrate_content_de(self, ste: SupportTextEntry):
        if not ste.content_de:
            return ""
        return ste.content_de

    def dehydrate_content_en(self, ste: SupportTextEntry):
        if not ste.content_en:
            return ""
        return ste.content_en

    def dehydrate_content_text_de(self, ste: SupportTextEntry):
        if not ste.content_de:
            return ""
        soup = BeautifulSoup(ste.content_de)
        return soup.get_text()

    def dehydrate_content_text_en(self, ste: SupportTextEntry):
        if not ste.content_en:
            return ""
        soup = BeautifulSoup(ste.content_en)
        return soup.get_text()


class WalletEntryResource(ModelResource):
    # TODO maybe export more fields https://django-import-export.readthedocs.io/en/latest/advanced_usage.html#advanced-data-manipulation-on-export
    user_category_id = Field()
    user_category_name = Field()
    co2e_reduction = Field()
    booking_start_time = Field()
    booking_start_date = Field()

    class Meta:
        model = WalletEntry

    def dehydrate_user_category_id(self, we: WalletEntry):
        if not we.user:
            return ""
        return we.user.category_id

    def dehydrate_user_category_name(self, we: WalletEntry):
        if not we.user:
            return ""
        return we.user.category.name

    def dehydrate_co2e_reduction(self, we: WalletEntry):
        return we.get_co2e_reduction_g()

    def dehydrate_booking_start_time(self, we: WalletEntry):
        if not we.booking:
            return ""
        return we.booking.start_time

    def dehydrate_booking_start_date(self, we: WalletEntry):
        if not we.booking:
            return ""
        return we.booking.start_time.date()


class WalletAdmin(GeoModelAdminMixin, ModelAdmin, ExportActionModelAdmin):  # GISModelAdmin):
    list_display = ("id", "wallet", "user", "link_to_booking", "created_at", "quantity", "unit", "source_information")
    list_display_links = ("id", "wallet", "user")
    list_filter = ('user', 'source_information')
    readonly_fields = ('created_at', 'unit', 'source_information')
    search_fields = ('user__email', 'user__last_name', 'source_information')

    resource_classes = [WalletEntryResource]
    export_form_class = ExportForm

    def link_to_booking(self, obj: WalletEntry):
        if not obj.booking:
            return "-"
        bid = obj.booking.id
        link = reverse("backend_admin_site:backend_booking_change", args=[bid])
        return format_html('<a href="{}">{}</a>', link, f"Booking {bid}")

    link_to_booking.short_description = 'Booking'


class VehicleAdmin(GeoModelAdminMixin, TranslationAdmin, ModelAdmin):  # GISModelAdmin):
    actions_detail = ["changeform_unlock_now", "changeform_lock_now"]

    list_display = ("id", 'vehicle_type', 'vehicle_model', 'vehicle_number', 'availability', 'battery_level_percent',
                    'lock_state')
    list_display_links = ("id", 'vehicle_type', 'vehicle_model', 'vehicle_number', 'battery_level_percent')
    list_filter = ('vehicle_model', 'vehicle_number', 'availability')
    readonly_fields = ('lock_state',)
    search_fields = ('id', 'vehicle_model', 'vehicle_number')

    @action(
        description=_("Sofort VERRIEGELN"),
        url_path="vehicle-lock-now",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def changeform_lock_now(self, request: HttpRequest, object_id: int):
        v = Vehicle.objects.get(id=object_id)
        # noinspection PyBroadException
        try:
            # noinspection PyTypeChecker
            v.lock(request.user)
        except:
            messages.add_message(request, messages.ERROR, _("Sperren fehlgeschlagen") + ': ' + traceback.format_exc())

        messages.add_message(request, messages.INFO, _("Sperren erfolgreich"))

        return redirect(
            reverse_lazy("backend_admin_site:backend_vehicle_change", args=(object_id,))
        )

    @action(
        description=_("Sofort ENTRIEGELN"),
        url_path="vehicle-unlock-now",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def changeform_unlock_now(self, request: HttpRequest, object_id: int):
        v = Vehicle.objects.get(id=object_id)
        # noinspection PyBroadException
        try:
            # noinspection PyTypeChecker
            v.unlock(request.user, None)
        except:
            messages.add_message(request, messages.ERROR,
                                 _("Entsperren fehlgeschlagen") + ': ' + traceback.format_exc())

        messages.add_message(request, messages.INFO, _("Entsperren erfolgreich"))

        return redirect(
            reverse_lazy("backend_admin_site:backend_vehicle_change", args=(object_id,))
        )


class NewsCategoryAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("news_type", "more_link_url", "more_link_label")
    list_display_links = ("news_type",)
    # list_filter = ("news_type",)
    # readonly_fields = ('news_type',)
    # search_fields = (,)

    fieldsets = (
        (None, {"fields": ("news_type", "more_link_url", "more_link_label")}),
    )


class NewsEntryAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("id", "header", "sub_header", "sub_header2", "created_at", "publish_from", "publish_until",
                    "news_type")
    list_display_links = ("id", "header", "sub_header")
    list_filter = ("news_type",)
    readonly_fields = ('created_at', 'modified_at')
    search_fields = ("header", "sub_header", "sub_header2", "text")

    formfield_overrides = {
        TextField: {"widget": tinymce_widgets.AdminTinyMCE},
    }

    actions_list = ["changelist_action"]

    @action(description=_("News Kategorien"), url_path="changelist-action", permissions=["changelist_action"])
    def changelist_action(self, request: HttpRequest):
        return redirect(
            reverse_lazy("backend_admin_site:backend_newscategory_changelist")
        )

    def has_changelist_action_permission(self, request: HttpRequest):
        return True


class MessageAdmin(ModelAdmin):
    list_display = ("id", "user", "created_at", "title", "push_notification_requested", "push_notification_done")
    list_display_links = ("id", "created_at", "title")
    list_filter = ("user", "created_at", "title", "push_notification_requested", "push_notification_done")
    readonly_fields = ("id", "created_at")
    search_fields = ("id", 'user__email', 'user__last_name', "created_at", "title", "sub_title", "content",
                     "push_notification_requested", "push_notification_done")

    formfield_overrides = {
        #        TextField: {"widget": tinymce_widgets.AdminTinyMCE},
    }


class BackendUserResource(ModelResource):
    # https://django-import-export.readthedocs.io/en/latest/advanced_usage.html#advanced-data-manipulation-on-export

    class Meta:
        model = BackendUser
        fields = [
            'id',
            'last_login',
            'is_superuser',
            'username',
            'email',
            'email_is_verified',
            'name',
            'date_joined',
            'category_name_de',
            'mobile_number_verified',
            'mobile_number_is_verified',
            'score_experience',
            'score_points',
        ]

    def dehydrate_name(self, be: BackendUser):
        return be.last_name or ''


class BackendUserAdmin(UserAdmin, ModelAdmin, ExportActionModelAdmin):
    actions_detail = ["changeform_action_sms", "changeform_action_email", "changeform_image_feedback",
                      "changeform_push_token", "changeform_score"]

    list_display = ("id", "username", "email", "is_active", "category", "last_name", "is_superuser", 'score_points',
                    'score_experience', 'date_joined')
    list_display_links = ("id", "username", "email", "last_name")
    fieldsets = (
        (None, {"fields": ("username", "category", "password")}),
        (_("Persönliche Informationen"),
         {"fields": ("first_name", "last_name", "email", "email_next", "email_is_verified", "mobile_number_verified",
                     "mobile_number_unverified", "mobile_number_is_verified")}),
        (
            _("Berechtigungen"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    # "groups",
                    # "user_permissions",
                ),
            },
        ),
        (_("Wichtige Zeitpunkte"), {"fields": ("last_login", "date_joined")}),
        (_("Punkte und Erfahrung"), {"fields": ("score_points", "score_experience")}),
        (_("Sonstiges"), {"fields": ("auth_key_external_service", 'pooling_is_linked')}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    resource_classes = [BackendUserResource]
    export_form_class = ExportForm

    @action(
        description=_("Image feedback"),
        url_path="image-feedback",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def changeform_image_feedback(self, request: HttpRequest, object_id: int):
        return redirect(
            reverse_lazy("backend_admin_site:backend_userimagefeedback_changelist") + f"?user__id__exact={object_id}"
        )

    @action(
        description=_("Push Notification Tokens"),
        url_path="push-notification-tokens",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def changeform_push_token(self, request: HttpRequest, object_id: int):
        return redirect(
            reverse_lazy(
                "backend_admin_site:backend_pushnotificationdevice_changelist") + f"?user__id__exact={object_id}"
        )

    @action(
        description=_("Score"),
        url_path="score",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def changeform_score(self, request: HttpRequest, object_id: int):
        return redirect(
            reverse_lazy("backend_admin_site:diagnostics-user-score", args=(object_id,))
        )

    @action(
        description=_("Mobilnummer Verifikation starten (SMS schicken)"),
        url_path="start-phone-verification",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def changeform_action_sms(self, request: HttpRequest, object_id: int):
        user = BackendUser.objects.get(pk=object_id)
        user.mobile_number_is_verified = False
        user.save()
        result = twilio.create_verification(user.mobile_number_unverified)

        messages.add_message(request, messages.INFO,
                             _("SMS verification gestartet (initialer Status: {status})").format(status=result.status))

        return redirect(
            reverse_lazy("backend_admin_site:backend_backenduser_change", args=(object_id,))
        )

    @action(
        description=_("E-Mail Verifikation starten"),
        url_path="start-email-verification",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def changeform_action_email(self, request: HttpRequest, object_id: int):
        user = BackendUser.objects.get(pk=object_id)
        user.start_email_verification(request=request)

        messages.add_message(request, messages.INFO, f"Email verification started")

        return redirect(
            reverse_lazy("backend_admin_site:backend_backenduser_change", args=(object_id,))
        )

    def get_urls(self):
        return super().get_urls() + [
            path(
                "diagnostics-user-score/<int:user_id>",
                UserScoreView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="diagnostics-user-score"
            ),
        ]

    # def has_changeform_action_permission(self, request: HttpRequest, object_id: Union[str, int]):
    #    pass


class PushNotificationDeviceAdmin(ModelAdmin):
    list_display = ("id", "user", "device_model", "push_system", "state", "token")
    list_display_links = ("id",)
    list_filter = ("user", "device_model", "push_system", "state")
    # readonly_fields = ("user", "device_model", "push_system")
    search_fields = ("user__last_name", "user__email", "device_model", "push_system", "state", "token")


class UserFeedbackAdmin(ModelAdmin):
    list_display = ("id", "user", "text", "vote", "booking")
    list_display_links = ("id", "text")
    list_filter = ("vote",)
    # readonly_fields = ("user", "device_model", "push_system")
    search_fields = ("user__last_name", "user__email", "text")


class UnfoldFolderAdmin(FolderAdmin, ModelAdmin):
    pass


class SupportTextCategoryAdmin(TranslationAdmin, ModelAdmin):
    list_display = ("sort_order", "title")
    list_display_links = ("title",)
    # list_filter = ('user', 'state', 'trip_mode', 'start_time')
    # readonly_fields = ('start_time', 'end_time')
    # search_fields = ('user__username', 'user__email', 'user__last_name', 'trip_mode', 'state')

    # actions_list = ["documentation"]


class SupportTextEntryAdmin(TranslationAdmin, ModelAdmin, ExportActionModelAdmin):
    list_display = ("id", 'title', "category_title", 'get_sort_order', 'get_entry_name')
    list_display_links = ("id", 'title')
    # list_filter = ('user', 'state', 'trip_mode', 'start_time')
    # readonly_fields = ('start_time', 'end_time')
    # search_fields = ('user__username', 'user__email', 'user__last_name', 'trip_mode', 'state')

    resource_classes = [SupportTextEntryResource]
    export_form_class = ExportForm

    actions_list = ["list_action_categories"]

    def category_title(self, obj):
        if not obj.category:
            return ""
        return obj.category.title

    category_title.short_description = _('Kategorie')

    def get_sort_order(self, obj):
        return f"{obj.category.sort_order or '-'} -> {obj.sort_order}"

    get_sort_order.short_description = _('Sortierung')

    def get_entry_name(self, obj):
        return obj.entry_name if obj.entry_name else ''

    get_entry_name.short_description = _('Name des Eintrags')

    @action(
        description=_("Kategorien"),
        url_path="supporttextentryadmin-kategorien",
        # attrs={"target": "_blank"},
        # permissions=["changeform_action"]
    )
    def list_action_categories(self, request: HttpRequest):
        return redirect(
            reverse_lazy("backend_admin_site:backend_supporttextcategory_changelist")
        )

    formfield_overrides = {
        TextField: {"widget": tinymce_widgets.AdminTinyMCE},
    }


class ConfigurationAdmin(ModelAdmin):
    list_display = ("id", "key", "schema")
    list_display_links = ("id", "key", "schema")


admin.site.register(BackendUser, UserAdmin)
admin.site.register(BackendPoi, BackendPoiAdmin)

backend_site = BackendAdminSite(name="backend_admin_site")
backend_site.site_title = "ICLMobil Backend Admin"
backend_site.register(BackendPoi, BackendPoiAdmin)

# admin.site.unregister(Group)
group_model = type("Group", (Group,), {'__module__': '', 'Meta': GroupNewMeta})
backend_site.register(group_model, GroupAdmin)
backend_site.register(BackendUser, BackendUserAdmin)
backend_site.register(PushNotificationDevice, PushNotificationDeviceAdmin)
backend_site.register(UserFeedback, UserFeedbackAdmin)
backend_site.register(UserCategory, UserCategoryAdmin)
backend_site.register(UserImageFeedback, UserImageFeedbackAdmin)
backend_site.register(django_celery_results.models.TaskResult, UnfoldTaskResultAdmin)

backend_site.register(PeriodicTask, PeriodicTaskAdmin)
backend_site.register(CrontabSchedule, CrontabScheduleAdmin)
# backend_site.register(django_celery_results.models.GroupResult, django_celery_results.admin.GroupResultAdmin)
backend_site.register(CO2eEmission, CO2eAdmin)
backend_site.register(Booking, BookingAdmin)
backend_site.register(WalletEntry, WalletAdmin)
backend_site.register(Vehicle, VehicleAdmin)
backend_site.register(NewsCategory, NewsCategoryAdmin)
backend_site.register(NewsEntry, NewsEntryAdmin)
backend_site.register(Message, MessageAdmin)

backend_site.register(SupportTextCategory, SupportTextCategoryAdmin)
backend_site.register(SupportTextEntry, SupportTextEntryAdmin)
backend_site.register(Configuration, ConfigurationAdmin)
