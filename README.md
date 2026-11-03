# KFATA website

Django + Wagtail, Arabic/English, server-rendered pages and editable content blocks.
Intended production origin: **https://kfata.elsaidy.org**.

## Delivery status

This is the first implementation for review, **not a verified production deployment**.
SSH to the supplied VPS was unavailable from the authoring environment (`Network is unreachable`).
No server configuration, Mailcow, ERPNext, DNS or TLS configuration has been changed.
The application tests and their results are documented in `docs/VALIDATION.md`.
Browser QA and production performance measurements remain outstanding.

## Local development (Python 3.12)

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createcachetable
python manage.py seed_content
python manage.py createsuperuser
python manage.py runserver
```

The four approved initial project images are included; see `assets/README.md` for provenance. The importer also supports an image-free setup.

Visit `/ar/`, `/en/`, `/admin/` (content), `/django-admin/home/enquiry/` (enquiries).
The Wagtail sidebar links to enquiry management for users with the required permission.
Development uses SQLite and a console email backend; production requires PostgreSQL.
Use `DATABASE_URL=sqlite:////tmp/kfata-dev.sqlite3` if the local workspace filesystem does not support SQLite locking correctly.

## Tests

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test home
DJANGO_SETTINGS_MODULE=config.settings.build python manage.py collectstatic --noinput
```

## Documents

- [Architecture](docs/ARCHITECTURE.md)
- [Deployment and ingress](docs/DEPLOYMENT.md)
- [Backup and restore](docs/BACKUP_RESTORE.md)
- [Arabic content guide](docs/CONTENT_GUIDE.md)
- [Content requiring review](docs/CONTENT_REVIEW.md)
- [Validation and remaining work](docs/VALIDATION.md)

Do not commit credentials, original company PDFs, database dumps, customer enquiries or customer attachments.
