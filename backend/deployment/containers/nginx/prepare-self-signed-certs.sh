#!/bin/bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -euxo pipefail
source /common

cd "$TLS"

DONE_FILE="${TLS}/.done.${PUBLIC_HOSTNAME}.${PUBLIC_HOSTNAME_FQDN}"

if ! [[ -f "${DONE_FILE}" ]]; then
    info "Creating certificates for '${PUBLIC_HOSTNAME}'"
    # Create a minimal CA-infrastructure with a server.
    # SSL cert creation fails if CN is more than 64 characters => SAN certificate
    HOSTLIST="${PUBLIC_HOSTNAME} ${PUBLIC_HOSTNAME_FQDN}" IPLIST="" /usr/local/bin/generate-CA.sh "${PUBLIC_HOSTNAME}"
    /usr/local/bin/generate-CA.sh client client
    chmod +r client.key
    cp "${PUBLIC_HOSTNAME}.crt" server.crt
    cp "${PUBLIC_HOSTNAME}.key" server.key
    # https://github.com/spujadas/elk-docker/issues/112
    openssl pkcs8 -in server.key -topk8 -nocrypt -out server.p8
    tar -cvf client-certificates.tar ca.crt client.crt client.key
    # curl e.g. healthcheck
    cat "${PUBLIC_HOSTNAME}.crt" "${PUBLIC_HOSTNAME}.key" > "${PUBLIC_HOSTNAME}.pem"
    touch "${DONE_FILE}"
else
    info "Using existing self-signed certificates."
    if ! { [[ -s "${TLS}/server.crt" ]] && [[ -s "${TLS}/server.key" ]] ; } ; then
        info "Repairing damaged server.crt/key."
        ls -lR "$TLS"
        cd "$TLS"
        cp "${PUBLIC_HOSTNAME}.crt" server.crt
        cp "${PUBLIC_HOSTNAME}.key" server.key
        cat "${PUBLIC_HOSTNAME}.crt" "${PUBLIC_HOSTNAME}.key" > "${PUBLIC_HOSTNAME}.pem"
        ls -lR "$TLS"
    fi
fi
mkdir -p "$TLS/clients"