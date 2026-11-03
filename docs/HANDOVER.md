# KFATA operational handover — 2026-11-03

## Available now

- [Arabic site](https://kfata.elsaidy.org/ar/), [English site](https://kfata.elsaidy.org/en/), [Wagtail](https://kfata.elsaidy.org/admin/).
- [PR 1](https://github.com/AliAhmedElseidy/kfata-web/pull/1) remains open; no merge or force push.
- Initial verified deployment: `886100ae7793a400c3681e3d8c02b7e0ed86ff2a`. The host records the active application commit in `/opt/kfata-web/operations/deployed-commit`.
- Review deployment, not final approved company-content launch. SITE_INDEXABLE=false. Real enquiries are disabled; a disabled POST returns 503 and saves nothing.
- Two home pages and 26 published content pages. Title-only sectors and empty sector indexes were hidden. Quality/safety, certifications, news, careers and privacy remain drafts. Uncertain Arabic legal spelling is withheld; the public brand is KFATA. No invented statistics/certificates or unreviewed PDFs were published.

## Owner access

Account: `kfata-owner`. A unique random password was created without printing it and is stored only at `/root/.config/kfata-web/owner-initial-password`, mode 0600, in a mode-0700 directory. Retrieve it through your own trusted SSH terminal; do not paste it into chat, GitHub or a support ticket. Change the application password after taking ownership. There is no shared/default password.

The authorized SSH public-key connection worked. The previously shared root password should be changed by the owner after retaining this tested key access; this session did not change it.

## Manage only KFATA

On the VPS:

```sh
cd /opt/kfata-web
docker compose -p kfata-web ps
docker compose -p kfata-web logs --tail=100 web
docker compose -p kfata-web restart web
bash deploy/backup.sh
cat operations/deployed-commit
```

Application listens on `127.0.0.1:8097`; the existing host Nginx routes only kfata.elsaidy.org to it. PostgreSQL has no published port. Web/database memory ceilings are 768/512 MiB, CPU ceilings 1.0/0.75, with their own network and volumes. No Docker socket, shared databases or Mailcow/ERPNext application networks are mounted.

Before an update, take a backup, review migrations, fetch/pull without overwriting editor data, build/test the exact commit, apply migrations once and update this Compose project only. Run `python manage.py setup_roles` after deliberate role configuration; editors save revisions and submit to publisher approval, publishers publish, managers also manage enquiries/brand settings, and the owner administers users/groups. Do not rerun owner provisioning for an existing account.

## TLS and backups

- Certificate is issued through the existing Certbot installation using the webroot `/var/lib/letsencrypt`. Existing `certbot.timer` schedules renewal. `/etc/letsencrypt/renewal-hooks/deploy/kfata-web` validates Nginx and reloads it only for this certificate.
- A real production renewal and hook succeeded. ACME staging dry runs failed with connection resets/timeouts; this is recorded separately from the successful real renewal.
- Nginx configuration was backed up before the domain route was added: `/opt/kfata-web/operations/nginx-before.tar.gz`. No existing vhost was replaced. The KFATA-only route and rate-zone templates are in `deploy/`.
- `kfata-backup.timer` runs daily at 03:15 Asia/Riyadh plus up to five minutes of jitter. It stops only KFATA web briefly to freeze database/file writers, restarts it via an EXIT trap, and retains completed local snapshots for 14 days. A brief application maintenance interval is expected; other stacks stay running.
- Verified snapshot: `/opt/kfata-web/backups/20261103T182811Z`. Custom PostgreSQL dump and public/private media archive were restored into `kfata-restore-check` with separate credentials, volumes, network and loopback port 8098. Restored public page count was 26 and enquiry count 0; Arabic, English and login returned 200; archive content comparison passed. The drill containers are stopped; their volumes remain for inspection.
- One access-controlled off-server copy is at `C:\Users\dell\.codex\backups\kfata-web\20261103T182811Z`; SHA-256 checks matched. This is a manual recovery copy. Scheduled off-server transfer is still unconfigured; choose an owner-controlled destination and credential mechanism. Local-only daily copies do not protect against loss of the VPS.
- `.env`, outbound mail credentials and the initial owner password are excluded from repository/image/backup archives. Keep necessary recovery secrets separately in an approved password manager. A restored instance can generate independent application/database credentials and reset the owner password through authorized administration.

## Required company inputs

Supply the original approved logo and the two source PDFs, approved Arabic legal name, public phone/email/address, enquiry inbox, retention period and privacy contact. Neither PDF was present in this session's attachments. Only the four explicitly approved source photographs were used.

Review the remaining project scope/client/date information and provide genuine quality/safety, certificate, news or careers material before publishing those drafts. Complete the privacy notice describing the actual hosting, storage, notification, retention, deletion and contact process; then enable enquiries from Brand settings. Configure SMTP through the protected environment and test with an internal test inbox. Never enable indexing until content, navigation, privacy and contact review are complete. Search Console/Bing account verification remains owner work.

Hero images, editorial video blocks, responsive galleries and motion controls are available. A background video in the main hero and an animation of the original logo still require an approved asset and further presentation work. Customer PDFs remain disabled pending a real scanning/sanitizing pipeline.

See [validation](VALIDATION.md) for measured performance limits and browser checks. No claim of full completion, guaranteed ranking, field Core Web Vitals or exhaustive accessibility certification is made.
