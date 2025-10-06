# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import json
import logging
import traceback
from typing import Iterable

from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.gis.forms import GeometryField
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.views.decorators.http import require_POST
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from twilio.rest.verify.v2.service.verification import VerificationInstance

from backend.api_v1.schemas import TripSearchRequest
from backend.api_v1.trip import post_trip_search
from backend.diagnostics import PoiForm, TripSearchForm, SendSMSForm, CheckVerifyForm, RriveCheckForm, RriveUseForm, \
    PushNotificationForm, SharingOSCheckForm
from backend.enum import BookingState
from backend.models import BackendPoi, BackendUser, PushNotificationDevice, Vehicle, Booking, SupportTextEntry
from backend.push import ApplePushHandler, AndroidPushHandler
from backend.rrive import poll_ride_reports, find_offers_for_request, datetime_to_ticks, RRiveStatusCodeEnum
from backend.twilio import get_verify_service, create_verification, check_verify_code

from django.utils.translation import gettext as _

from protos.rrive_pb2 import RideRequestMessage
from sharingos.client import SharingOSClient

logger = logging.getLogger(__name__)


@user_passes_test(lambda user: user.is_superuser)
@require_POST
def poi(request: HttpRequest):
    form = PoiForm(request.POST)
    context = {'errors': []}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        logger.info(f"POI request: {form.cleaned_data}")
        near: Point = form.cleaned_data['near']
        # near_4326 = near.transform(4326, clone=True)
        poi_type = int(form.cleaned_data['poi_type'])
        pois = BackendPoi.objects
        if poi_type is not None and poi_type >= 0:
            pois = pois.filter(poi_type=poi_type)
        pois = pois.annotate(distance=Distance('location', near, spheroid=True)). \
                   order_by('distance'). \
                   all()[:10]

        context['pois'] = pois
    return render(request, 'diagnostics/_poi_result.html', context=context)

@user_passes_test(lambda user: user.is_superuser)
@require_POST
def trip(request: HttpRequest):
    form = TripSearchForm(request.POST)
    context = {'errors': []}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        tsr = TripSearchRequest(
            start_timestamp=form.cleaned_data['start_timestamp'],
            location_from_longitude=form.cleaned_data['from_location'][0],
            location_from_latitude=form.cleaned_data['from_location'][1],
            location_to_longitude=form.cleaned_data['to_location'][0],
            location_to_latitude=form.cleaned_data['to_location'][1],
        )
        status, response = post_trip_search(request, tsr)
        assert status == 200, f"Status: {status}"

        context['tsr'] = response
    return render(request, 'diagnostics/_trip_result.html', context=context)


@user_passes_test(lambda user: user.is_superuser)
@require_POST
def send_sms(request: HttpRequest):
    form = SendSMSForm(request.POST)
    context = {'errors': {}}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        # verify = get_verify_service()
        logger.info(f"Starting new verification for {form.cleaned_data['phone_number']}")
        # noinspection PyBroadException
        try:
            result = create_verification(form.cleaned_data['phone_number']) #verify.create(to=form.cleaned_data['phone_number'], channel='sms', custom_message=form.cleaned_data['text'])
            context['verify_created'] = result
        except:
            context['errors']["Request to Twilio failed"] = traceback.format_exc()

    rendered = render(request, 'diagnostics/_verify_result.html', context=context)
    return rendered

@user_passes_test(lambda user: user.is_superuser)
@require_POST
def send_push(request: HttpRequest):
    form = PushNotificationForm(request.POST)
    context = {'errors': {}, 'success': {}}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        try:
            push_user = BackendUser.objects.get(id=int(form.cleaned_data['user']))
            pnds = PushNotificationDevice.objects.filter(user=push_user, state='valid')
            title = form.cleaned_data['message']
            logger.info(f"Push requested for user '{push_user}' message '{title}' to tokens: {pnds}")
            if not pnds:
                context['errors']['No push tokens registered'] = 'No push tokens registered'
            else:
                for pnd in pnds:
                    result = None
                    if pnd.push_system == 'apple':
                        result = ApplePushHandler().send_push(title, pnd)
                    elif pnd.push_system == 'android':
                        result = AndroidPushHandler().send_push(title, pnd)
                    else:
                        context['errors'][f'Failed to send to {pnd.token}'] = 'Unknown push system'
                    if result:
                        if result.successful:
                            context['success'][f"Push to {pnd.push_system} {pnd.device_model} '{pnd.token}'"] = f"Successful"
                        if not result.successful or result.invalidate_device:
                            context['errors'][f"Push to {pnd.push_system} {pnd.device_model} '{pnd.token}'"] = f"Success: {result.successful}, Invalidate device: {result.invalidate_device}, Notes: {result.notes}'"


        except BackendUser.DoesNotExist:
            context['errors']['Unknown user'] = traceback.format_exc()

    rendered = render(request, 'diagnostics/_push_result.html', context=context)
    return rendered

