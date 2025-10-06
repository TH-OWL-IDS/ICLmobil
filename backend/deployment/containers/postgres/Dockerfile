# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
# FROM postgres:15
FROM postgis/postgis:15-3.4
RUN localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8
ENV LANG de_DE.utf8
COPY docker-initdb-or-bust.sh /usr/local/bin/docker-initdb-or-bust.sh
COPY docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
RUN sed -i 's/"$.psql.@.."/psql -v ON_ERROR_STOP=1 --username postgres --no-password --no-psqlrc/' \
    /docker-entrypoint-initdb.d/10_postgis.sh
RUN chmod +x \
    /docker-entrypoint-initdb.d/*.sh \
     /usr/local/bin/docker-initdb-or-bust.sh
RUN useradd --uid 5432 -m user \
    && mkdir /db \
    && chown 5432 /db
USER user
ENTRYPOINT ["docker-initdb-or-bust.sh"]
CMD ["postgres", \
"-c", "shared_buffers=512MB",  \
"-c", "wal_level=logical", \
"-c", "archive_mode=off", \
"-c", "max_connections=200"]

