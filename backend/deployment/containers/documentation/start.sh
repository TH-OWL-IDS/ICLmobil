#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
set -eo pipefail

cd /docs
envsubst < /docs/mkdocs.TEMPLATE.yml > /mkdocs.yml
sed 's/^/mkdocs.yml: /' < /mkdocs.yml
# rm /docs/mkdocs.TEMPLATE.yml
mkdocs serve --config-file /mkdocs.yml --dev-addr 0.0.0.0:8300
