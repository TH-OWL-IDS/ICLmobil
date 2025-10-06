# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
FROM python:3.12-alpine
EXPOSE 8888
RUN apk add curl tini bash envsubst

RUN pip install --root-user-action=ignore --no-cache-dir --upgrade pip \
    && pip install --root-user-action=ignore --no-cache-dir \
        mkdocs==1.6.1 \
        mkdocs-d2-plugin==1.5.0 \
        mkdocs-mermaid2-plugin==1.1.1 \
        mkdocs-drawio-file==1.5.2 \
    && pip check

ADD start.sh /start.sh
RUN chmod +x /start.sh

ADD docs /docs
RUN addgroup -S user && adduser -D user -G user \
    && touch /mkdocs.yml \
    && chown -R user:user /docs /mkdocs.yml
USER user

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
