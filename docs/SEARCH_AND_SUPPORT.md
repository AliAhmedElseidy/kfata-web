# Runtime support and discovery review — 2026-11-03

The pinned dependency lock remains `requirements.txt`. The runtime uses Python 3.12, Django 5.2 LTS and Wagtail 7.4 LTS; no framework rewrite was needed. Wagtail's release notes list Django 5.2 / Python 3.12 compatibility. Review patch updates against the lock before deployment.

Official sources checked:

- [Wagtail 7.4 LTS and compatibility](https://docs.wagtail.org/en/stable-7.4.x/releases/7.4.html)
- [Django supported releases](https://www.djangoproject.com/download/)
- [OpenAI crawler controls](https://developers.openai.com/api/docs/bots)
- [Google crawler overview](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers)
- [Google common crawlers and Google-Extended](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers)
- [Bing crawler documentation](https://www.bing.com/webmasters/help/which-crawlers-does-bing-use-8c184ec0) (JavaScript required by the documentation site).

Search discovery and training are separate decisions. When indexing is enabled, ordinary search crawlers, including OAI-SearchBot, follow the public rules. The brand setting `allow_ai_training` separately controls GPTBot and Google-Extended (default: disallowed). Google-Extended is not a Google Search ranking control. When SITE_INDEXABLE is false, all automatic crawling remains disallowed and pages send noindex headers. Robots directives are voluntary crawler controls, not access control.

Published public pages have canonical URLs, reciprocal language alternates, sitemap entries, social metadata, Organization and breadcrumb JSON-LD; Article data applies to article pages. Keep contact data and publication permissions reviewed. Search Console and Bing verification values are editable in Brand settings; ownership verification and submissions require the owner's accounts. No submission, ranking, assistant inclusion or field performance result is promised. No special AI file is necessary for the current implementation.

SMTP encryption uses the locked cryptography 50.0.2 Fernet implementation; [official Fernet documentation](https://cryptography.io/en/50.0.2/fernet/). Organization data uses [schema.org GeneralContractor](https://schema.org/GeneralContractor), with reviewed public address/contacts. No legal-compliance certification is claimed for the privacy notice.
