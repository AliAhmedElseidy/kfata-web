# KFATA visual decision — 2026-11-05

The owner supplied five video references and delegated the design decision. This supersedes vague requests for more fade-in effects.

## Chosen direction

Use the warm architectural presentation in **508810.mp4** as the main direction, with the strong project imagery and Arabic hierarchy in **508807.mp4**. Keep KFATA’s original logo and restrained charcoal/gold/stone palette. The neon city and enclosing wire grid in 508808 are a secondary reference; the wire grid outside the displayed website is part of that video presentation and is not proof of a website feature. Do not combine all reference styles.

The critical feature is the construction sequence around 1–8 seconds in 508810: foundations/columns, floor structure, wall and glazing completion, materials, lighting and landscape, ending on the completed villa. It is a coherent architectural scene, not the existing logo-path intro or ordinary section fades.

## Implementation choice

Use one original **pre-rendered architectural video** as the hero asset, with responsive static poster fallback. Keep live 3D off the public visitor path to avoid loading a renderer on every phone. Target a 6–8-second scene, one play then a finished-building hold. This is a design brief, not a claim that the video has been created.

If an original scene cannot be generated/rendered with the execution environment’s actual tools, identify that precise asset dependency. Do not consume repeated site-wide redesign cycles substituting logo lines, CSS cubes or unrelated stock buildings. The supplied reference video must not be embedded/copied as the asset.

Keep text, navigation and quote/project actions in HTML and immediately usable. Do not use this as a blocking preloader. Use muted/playsinline playback, reduced-motion/static fallback and a visible skip/pause mechanism. Label the generated architectural scene as an illustrative concept; do not identify it as a KFATA project. Preserve real project photographs for the portfolio.

## Site composition

The content work in CONTENT_RECONCILIATION.md is separate and should proceed without waiting for the video. Build the story from verified company capabilities and project categories: banking/headquarters, offices, schools, residential villas, cash-centre construction, industrial works, roads/landmarks, parking and fit-out. Keep the footer and policy work already delivered; no further full-site restyling is required to make the hero asset.

Acceptance for the hero is an actual short preview recording showing all construction stages and a usable 360px/mobile layout, followed by targeted browser/performance checks. Do not restart database seeding or overwrite the owner’s content.

## Added reference review: AMAQ and Red Sea Global

References supplied by the owner:
- https://amaqksa.com/
- https://www.redseaglobal.com/en/

AMAQ was inspected in the browser: a large photographic hero/slider with prominent headings, followed by company story, recognition, services, featured projects, contact and footer. Adopt the hierarchy and image-led presentation; do not copy its content, claims, assets or awards.

Red Sea Global's readable homepage presents separate company, business/services and portfolio navigation with a rich institutional footer. It describes itself as an integrated real-estate developer, not just a contractor. Direct browser rendering returned a CloudFront 403 in this environment; its animation was not visually reviewed. Adopt information organization only, scaled to KFATA's actual capabilities. Do not invent investment, destination, subsidiary or government-affiliation sections for KFATA.

## Unified delivery sequence

1. Apply source-grounded content from CONTENT_RECONCILIATION.md to the actual site with the protected updater, resolving missing parents and explicitly reviewing any skipped editorial revisions.
2. Expose that content through a focused navigation: Company / Expertise / Sectors / Projects / Contact. Keep Arabic and English connected and maintain public URLs.
3. Use a complete architectural-video hero as specified above. Its production is a separate original-asset task; plain section fades are not acceptance evidence for the construction scene.
4. Curate the homepage around company identity, six source-backed services, real approved selected projects, sectors, work process, quality, contact and corporate footer.
5. Build project pages as case studies with verified scope/location, appropriate real imagery, gallery and related services. Never fill a missing project photograph with another project's photo.
6. Preserve editable footer columns for Company, Expertise, Projects and Policies plus real contact channels. Keep only live meaningful links, including privacy, terms and cookies.
7. Capture a real desktop/mobile preview showing content and construction motion. Run targeted checks, deploy KFATA alone, then verify the public pages and record the actual deployed commit.

The supplied reference videos remain analysis references, not website assets. The approved public source photographs remain subject to their existing scope; obtain an explicit decision for additional original imagery before publishing it. Do not hold the already sourced text update while waiting for a motion asset.
