#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -eo pipefail
SCRIPTDIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

cd "$SCRIPTDIR/.."

COMPOSE_OPTIONS=( down --remove-orphans )
if [[ "${BASH_ARGV[*]}" == *"--remove-volumes"* ]] ; then
    COMPOSE_OPTIONS+=( --volumes )
fi

docker compose "${COMPOSE_OPTIONS[@]}"
