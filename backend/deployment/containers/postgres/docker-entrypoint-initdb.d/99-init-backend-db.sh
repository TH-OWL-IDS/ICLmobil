#!/bin/bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
set -e

if [[ -z $POSTGRES_PASSWORD ]] ; then
    echo "Set POSTGRES_PASSWORD!"
    exit 1
fi

if [[ -z $POSTGRES_BACKEND_USERNAME ]] || [[ -z $POSTGRES_BACKEND_PASSWORD ]]; then
    echo "Set POSTGRES_BACKEND_USERNAME and POSTGRES_BACKEND_PASSWORD!"
    exit 1
fi

echo "Creating DB backend if needed"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE backend;
DO
\$\$
BEGIN
   -- Create the user with a password if the user does not exist
   IF NOT EXISTS (
       SELECT FROM pg_roles
       WHERE rolname = 'backend'
   ) THEN
        RAISE NOTICE 'CREATE USER backend';
       CREATE USER backend WITH PASSWORD '${POSTGRES_BACKEND_PASSWORD?}';
    ELSE
        RAISE NOTICE 'USER backend exists';

   END IF;

    RAISE NOTICE 'GRANTing backend user';
   -- Grant all privileges on the new database to the user
   GRANT ALL PRIVILEGES ON DATABASE backend TO backend;
END
\$\$;
EOSQL
echo "Granting permissions on public schema of backend database"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" backend <<-EOSQL
DO
\$\$
BEGIN
   GRANT ALL ON SCHEMA public TO backend;
END
\$\$;
EOSQL
echo "Creating extension postgis"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" backend <<-EOSQL
CREATE EXTENSION postgis;
SELECT PostGIS_Full_Version();
SELECT * FROM pg_available_extensions WHERE name = 'postgis';
EOSQL
echo "$0 done"
touch "${PGDATA}/../init-scripts-completed"