# KFATA website

Django + Wagtail, Arabic/English, server-rendered pages and editable content blocks.
Intended production origin: **https://kfata.elsaidy.org**.

## Delivery status

The site is running on **https://kfata.elsaidy.org** with independent Docker/PostgreSQL services and valid HTTPS. Indexing and enquiries are enabled after owner-approved contacts, privacy and 90-day retention. There are 50 public Arabic/English routes. Unapproved company material remains draft. Owner-only encrypted SMTP settings are available in Wagtail; delivery is off until an account is configured.

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

The 2026-11-04 presentation/content phase adds stone/charcoal editorial layouts, curated project/service/sector selections, local typography, approved project galleries and an editable corporate footer. See [design review](docs/DESIGN_REVIEW.md) and [redesign validation](docs/REDESIGN_VALIDATION.md), including the browser-verification interruption and remaining after screenshots.

The 2026-11-05 motion phase adds the finite architectural logo introduction, unified quiet/standard animation, sticky/mobile navigation refinements and accessible gallery focus handling. See [current delivery and real browser evidence](docs/MOTION_VALIDATION.md), which supersedes the preceding browser-verification interruption.

The owner-authorized PR2 source enrichment is now live:94 public routes and24 case-study topics per language, with the English owner draft protected. See [current content delivery](docs/CONTENT_DELIVERY.md). The original construction video is a local review prototype; [preview source](tools/scene/README.md) is separate from production activation.
