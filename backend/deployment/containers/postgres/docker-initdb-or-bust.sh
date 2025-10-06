#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: PostgreSQL
set -Eeuo pipefail

# Copy of docker-enforce-initdb.sh/ docker-ensure-initdb.sh that expects docker-entrypoint-initdb.d scripts to
# create a file "${PGDATA}/../init-scripts-completed" once finished.
# If a DB already exists and that flag file is missing (indicating incomplete init script run), it aborts
# without running the DB.


source /usr/local/bin/docker-entrypoint.sh

# arguments to this script are assumed to be arguments to the "postgres" server (same as "docker-entrypoint.sh"), and most "docker-entrypoint.sh" functions assume "postgres" is the first argument (see "_main" over there)
if [ "$#" -eq 0 ] || [ "$1" != 'postgres' ]; then
        set -- postgres "$@"
fi

# https://github.com/postgis/docker-postgis/issues/360#issuecomment-1722358956
docker_process_sql() {
	local query_runner=( psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --no-password --no-psqlrc )
	if [ -n "${POSTGRES_DB:-}" ]; then
		query_runner+=( --dbname "$POSTGRES_DB" )
	fi

	PGHOST= PGHOSTADDR= "${query_runner[@]}" "$@"
}
psql=( docker_process_sql )
echo "psql: $psql"
export psql

# see also "_main" in "docker-entrypoint.sh"

docker_setup_env
# setup data directories and permissions (when run as root)
docker_create_db_directories
if [ "$(id -u)" = '0' ]; then
        # then restart script as postgres user
        exec gosu postgres "$BASH_SOURCE" "$@"
fi

# only run initialization on an empty data directory
if [ -z "$DATABASE_ALREADY_EXISTS" ]; then
        docker_verify_minimum_env

        # check dir permissions to reduce likelihood of half-initialized database
        ls /docker-entrypoint-initdb.d/ > /dev/null

        docker_init_database_dir
        pg_setup_hba_conf "$@"

        # PGPASSWORD is required for psql when authentication is required for 'local' connections via pg_hba.conf and is otherwise harmless
        # e.g. when '--auth=md5' or '--auth-local=md5' is used in POSTGRES_INITDB_ARGS
        export PGPASSWORD="${PGPASSWORD:-$POSTGRES_PASSWORD}"
        docker_temp_server_start "$@"

        docker_setup_db
        for file in /docker-entrypoint-initdb.d/* ; do sed "s#^#$file: #" < $file ; done
        docker_process_init_files /docker-entrypoint-initdb.d/*

        docker_temp_server_stop
        unset PGPASSWORD
else
        if ! [[ -f "${PGDATA}/../init-scripts-completed" ]] ; then
            echo "Database found in $PGDATA but ${PGDATA}/../init-scripts-completed is missing. Incomplete init?"
            sleep 120
            exit 1
        fi
fi

_main "$@"