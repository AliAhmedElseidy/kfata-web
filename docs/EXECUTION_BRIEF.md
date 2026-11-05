# KFATA: one execution brief — 2026-11-05

## Existing work to continue

Repository: https://github.com/AliAhmedElseidy/kfata-web
Site: https://kfata.elsaidy.org
Source-content follow-up: PR #2, feat/kfata-source-enrichment, based on feat/kfata-initial-site.

Read AGENTS.md, CONTENT_RECONCILIATION.md and VISUAL_DIRECTION.md. The owner delegated the visual decision. Keep the Django/Wagtail CMS and independent Docker deployment; preserve Mailcow, ERPNext, owner edits, accounts, enquiries and SMTP.

## Execute two connected workstreams

### Source content: ready to apply

There are 39 bilingual source-mapped records: 24 project/case-study topics, 6 services, 7 sectors, About and Quality. Topics are not a claim of 24 distinct contracts.

After retrieving the reviewed code into the actual existing KFATA checkout and taking a consistent backup, run the updated application image's command in its existing Compose environment:

    python manage.py enrich_company_content
    python manage.py enrich_company_content --apply --publish

Default mode is read-only. Inspect reported protected/editorial pages; never force replacement. The second command is the explicit publication path on first application. Draft-only updates are subsequently published through deliberate Wagtail review. Do not run legacy seed/reset commands.

Verify Arabic/English content bodies, service/sector relationships, project listings and canonical routes after application. Link selected pages into the homepage through existing Wagtail fields; do not treat new database rows alone as completion. Avoid exposing an image-empty project grid as the hero showcase. Keep unphotographed but useful case-study text accessible in the appropriate listing/category.

### Visuals: precise reference target

Use the warm architectural style of 508810.mp4, large readable project imagery/hierarchy from 508807.mp4, AMAQ's company/service/project presentation and Red Sea Global's institutional content organization. Do not copy the sites or introduce unrelated destination/investment claims.

Create one original 6–8 second architectural construction asset: foundations, columns, slabs, walls/glazing, facade materials, lighting/landscape, completed building. Choose a pre-rendered video with a mobile poster rather than live visitor-side 3D. Produce/render it only if actual tools support the task; otherwise identify the missing original asset specifically. Do not substitute the existing logo intro or CSS cubes and call it complete.

Integrate the scene into the usable hero, not a blocking loading screen. Navigation and HTML title/actions remain immediately available. Add muted inline playback, skip/pause, once-play/final-frame behavior and reduced-motion/no-video fallback. The scene is an illustrative concept, not a KFATA project. Do not publish the user's reference clip as the asset.

Use current public real photographs for portfolio cases; maintain source-image publication permissions.

## Homepage and footer

Hero -> source-based company introduction -> selected real projects -> six service capabilities -> sectors -> project-start process -> quality -> contact CTA -> substantial footer.

Navigation: Company, Expertise, Sectors, Projects, Contact, language toggle and Request a quote.

Footer: logo and brief description, company links, expertise/services, projects, contact channels and meaningful privacy/terms/cookies links. All editable from the CMS, no placeholder links or invented affiliations/awards/metrics.

## Evidence and completion

Demonstrate the actual construction scene in a short recording and save desktop/mobile before/after captures. Test relevant language links, menu, gallery, forms, reduced motion and first-visit image/video loading. Measure performance with stated conditions; no unsupported improvement claims.

Deploy only tested KFATA changes after backup, verify live site and existing service availability, push the code and record the deployed commit. Distinguish code pushed, content applied, asset created and live deployment verified as separate facts.

Initial authoring environment still cannot reach SSH; this brief and the content package are not evidence of a live content/design update.
