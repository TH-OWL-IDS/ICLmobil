#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -eo pipefail
source /common

set -u

HOMEDIR="$1"
WELL_KNOWN_DIR="$2"
PUBLIC_HOSTNAME_FQDN=${CLUSTER_FQDN}

I_AM_CERTIFICATE_CONTROLLER=1

# Only run certbot on one (the first) pod
if ! [[ $I_AM_CERTIFICATE_CONTROLLER == 1 ]] ; then
    info "Not first pod, nothing to do"
    exit 0
fi

if ! [[ -d "$HOMEDIR/live" ]] ; then
    error "Cannot find $HOMEDIR/live"
fi
if ! [[ -d "$WELL_KNOWN_DIR" ]] ; then
    error "Cannot find webroot $WELL_KNOWN_DIR"
fi

info "Using certbot to try renewing certificate in $HOMEDIR"

find "$WELL_KNOWN_DIR/.." -type f -exec ls -l "{}" \;
UUID="$(python3 -c "import uuid;print(uuid.uuid4())")"
UUID_FILE="$WELL_KNOWN_DIR/acme-challenge/public-access-detection-$UUID"
UUID_URL="http://$PUBLIC_HOSTNAME_FQDN/.well-known/acme-challenge/public-access-detection-$UUID"
echo "UUID_WAS_FOUND" > "$UUID_FILE"

info "Trying to access from the public side."
START_TIME="$(date +%s)"
while true ; do
    info "Requesting $UUID_URL"
    # re --insecure: https://letsencrypt.org/docs/challenge-types/#http-01-challenge
    # "Our implementation of the HTTP-01 challenge follows redirects, up to 10 redirects deep.
    # It only accepts redirects to "http:" or "https:", and only to ports 80 or 443.
    # It does not accept redirects to IP addresses. When redirected to an HTTPS URL,
    # it does not validate certificates (since this challenge is intended to bootstrap valid certificates,
    # it may encounter self-signed or expired certificates along the way)."
    BODY="$(curl --insecure -Lv "$UUID_URL" 2>&1 || true)"
    if [[ $BODY == *UUID_WAS_FOUND* ]] ; then
        info "Access was successful -> public access OK"
        break
    fi
    echo "${BODY/^/    /}"
    info "Failed getting UUID file -> no public access possible (yet?)"
    NOW="$(date +%s)"
    if (( NOW - START_TIME > 300 )) ; then
        error "Failed to be publicly reachable"
    fi
    sleep 10
done

OPTIONS=(--config-dir "$HOMEDIR" -n --disable-renew-updates)

if /opt/certbot/bin/certbot "${OPTIONS[@]}" renew --webroot --webroot-path "$WELL_KNOWN_DIR/.."  ; then
    ls -lR "$HOMEDIR"
    info "Success renewing certificate (or not yet needed)"
else
    ls -lR "$HOMEDIR"
    info "Failed getting certificate. Sleeping some time to avoid triggering the staging environments rate limits."
    sleep 3600 || true
    error "Failed getting certificate"
fi

rm "$WELL_KNOWN_DIR/acme-challenge/public-access-detection-"* || true
