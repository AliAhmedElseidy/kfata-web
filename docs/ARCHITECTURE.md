# Architecture

- Python 3.12, Django 5.2 LTS, Wagtail 7.4 LTS; exact installed dependencies in requirements.txt.
- Wagtail HomePage and ContentPage expose revisioned pages and reorderable StreamField blocks.
- Arabic and English pages have linked translation keys. All published page content is server-rendered.
- Content types: pages, services, sectors, projects, articles, listing pages.
- BrandSettings controls logo, favicon, accent color, contacts, navigation and motion switches.
- Enquiries are database records; their attachment storage is outside public media and downloaded only with model permission.
- Enquiry attachment images are decoded and re-encoded. Public PDF upload is deliberately unavailable until sanitization/scanning is implemented.
- Document-library PDF publication remains an authenticated editor action, separate from customer uploads.
- PostgreSQL-backed cache stores form throttle counters across workers. For higher-volume abuse protection add audited ingress rate limiting and/or a dedicated rate limiter; database cache increments are not a strict atomic abuse-control boundary.
- SMTP failure does not remove saved enquiries. notify_enquiries retries pending notifications when SMTP is configured; delivery is at-least-once.
- Docker web + db services share only their own network and persistent volumes.
- Ingress: existing proxy forwards only this domain to a loopback-bound port after inspection.
- Static assets use WhiteNoise; only public image prefixes are served by the image endpoint. Sensitive documents and customer uploads do not share this endpoint.
- No full-page cache yet: this avoids stale content and accidental caching of sessions/forms. Add a measured public-page caching layer after defining invalidation.

Wagtail is the page editor; enquiry management currently uses Django admin, linked from Wagtail.
This is not yet one fully unified custom dashboard.
