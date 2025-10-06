#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -eo pipefail
SCRIPTDIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

cd "$SCRIPTDIR/.."

source .env
export DOCKER_BUILDKIT=1

if [[ $# == 0 ]] ; then
    docker compose --progress plain build
else
    # --parallel 1 build --progress plain
    docker compose "$@"
fi