@user_passes_test(lambda user: user.is_superuser)
@require_POST
def rrive_check(request: HttpRequest):
    form = RriveCheckForm(request.POST)
    context = {'errors': {}}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        # verify = get_verify_service()
        logger.info(f"Getting RRive state")
        # noinspection PyBroadException
        try:
            result = poll_ride_reports()
            context['statusCode'] = RRiveStatusCodeEnum(result.statusCode)
            context['result'] = result
        except:
            context['errors']["Request to Rrive failed"] = traceback.format_exc()

    rendered = render(request, 'diagnostics/_rrive_check_result.html', context=context)
    return rendered

@user_passes_test(lambda user: user.is_superuser)
@require_POST
def rrive_use(request: HttpRequest):
    form = RriveUseForm(request.POST)
    context = {'errors': {}}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        # verify = get_verify_service()
        data = form.cleaned_data
        params = dict(
            fromLat=data['from_location'][1], fromLng=data['from_location'][0],
            toLat=data['to_location'][1], toLng=data['to_location'][0],
            startingEarliest=datetime_to_ticks(data['start_earliest']),
            startingLatest=datetime_to_ticks(data['start_latest']),
            userId=request.user.username,
        )
        logger.info(f"Getting RRive offers for {params}")
        # noinspection PyBroadException
        try:
            rrm = RideRequestMessage(**params)
            result = find_offers_for_request(rrm)
            context['statusCode'] = RRiveStatusCodeEnum(result.statusCode)
            context['result'] = result
        except:
            context['errors']["Request to Rrive failed"] = traceback.format_exc()
            context['errors']["Parameters were"] = repr(params)

    rendered = render(request, 'diagnostics/_rrive_use_result.html', context=context)
    return rendered


@user_passes_test(lambda user: user.is_superuser)
@require_POST
def check_verify(request: HttpRequest):
    form = CheckVerifyForm(request.POST)
    context = {'errors': []}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        sid = form.cleaned_data['sid']
        code = form.cleaned_data['code']
        # After successful verification, status cannot be requested anymore!
        if code:
            status, verify_result = check_verify_code(sid, None, code) if code else None
            context['check_result'] = status
            context['verify_result'] = verify_result
        else:
            verify = get_verify_service()
            logger.info(f"Getting verification for {sid}")
            result = verify(sid).fetch()
            context['verify_result'] = result
            logger.info(f"Verification result {result}")

    return render(request, 'diagnostics/_verify_result.html', context=context)

@user_passes_test(lambda user: user.is_superuser)
@require_POST
def sharingos_vehicles(request: HttpRequest):
    form = SharingOSCheckForm(request.POST)
    context = {'errors': {}}
    if form.errors:
        context['errors'] = form.errors
    else:
        assert form.is_valid()
        # noinspection PyBroadException
        try:
            client = SharingOSClient()
            context['vehicle_list'] = client.get_vehicle_list()
        except:
            context['errors']['Exception'] = traceback.format_exc()
            context['vehicle_list'] = []

    return render(request, 'diagnostics/_sharingos_vehicle_result.html', context=context)

