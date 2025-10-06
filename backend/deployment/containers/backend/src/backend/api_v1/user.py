# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import base64
import datetime
import io
import logging
import os
import uuid
from typing import List

from PIL import Image
from celery.worker.state import total_count
from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.http import HttpRequest
from filer.models import Folder
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate, PageNumberPagination
from twilio.base.exceptions import TwilioRestException

from backend import twilio
from backend.api_v1 import user_public
from backend.api_v1.authz import can_administer_users, can_administer_roles, can_administer_groups
from backend.api_v1.schemas import UserMetadata, TokenNotValidResponse, ErrorResponse, BitPermission, Role, \
    CreateRoleRequest, MsgResponse, BackendGroup, CreateGroupRequest, UpdateGroupRequest, UpdateUserRequest, \
    DeleteGroupRequest, UpdateRoleRequest, DeleteRoleRequest, CreateAssignedGroupsRequest, \
    CreateAssignedRolesRequest, UploadProfileImageRequest, CheckVerificationCodeRequest, CheckVerificationCodeResponse, \
    CheckPasswordRequest, MessageSchema, RegisterPushTokenRequest, UserStatisticsResponse, FeedbackRequest, \
    UploadImageProofRequest
from backend.enum import BookingState, OptionType, VehicleType, UserImageFeedbackType
from backend.files import filer_add_image_from_data
from backend.models import BackendUser, backend_permissions, BackendRole, GroupMetadata, UserCategory, Message, \
    PushNotificationDevice, Booking, WalletEntry, UserFeedback, UserImageFeedback, USER_IMAGE_FEEDBACK_FOLDER_NAME
from backend.twilio import VerifyCodeResult
from backend.utils import send_email_template

router = Router()

logger = logging.getLogger(__name__)

user_public.register_routes(router, logger)


# @router.get("/getUserStatus/{workingID}", response={501: None},
#             openapi_extra={'security': [{'bearerAuth': []}]}, tags=['user'])
# def get_user_status(request: HttpRequest, workingID: str):
#     raise HttpErrorNotImplemented()


@router.get("/getUserData",
            response={
                200: UserMetadata,
                401: TokenNotValidResponse,
                404: ErrorResponse,
            },
            summary="User metadata of authenticated user",
            tags=['user'])
def get_user_data(request: HttpRequest):
    if request.user.is_anonymous or not request.user:
        return 401, TokenNotValidResponse(error="No valid token or cookie")

    # noinspection PyTypeChecker
    user: BackendUser = request.user
    metadata = UserMetadata.from_django_user(user)
    if metadata:
        return metadata
    else:
        return 404, ErrorResponse(error="User not found")


@router.get("/getUsers", response={
    200: List[UserMetadata],
    401: TokenNotValidResponse,
},
            tags=['user'])
def get_users(request: HttpRequest):
    if can_administer_users(request.user):
        return [
            UserMetadata.from_django_user(u)
            for u in BackendUser.objects.all()
        ]
    else:
        return 401, TokenNotValidResponse(error="Not authorized")


