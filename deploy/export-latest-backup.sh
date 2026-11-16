#!/usr/bin/env bash
# Root-owned, called only by the restricted off-host SSH account.
set -euo pipefail
root=/opt/kfata-web
[[ $# -eq 0 ]]
# Use the same lock as the backup task so retention cannot remove a snapshot
# between checksum verification and streaming.
exec 9<"$root/operations-backup.lock"
flock -s -w 30 9
for snapshot in "$root"/backups/*; do
    name=${snapshot##*/}
    if [[ "$name" =~ ^[0-9]{8}T[0-9]{6}Z$ && -d "$snapshot" && ! -L "$snapshot" && -f "$snapshot/.complete" ]]; then
        latest=$snapshot
    fi
done
[[ -n "${latest:-}" ]] || { echo "No complete KFATA backup." >&2; exit 1; }
cd "$latest"
[[ -n "$(find .complete -mmin -2160 -print -quit)" ]] || { echo "Latest complete KFATA backup is stale." >&2; exit 1; }
sha256sum --check --status SHA256SUMS
# The first newline-terminated record names the authenticated binary stream.
printf '%s\n' "${latest##*/}"
tar -cf - -C "$root" .env -C "$latest" database.dump files.tar.gz commit.txt image-id.txt SHA256SUMS
