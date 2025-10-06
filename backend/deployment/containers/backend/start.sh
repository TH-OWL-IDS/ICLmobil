#!/bin/bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -eo pipefail

SCRIPTDIR="$(dirname "$(realpath "$0")")"

export PYTHONUNBUFFERED=1


info() {
    echo -e "$(date +"[%Y-%m-%d %H:%M:%S]") INFO: $(basename $0): $1"
}

error() {
    echo -e "$(date +"[%Y-%m-%d %H:%M:%S]") ERROR: $(basename $0): $1"
    exit 1
}

if [[ -f "$SCRIPTDIR/.env" ]] ; then
    # May define VIRTUAL_ENV
    info "Sourcing $SCRIPTDIR/.env"
    source "$SCRIPTDIR/.env"
fi


DEBUG="${DEBUG:-no}"
VIRTUAL_ENV="${VIRTUAL_ENV}"

if [[ -z "$STORAGE_DIR" ]] ; then
    USERDATA="$(realpath -m "${SCRIPTDIR}/../../../../userdata/backend")"
    if [[ -d "$USERDATA" ]] ; then
        STORAGE_DIR="${USERDATA}"
    fi
fi

set -u

cd "${SCRIPTDIR}/src"

if ! [[ -d "${STORAGE_DIR}" ]] ; then
    info "Please set environment variable STORAGE_DIR to a persistent storage directory or create the following directory:"
    info "   mkdir -p '$USERDATA'"
    error "See above"
fi

# export DB_FILENAME="${STORAGE_DIR}/backend.sqlite"

# Generate a fresh secret initially
if ! [[ -f "${STORAGE_DIR}/secret.txt" ]] || [[ -s "${STORAGE_DIR}/secret.txt" ]] ; then
    pwgen 70 1 | tr -d '\n' > "${STORAGE_DIR}/secret.txt"
fi
export SECRET_KEY="$(cat "${STORAGE_DIR}/secret.txt")"

if [[ -n ${BACKEND_ADMIN_PASSWORD:-} ]] ; then
    info "Using password from environment variable BACKEND_ADMIN_PASSWORD"
    echo -n "$BACKEND_ADMIN_PASSWORD" > "${STORAGE_DIR}/admin-password.txt"
else
    # Generate a fresh admin password initially
    if ! [[ -f "${STORAGE_DIR}/admin-password.txt" ]] ; then
        pwgen 20 1 | tr -d '\n' > "${STORAGE_DIR}/admin-password.txt"
    fi
fi
if [[ $(stat --printf="%s" "${STORAGE_DIR}/admin-password.txt") -lt 20 ]] ; then
    error "Password too short in: ${STORAGE_DIR}/admin-password.txt"
fi

ADMIN_PASSWORD="$(cat "${STORAGE_DIR}/admin-password.txt" 2>/dev/null || true | tr -d '\n')"

if [[ -f "$VIRTUAL_ENV/bin/python" ]] ; then
    PYTHON="$VIRTUAL_ENV/bin/python"
else
    if [[ -d "${STORAGE_DIR}/venv" ]] ; then
        PYTHON="${STORAGE_DIR}/venv/bin/python"
    else
        if ! [ -f /.dockerenv ]; then
            info "Running locally (not inside Docker container) - please provide virtualenv like this:"
            info "    python3 -mvenv '${STORAGE_DIR}/venv'"
            info "    ${STORAGE_DIR}/venv/bin/python -mpip install -r '${SCRIPTDIR}/src/requirements.txt'"
            error "See above"
        fi
        PYTHON=python
    fi
fi

export PGPASSWORD="$POSTGRES_BACKEND_PASSWORD"
while ! psql -v ON_ERROR_STOP=1 -h db -U backend -d backend -c 'select version();'  > /dev/null 2>&1  ; do
    info "Waiting for DB..."
    sleep 2
done
info "DB is accessible"

if ! "$PYTHON" manage.py makemigrations --check --dry-run --verbosity 3 ; then
    error "Migrations are needed but not included in sources. Check for missing migrations above."
fi

# Migrations suppress the save signal that usually syncs user permissions with GL and friends.
# So this should not yield messages about GL being not ready (and resulting in 500).
info "Running migrations."
"$PYTHON" manage.py migrate --run-syncdb --no-input --fake-initial


# Django collect static files of all apps in STATIC_ROOT
#info "Collecting static files"
#"$PYTHON" manage.py collectstatic --no-input 2>&1 | sed -u 's/^/collectstatic: /'

info "Setting superuser password"
"$PYTHON" add_user.py --superuser -- admin "$ADMIN_PASSWORD" 2>&1 | sed -u 's/^/set password: /'


# Load initial data
# info "Loading initial datasource data to DB."
# bash -c "python manage.py loaddata datahub/initial_data.yaml"

FILTER="^$" # deactivated by default
if [[ "$DEBUG" == "yes" ]] ; then
    info "Dumping known URLs."
    "$PYTHON" manage.py show_urls
else
   FILTER="^.pid.* 200. "
fi
info "Admin password is in '${STORAGE_DIR}/admin-password.txt'"
info "Starting with Python in $PYTHON"
"$PYTHON" -m gunicorn backend.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind=0.0.0.0 \
    2>&1 | grep --line-buffered -v "$FILTER"