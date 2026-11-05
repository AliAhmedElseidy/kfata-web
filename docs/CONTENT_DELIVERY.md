# Source content applied; construction scene in preview — 2026-11-05

## Production

Application: `e3b88861a42a4bba022eed31097b0d1a82c7076f`, recorded in `/opt/kfata-web/operations/deployed-commit`. [PR 2](https://github.com/AliAhmedElseidy/kfata-web/pull/2) remains open on `feat/kfata-source-enrichment`; no PR merge or force push. Later preview/documentation commits are not the running application image.

The owner explicitly requested applying and publishing PR2's sourced text. Read-only host inventory (`deploy/audit.sh`) and the actual Nginx vhost were inspected first. Independent loopback8097 KFATA project, existing host TLS/ingress, PostgreSQL without host port, Mailcow and ERPNext preserved. Pre-enrichment consistent backup: `/opt/kfata-web/backups/20261105T094407Z`; previous image tagged `kfata-web-web:before-enrichment`. Only KFATA web was briefly stopped by the backup and automatically restarted. No new restore drill/off-server-copy claim.

The newly built image ran `enrich_company_content` in read-only mode first: 14 would-create, 63 would-update, one editor revision preserved, no missing parent/locale/conflict. Then `--apply --publish` created/published14 and updated/published63. The pending owner-authored English ANB tower revision was the preserved page. No force replacement, seed/reset or schema migration was run.

The public site now has **94 routes**:92 ContentPages plus2 homes. It contains24 published project/case-study topics per language,6 services,7 sectors, About and Quality. The English tower keeps its prior published content and protected pending revision. These are portfolio topics, not a claim of24 distinct contracts. Golden Belt remains unpublished; certificates/news/careers remain drafts. No new company photo permissions or numerical/certification claims were inferred.

Projects with approved photographs remain prominent at the start of the listing. Text-only case studies use compact full-width rows without unrelated photographs, remain paginated/discoverable, and link their services/sectors. Sector filters use published relationships, avoiding duplicate Arabic labels such as مصرفي/القطاع المصرفي without overwriting the owner's project facts. Home's curated real-photo selection and existing editable layout were preserved; its project/service/sector links lead to the enriched public pages.

## Verified live

- All78 source-record routes returned200; the first sourced paragraph was found in77 public responses, excluding the intentionally protected English tower.
- All24 project topics in each language were discovered through the three-page public project index.128 project→service/sector links were verified in rendered responses.
- All94 public routes passed canonical, unique language description and JSON-LD checks. Golden Belt remains draft/404. Public Arabic/English project index, Arabic banking filter (two result pages), clinic detail and language switching were also exercised in the actual browser at360px; no horizontal overflow in those views.
- Before/after SHA256 comparisons matched entire HomePage/BrandSettings/SMTP data, account credential/status fields, protected page/revision data and all existing enquiry contents. Private snapshots live in host operations/enrichment-preserve-*.json, outside Git. No raw customer data/credentials are published. Permissions were not changed.
-40 SQLite tests passed45.070s and40 PostgreSQL16 tests passed266.406s at93d3381. The relationship-filter patch then passed10 source tests on SQLite68.979s and its targeted PostgreSQL regression45.420s. No model drift; JS syntax check passes. [Initial deployed enrichment CI](https://github.com/AliAhmedElseidy/kfata-web/actions/runs/42005400915) passed. Raw logs are under validation/enrichment-*.txt.
- Final KFATA containers healthy; Mailcow200/ERPNext302. No existing stack restart, proxy rewrite, mail-DNS change, public database, global Docker prune or volume deletion. No real email/enquiry notification was sent during this phase.

Examples: [Arabic clinic](https://kfata.elsaidy.org/ar/projects/anb-internal-clinic/), [English clinic](https://kfata.elsaidy.org/en/projects/anb-internal-clinic/), [Arabic projects](https://kfata.elsaidy.org/ar/projects/), [English projects](https://kfata.elsaidy.org/en/projects/), [construction](https://kfata.elsaidy.org/en/services/contracting/), [banking](https://kfata.elsaidy.org/ar/sectors/banking/).

## Original scene: preview only

The supplied reference clips508810/508807 were not available on this machine; the owner confirmed that. The written brief was followed. An original offline Blender scene was created and actually rendered: foundations/pads, columns, floor and roof slabs, walls, glazing/bronze mullions, timber fins, steps, reflecting water, planting and linear lighting. This is a first technical/art-direction prototype, not a claim of matching unavailable reference footage or a finished photoreal film.

The movie is7s,768×432,12fps,H.264,227,173bytes; final poster1280×720. No reference frames, stock models or outside textures were used. The scene is explicitly labeled as an architectural concept, not a completed KFATA project. It is distinct from the existing logo intro. No visitor-side renderer is used.

Actual local browser recording: ignored `operations/scene-preview/homepage-browser-preview.mp4`, approximately8.5s, captured through72 timestamped browser screenshots and encoded with their measured timing. It shows the actual browser player, HTML title/actions and construction stages. This is not a synthetic video composited over a fabricated browser. Also available: raw `construction-preview.mp4`, `.blend`, render frames, timing JSON and Arabic/English screenshots under the same ignored folder.

The preview template uses the local Wagtail home content and shared header/footer. Muted inline player has once/session autoplay, pause/replay, completed-building skip/poster and explicit concept disclosure. Actual Windows reduced-motion test: video source stayed unset, paused, static poster available; original Windows Animation effects On was restored. Local CSP `script-src 'none'` test: poster loaded, controls hidden, no video source or script diagnostics; the native mobile menu opened/closed normally. Arabic360px has both CTA bottoms452px and scene bottom647px within800px; English360px CTA bottoms572px; no horizontal overflow in those inspected previews.

Source/reproduction instructions: [tools/scene/README.md](../tools/scene/README.md). Opt-in local preview routes are not in production URL configuration. Generated scene media, screenshots containing it and recordings have not been uploaded to the public repository or server. The source code is reviewable in PR2; the new motion is **not live**. Original approved company imagery remains on production's hero/showcase.

Next: owner review of building form/materials/composition, then final-resolution desktop/mobile assets, production CMS selection/activation, first-visit loading/performance and final accessibility checks before motion deployment. Existing cached LCP observations in MOTION_VALIDATION.md concern the older f5e2454 presentation; no new production LCP/INP improvement or field-performance guarantee is claimed here.

## Final checks

Final application e3b8886 includes the inactive preview code but no preview route in production and no generated media on the host. It also escapes pagination query separators correctly. The targeted pagination regression passed1 test in6.471s; actual browser banking page2 retained the selected filter. [Final application CI passed](https://github.com/AliAhmedElseidy/kfata-web/actions/runs/42011010205). An external HTTPS crawl fetched94 public pages plus47 additional internal links/assets, all200; [raw result](validation/enrichment-http.json). This is availability/link evidence, not a new LCP/INP measurement. Local preview stays at loopback8035 for owner review.
