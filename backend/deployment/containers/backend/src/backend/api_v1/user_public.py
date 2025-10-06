# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import logging

from django.conf import settings
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.auth import authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpRequest
from ninja import Router

from backend.api_v1.schemas import TokenValidResponse, TokenNotValidResponse, LoginResponseSuccess, ErrorResponse, \
    LoginCredentials, UserMetadata, RegisterResponseSuccess, RegisterUser, ValidateResponseSuccess, Email, MsgResponse, \
    PasswordResetRequest, UserCategoryResponse, UserCategorySchema, LoginResponseFailure, SupportTextResponse, \
    SupportText, PoolingLinkResultRequest
from backend.api_v1.system import get_supporttext_response
from backend.models import BackendUser, UserCategory, SupportTextEntry
from backend.utils import generate_verification_code, send_email_template


def register_routes(router: Router, logger: logging.Logger):
    @router.get("/isTokenValid", response={200: TokenValidResponse, 401: TokenNotValidResponse},
                openapi_extra={'security': [{'bearerAuth': []}]}, tags=['user_public'],
                summary="Check if token is still valid")
    def get_is_token_valid(request: HttpRequest):
        if request.user.is_anonymous:
            return 401, TokenNotValidResponse(error="No valid token or cookie")
        else:
            return 200, TokenValidResponse()


    @router.post("/login", response={200: LoginResponseSuccess, 401: LoginResponseFailure}, tags=['user_public'],
                 openapi_extra={'security': [{'bearerAuth': []}]},
                 summary="Log a user in with email/password credentials", description="""
On success, the session token is delivered in key "token" of the response. Also, the Set-Cookie header will be used
to set the appropriate cookie for further authenticated requests. 
""")
    def post_login(request, credentials: LoginCredentials):
        users = BackendUser.objects.filter(email=credentials.email).all()
        if not users:
            return 401, LoginResponseFailure(reason='unknown_email', error=f"Unknown user with email '{credentials.email}'")
        user = authenticate(username=users[0].username, password=credentials.password)
        if user is None:
            return 401, LoginResponseFailure(
                reason='wrong_password',
                error=f"Authentication failed for email '{credentials.email}' and password of length {len(credentials.password)}")
        login(request, user)

        return LoginResponseSuccess(
            token=request.session.session_key,
            user=UserMetadata.from_django_user(user)
        )

    @router.post("/register", response={200: RegisterResponseSuccess, 400: ErrorResponse}, tags=['user_public'],
                 openapi_extra={'security': [{'bearerAuth': []}]},
                 summary="Register a new user", description="""

""")
    def post_register(request, new_user_data: RegisterUser):
        username = BackendUser.email_to_username(str(new_user_data.email))
        if BackendUser.objects.filter(email=new_user_data.email).exists():
            return 400, ErrorResponse(error=f"User for email '{new_user_data.email}' already exists")
        phone_number = new_user_data.mobile_phone_number
        if phone_number:
            try:
                normalized = BackendUser.normalize_mobile_phone_number(phone_number)
                logger.debug(
                    f"Username {username}: Mobile number normalized {phone_number} -> {normalized}")
                phone_number = normalized
            except ValueError as e:
                return 400, ErrorResponse(error=str(e))

        # noinspection PyBroadException
        try:
            data = {
                'username': username,
                'first_name': "",
                'last_name': new_user_data.name,
                'password': new_user_data.password,
                'email': new_user_data.email,
                'mobile_number_unverified': phone_number,
            }
            if new_user_data.pooling_is_linked is not None:
                data['pooling_is_linked'] = new_user_data.pooling_is_linked
            if new_user_data.category_id:
                try:
                    data['category'] = UserCategory.objects.get(id=int(new_user_data.category_id))
                except (ValueError, UserCategory.DoesNotExist):
                    return 400, ErrorResponse(error=f"No category with ID '{new_user_data.category_id}'")
            user = BackendUser.objects.create_user(**data)
            user.email_is_verified = False
            user.email_next = user.email
            user.save()
        except Exception as exc:
            logger.exception(f"Creating user failed with data: {new_user_data}")
            return 400, ErrorResponse(error=f"Registering user failed: {exc}")

        return 200, RegisterResponseSuccess(msg='OK', userID=str(user.id))

    # @router.post("/validate_user", response={200: ValidateResponseSuccess, 409: ErrorResponse}, tags=['user_public'],
    #              openapi_extra={'security': [{'bearerAuth': []}]},
    #              summary="Check if user with username already exists")
    # def post_validate_user(request, data: Username):
    #     if not data:
    #         return 409, ErrorResponse(error="Not a valid username address")
    #     if BackendUser.objects.filter(username=data.username).exists():
    #         return 409, ErrorResponse(error=f"Username is already taken")
    #     return 200, ValidateResponseSuccess()

    @router.post("/validateEmail", response={
        200: ValidateResponseSuccess,
        400: ErrorResponse,
        409: ErrorResponse,
    }, tags=['user_public'],
                 openapi_extra={'security': [{'bearerAuth': []}]},
                 summary="Check if user with username already exists (returns 409) or is not yet known (returns 200). If email is not valid, returns 400.")
    def post_validate_email(request, data: Email):
        if not data:
            return 400, ErrorResponse(error="Not a valid email address")
        if BackendUser.objects.filter(email=data.email).exists():
            return 409, ErrorResponse(error=f"Email address is already taken")
        return 200, ValidateResponseSuccess()


    @router.post("/recover", response={200: MsgResponse, 409: ErrorResponse}, tags=['user_public'],
                 openapi_extra={'security': [{'bearerAuth': []}]},
                 summary="Trigger sending a recovery email with a password reset token")
    def post_recover(request, data: Email):
        email = data.email
        users = BackendUser.objects.filter(email=email).all()
        if not users:
            return 409, ErrorResponse(error=f"Email not known")
        user = users[0]
        code = generate_verification_code()

        user.password_reset_secret = code
        user.password_reset_validity = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=30)
        user.save()

        send_email_template(settings.EMAIL_FROM_ADDRESS, [str(email)], 'RESET_PASSWORD', {
            "reset_code": code,
        })

        logger.info(f"Recovery mail for '{email}' triggered. Secret is {code}")
        return 200, MsgResponse(msg="OK")


    @router.post("/reset", response={
        200: MsgResponse,
        409: ErrorResponse
    }, tags=['user_public'],
                 openapi_extra={'security': [{'bearerAuth': []}]},
                 url_name="post_password_reset",
                 summary="Given the email, a new password and the reset secret from the email, set the user's password. "
                         "Users are expected to be sent here from a view opened with the email and secret where they enter the new password.")
    def post_reset(request, data: PasswordResetRequest):

        users = BackendUser.objects.filter(email=data.email).all()
        if not users:
            return 409, ErrorResponse(error=f"Email not known")
        user = users[0]
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if not user.password_reset_secret or not user.password_reset_validity or user.password_reset_validity < now:
            return 409, ErrorResponse(error="Account cannot be reset anymore")

        if data.code != user.password_reset_secret:
            return 409, ErrorResponse(error="Invalid code")

        user.set_password(data.newPassword)
        user.password_reset_secret = None
        user.password_reset_validity = None
        user.save()

        return 200, MsgResponse(msg="OK")

    @router.get("/category", response={200: UserCategoryResponse},
                openapi_extra={'security': [{'bearerAuth': []}]}, tags=['user_public'],
                summary="Get list of user categories")
    def get_user_category(request: HttpRequest):
        categories = [
            UserCategorySchema.from_django(uc)
            for uc in UserCategory.objects.all()
        ]
        return 200, UserCategoryResponse(categories=categories)

    @router.get("/supportTexts", response={200: SupportTextResponse},
                deprecated=True,
                openapi_extra={'security': [{'bearerAuth': []}]}, tags=['user_public'],
                summary="Please use /system/supportTexts instead! Get the list of support texts along with their category information")
    def get_support_texts(request: HttpRequest):
        entries = SupportTextEntry.objects.filter(Q(entry_name__isnull=True) | Q(entry_name='')).order_by('category__sort_order', 'category__title', 'sort_order', 'id').all()
        return 200, get_supporttext_response(entries)

    @router.get("/specialPages", response={200: SupportTextResponse},
                deprecated=True,
                openapi_extra={'security': [{'bearerAuth': []}]}, tags=['user_public'],
                summary="Please use /system/supportTexts instead! Get the list of special pages. Use field 'entry_name' to distinguish them.")
    def get_special_pages(request: HttpRequest):
        entries = SupportTextEntry.objects.exclude(entry_name__isnull=True).exclude(entry_name='').order_by('sort_order', 'id').all()
        return 200, get_supporttext_response(entries)


    @router.post("/reportPoolingLinkResult", response={
        200: MsgResponse,
        400: ErrorResponse,
        401: ErrorResponse,
    }, tags=['user_public'],
                 openapi_extra={'security': [{'bearerAuth': []}]},
                 summary="Call to set the user's link state to the pooling service. This is expected to be called after the user linked the apps. Returns 400 if request had missing or unexpected data; returns 401 if user_id and key don't match")
    def post_report_pooling_link_result(request, data: PoolingLinkResultRequest):
        if not data:
            return 400, ErrorResponse(error="Not a valid email address")
        error_401 = "Unknown user with this ID or key does not match"
        try:
            users = BackendUser.objects.filter(id=int(data.user_id))
            if not users:
                logger.warning(f"No user for: {data}")
                return 401, ErrorResponse(error=error_401)
            user = users[0]
            if len(data.key) < 10:
                logger.warning(f"Key too short for: {data}")
                return 401, ErrorResponse(error=error_401)
            if user.auth_key_external_service != data.key:
                logger.warning(f"User's key '{user.auth_key_external_service}' does not match: {data}")
                return 401, ErrorResponse(error=error_401)

            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(BackendUser).id,
                object_id=user.id,
                object_repr=repr(user),
                action_flag=CHANGE,
                change_message=f"Pooling link {user.pooling_is_linked} -> {data.is_linked}")
            logger.info(f"Pooling was linked: {data}")
            user.pooling_is_linked = data.is_linked
            user.save()
        except ValueError:
            return 401, ErrorResponse(error="Invalid user id format")
        return 200, MsgResponse(msg="OK")

