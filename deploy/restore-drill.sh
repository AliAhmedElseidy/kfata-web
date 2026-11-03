#!/usr/bin/env bash
# Explicit isolated restore, retained for inspection. Never points at production volumes.
set -euo pipefail
cd "$(dirname "$0")/.."
backup="$(realpath "${1:?Pass a KFATA backup directory}")"
project="${KFATA_DRILL_PROJECT:-kfata-restore-check}"
port="${KFATA_DRILL_PORT:-8098}"
[[ "$project" =~ ^kfata-restore-[a-z0-9-]+$ ]] || { echo 'Invalid isolated drill project name.' >&2; exit 1; }
[[ "$port" =~ ^[0-9]+$ ]] && (( port > 1024 && port < 65536 )) || { echo 'Invalid drill port.' >&2; exit 1; }
test -z "$(docker ps -a --filter "label=com.docker.compose.project=$project" -q)" || { echo 'Drill containers already exist; choose a fresh name.' >&2; exit 1; }
test -z "$(docker volume ls --filter "label=com.docker.compose.project=$project" -q)" || { echo 'Drill volumes already exist; choose a fresh name.' >&2; exit 1; }
test -f "$backup/database.dump"
test -f "$backup/files.tar.gz"
umask 077
mkdir -p operations
env_path="operations/$project.env"
override_path="operations/$project.yaml"
test ! -e "$env_path" || { echo 'Existing drill configuration found; inspect it before reusing.' >&2; exit 1; }
python3 - "$env_path" "$override_path" "$port" <<'PY'
from pathlib import Path
import secrets,sys
lines = dict(line.split('=',1) for line in Path('.env').read_text().splitlines() if line and not line.startswith('#') and '=' in line)
password = secrets.token_urlsafe(36)
lines.update(POSTGRES_PASSWORD=password, DATABASE_URL=f'postgres://kfata:{password}@db:5432/kfata',KFATA_LOCAL_PORT=sys.argv[3],SITE_INDEXABLE='false',EMAIL_HOST='',ENQUIRY_EMAIL='',OUTBOUND_EMAIL_DISABLED='true',SECURE_SSL_REDIRECT='false',WEB_MEMORY='512m',DB_MEMORY='256m')
Path(sys.argv[1]).write_text('\n'.join(f'{k}={v}' for k,v in lines.items())+'\n')
Path(sys.argv[2]).write_text('services:\n  web:\n    image: kfata-web-web:latest\n    env_file: '+sys.argv[1]+'\n')
PY
drill=(docker compose -p "$project" --env-file "$env_path" -f compose.yaml -f "$override_path")
"${drill[@]}" up -d db
ready=false
for i in $(seq 1 30); do
    # The entrypoint's temporary initialization server accepts Unix sockets only.
    # Wait for TCP so pg_restore cannot race that server shutting down.
    if "${drill[@]}" exec -T db sh -c 'pg_isready -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null; then ready=true; break; fi
    sleep 2
done
[[ "$ready" = true ]] || { echo 'Restore database did not become ready.' >&2; exit 1; }
"${drill[@]}" exec -T db sh -c 'pg_restore --exit-on-error --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$backup/database.dump"
python3 - "$backup/files.tar.gz" <<'PY'
import sys,tarfile
from pathlib import PurePosixPath
with tarfile.open(sys.argv[1]) as archive:
    for member in archive.getmembers():
        p=PurePosixPath(member.name)
        if p.is_absolute() or '..' in p.parts or p.parts[0] not in {'media','private-media'} or not (member.isfile() or member.isdir()):
            raise SystemExit('Unsafe backup archive')
PY
"${drill[@]}" run --rm --no-deps -T web tar -C /app -xzf - < "$backup/files.tar.gz"
"${drill[@]}" up -d --no-build web
"${drill[@]}" exec -T web python manage.py check
"${drill[@]}" exec -T web python manage.py shell -c 'from home.models import ContentPage,Enquiry; print("Restored published pages:",ContentPage.objects.live().count(),"enquiries:",Enquiry.objects.count())'
printf 'Restore project %s running on loopback %s. Verify pages/files, then stop only this drill project; retain its volumes for inspection.\n' "$project" "$port"
