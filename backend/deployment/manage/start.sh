#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -eo pipefail
SCRIPTDIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

cd "$SCRIPTDIR/.."

if ! [[ -f .env ]] ; then
    cp env.sample .env
    sed -i -e 's/__PUBLIC_FQDN__/localhost/g' .env
fi

[[ -f env.global ]] && source env.global

source .env

if [[ -z "$USERDATA_BASEDIR" ]] ; then
    echo ".env is missing USERDATA_BASEDIR"
    echo "Cannot start"
    exit 1
fi

if [[ "${BASH_ARGV[*]}" == *"--no-volumes"* ]] ; then
    NO_VOLUMES=1
else
    NO_VOLUMES=0
fi

set -u

if [[ $NO_VOLUMES = 0 ]] ; then
    echo "Preparing directories..."
    for subdir in lock backend/storage/media/public backend/storage/media/private db/data ; do
            userdata_dir="${USERDATA_BASEDIR}/${subdir}"
            if ! [[ -d "${userdata_dir}" ]] ; then
                echo "  ... ${userdata_dir}"
                if ! sudo mkdir -p "${userdata_dir}" ; then
                    echo "WARNING: Could not create directory. Consider running: sudo mkdir -p ${userdata_dir}"
                fi
            fi
    done
    echo "Ensuring permissions ..."
    for subdir in backend lock ; do
        echo "  ... ${subdir}"
        chown -R 1000 "${USERDATA_BASEDIR}/${subdir}" 2>/dev/null || sudo chown -R 1000 "${USERDATA_BASEDIR}/${subdir}"
    done
    for subdir in db ; do
        echo "  ... ${subdir}"
        chown -R 5432 "${USERDATA_BASEDIR}/${subdir}" 2>/dev/null || sudo chown -R 5432 "${USERDATA_BASEDIR}/${subdir}"
    done
fi


if docker compose ps | grep -E '.*nginx.*[[:space:]]+Up[[:space:]]' > /dev/null ; then
    echo "Ensuring nginx restart ..."
    # Nginx takes a long time to get fresh DNS entries on spog restart - so we restart it as well
    docker compose stop -t 0 nginx || true
fi

echo "Starting containers ..."
docker compose up -d --remove-orphans
echo "... done"