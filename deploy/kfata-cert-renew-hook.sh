#!/usr/bin/env bash
set -euo pipefail
if [ "${RENEWED_LINEAGE:-}" = /etc/letsencrypt/live/kfata.elsaidy.org ]; then
    nginx -t
    systemctl reload nginx
fi
