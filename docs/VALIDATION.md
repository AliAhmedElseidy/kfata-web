# Earlier deployment validation (superseded for current presentation)

For the 2026-11-04 redesign, read [REDESIGN_VALIDATION.md](REDESIGN_VALIDATION.md) and [DESIGN_REVIEW.md](DESIGN_REVIEW.md). The historical measurements below are not after-redesign evidence.

# Validation — 2026-11-04 (Asia/Riyadh)

## Executed evidence

- Running application `5d5bd9bf016c95581f08e375214cf3a312eb99fd`: [GitHub Actions success](https://github.com/AliAhmedElseidy/kfata-web/actions/runs/41719053434), checks/migrations/SQLite tests, repeat seed, static collection and Docker build. The Git credential lacks workflow scope, so PostgreSQL integration was run directly on the VPS rather than claiming a CI PostgreSQL service.
- **28 Django tests pass** on PostgreSQL 16 (96.170s) and SQLite (33.093s). Raw reports: [PostgreSQL](validation/postgresql.txt), [SQLite](validation/sqlite.txt). Covers publication/drafts/translations, role workflow, revisioned associations, idempotent imports preserving owner edits, section visibility/navigation/CTA controls, metadata, CSRF/honeypot/throttling, image validation/re-encoding, private downloads, SMTP failure persistence, 90-day retention/file deletion, encrypted SMTP form/backend, owner-only access, blank/clear credential semantics and restore delivery kill switch.
- Production migration 0010 applied; no pending model changes. Django deployment check reports only intentional HSTS includeSubDomains/preload warnings. `pip check`, Docker build and static manifest collection passed. Gunicorn web UID 10001; database and web healthy. Restore helper passes `bash -n` and a fresh actual recovery run after fixing TCP readiness.
- Deployed client verified **all 44 public page routes**, 200 responses, unique descriptions per language, canonical URLs and parseable JSON-LD; 42 published ContentPages and 16 draft project groups. Ambiguous branch draft is not public. Quote and owner SMTP pages use no-store/noindex protections; indexing is on for reviewed public content. Robots includes sitemap and blocks private/admin/form paths; training controls are separate.
- Real HTTPS synthetic form exercise: CSRF-missing 403; valid consent/PNG submission redirects with truthful receipt, persists language/privacy version, re-encodes JPEG; anonymous private download 302, staff without model permission 403, authorized staff 200, public media attempt 404. Test record/file/user removed. No real recipient email sent.
- Production owner SMTP page 200 with blank password field and no-store; mode off, ciphertext empty, independent encryption key available. Actual provider delivery was not tested because the owner has no account details. Enquiries save independently.
- Read-only host/ingress audit preceded mutation. Separate loopback8097 Docker project; PostgreSQL has no public port. Existing Nginx/Certbot retained, vhosts backed up, no MX/SPF/DKIM/DMARC edits and no existing-stack restart/prune. Mailcow 200 and ERPNext 302 before/after.
- HTTP→HTTPS 301, HTTPS 200, certificate issuance and real production renewal/hook succeeded. Cert expires 2027-02-01 17:24:44 UTC. Staging dry runs reset/timed out and did not pass.
- Snapshot `20261103T211956Z`: isolated PostgreSQL/media/private restore into `kfata-restore-final2` (8099), 42 ContentPages plus two homes and one synthetic enquiry. `tar --diff` passed. Recovered private JPEG verified 10×10, owner download200/anonymous302. Outbound kill switch true on drill/false on production. Synthetic record/file removed from both after verification; isolated containers stopped, volumes retained.
- Backup manual PC copy hashes match. Daily Riyadh 03:15 backup +14-day local retention and 03:05 enquiry purge timers active, as is certbot.timer. Automated off-server transfer remains unconfigured.

## Real browser observations

Codex in-app Chromium on the owner's Windows machine, live HTTPS, unthrottled current network; screenshots in [preview](preview/). Final original logo/contact state checked at 360, 768, 1440px. No horizontal overflow or broken loaded images on the inspected home views; English quote form also fits 360px. Language switching and quote navigation worked. Earlier keyboard Tab/Enter navigation showed visible focus. Solid-color contrast measured 7.88:1 gold/background, 8.63:1 muted/panel, 15.72:1 body/background. No exhaustive screen-reader, keyboard or overlay-contrast certification is claimed.

PerformanceObserver values are local observations, not Lighthouse scores or field Core Web Vitals:

| Visit | Width | LCP |
| --- | ---: | ---: |
| Earlier initial visit, uncontrolled cache |1280|2612ms|
| Earlier subsequent visit |360|1164ms|
| Earlier subsequent visit |768|756ms|
| Earlier subsequent visit |1440|808ms|
| Final responsive pass while recovery work was active |360|9384ms|
| Final responsive pass |768|2220ms|
| Final responsive pass |1440|2844ms|
| Subsequent visit after drill containers stopped |360|1940ms|

The final pass varied materially and exceeded the 2.5s target on some visits. Recovery load/current network/cache were not controlled; these observations cannot isolate the cause. Do not present the earlier fast values alone as a passing assessment. A subsequent server-side curl observed 1.240s TTFB; this is not a mobile LCP test. No layout-shift entries appeared in the earlier visits, but this is not certified CLS. Representative INP, controlled cold-cache/slow-network measurements and field data remain outstanding.

Core content/forms/links render on the server; the 44-route check executes no page JavaScript. Source supports reduced motion and animation fail-open. A real browser session with JavaScript disabled or OS reduced motion was not available through the current browser control capability and was not executed. See [handover](HANDOVER.md) for remaining content/provider/hosting-location verification.
