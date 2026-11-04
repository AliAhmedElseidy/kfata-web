#!/usr/bin/env bash
# Run on the host from this checkout; contains private data. Store off-server securely.
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
backup_dir="${KFATA_BACKUP_DIR:-./backups}/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$backup_dir"
exec 9>./operations-backup.lock
flock -n 9 || { echo 'A KFATA backup is already running.' >&2; exit 1; }
# Stop only KFATA writers for a consistent database/files snapshot.
was_running="$(docker compose ps --status running --services web)"
web_image="$(docker inspect --format '{{.Image}}' "$(docker compose ps --all -q web)")"
restore_web() { if [ "$was_running" = web ]; then docker compose start web >/dev/null; fi; }
trap restore_web EXIT
docker compose stop web >/dev/null
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_dir/database.dump"
docker compose run --rm --no-deps -T web tar -C /app -czf - media private-media > "$backup_dir/files.tar.gz"
if [ -f operations/deployed-commit ]; then
    cat operations/deployed-commit > "$backup_dir/commit.txt"
else
    git rev-parse HEAD > "$backup_dir/commit.txt"
fi
printf '%s\n' "$web_image" > "$backup_dir/image-id.txt"
(cd "$backup_dir" && sha256sum database.dump files.tar.gz > SHA256SUMS)
touch "$backup_dir/.complete"
# Retain 14 days of completed local snapshots; never follow paths outside the backup root.
python3 - <<'PY'
from pathlib import Path
import datetime,os,re,shutil
root=Path(os.environ.get('KFATA_BACKUP_DIR','./backups')).resolve()
cutoff=datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=14)
for directory in root.iterdir():
    if directory.is_symlink() or not directory.is_dir() or not re.fullmatch(r'\d{8}T\d{6}Z',directory.name): continue
    if directory.resolve().parent != root or not (directory/'.complete').is_file(): continue
    date=datetime.datetime.strptime(directory.name,'%Y%m%dT%H%M%SZ').replace(tzinfo=datetime.timezone.utc)
    if date < cutoff: shutil.rmtree(directory)
PY
printf 'Backup completed: %s\n' "$backup_dir"
