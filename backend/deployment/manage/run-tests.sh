#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

# Run like this to only test with one file:
#     manage/run-tests.sh backend/tests/test_phone_number.py

# Note for manual testing *without* this script (e.g. in development):
# Start normal docker-compose deployment
# docker compose exec backend bash -o pipefail -ec 'export POSTGRES_BACKEND_USERNAME=postgres ; export POSTGRES_BACKEND_PASSWORD=$POSTGRES_PASSWORD ;env | grep POSTG ; pytest -s'

set -eo pipefail
SCRIPTDIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
BASEDIR="${SCRIPTDIR}/.."

cd "$BASEDIR"

info() {
    echo -e "$(date +"[%Y-%m-%d %H:%M:%S]") INFO: $(basename $0): $1"
}

if ! [[ -f .env ]] ; then
    cp env.sample .env
    sed -i -e 's/__PUBLIC_FQDN__/localhost/g' .env
fi

[[ -f env.global ]] && source env.global

if ! sudo id >/dev/null 2>&1 ; then
    info "Sorry, we need to become root via sudo for cleanup."
    exit 1
fi

TEMP_DIR="$(mktemp --directory --tmpdir testing.XXXX)/"


function cleanup()
{
    docker compose down --remove-orphans --volumes -t 0 || true
    info "Restoring .env"
    set +u
    set +e
    if [[ $1 != 0 ]] ; then
        FAILED_TEMP="$(mktemp -t .env.failed.XXXXXX)"
        info "Leaving copy of last .env as $FAILED_TEMP"
        cp "${BASEDIR}/.env" "$FAILED_TEMP"
    fi
    if [[ -d "$TEMP_DIR" ]] ; then
        info "Removing temporary directory $TEMP_DIR"
        sudo rm -rf "$TEMP_DIR"
    fi
    mv "${BASEDIR}/.env.pre" "${BASEDIR}/.env"
    if [[ $1 != 0 ]] ; then
        info "ERROR - see above"
        kill 0
    else
        exit 0
    fi
}


info "Moving your .env to the side"
rm -f "${BASEDIR}/.env.pre"
mv "${BASEDIR}/.env" "${BASEDIR}/.env.pre"
trap "exit_code=\$?; cleanup \$exit_code" EXIT

cp env.sample .env
sed -i 's#PUBLIC_URL.*#PUBLIC_URL=https://localhost/#' .env
sed -i 's#CLUSTER_FQDN.*#CLUSTER_FQDN=localhost#' .env
sed -i "s#USERDATA_BASEDIR.*#USERDATA_BASEDIR=$TEMP_DIR#" .env
sed -i -r 's#(POSTGRES_PASSWORD|POSTGRES_BACKEND_PASSWORD)=.*#\1=passwordpasswordpassword#' .env
echo -e '\nBACKEND_ADMIN_PASSWORD=passwordpasswordpassword' >> .env
echo "TESTING_IN_PROGRESS=1" >> .env
echo "HTTP_PORT=47080" >> .env
echo "HTTPS_PORT=47443" >> .env

sed -i "s#COMPOSE_PROJECT_NAME.*#COMPOSE_PROJECT_NAME=iclmobil-testing#" .env
echo "COMPOSE_FILE='docker-compose.yml:docker-compose.no-volumes.yml'" >> .env

info "Building"
"${BASEDIR}/manage/build.sh"
info "Starting"
bash "${BASEDIR}/manage/start.sh" --no-volumes
START=$SECONDS
while ! "${BASEDIR}/manage/status.sh" ; do
    if (( SECONDS - START > 240 )) ; then
        echo "TIMEOUT waiting for all containers to be healthy"
        exit 1
    fi
    echo "Waiting for all containers to be healthy"
    sleep 4
done

info "Granting test permissions to user"
docker compose exec db sh -c 'psql --user=postgres -c "ALTER USER backend SUPERUSER;"'

info "Starting tests"
docker compose exec backend pytest -s "$@"

info "Stopping"
"${BASEDIR}/manage/stop.sh" --remove-volumes





