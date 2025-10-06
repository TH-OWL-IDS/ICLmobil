# syntax=docker/dockerfile:1
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

# "acme<2"
FROM nginx:1.27.1
RUN apt update \
    && apt dist-upgrade -y --auto-remove \
    && apt install -y python3 python3-pip python3-venv openssl net-tools procps vim moreutils libaugeas0 dnsutils netcat-openbsd \
    && python3 -mvenv /opt/certbot \
    && /opt/certbot/bin/python3 -mpip install --upgrade pip \
    && /opt/certbot/bin/python3 -mpip install certbot certbot-nginx \
    && /opt/certbot/bin/certbot --version \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#ADD https://github.com/nginx/njs-acme/releases/download/v1.0.0/acme.js /usr/lib/nginx/njs_modules/acme.js
#RUN sha256sum /usr/lib/nginx/njs_modules/acme.js | grep -q -i 1AEFB709AFC2ED81C07FBC5F6AB658782FE99E88569EE868E25D3A6F1E5355CB
COPY *.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

COPY *.conf.TEMPLATE /etc/nginx/
COPY common /
#RUN mkdir /etc/nginx/njs-acme
#RUN chown nginx: /etc/nginx/njs-acme

ENV CLUSTER_WITH_CERTIFICATES=yes
ENV CLUSTER_CERTIFICATES_SELF_SIGNED=yes
CMD ["bash", "-c", "/usr/local/bin/render-config.sh && /usr/local/bin/start.sh"]