# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only
FROM debian:bookworm
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*
RUN curl -sSfL -o /tmp/protoc.zip \
    https://github.com/protocolbuffers/protobuf/releases/download/v27.1/protoc-27.1-linux-x86_64.zip \
    && sha256sum /tmp/protoc.zip | grep -i -q 8970E3D8BBD67D53768FE8C2E3971BDD71E51CFE2001CA06DACAD17258A7DAE3 \
    && unzip -d /usr/local /tmp/protoc.zip "bin/*" "include/*" \
    && ls -lR /usr/local/bin /usr/local/include/google/ \
    && rm /tmp/protoc.zip
# Keep versions in sync with ../src/requirements.txt
RUN python3 -mpip install --break-system-packages grpcio==1.71.0 grpcio-tools==1.71.0
ENV PATH="$PATH:/usr/local/bin"