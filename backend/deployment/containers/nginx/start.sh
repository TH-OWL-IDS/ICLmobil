#!/bin/bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -exo pipefail
SCRIPTDIR="$(dirname "$(realpath "$0")")"
source /common

if [[ $CLUSTER_LETS_ENCRYPT_CERTIFICATES == yes ]] ; then
    CLUSTER_CERTIFICATES_SELF_SIGNED=no
else
    if ! [[ $CLUSTER_CERTIFICATES_SELF_SIGNED == yes ]] ; then
        error "Either set CLUSTER_LETS_ENCRYPT_CERTIFICATES or CLUSTER_CERTIFICATES_SELF_SIGNED to yes"
    else
        CLUSTER_LETS_ENCRYPT_CERTIFICATES=no
    fi
fi

set -u

export TLS=/userdata/certificates/certs
BYOC=/certs
export PUBLIC_HOSTNAME_FQDN=${CLUSTER_FQDN}
export PUBLIC_HOSTNAME=${PUBLIC_HOSTNAME_FQDN}
if [ ${#PUBLIC_HOSTNAME_FQDN} -gt 64 ]; then
    PUBLIC_HOSTNAME=${PUBLIC_HOSTNAME_FQDN%%.*}
fi
info "Public hostname is '${PUBLIC_HOSTNAME}'"

LECERTS_PROD=/userdata/certificates/letsencrypt/production
LECERTS_DOMAIN_DIRECTORY="$LECERTS_PROD/live/$PUBLIC_HOSTNAME_FQDN"
LECERTS_PROD_LAST_FAILURE_FILE="$LECERTS_PROD/last_fail"
LECERTS_STAGING="$(mktemp -d --tmpdir staging-XXXXXX)"
LECERTS_TEMP=/userdata/certificates/letsencrypt/temp
mkdir -p "$LECERTS_PROD" "$LECERTS_STAGING" "$LECERTS_TEMP"

I_AM_CERTIFICATE_CONTROLLER=1

mkdir -p "$TLS"
if [[ "${CLUSTER_WITH_CERTIFICATES}" == "yes" ]] ; then
    if [[ "${CLUSTER_CERTIFICATES_SELF_SIGNED}" == "yes" ]] || [[ $CLUSTER_LETS_ENCRYPT_CERTIFICATES == yes ]] ; then
        info "Preparing self-signed certificates"
        if ! lckdo -W 60 "$TLS/.certificate-processing.lock" /usr/local/bin/prepare-self-signed-certs.sh "$TLS" ; then
            error "Failed preparing self-signed certificates"
        fi
        info "Self-signed certificates prepared"
    fi
    if [[ "${CLUSTER_CERTIFICATES_SELF_SIGNED}" == "yes" ]]; then
        # Avoid corrupted certificate files.
        cp "$TLS/server.crt" /etc/nginx/server.crt
        cp "$TLS/server.key" /etc/nginx/server.key
        cp "$TLS/ca.crt" /etc/nginx/ca.crt
    elif [[ $CLUSTER_LETS_ENCRYPT_CERTIFICATES == yes ]] ; then
        info "Configured for Let's Encrypt certificates"
        if ! [[ -d $LECERTS_DOMAIN_DIRECTORY ]] ; then
            info "No Let's Encrypt certifcates found"
            # Temporary webserver must be started on all master nodes since the nginx-0 pod does not need to end up on -ma1
            info "Starting temporary webserver"
            bash -c "cd $LECERTS_TEMP && python3 -mhttp.server 80" &
            SERVER_PID=$!

            # Only run certbot on one (the first) node
            if [[ $I_AM_CERTIFICATE_CONTROLLER == 1 ]] ; then
                info "Testing using the staging environment"
                /usr/local/bin/certbot-initial.sh staging "$LECERTS_STAGING" "$LECERTS_TEMP"
                if [[ -f $LECERTS_PROD_LAST_FAILURE_FILE ]] ; then
                    LAST_FAILURE_AGE_SECONDS=$(($(date +%s) - $(date +%s -r "$LECERTS_PROD_LAST_FAILURE_FILE")))
                    if (( LAST_FAILURE_AGE_SECONDS < 900)) ; then
                        info "Getting Let's Encrypt production certificates failed $LAST_FAILURE_AGE_SECONDS seconds ago."
                        info "To avoid hitting the rate limiting, at least 15min must pass after the failed attempt."
                        info "If you want to bypass this limit, delete the file $LECERTS_PROD_LAST_FAILURE_FILE and let this pod restart."
                        error "Delay for Let's Encrypt rate limiting not up yet."
                    fi
                fi
                info "Staging was successful, trying to request production certificates"
                if ! /usr/local/bin/certbot-initial.sh production "$LECERTS_PROD" "$LECERTS_TEMP" ; then
                    touch $LECERTS_PROD_LAST_FAILURE_FILE
                    error "Let's Encrypt PROD FAILED. Waiting a long time for admin to react - running this multiple times will "
                fi
            else
                while ! [[ -d $LECERTS_DOMAIN_DIRECTORY ]] ; do
                    info "Not first pod, waiting for Let's Encrypt certificates"
                    sleep 5
                done
            fi
            kill -9 $SERVER_PID
        fi
        info "Let's Encrypt certificates found."
        # keep in sync with periodic reloading below
        cp "$LECERTS_PROD/fullchain.pem" /etc/nginx/server.crt
        cp "$LECERTS_PROD/privkey.pem" /etc/nginx/server.key
        cp "$LECERTS_PROD/options-ssl-nginx.conf" /etc/nginx/
        cp "$LECERTS_PROD/ssl-dhparams.pem" /etc/nginx/
        rm "$LECERTS_PROD_LAST_FAILURE_FILE" > /dev/null 2>&1 || true
        # CA with intermediates is included in fullchain.pem
        rm /etc/nginx/ca.crt > /dev/null 2>&1 || true
    else
        if [[ -f "$BYOC/ca.crt" ]] && [[ -f "$BYOC/server.crt" ]] && [[ -f "$BYOC/server.key" ]] ; then
            info "Using bring-your-own certificates from certs-configmap."
            ls -lR "$BYOC"
            cp "$BYOC/server.crt" /etc/nginx/server.crt
            cp "$BYOC/server.key" /etc/nginx/server.key
            cp "$BYOC/ca.crt" /etc/nginx/ca.crt
        elif [[ -f "$TLS/ca.crt" ]] && [[ -f "$TLS/server.crt" ]] && [[ -f "$TLS/server.key" ]] ; then
            info "Using bring-your-own certificates from /userdata/.../ha/certificates/certs/"
            ls -lR "$TLS"
            cp "$TLS/server.crt" /etc/nginx/server.crt
            cp "$TLS/server.key" /etc/nginx/server.key
            cp "$TLS/ca.crt" /etc/nginx/ca.crt
        else
            error "Cannot find ca.crt, server.crt in key in neither '$BYOC' nor '$TLS'"
        fi
    fi
fi
ls -lR $TLS
ls -lR /etc/nginx/

if [[ $CLUSTER_LETS_ENCRYPT_CERTIFICATES == yes ]] ; then
    mkdir -p /userdata/certificates/letsencrypt/temp/.well-known/acme-challenge/
    bash -c "sleep 600 ; while true ; do echo 'Renewing periodically' ; /usr/local/bin/certbot-renew.sh /userdata/certificates/letsencrypt/production /userdata/certificates/letsencrypt/temp/.well-known ; sleep 86400 ; done" &
    bash -c "sleep 800 ; while true ; do echo 'Reloading periodically to pick up potentially renewed certificates' ; cp '$LECERTS_PROD/fullchain.pem' /etc/nginx/server.crt ; cp "$LECERTS_PROD/privkey.pem" /etc/nginx/server.key ; nginx -s reload ; sleep 3600 ; done" &
fi

exec nginx-debug -g "daemon off;"
#exec nginx -g "daemon off;"

