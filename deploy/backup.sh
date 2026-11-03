#!/usr/bin/env bash
# Run on the host from this checkout; contains private data. Store off-server securely.
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
backup_dir="${KFATA_BACKUP_DIR:-./backups}/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$backup_dir"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_dir/database.dump"
docker compose exec -T web tar -C /app -czf - media private-media > "$backup_dir/files.tar.gz"
git rev-parse HEAD > "$backup_dir/commit.txt"
printf 'Backup completed: %s\n' "$backup_dir"