@router.post("/updateUser", response={
    200: MsgResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             tags=['user'], summary="Update one or more attribute of the current user", description="""
Each value that is set and not null will be updated in the logged in user.
Changing the mobile number or email address does not change the verified versions
immediately but just store the new value in `email_next` or `mobile_number_unverified`.
To get them activated, use
`/api/v1/user/startPhoneNumberVerification`/`/api/v1/user/checkPhoneNumberVerificationCode`
or
`/api/v1/user/startEmailVerification`/`/api/v1/user/checkEmailVerificationCode`
""")
def put_update_user(request: HttpRequest, data: UpdateUserRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    # noinspection PyTypeChecker
    user: BackendUser = request.user
    if data.name is not None:
        user.last_name = data.name
    if data.email is not None:
        user.email_next = data.email
    if data.mobile_number is not None:
        try:
            user.mobile_number_unverified = BackendUser.normalize_mobile_phone_number(data.mobile_number)
            logger.debug(f"User {user}: Update mobile number {data.mobile_number} -> {user.mobile_number_unverified}")
        except ValueError as e:
            return 400, ErrorResponse(error=str(e))
        if user.mobile_number_unverified != user.mobile_number_verified:
            logger.debug(f"User {user}: New unverified mobile number {user.mobile_number_unverified} differs from verified number {user.mobile_number_verified}. mobile_number_is_verified {user.mobile_number_is_verified} -> False")
            user.mobile_number_is_verified = False
    if data.category_id is not None:
        # noinspection PyBroadException
        try:
            user.category = UserCategory.objects.get(id=int(data.category_id))
        except (ValueError, UserCategory.DoesNotExist):
            return 400, ErrorResponse(error=f"No category with ID '{data.category_id}'")
        except:
            return 400, ErrorResponse(error=f"Unexpected error")
    if data.password:
        user.set_password(data.password)
    if data.pooling_is_linked is not None:
        user.pooling_is_linked = data.pooling_is_linked
    user.save()

    return 200, MsgResponse(msg='OK')


@router.post("/startPhoneNumberVerification", response={
    200: MsgResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
},
             tags=['user'])
def post_start_phone_number_verification(request: HttpRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    user: BackendUser = request.user
    try:
        result = twilio.create_verification(user.mobile_number_unverified)
    except TwilioRestException as exc:
        return 400, ErrorResponse(error=f"Verification failed: {exc}")
    # `pending`, `approved`, `canceled`, `max_attempts_reached`, `deleted`, `failed` or `expired`.
    if result.status in {'canceled', 'max_attempts_reached', 'deleted', 'failed', 'expired'}:
        return 400, ErrorResponse(error=f"Verification failed: {result.status}")
    return 200, MsgResponse(msg='OK')


@router.post("/checkPhoneNumberVerificationCode", response={
    200: CheckVerificationCodeResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
},
             description="""
Check if the delivered verification code is valid for the phone number last set for this user.
It is assumed that `/startPhoneNumberVerification` has been called earlier to send the SMS.

Response is 401 if user is not authenticated.
Response is 400 if no phone number has been set before.
Otherwise, response is always 200 and the verification result is contained in the JSON body.
Key `verified` is `true` if the verification is successful and `false` if the code did not match.
""",
             tags=['user'])
def post_check_phone_number_verification_code(request: HttpRequest, data: CheckVerificationCodeRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    user: BackendUser = request.user
    if not user.mobile_number_unverified:
        return 400, ErrorResponse(error=f"Missing phone number")
    if not user.mobile_number_is_verified:
        try:
            verify_code_result, check_instance = twilio.check_verify_code(None, phone_number=user.mobile_number_unverified,
                                                                          code=data.code)
        except TwilioRestException as e:
            if e.status == 404:
                verify_code_result, check_instance = 'expired', None
            else:
                raise e
        # verify_code_result = Literal['unknown', 'pending', 'approved', 'canceled', 'max_attempts_reached', 'deleted', 'failed', 'expired']
        if verify_code_result == 'approved':
            logger.debug(
                f"User {user}: Setting user.mobile_number_is_verified = True (verify_code_result = {verify_code_result}) user.mobile_number_verified {user.mobile_number_verified} <- user.mobile_number_unverified {user.mobile_number_unverified} ")
            user.mobile_number_is_verified = True
            user.mobile_number_verified = user.mobile_number_unverified
            user.save()
    else:
        logger.debug(f"User {user}: Users mobile phone number already approved")
        verify_code_result: VerifyCodeResult = 'approved'
    return 200, CheckVerificationCodeResponse(verified=user.mobile_number_is_verified, status=verify_code_result)


@router.post("/startEmailVerification", response={
    200: MsgResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             tags=['user'])
def post_start_email_verification(request: HttpRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    user: BackendUser = request.user
    user.start_email_verification(request=request)

    return 200, MsgResponse(msg='OK')


@router.post("/checkEmailVerificationCode", response={
    200: CheckVerificationCodeResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             tags=['user'])
def post_check_email_verification_code(request: HttpRequest, data: CheckVerificationCodeRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    user: BackendUser = request.user
    if not user.email:
        return 400, ErrorResponse(error=f"Missing email address")
    if user.email_next:
        verify_code_result = user.process_email_verification_code(data.code)
        # verify_code_result = Literal['unknown', 'pending', 'approved', 'canceled', 'max_attempts_reached', 'deleted', 'failed', 'expired']
    else:
        logger.debug(f"User {user}: Users email address already approved")
        verify_code_result: VerifyCodeResult = 'approved'
    return 200, CheckVerificationCodeResponse(verified=user.email_is_verified, status=verify_code_result)


@router.delete("/deleteUser", response={
    200: MsgResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
}, summary="Delete the logged in user",
               description="Returns 200 if user was successfully deleted. 401 if the user is not logged in. 400 in the special case where the last admin would be deleted.",
               tags=['user'])
def delete_user(request: HttpRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")

    if not BackendUser.objects.exclude(id=request.user.id, is_superuser=True).exists():
        return 400, ErrorResponse(error="Cannot delete last superuser")

    request.user.delete()

    return 200, MsgResponse(msg='OK')


@router.get("/getPermissions", response={
    200: List[BitPermission],
    401: TokenNotValidResponse,
},
            include_in_schema=False,
            tags=['user'])
def get_permissions(request: HttpRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    return 200, [
        BitPermission(bit=k ** 2, permissionName=v)
        for k, v in backend_permissions.items()
    ]


@router.get("/getRolePermissions/{roleID}", response={
    200: List[BitPermission],
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
            include_in_schema=False,
            tags=['user'])
def get_role_permissions(request: HttpRequest, roleID: str):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    try:
        role_id = int(roleID)
        role = BackendRole.objects.get(id=role_id)
    except (ValueError, BackendRole.DoesNotExist):
        return 404, ErrorResponse(error=f"No role with ID {roleID}")

    return 200, [
        BitPermission(bit=k ** 2, permissionName=v)
        for k, v in role.get_permission_bits().items()
    ]


@router.get("/getRoles", response={
    200: List[Role],
    401: TokenNotValidResponse,
},
            include_in_schema=False,
            tags=['user'])
def get_roles(request: HttpRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")

    return 200, [Role.from_backend_role(br) for br in BackendRole.objects.all()]


# @router.get("/getGroups", response={
#     200: List[BackendGroup],
#     401: TokenNotValidResponse,
# },
#             tags=['user'])
# def get_roles(request: HttpRequest, roleID: str):
#     if not request.user.is_authenticated:
#         return 401, TokenNotValidResponse(error="NO_TOKEN")
#
#     return 200, [Role.from_backend_role(br) for br in BackendRole.objects.all()]


# TODO getAssignedGroups

# TODO refreshToken

@router.post("/createRole", response={
    200: MsgResponse,
    400: ErrorResponse,
    409: ErrorResponse,
},
             include_in_schema=False,
             tags=['user'])
def post_createRole(request: HttpRequest, data: CreateRoleRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_roles(request.user):
        return 401, TokenNotValidResponse(error="Not authorized")
    permissions = sum([e.bit for e in data.permissions])
    role, created = BackendRole.objects.get_or_create(name=data.name, defaults={
        "description": data.description,
        "permissions": permissions,
    })
    if not created:
        return 409, ErrorResponse(error="Role already exists")

    return 200, MsgResponse(msg="OK")


@router.put("/updateRole", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
            include_in_schema=False,
            tags=['user'])
def put_updateRole(request: HttpRequest, data: UpdateRoleRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_roles(request.user):
        return 401, TokenNotValidResponse(error="Not authorized")
    permissions = sum([e.bit for e in data.permissions])
    try:
        role = BackendRole.objects.get(id=int(data.roleID))
    except (ValueError, BackendRole.DoesNotExist):
        return 404, ErrorResponse(error=f"No role with ID '{data.roleID}'")
    role.name = data.name
    role.description = data.description
    role.permissions = permissions
    role.save()

    return 200, MsgResponse(msg="OK")


@router.delete("/deleteRole", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
               include_in_schema=False,
               tags=['user'])
def delete_role(request: HttpRequest, data: DeleteRoleRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_roles(request.user):
        return 401, TokenNotValidResponse(error="Not authorized")

    try:
        role = BackendRole.objects.get(id=int(data.roleID))
    except (ValueError, BackendRole.DoesNotExist):
        return 404, ErrorResponse(error=f"No role with ID '{data.roleID}'")
    role.delete()

    return 200, MsgResponse(msg="OK")


@router.get("/getGroups", response={
    200: List[BackendGroup],
    401: TokenNotValidResponse,
},
            include_in_schema=False,
            tags=['user'])
def get_groups(request: HttpRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_groups(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    return 200, [BackendGroup.from_django_group(dg) for dg in Group.objects.all()]


@router.post("/createGroup", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
},
             include_in_schema=False,
             tags=['user'])
def post_create_group(request: HttpRequest, data: CreateGroupRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_groups(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    group, created = Group.objects.get_or_create(name=data.name, defaults={})
    group_metadata, created = GroupMetadata.objects.get_or_create(group=group,
                                                                  defaults={'description': data.description})

    return 200, MsgResponse(msg='OK')


@router.put("/updateGroup", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
            include_in_schema=False,
            tags=['user'])
def put_update_group(request: HttpRequest, data: UpdateGroupRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_groups(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        group = Group.objects.get(id=int(data.groupID))
    except (ValueError, Group.DoesNotExist):
        return 404, ErrorResponse(error=f"No group with ID '{data.groupID}'")
    group.name = data.name
    group.save()

    group_metadata, created = GroupMetadata.objects.get_or_create(group=group,
                                                                  defaults={'description': data.description})
    if not created:
        group_metadata.description = data.description
        group_metadata.save()

    return 200, MsgResponse(msg='OK')


@router.delete("/deleteGroup", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
               include_in_schema=False,
               tags=['user'])
def delete_group(request: HttpRequest, data: DeleteGroupRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_groups(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        group = Group.objects.get(id=int(data.groupID))
    except (ValueError, Group.DoesNotExist):
        return 404, ErrorResponse(error=f"No group with ID '{data.groupID}'")
    group.delete()

    return 200, MsgResponse(msg='OK')


@router.put("/logout", response={
    200: MsgResponse,
},
            tags=['user'])
def logout(request: HttpRequest):
    if not request.user.is_authenticated:
        return 200, MsgResponse(msg="Not logged in")

    django_logout(request)

    return 200, MsgResponse(msg='OK')


@router.post("/createAssignedGroups", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             include_in_schema=False,
             tags=['user'])
def post_create_assigned_groups(request: HttpRequest, data: CreateAssignedGroupsRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_users(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        user = BackendUser.objects.get(id=int(data.userID))
    except (ValueError, BackendUser.DoesNotExist):
        return 404, ErrorResponse(error=f"No user with ID '{data.userID}'")
    try:
        groups = Group.objects.filter(id__in=[int(group['id']) for group in data.groups])
    except (ValueError, BackendGroup.DoesNotExist):
        return 404, ErrorResponse(error=f"At leasts one group ID is invalid in '{data.groups}'")
    user.groups.clear()
    user.groups.add(*groups)

    return 200, MsgResponse(msg='OK')


@router.get("/getAssignedGroups/{user_id}", response={
    200: List[BackendGroup],
    401: TokenNotValidResponse,
},
            include_in_schema=False,
            tags=['user'])
def get_assigned_groups(request: HttpRequest, user_id: str):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_groups(request.user) or not can_administer_users(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        user = BackendUser.objects.get(id=int(user_id))
    except (ValueError, BackendUser.DoesNotExist):
        return 404, ErrorResponse(error=f"No user with ID '{user_id}'")

    return 200, [BackendGroup.from_django_group(dg) for dg in user.groups.all()]


@router.post("/createAssignedRoles", response={
    200: MsgResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             include_in_schema=False,
             tags=['user'])
def post_create_assigned_roles(request: HttpRequest, data: CreateAssignedRolesRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_users(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        user = BackendUser.objects.get(id=int(data.userID))
    except (ValueError, BackendUser.DoesNotExist):
        return 404, ErrorResponse(error=f"No user with ID '{data.userID}'")
    try:
        roles = BackendRole.objects.filter(id__in=[int(role['id']) for role in data.roles])
    except (ValueError, BackendRole.DoesNotExist):
        return 404, ErrorResponse(error=f"At leasts one role ID is invalid in '{data.roles}'")
    user.roles.clear()
    user.roles.add(*roles)

    return 200, MsgResponse(msg='OK')


@router.get("/getAssignedRoles/{user_id}", response={
    200: List[Role],
    401: TokenNotValidResponse,
},
            include_in_schema=False,
            tags=['user'])
def get_assigned_roles(request: HttpRequest, user_id: str):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if not can_administer_roles(request.user) or not can_administer_users(request.user):
        return 401, TokenNotValidResponse(error="Unauthorized")

    try:
        user = BackendUser.objects.get(id=int(user_id))
    except (ValueError, BackendUser.DoesNotExist):
        return 404, ErrorResponse(error=f"No user with ID '{user_id}'")

    result = [Role.from_backend_role(br) for br in user.roles.all()]
    return 200, result


@router.post("/uploadProfileImage", response={
    200: MsgResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             tags=['user'], summary="Upload profile image for user", description="""
The image must be in JPEG or PNG format with no dimension larger than 4096 pixel.
It must be Base64 encoded and sent as a string in the key "profileImage". 
The string length (image after Base64 encoding) must be <50 MiB.
""")
def post_upload_profile_image(request: HttpRequest, data: UploadProfileImageRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if len(data.profileImage) > 50 * 1024 * 1024:
        return 400, ErrorResponse(error=f"Encoded image data too large ({len(data.profileImage)} Byte > 50 MiB")
    # noinspection PyTypeChecker
    user: BackendUser = request.user
    # noinspection PyBroadException
    try:
        image_data = base64.b64decode(data.profileImage)
    except:
        return 400, ErrorResponse(
            error=f"Invalid data in profileImage. Should be base64 encoded JPEG, PNG or HEIC image. Starts with: {data.profileImage[:20]!r}")

    image = Image.open(io.BytesIO(image_data))
    image = image.convert('RGB')
    image.thumbnail((1000, 1000))

    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0, os.SEEK_SET)
    user.profile_image_data = buffer.read()

    user.profile_image_mimetype = "image/jpeg"
    user.save()

    return 200, MsgResponse(msg='OK')

@router.post("/uploadImageProof", response={
    200: MsgResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
    404: ErrorResponse,
},
             tags=['user'], summary="Upload an image showing an asset after giving it back.", description="""
The image must be in JPEG or PNG format with no dimension larger than 4096 pixel.
It must be Base64 encoded and sent as a string in the key "image". 
The string length (image after Base64 encoding) must be <50 MiB.
""")
def post_upload_image_proof(request: HttpRequest, data: UploadImageProofRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    if len(data.image) > 50 * 1024 * 1024:
        return 400, ErrorResponse(error=f"Encoded image data too large ({len(data.image)} Byte > 50 MiB")
    # noinspection PyTypeChecker
    user: BackendUser = request.user
    # noinspection PyBroadException
    try:
        image_data = base64.b64decode(data.image)
    except:
        logger.exception(f"Data was: {repr(data)[:1500]}")
        return 400, ErrorResponse(
            error=f"Invalid data in image. Should be base64 encoded JPEG, PNG or HEIC image. Starts with: {data.image[:100]!r}")
    if data.booking_id:
        try:
            booking = Booking.objects.get(id=int(data.booking_id))
        except (TypeError, ValueError, Booking.DoesNotExist):
            logger.exception(f"booking_id was: {data.booking_id}")
            return 400, ErrorResponse(error=f"Invalid booking_id '{data.booking_id!r}'")
    else:
        booking = None

    image = Image.open(io.BytesIO(image_data))
    image = image.convert('RGB')
    image.thumbnail((1000, 1000))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    # buffer.seek(0, os.SEEK_SET)
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    # Be sure to keep the randomness (from uuid4) in here as we rely on it for the files to not be (trivially) guessable!
    filename = f"user_{user.id}_{now.isoformat().replace(':', '-')}_{uuid.uuid4()}.jpeg"
    folder, created = Folder.objects.get_or_create(name=USER_IMAGE_FEEDBACK_FOLDER_NAME)

    image = filer_add_image_from_data(buffer.getvalue(), filename, folder)

    uif = UserImageFeedback.objects.create(
        feedback_type=UserImageFeedbackType.image_proof.value,
        user=user,
        image=image,
        location=Point(data.longitude, data.latitude, srid=4326) if data.longitude and data.latitude else None,
        booking=booking,
    )

    return 200, MsgResponse(msg='OK')


@router.post("/checkPassword", response={200: MsgResponse, 400: ErrorResponse, 401: TokenNotValidResponse}, tags=['user'],
             summary="Check if the given password matches the logged in user", description="""
    Returns 200 if the password matches, 400 if it does not match and 401 if no user session is detected, e.g. the user is not logged in. 
    """)
def post_check_password(request, credentials: CheckPasswordRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="Not authenticated")
    if request.user.check_password(credentials.password):
        return 200, MsgResponse(msg='Password matches')
    else:
        return 400, ErrorResponse(error="Incorrect password")


@router.delete("/message", response={200: MsgResponse, 404: ErrorResponse, 401: TokenNotValidResponse}, tags=['user'],
             summary="Delete the message with the given ID")
def delete_message(request, message_id: str):
    if not request.user.is_authenticated:
        return 401, ErrorResponse(error="Not authenticated")
    try:
        m = Message.objects.get(user=request.user, id=message_id)
        m.soft_delete = True
        m.save()
    except Message.DoesNotExist:
        return 404, ErrorResponse(error=f"Message '{message_id}' not found")
    return 200, MsgResponse(msg="OK")


@router.get("/message/list", response={200: List[MessageSchema], 401: TokenNotValidResponse}, tags=['user'],
             summary="Get list of messages for this user. ", description="""
    Sorted with newest messages first. This request is paginated. First (and default) page is 1. Pass parameter `?page=2`
    for the second page etc. 
    """)
@paginate(PageNumberPagination)  # does not support Tuple return format (e.g. return 200, Message...all())
def get_messages(request):
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return [MessageSchema.from_model(m) for m in Message.objects.filter(
        user=request.user,
        soft_delete=False,
    ).exclude(
        publish_after__gt=now,
    ).order_by('-created_at').all()]



@router.post("/device/registerPushToken", response={200: MsgResponse, 401: TokenNotValidResponse}, tags=['user'],
             summary="Register a push token for this device", description="""
Each user can have one or more devices associated with their account.
Each device will be adressed when a push notification is to be sent.
To allow push notifications to be sent to a device, the app on the device needs to get a device-app-specific
token. The backend later uses this token to issue the push notification.

The endpoint is used by the app to register the token.
It can (and should) be called any time a new token might be available.
Calling it with the same data multiple times is fine.

Invalid tokens in the backend are removed automatically once a push notification attempt using the token fails.
No manual removal by the app is needed.  
    """)
def post_register_push_token(request, register_request: RegisterPushTokenRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="Not authenticated")
    pnd, created = PushNotificationDevice.objects.get_or_create(
        user=request.user,
        push_system=register_request.push_system,
        token=register_request.token,
    )
    pnd.device_model = register_request.device_model
    pnd.save()
    return 200, MsgResponse(msg="OK "+('Token registered' if created else 'Token already known'))


@router.get("/statistics", response={200: UserStatisticsResponse, 401: TokenNotValidResponse}, tags=['user'],
            summary="Get user statistics", description="""
    """)
def get_statistics(request):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="Not authenticated")

    wallet_entries = WalletEntry.objects \
        .filter(wallet=WalletEntry.Wallets.CO2e) \
        .filter(booking_state__in={BookingState.finished, BookingState.timeout}) \
        .filter(user=request.user)

    wallet_entries.select_related('booking')

    wallet_bookings = [we.booking for we in wallet_entries if we.booking]

    wallet_reductions = [we.get_co2e_reduction_g() for we in wallet_entries]

    b: Booking
    distances = [b.get_distance()[1] for b in wallet_bookings]
    distances = [d for d in distances if d is not None]
    logger.debug(f"Distances for user {request.user.id}: {distances}")

    bookings = Booking.objects.filter(user=request.user).exclude(state=BookingState.created).all()

    bookings_per_mode = {
        'pt': 0,
        'bike': 0,
        'scooter': 0,
        'car': 0,  # RRive
        'walk': 0,
    }

    completed_bookings_count = 0
    completed_bookings_distance_km = 0
    completed_bookings_duration = datetime.timedelta(minutes=0)

    for b in bookings:
        if b.state not in {BookingState.canceled, BookingState.created, BookingState.planned}:
            completed_bookings_count += 1
            completed_bookings_distance_km += (b.get_distance()[1] or 0.0)/1000.0
            if b.end_time and b.start_time:
                completed_bookings_duration += b.end_time-b.start_time


        if b.trip_mode == OptionType.sharing:
            if b.vehicle and b.vehicle.vehicle_type in {VehicleType.scooter, VehicleType.bike}:
                bookings_per_mode[b.vehicle.vehicle_type] += 1
            else:
                logger.warning(f"Unaccounted for vehicle or vehicle_type in '{b.vehicle}'")
        elif b.trip_mode == OptionType.own_bike:
            bookings_per_mode['bike'] += 1
        elif b.trip_mode == OptionType.own_scooter:
            bookings_per_mode['scooter'] += 1
        elif b.trip_mode in {OptionType.rriveUse, OptionType.rriveOffer}:
            bookings_per_mode['car'] += 1
        else:
            if b.trip_mode in bookings_per_mode:
                bookings_per_mode[b.trip_mode] += 1
            else:
                logger.warning(f"Unaccounted for trip_mode in '{b}': {b.trip_mode}")
    
    count = sum(bookings_per_mode.values())
    booking_percentage_per_mode = {
        k: v/count*100.0 if count else 0.0 for k, v in bookings_per_mode.items()
    }
    scored_users = BackendUser.objects.filter(
        email_is_verified=True,
        score_points__gt=0,
        score_experience__gt=0,
    )
    leaderboard = scored_users.order_by('-score_points')[:100]

    if not request.user.score_points:
        rank = 0
    else:
        rank = 1+scored_users.filter(score_points__gt=request.user.score_points).count()

    leaderboard_formatted = []
    for lb in leaderboard:
        if not lb.last_name:
            leaderboard_formatted.append(('-', lb.score_experience, lb.score_points))
        else:
            leaderboard_formatted.append((lb.last_name.split(' ')[0], lb.score_experience, lb.score_points))
    return 200, UserStatisticsResponse(
        completed_bookings_count=completed_bookings_count,
        completed_bookings_distance_km=completed_bookings_distance_km,
        completed_bookings_duration_hour=completed_bookings_duration.total_seconds()/3_600,
        completed_bookings_co2e_reduction_g=sum(wallet_reductions),
        experience=request.user.score_experience,
        points=request.user.score_points,
        rank=rank,
        booking_percentage_per_mode=booking_percentage_per_mode,
        leaderboard=leaderboard_formatted,
    )



@router.post("/feedback", response={
    200: MsgResponse,
    400: ErrorResponse,
    401: TokenNotValidResponse,
},
             tags=['user'], summary="Send a feedback message to the operator", description="")
def post_user_feedback(request: HttpRequest, data: FeedbackRequest):
    if not request.user.is_authenticated:
        return 401, TokenNotValidResponse(error="NO_TOKEN")
    # noinspection PyTypeChecker
    user: BackendUser = request.user
    booking = None
    try:
        ride_id = (data.rideData or {}).get('id')
        if ride_id:
            booking = Booking.objects.get(id=int(ride_id))
            if booking.user != user:
                logger.warning(f"Removed fake booking ID {booking.id} which is not for user {user.id}")
                booking = None
    except (ValueError, Booking.DoesNotExist):
        logger.warning(f"Could not find booking from '{data.rideData}'")
    UserFeedback.objects.create(user=user, text=data.feedbackText, booking=booking, vote=data.vote)
    if settings.EMAIL_OPERATOR_ADDRESSES:
        # noinspection PyBroadException
        try:
            metadata = {
                "subject": f"Feedback from {user.email}"+(" (unverified!)" if user.email_is_verified else ""),
                "message": data.feedbackText,
                "user": f"""Name '{user.last_name}' E-Mail '{user.email}' {'(verified)' if user.email_is_verified else '(unverified!)'} ID {user.id}""",
                "booking": str(booking) if booking else "",
                "vote": {'up': '👍', 'down': '👎', 'neutral': '-'}.get(data.vote, '<invalid value>'),
            }
            if booking:
                metadata['booking'] = str(booking)
            send_email_template(settings.EMAIL_FROM_ADDRESS, settings.EMAIL_OPERATOR_ADDRESSES, 'FEEDBACK', metadata)
        except:
            logger.exception(f"Failed to send email for feedback")


    return 200, MsgResponse(msg='OK')