@user_passes_test(lambda user: user.is_superuser)
def vehicle_timeline(request: HttpRequest, vehicle_id: int|None=None):
    if vehicle_id is None:
        return HttpResponseBadRequest("Invalid vehicle ID")
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return HttpResponseBadRequest(f"No vehicle for ID {vehicle_id}")
    bookings: Iterable[Booking] = vehicle.booking_set.exclude(state__in={BookingState.canceled}).all()
    # http://timeline.knightlab.com/docs/json-format.html
    data = {
        "events": [
            {
                "start_date": {"year": 2025, "month": 3, "day": 11, "hour": 14, "minute": 45},
                "end_date": {"year": 2025, "month": 3, "day": 11, "hour": 14, "minute": 53},
                "text": {"headline": "bla <b>bla</b> <a href=\"google.com\">link</a>", "text": "blubb"},
                "background": {"color": "yellow"},
                "autolink": False,

            }
        ],  # list of slide objects
    }
    # https://visjs.github.io/vis-timeline/docs/timeline/#Data_Format
    data = []
    for b in bookings:
        url = reverse("backend_admin_site:backend_booking_change", args=(b.id,))
        # Show a minimum duration to make the box not too small
        end_time = max(b.end_time, b.start_time + datetime.timedelta(minutes=60))
        _, distance = b.get_distance()
        distance_string = f"{distance/1000.0:0.1f}km " if distance else ""
        data.append({
            "id": b.id,
            "content": f"Buchung von '<a href=\"{ reverse('backend_admin_site:backend_backenduser_change', args=(b.user.id,)) }\" target=\"_blank\">{b.user}</a>': {distance_string}<a href=\"{url}\" target=\"_blank\">ansehen</a> (Status: {b.state})",
            "start": b.start_time.isoformat(),
            "end": end_time.isoformat(),
            "style": "background-color: #eee;" if b.state == BookingState.canceled else "background-color: #e1f2d0;",
            "selectable": False,
        })
    return JsonResponse(data, safe=False)

class HiddenVerifyForm(forms.Form):
    email = forms.CharField()
    code = forms.CharField()

def email_verify(request: HttpRequest):
    if request.method == 'GET':
        error_msg = "Diese Seite ist nur zur E-Mail-Verifikation nutzbar. Bitte wechseln Sie in die App!  /  " + \
            "This page is only usable for e-mail verification. Please use the app!"
        if not request.GET.get('code'):
            return HttpResponseBadRequest(error_msg + " (Missing code parameter)")
        if not request.GET.get('email'):
            return HttpResponseBadRequest(error_msg + " (Missing email parameter)")
        return render(request,
                      'backend/user/email_verify.html',
                      context={
                          'method': request.method,
                          'msg': _("E-Mail verifizieren"),
                          'code': request.GET.get('code'),
                          'email': request.GET.get('email'),
                      })
    elif request.method == 'POST':
        form = HiddenVerifyForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest("Invalid data")
        email = form.cleaned_data['email']
        code = form.cleaned_data['code']
        try:
            user = BackendUser.objects.get(email_next=email)
            verify_code_result = user.process_email_verification_code(code)
        except BackendUser.DoesNotExist:
            verify_code_result = 'unknown'
        
        if verify_code_result == 'approved':
            ok = True
            msg = _("E-Mail-Adresse erfolgreich verifiziert - in der App geht es weiter!")
        else:
            ok = False
            if verify_code_result == 'unknown':
                msg = _("Keine gültige E-Mail-Adresse für die Verifikation")
            elif verify_code_result == 'expired':
                msg = _("Code ist abgelaufen: Bitte fordern Sie einen neuen Code an")
            else:
                msg = _("Unbekannter Fehler")

        return render(request,
                      'backend/user/email_verify.html',
                      context={
                          'method': request.method,
                          'verify_ok': ok,
                          'msg': msg,
                      })
    else:
        return HttpResponseBadRequest("Wrong HTTP method")


def account_deletion_request(request: HttpRequest):
    language = translation.get_language()

    stes = SupportTextEntry.objects.filter(entry_name='account-deletion').all()
    if not stes:
        return HttpResponseBadRequest("ERROR: Support text 'account-deletion' was expected but is missing. Please ask an administrator to add a support text with this 'entry_name'.")
    ste = stes[0]
    context = {
        'title': getattr(ste, 'title_'+language) or ste.title,
        'content': getattr(ste, 'content_' + language) or ste.content,
    }
    return render(request,'backend/user/account_deletion_request.html', context=context)
