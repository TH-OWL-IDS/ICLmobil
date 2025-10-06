#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -euo pipefail

for c in /etc/nginx/*.conf.TEMPLATE  ; do
    STEM="$(sed -E 's#^.*/(.*).TEMPLATE#\1#' <<< "$c")"
    # shellcheck disable=SC2016
    envsubst '$CLUSTER_FQDN $HTTPS_PORT $PUBLIC_URL' < "/etc/nginx/${STEM}.TEMPLATE" > "/etc/nginx/${STEM}"
done
if ! [[ $CLUSTER_WITH_CERTIFICATES == yes ]] ; then
    echo > /etc/nginx/ssl.conf
fi
find /etc/nginx -name "*.conf" -exec sed "s#^#{}: #" "{}" \;
