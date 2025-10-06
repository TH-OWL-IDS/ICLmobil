# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import logging

from django.http import HttpRequest, HttpResponse
from ninja import Router, Schema

from backend.api_v1.schemas import ErrorResponse
from backend.file_v1.utils import BinaryDataResponse
from backend.models import BackendUser

router = Router()

logger = logging.getLogger(__name__)


@router.get("/getProfileImage/{userID}",
            response={
                200: BinaryDataResponse,
                404: ErrorResponse,
                500: ErrorResponse,
            },
            tags=['file_public'],
            summary="Get image for user with Content-Type image/jpeg or image/png")
def get_profile_image(request: HttpRequest, response: HttpResponse, userID: str):
    try:
        user = BackendUser.objects.get(id=int(userID))
    except (ValueError, BackendUser.DoesNotExist):
        response.headers['Content-Type'] = 'application/json'
        return 404, ErrorResponse(error=f"No user with ID '{userID}'")

    if not user.profile_image_data or not user.profile_image_mimetype:
        response.headers['Content-Type'] = 'application/json'
        return 404, ErrorResponse(error="No image available")

    if user.profile_image_mimetype in BackendUser.ImageFormats.labels:
        content_type = user.profile_image_mimetype
    else:
        try:
            content_type = BackendUser.ImageFormats[user.profile_image_mimetype].label
        except KeyError:
            logger.exception(f"User '{user}' has invalid profile_image_mimetype '{user.profile_image_mimetype}'")
            return 500, ErrorResponse(error="Invalid image data")

    response.headers['Content-Type'] = content_type

    binary_data = BinaryDataResponse(data=user.profile_image_data,
                                     mime_type=str(content_type))
    return 200, binary_data

