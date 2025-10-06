# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

from django.core.validators import EMPTY_VALUES
from django.template.loaders.filesystem import Loader as FilesystemLoader
from django.template.utils import get_app_template_dirs
from django.urls import Resolver404, resolve

from backend.middleware import _thread_data


class UnfoldAdminLoader(FilesystemLoader):
    def _has_unfold_dir(self, template_dir):
        request = getattr(_thread_data, "request", None)

        if not request or request.path in EMPTY_VALUES:
            return False

        try:
            if "admin" in resolve(request.path).namespaces:
                for dir in template_dir.iterdir():
                    if dir.name == "unfold":
                        return True
        except Resolver404:
            pass

        return False

    def get_dirs(self):
        template_dirs = []

        for template_dir in get_app_template_dirs("templates"):
            if not self._has_unfold_dir(template_dir):
                template_dirs.append(template_dir)

        return template_dirs