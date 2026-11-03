# Deployment: audit first

## Current state

The live deployment uses /opt/kfata-web, independent kfata-web Compose services, loopback 8097, existing host Nginx and existing Certbot. See [HANDOVER.md](HANDOVER.md) for actual results, credential handoff, backups and remaining launch inputs. Indexing and enquiries are enabled after the documented owner approvals. SMTP delivery is off and can later be configured from owner-only Wagtail settings. The instructions below describe the operational procedure; they are not evidence of an unexecuted step.

## 1. Read-only inventory

Run `bash deploy/audit.sh` on the VPS. Separately inspect only relevant existing proxy configuration, avoiding secret output. Determine:
- RAM/CPU/disk and existing load.
- Current port 80/443 owner and TLS/ACME strategy.
- Whether ingress runs on the host or inside Docker.
- Availability of an unused loopback port (default example: 8097).
- A/AAAA records for kfata.elsaidy.org and correct IPv6 routing if present.
- Whether another KFATA installation already exists.

The target host is shared with Mailcow and ERPNext. Never install a competing proxy or run global Docker cleanup. Resource defaults are provisional until measured.

## 2. Application preparation

Use an isolated checkout such as `/opt/kfata-web`, on the reviewed commit. Copy `.env.example` to `.env`, with permissions 0600. Generate new independent secrets; URL-encode PostgreSQL credentials in DATABASE_URL if necessary.

Set PUBLIC_BASE_URL, ALLOWED_HOSTS and matching PostgreSQL credentials. Keep SITE_INDEXABLE=false pending company-content review. Provision an independent Fernet SMTP_ENCRYPTION_KEY in root-only .env; keep its recovery copy outside the checkout. Configure the intended outbound account later through owner-only Wagtail SMTP settings, using STARTTLS or SSL. Keep mode off until tested. Set TRUSTED_PROXY_NETWORKS only to actual trusted proxy addresses; the proxy must overwrite X-Real-IP and X-Forwarded-Proto. Never trust 0.0.0.0/0.

```sh
docker compose config --quiet
docker compose build
docker compose up -d db
docker compose run --rm web python manage.py migrate --noinput
docker compose run --rm web python manage.py createcachetable
docker compose run --rm web python manage.py seed_content
docker compose run --rm web python manage.py createsuperuser
docker compose up -d web
```

There is no automatic migration-on-startup. The Docker build creates the compressed static manifest using build settings. Production does not load `.env` through Django; Compose injects it.

## 3. Ingress and HTTPS

`deploy/nginx-site.example.conf` is an example, not an automatic installer.
For a host proxy, forward to 127.0.0.1:8097 after confirming port availability.
A container proxy cannot reach the host application's loopback by using its own 127.0.0.1: an audited ingress integration is required. Do not join ERPNext/Mailcow application networks automatically.

Keep PostgreSQL unexposed. The compose file does not listen on public ports. Preserve proxy persistence and ACME renewals through the existing system's supported configuration mechanism.

Back up relevant proxy files before changes. Validate configuration before reload. Obtain a certificate through the existing TLS/ACME mechanism only after DNS is correct. Do not stop existing stacks to run standalone ACME.
SECURE_SSL_REDIRECT=true expects HTTPS termination and an overwritten trusted header. Review any HTTP health checks and certificate-challenge routes to avoid redirects breaking them.

Do not edit MX/SPF/DKIM/DMARC. Do not replace the domain zone. Restrict DNS edits to necessary web records and eliminate incorrect AAAA records only after review.

## 4. Acceptance

- Inspect compose health and application logs without exposing secrets.
- Check HTTPS chain, renewal path, redirects, /ar/, /en/, /admin/, static assets and public image endpoints.
- Test CSRF-protected enquiry persistence using an internal test inbox; test private downloads.
- Set group permissions deliberately; no default shared admin password.
- Verify Mailcow and ERPNext availability against the pre-change baseline.
- Measure mobile performance; do not claim scores without a report.
- Follow docs/CONTENT_REVIEW.md before enabling indexing.

## 5. Updates and rollback

Capture deployed commit, back up data, review migrations, build/test the new image, apply migrations once, update only this compose project. A previous image may not work with a new schema: use a reviewed migration rollback or restore the matching database/files snapshot. Never assume `git checkout` restores data.
