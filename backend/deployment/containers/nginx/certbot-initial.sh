#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -exo pipefail
source /common

set -u

ENVIRONMENT="$1"
HOMEDIR="$2"
WEBROOTDIR="$3"

info "Using certbot to request certificate for domain $PUBLIC_HOSTNAME_FQDN from Let's Encrypt environment $ENVIRONMENT with files put into $HOMEDIR"

mkdir -p "$WEBROOTDIR/.well-known"
UUID="$(python3 -c "import uuid;print(uuid.uuid4())")"
echo UUID_WAS_FOUND > "$WEBROOTDIR/.well-known/$UUID"
cat <<EOF > "$WEBROOTDIR/index.html"
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Temporary website</title>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
  </head>
  <body>
    Temporary website. $UUID
    <script type="text/javascript">
    setTimeout(function () {
        location.reload()
    }, 5000);
    </script>
  </body>
</html>
EOF

# We need to do this step for the case where an external load balancer needs to detect
info "Trying to access from the public side."
START_TIME="$(date +%s)"
while true ; do
    URL="http://$PUBLIC_HOSTNAME_FQDN/.well-known/$UUID"
    info "Requesting $URL with Host: $PUBLIC_HOSTNAME_FQDN"
    BODY="$(curl -v "$URL" 2>&1 || true)"
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

OPTIONS=(--config-dir "$HOMEDIR" --register-unsafely-without-email --agree-tos -n)
if ! [[ $ENVIRONMENT == production ]] ; then
    OPTIONS+=(--staging)
fi

# Use nginx configuration files from certbot-nginx package
SITE_PACKAGES="$(/opt/certbot/bin/python3 -c 'import site; print(" ".join(site.getsitepackages()))')"
# shellcheck disable=SC2086
find $SITE_PACKAGES -name options-ssl-nginx.conf -print -exec cp "{}" "$HOMEDIR/" \; 2> /dev/null || true
# shellcheck disable=SC2086
find $SITE_PACKAGES -name ssl-dhparams.pem -print -exec cp "{}" "$HOMEDIR/" \; 2> /dev/null || true

if /opt/certbot/bin/certbot "${OPTIONS[@]}" certonly --webroot -w "$WEBROOTDIR" -d "$PUBLIC_HOSTNAME_FQDN" ; then
    ls -lR "$HOMEDIR"
    info "Success getting certificate"
    cd "$HOMEDIR"
    # Make it more convenient to find the certificate (without knowing the domain)
    for relname in "live/$PUBLIC_HOSTNAME_FQDN/"*.pem ; do
        FILENAME="$(basename "$relname")"
        ln -sf "$relname" "./$FILENAME"
    done
    # Prepare the root CA certificate (last in the chain) used to sign our certificate.
    awk '/-----BEGIN CERTIFICATE-----/{rec=""; f=1} f{rec=rec $0 ORS} /-----END CERTIFICATE-----/{f=0} END{printf "%s", rec}' \
        < fullchain.pem \
        > ca.pem
    info "Root CA follows"
    openssl x509 -in ca.pem -text -noout
    if ! openssl x509 -in ca.pem -text -noout | grep -Eq " *CA:TRUE($|, pathlen)" ; then
        error "Could not assure that this is actually a root CA certificate"
    fi
else
    ls -lR "$HOMEDIR"
    info "Failed getting certificate. Sleeping some time to avoid triggering the staging environments rate limits."
    # Error might be in registration of new accountsm, which hass pretty aggressive rate limits even in staging (50/3h)
    # https://letsencrypt.org/docs/staging-environment/#rate-limits
    sleep 300
    error "Failed getting certificate"
fi
