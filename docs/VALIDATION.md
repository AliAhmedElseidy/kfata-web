# Validation — 2026-11-03

## Executed

- Baseline GitHub Actions on 02c7b2e passed. Actions on implementation commit 886100a passed, including its Docker build: https://github.com/AliAhmedElseidy/kfata-web/actions/runs/41693875195 . Workflow changes were not pushed: the available Git credential lacks workflow scope. PostgreSQL integration was executed on the VPS instead.
- 21 Django tests passed on PostgreSQL 16 (48.778s) and SQLite (21.501s). Raw reports: [PostgreSQL](validation/postgresql.txt), [SQLite](validation/sqlite.txt). Coverage includes public pages/translation links, all generated published URLs, drafts, editor/publisher permissions, Wagtail enquiry screens, protected attachments, CSRF, honeypot, invalid upload rejection, image re-encoding, submission throttling, SMTP failure persistence, related projects, distinct filters, metadata and safe repeated initialization.
- Fresh migrations, production migrations, `makemigrations --check --dry-run`, Django checks, compressed static collection and Docker image build passed. Production checks have only the two deliberately disabled HSTS includeSubDomains/preload warnings. App runs as UID 10001 under Gunicorn; Compose web/db are healthy and private volumes persist across web recreation.
- Read-only VPS audit ran before mutation: Ubuntu 24.04, six CPUs, 11 GiB RAM, about 5.2 GiB available, 66 GiB free disk. Host Nginx owns 80/443; existing Certbot timer was reused. Existing Mailcow and ERPNext containers/networks were not stopped, reconfigured or pruned.
- A record already pointed to 144.91.120.177; no AAAA record was returned. DNS/mail records were not changed. KFATA listens only on loopback 8097.
- Public HTTPS works, certificate issuance and a real production renewal succeeded; the domain-specific deploy hook validated and reloaded Nginx. Staging ACME dry runs failed with connection reset/timeouts, so those were not counted as success.
- Backup and isolated PostgreSQL/media restore passed. 26 published ContentPages and zero enquiries matched production. Restored /ar/, /en/ and /admin/login/ returned 200. `tar --diff` against the restored archive passed. Drill project is stopped with its separate volumes retained. Real enquiry records/private customer attachments did not exist; attachment access and re-encoding were exercised using synthetic Django test data.
- Daily 03:15 Riyadh backup timer installed; completed local snapshots retain 14 days. One manual off-server copy on the owner's Windows computer was checked against both SHA-256 hashes. Recurring off-server transport is not configured.
- Mailcow public endpoint returned 200 and ERPNext returned 302 before and after the work. Existing stacks were not restarted by this session.

## Browser observations

Real Codex in-app Chromium on the current Windows machine, unthrottled current network, live HTTPS origin. Screenshots are in [preview](preview/). Arabic RTL and English LTR, images, language switching, project navigation and the disabled enquiry notice were inspected. No broken loaded images or horizontal overflow were found at 360, 768 and 1440px.

Local PerformanceObserver values, not Lighthouse scores or field data:

| Visit | Width | LCP |
| --- | ---: | ---: |
| Initial Arabic navigation (cache state not controlled) | 1280 | 2612ms |
| Subsequent Arabic navigation | 360 | 1164ms |
| Subsequent Arabic navigation | 768 | 756ms |
| Subsequent Arabic navigation | 1440 | 808ms |

No layout-shift entries were recorded in these inspected visits; this is a limited observation, not a certified CLS assessment. A representative INP distribution was not measured. Cold-cache slow-network mobile testing and real-user Core Web Vitals remain outstanding; the first observed LCP slightly exceeded 2.5 seconds. Do not claim all performance targets were met.

Core content/forms/links are server-rendered, and source code respects reduced motion and fails open if animation/storage APIs fail. A browser session with JavaScript disabled and an OS-level reduced-motion toggle was not separately executed. Keyboard Tab moved from the brand link to About KFATA with a visible focus outline; Enter navigation worked. Computed solid-color contrast ratios were 7.88:1 (gold/background), 8.63:1 (muted text/panel), and 15.72:1 (body text/background). Image-overlay contrast, full screen-reader and exhaustive keyboard audit remain outstanding. No formal accessibility certification is claimed.

## Remaining launch blockers

Approved company contact/retention/privacy information, original logo and source PDFs are missing. Enquiries and indexing remain off. Title-only/unsupported content remains draft, including empty sectors, quality/safety, certifications, news, careers and privacy. Customer PDF upload stays disabled. SMTP, account-level search verification, automated off-server backup transport and the remaining editorial source review must be completed with owner input. See [handover](HANDOVER.md).