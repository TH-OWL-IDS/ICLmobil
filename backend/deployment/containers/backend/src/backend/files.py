# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
import glob
import os
import tempfile
from typing import BinaryIO

import magic
from django.core.files import File as DjangoFile
from filer.models import Folder, Image, File

from backend.utils import logger


def get_mime_type(f: BinaryIO) -> str:
    initial_pos = f.tell()
    f.seek(0)
    mime_type = magic.from_buffer(f.read(2048), mime=True)
    f.seek(initial_pos)
    return mime_type


def filer_upload_local_file(filename: str, folder: Folder):
    """Uploads local file 'filename' if no file with this name is already in the folder."""
    assert os.path.isfile(filename), f"Expected '{filename}' to be a local file"
    name = os.path.split(filename)[-1]
    if File.objects.filter(name=name, folder=folder).exists():
        logger.debug(f"File with name '{name}' already exists in folder '{folder}'")
        return
    with open(filename, 'rb') as f:
        content = f.read()
    mime_type = magic.from_buffer(content, mime=True)

    with tempfile.NamedTemporaryFile('w+b', delete=True) as img_temp:
        img_temp.write(content)
        img_temp.flush()
        logger.debug(f"Adding image '{name}' to folder '{folder}' mime-type '{mime_type}' from file '{filename}'")
        im = Image.objects.create(file=DjangoFile(img_temp, name=name), name=name, folder=folder,
                                  original_filename=name)
        im.mime_type = mime_type
        im.save()


def filer_upload_all_from_folder(path: str, folder: Folder):
    for filename in glob.glob(os.path.join(path, "*")):
        if os.path.isfile(filename):
            filer_upload_local_file(filename, folder)


def filer_add_image_from_data(data: bytes, filename: str, folder: Folder) -> Image:
    mime_type = magic.from_buffer(data, mime=True)
    with tempfile.NamedTemporaryFile('w+b', delete=True) as img_temp:
        img_temp.write(data)
        img_temp.flush()
        logger.debug(f"Adding image '{filename}' to folder '{folder}' mime-type '{mime_type}' from file '{filename}'")
        im = Image.objects.create(file=DjangoFile(img_temp, name=filename), name=filename, folder=folder,
                                  original_filename=filename)
        im.mime_type = mime_type
        im.save()
    return im
