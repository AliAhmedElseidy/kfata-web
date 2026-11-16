# KFATA security hardening

See [security operations follow-up](SECURITY_OPERATIONS.md) for current SSH, Fail2ban, off-host backup and PostgreSQL readiness.

Application release `3e8dbc8ea4bff66d3181a407ae29861d8d7b757d` is deployed on kfata.elsaidy.org. [Application PR](https://github.com/AliAhmedElseidy/kfata-web/pull/4) and [weekly workflow](https://github.com/AliAhmedElseidy/kfata-web/actions/workflows/kfata-security-scheduled.yml).

- Pillow 13.0.0 replaces the affected 12.3.0. Pip-audit and the configured medium-and-higher Bandit checks passed. The release keeps Django 5.2 and Wagtail 7.4 on their installed security-supported patch series.
- The public site enforces CSP. Wagtail enforces the base, form, object and frame directives. Script and style restrictions are in report-only while the authenticated editing interface receives broader verification. HSTS applies for one year on this hostname. Shared rules, ports and unrelated services remain untouched.
- For Wagtail TOTP, open your account settings, choose **2 factor authentication**, add an authenticator, then confirm it with the current password and code. From then on, a fresh session for that account requires a confirmed device before access to Wagtail and private attachment routes. Existing unenrolled accounts retain access. Confirm a recovery procedure before removing the last device.
- The KFATA edge rate limit covers login, password reset and OTP challenges. New sessions expire within eight hours. Security event lines carry fixed categories. The host timer records threshold alerts in the journal, with no external delivery target configured.
- Public media is restricted to allowed raster extensions. Enquiries accept only JPEG or PNG, with size and decoded dimension limits and JPEG re-encoding. Private responses carry a no-store policy. Gunicorn and the KFATA Nginx access logs omit the query string.

## Backup and rollback

The pre-release online snapshot was restored into separate volumes and an isolated loopback stack with outbound email disabled. Both languages and all 72 referenced stored image/document files were checked. The verified off-host Windows copy uses DPAPI CurrentUser encryption. Decryption depends on that Windows profile. No automatic off-host copy or independent key escrow was set up.

The release keeps the previous KFATA image tagged `kfata-web-web:before-security-2026`. The host stores the pre-release vhost and rate config alongside the operational release record. The temporary loopback upstream let the normal web service be recreated before changing traffic back. To roll back, use the previously audited vhost and image only for this domain, validate Nginx, reload gracefully, and verify the deployed marker and public and protected routes. The TOTP migrations are additive.

## Validation

- The final application passed the 57-test GitHub suite and the package and source scans. Four PostgreSQL integration tests passed for the final application, including confirmed TOTP and private file access.
- All 37 health samples taken during rollout were HTTP 200. The post-release crawl checked all 112 public pages, 126 WebP renditions and both video range sources. Chromium verified public CSP, autoplay, gallery, quote and the Wagtail login page at desktop and mobile widths.
- The pinned PostgreSQL 16.16 image successfully restored and served the snapshot in a separate drill. The running database is on 16.15. A service maintenance window is required for the production update of the single database instance. [PostgreSQL 16.16 release notes](https://www.postgresql.org/docs/16/release-16-16.html)
