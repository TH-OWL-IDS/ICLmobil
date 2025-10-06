# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

FROM python:3.11-slim-bookworm


# ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y \
       binutils \
       bsdmainutils \
       curl \
       gdal-bin \
       iproute2 \
       jq \
       libmagic1 \
       libmemcached-tools \
       libproj-dev \
       netcat-openbsd \
       postgresql-client-15 \
       procps \
       pwgen \
    && apt-get clean

WORKDIR /app/src
RUN useradd -m -u 1000 user
RUN mkdir static/ \
    && chown 1000 static

COPY vendor /vendor
COPY src/requirements.txt /app/src/requirements.txt
RUN python3 -mpip install --no-cache-dir --upgrade pip wheel setuptools \
    && python3 -mpip install --no-cache-dir /vendor/pyphoton \
    && python3 -mpip install --no-cache-dir -r /app/src/requirements.txt \
    && python3 -mpip check

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

COPY src /app/src
COPY generated/protos /app/src/protos
RUN python -m compileall .
RUN python manage.py collectstatic --no-input

RUN mkdir /storage \
    && chown user:user /storage

USER user

CMD ["/app/start.sh"]