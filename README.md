# KFATA website

Django + Wagtail, Arabic/English, server-rendered pages and editable content blocks.
Intended production origin: **https://kfata.elsaidy.org**.

## Delivery status

The site is running on **https://kfata.elsaidy.org** with independent Docker/PostgreSQL services and valid HTTPS. This is a review deployment: indexing and real enquiry collection remain disabled until approved company contacts, privacy terms and source content are supplied.

See [handover](docs/HANDOVER.md), [validation](docs/VALIDATION.md) and [content review](docs/CONTENT_REVIEW.md) for verified results and remaining external inputs. Mailcow and ERPNext were not restarted or reconfigured.
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
Enquiries are managed directly inside Wagtail; the legacy Django admin remains available for authorized administrators.
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
