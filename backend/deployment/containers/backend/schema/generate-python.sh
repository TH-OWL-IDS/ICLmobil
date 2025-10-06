#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

set -euo pipefail
SCRIPTDIR="$(dirname "$(realpath "$0")")"

mkdir -p "${SCRIPTDIR}/../generated/protos/"

function cleanup() {
    rm -f "$SCRIPTDIR/iid"
}

trap "exit_code=\$?; cleanup \$exit_code; kill 0" EXIT
docker build --iidfile "$SCRIPTDIR/iid" "$SCRIPTDIR"
echo "Build complete: $(cat "$SCRIPTDIR/iid")"
cp -r "${SCRIPTDIR}/protos" "${SCRIPTDIR}/../generated/"
if docker run --rm -i \
    -v "${SCRIPTDIR}/../generated:/output" \
    "$(cat "$SCRIPTDIR/iid")" \
    bash -xc 'cd /output && ls -lRa . ; python3 -m grpc_tools.protoc -I .  --grpc_python_out=. --python_out=. --pyi_out=. protos/*.proto' \
; then
        find "${SCRIPTDIR}/../generated/" -type f -name "*.proto" -delete
        echo "SUCCESS"
else
        echo "FAILED"
        exit 1
fi
