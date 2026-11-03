#!/usr/bin/env bash
# Explicit isolated restore, retained for inspection. Never points at production volumes.
set -euo pipefail
cd "$(dirname "$0")/.."
backup="$(realpath "${1:?Pass a KFATA backup directory}")"
test -f "$backup/database.dump"
test -f "$backup/files.tar.gz"
umask 077
mkdir -p operations
test ! -e operations/drill.env || { echo 'Existing drill found; inspect it before reusing.' >&2; exit 1; }
python3 - <<'PY'
from pathlib import Path
import secrets
lines = dict(line.split('=',1) for line in Path('.env').read_text().splitlines() if line and not line.startswith('#') and '=' in line)
password = secrets.token_urlsafe(36)
lines.update(POSTGRES_PASSWORD=password, DATABASE_URL=f'postgres://kfata:{password}@db:5432/kfata',KFATA_LOCAL_PORT='8098',SITE_INDEXABLE='false',EMAIL_HOST='',ENQUIRY_EMAIL='',SECURE_SSL_REDIRECT='false',WEB_MEMORY='512m',DB_MEMORY='256m')
Path('operations/drill.env').write_text('\n'.join(f'{k}={v}' for k,v in lines.items())+'\n')
Path('operations/drill.yaml').write_text('services:\n  web:\n    image: kfata-web-web:latest\n    env_file: operations/drill.env\n')
PY
drill=(docker compose -p kfata-restore-check --env-file operations/drill.env -f compose.yaml -f operations/drill.yaml)
"${drill[@]}" up -d db
for i in $(seq 1 30); do
    if "${drill[@]}" exec -T db sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null; then break; fi
    sleep 2
done
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
echo 'Restore running on loopback 8098. Verify pages and files, then stop only kfata-restore-check (retain volumes for inspection).'
