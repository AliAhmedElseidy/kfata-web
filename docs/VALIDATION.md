# Validation and remaining work

## Verified in the authoring environment (2026-11-03)

- Django system check: passed.
- Migration drift check: no changes detected.
- Fresh migrations: passed using a temporary SQLite database.
- Initial content import and repeat import: passed; edited content preserved.
- 16 Django tests: passed, including bilingual pages, draft protection, sitemap, metadata, CSRF, enquiry persistence when SMTP fails, invalid upload rejection, image re-encoding, throttling, admin edit screens, authorized/private attachment download, and image-free initialization.
- Static collection with compressed manifest storage: passed (217 static files, 631 post-processed).
- Python compilation and shell-script syntax: passed.
- Production deployment system check: no errors; two intentional HSTS warnings for includeSubDomains/preload. They remain off until TLS and host scope are audited.

## Not verified / external blockers

- Four initial project images were explicitly approved for this public GitHub repository on 2026-11-03 and are now included. The source PDFs and other unreviewed material remain excluded.
- VPS access: SSH TCP connection returned `Network is unreachable` before authentication. Server inventory did not run.
- DNS, TLS issuance/renewal, live domain, ingress routing and coexistence with Mailcow/ERPNext: unverified and unchanged.
- Docker image/Compose runtime: Docker is not available in the authoring environment. CI includes an image build, but its result has not been observed yet.
- PostgreSQL integration and backup restoration: not run locally.
- Browser visual/interaction QA: preview infrastructure cannot launch this environment's Python runtime. No screenshots or browser results are claimed.
- Mobile performance/Core Web Vitals: not measured.
- Real SMTP, Google/Bing verification and production indexing: not configured.

## Scope remaining before the requested full handover

This is an initial implementation, not the complete commissioned website.

- Review and import the rest of the company portfolio, project metadata and approved legal/public certificate content.
- Confirm legal company spelling, contact data, original logo and contradictory profile statistics.
- Complete privacy notice before accepting real enquiries; publish quality/safety/certificate/news/careers content only with approved information.
- Unify enquiries fully into Wagtail if desired (currently linked Django admin).
- Implement audited scanning/sanitization before enabling PDF customer uploads; currently only re-encoded JPEG/PNG are accepted.
- Add remaining approved editor blocks/options: optional hero video, metrics, sector-related project selections, per-page social image, breadcrumb structured data, related projects, nested menus, editable footer navigation, font choices and animation intensity. These are not yet implemented.
- Extend the initial introduction animation to the approved architectural-logo treatment after receiving the original logo.
- Configure editorial publishing groups and test non-admin editing workflows.
- Add measured cache strategy and stricter ingress abuse controls if traffic requires them.
- Choose and test off-server backup storage, restore procedure, scheduling and retention.
- Complete browser QA, accessibility and performance review, Docker/PostgreSQL validation and shared-server audit, then perform HTTPS deployment and live acceptance tests.

Do not mark the project complete, production-ready or deployed until these checks and the agreed remaining scope are resolved.
