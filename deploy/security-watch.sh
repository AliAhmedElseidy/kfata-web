#!/usr/bin/env bash
# A host-local alert. Thresholds count sanitized application events only.
set -euo pipefail
cd /opt/kfata-web
events="$(docker compose logs --no-color --since=5m --tail=4000 web 2>&1)"
failures="$(grep -c -E 'KFATA_SECURITY .*event=admin_(password|otp)_failure' <<< "$events" || true)"
errors="$(grep -c 'KFATA_SECURITY .*event=http_server_error' <<< "$events" || true)"
if (( failures >= 10 || errors >= 5 )); then
    printf 'KFATA security alert: auth failures=%s; server errors=%s (5 min)\n' "$failures" "$errors" >&2
    exit 1
fi
