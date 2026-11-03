# KFATA design/content phase — 2026-11-04 (Riyadh)

## Implemented direction

Charcoal/gold identity with stone sections, locally hosted IBM Plex Arabic/Latin, measured typographic hierarchy, fine plan lines and distinct layouts. The homepage now has a source-informed introduction, curated asymmetric project showcase, six service rows with appropriately sized thumbnails, seven sector descriptions, owner-approved four-step process, illustrated engineering activity with explicit origin disclosure, approved quality copy, practical FAQ and enquiry CTA. Footer has an editable introduction/callout and three editable link columns plus company contact, WhatsApp, address-search map and policies. No tracker or unnecessary consent banner was added.

Project pages have a stone heading/facts band, wide project cover, protected published data, real-source image galleries, direct enquiry action and existing sector/service relationships. Galleries progressively enhance ordinary image links using a native dialog, buttons and arrow-key navigation; Escape and native dialog focus confinement/restoration are implemented. Full images are requested when opened rather than loading every full-size gallery image at once. Runtime keyboard/focus verification remains pending because computer control stopped (below).

The four new source photos, one generated illustration and process/quality wording were individually approved by the owner in this phase. See assets/README.md. The generated engineering activity is visibly described as illustration, not staff or a company project, and is excluded from project galleries. Original source scans/legal materials remain private. ANB Al Hizam/Golden Belt remains unpublished; sixteen project groups remain drafts. Only the quality/safety summary was approved for publication; current certificates/news/careers remain drafts.

## Editorial protection

`refresh_presentation` is preview-only by default; `--apply` is an explicit one-time update after backup. It uses transactions/row locks, skips user-authored revisions and live pages with pending changes, and records applied page/brand/policy roles in PresentationUpdate. Re-running does not restore a footer or body the owner cleared or recreate a policy after its slug was renamed. Stable image keys avoid duplicate imports after image-title edits. No seed reset, SMTP replacement, enquiry deletion, user recreation or permission reset is part of the update.

The live **English ANB tower** page has an owner-authored pending revision. It was preserved and skipped, so its gallery/content refresh is not published. Review/merge that draft in Wagtail deliberately. Arabic tower and both residential pages received the approved gallery content. All existing public page paths remain unchanged; terms/cookies are added. A sitemap crawl found the structural `/` language redirect listed as content; the sitemap now excludes it and includes canonical public content only.

## References reviewed, without copied content/assets

- [AlBawani](https://albawani.com/en/): distinct focus areas and a selected project section informed the decision to give services and projects different layouts.
- [El Seif](https://el-seif.com.sa/en/about-us): separate company, capabilities/people, projects and expertise navigation informed content organization.
- Almabani's home URL returned no readable content in the available fetch; no claim of a visual review is made for it.
- [IBM font source and OFL](https://github.com/google/fonts/tree/main/ofl/ibmplexsansarabic): Regular/SemiBold locally served WOFF2, license included under config/static/fonts.
- [Django cookie settings](https://docs.djangoproject.com/en/5.2/ref/settings/#csrf-cookie-age) and actual application settings informed the functional-cookie notice. [SDAIA knowledge center](https://dgp.sdaia.gov.sa/wps/portal/pdp/knowledgecenter) consulted for notice/minimization context. No legal compliance certification is claimed.

## Actual browser evidence and interruption

Before changes, live Arabic home/project screenshots were saved at 1440 and 360px in `docs/preview/redesign-before/`. This phase's baseline LCP observations were 1756ms at1440 and616ms at360, unthrottled IAB Chromium/Windows with uncontrolled cache. A local preview of the new homepage was inspected at1440: new type/hero/stone introduction/asymmetric project section, no horizontal overflow or broken loaded images. Preview screenshots were shown inline during work but no final after-image files were saved before interruption.

An attempt to open a separate native Chrome window to test DevTools JavaScript-disabled/reduced-motion settings caused computer control to stop: the tool could not establish the Windows browser URL with sufficient confidence. No browser control bypass or alternative automation was used. No JavaScript/OS setting was changed before the stop. The owned local development server was stopped later. Final **after screenshots at360/768/1440, mobile/menu/gallery/keyboard interactions, actual JavaScript-off/reduced-motion sessions, post-change LCP/CLS and English visual inspection remain outstanding**. Old screenshots elsewhere in docs/preview predate this redesign and must not be presented as after evidence. Backend/HTTP checks are separate evidence, not a substitute for these browser checks.

## Performance measurements

Five sequential HTTPS curl requests from this Windows machine to the same `/ar/` origin before and after publishing the redesign; unthrottled current network, no controlled cache/CPU conditions. Before TTFB seconds: 1.931363,0.875060,1.272676,1.638333,2.169057 (median1.638333). After: 1.239596,1.436190,1.049263,1.143878,1.374050 (median1.239596). These are small-sample server-response observations, not proof of a general speed improvement or mobile CWV pass. Font/image loading, LCP and CLS after deployment were not measured because browser access stopped. No INP target or accessibility certification is claimed.

New service thumbnails use240/400px renditions and accurate sizes; hero uses480/800 mobile and1200/1800 desktop srcset with high priority/reserved geometry. Images below the fold are lazy. Menu translation lookup is batched per request. The no-JS page keeps ordinary links/native details usable, and CSS/JS respect reduced motion; these fallbacks still need their requested final browser exercises.
