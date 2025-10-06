#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -eo pipefail
SCRIPTDIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

cd "$SCRIPTDIR/.."

DC_OUTPUT="$(docker compose ps  --all --format json --no-trunc | jq .)"

TABLE="$(jq --slurp -r '["Service", "State", "Health"], ["-------", "-----", "------"], (.[]| [.Service, .State, .Health]) | @tsv' <<<"$DC_OUTPUT")"
echo "Services overview:"
echo
column -t <<<"$TABLE" | sed 's/^/    /'

SERVICES=$(( $(wc -l <<<"$TABLE" ) - 2 ))

HEALTHY_SERVICES="$(grep -Ec 'running\s+healthy' <<<"$TABLE")"

echo

if (( HEALTHY_SERVICES < SERVICES )) ; then
    echo "Non-healthy services:"
    echo
    column -t <<<"$TABLE" | sed 's/^/    /' | grep -Ev 'running\s+healthy'
    echo
    echo "NOT HEALTHY - see services above"
    exit 1
else
    echo "OK - everything running as expected"
fi