# Redesign validation — 2026-11-04

## Executed

- 31 local SQLite tests passed on the final sitemap/application changes (18.977s); raw `validation/redesign-sqlite.txt`. Earlier final presentation-only subset:3 passed in11.659s. Covers dry-run safety, row/revision preservation, pending drafts, stable policy identity after rename, intentionally cleared footer/body, private/draft chooser suppression, translated footer/policy URLs, approved gallery rendering and canonical-only sitemap.
- PostgreSQL16 full suite passed on final app b4b98b3 (31 tests,152.465s). CI also passed: https://github.com/AliAhmedElseidy/kfata-web/actions/runs/41734281221 . The active SHA is recorded in HANDOVER.md and the deployment marker; raw final report is `validation/redesign-postgresql.txt`. Initial test invocation accidentally used production HTTPS-redirect settings, causing redirect assertions; corrected to dev test settings with the real PostgreSQL DATABASE_URL and isolated temporary media roots. No test failure was deployed.
- Build/static manifest, dependency check, Django check, migration0011, no model drift and Node JavaScript syntax check passed. Production retains only deliberate HSTS includeSubDomains/preload warnings.
- Deployed Django client checked50 public routes, unique descriptions per language, canonical URLs and valid JSON-LD;48 ContentPages plus2 homes. Sixteen project groups remain drafts, ambiguous branch404.
- Actual HTTPS crawl checked50 content routes and36 additional internal link/asset URLs, all200.25 distinct referenced asset URLs observed. Verified approved phone/WhatsApp/address-map hrefs; no WhatsApp message was sent, and destination account ownership/exact geocoded pin is not asserted. Root302 is a language redirect, removed from sitemap by the final patch.
- Actual HTTPS form retest: missing CSRF403; valid PNG/consent POST302 with receipt, persistence, JPEG sanitization; anonymous private download302, permissionless staff403, authorized200, public path404. The synthetic record/file and temporary test user were removed.
- Before/after SMTP configuration fingerprints match. Existing account/enquiry IDs preserved; no SMTP credential, owner password or real enquiry data was printed, changed or committed. Existing owner English tower draft was skipped.
- Separate KFATA web/db remain loopback8097/private. Mailcow200/ERPNext302 before/after. Existing stacks and mail DNS untouched. Consistent backup precedes content/deployment; previous app image retained as `kfata-web-web:before-redesign`.

## Limits

See DESIGN_REVIEW.md for the exact browser interruption, missing after screenshots and pending360/768/1440/keyboard/gallery/JavaScript-off/reduced-motion checks. Only a desktop local preview was visually inspected after design changes. HTTP200 and template tests do not prove final responsive design or native dialog focus behavior.

TTFB median from five Windows curl visits:1.638333s before,1.239596s after, uncontrolled network/cache. Raw timing files are under validation/. New LCP/CLS/INP were not measured. Existing legacy validation belongs to the earlier phase.

Country remains Saudi Arabia **as management-provided information**, at the owner's renewed instruction. No hosting contract/provider-control-panel evidence established the physical location; RIPE registration is not physical evidence. Automated off-server backup transfer and actual SMTP-provider testing remain unconfigured. Terms/cookies describe this informational/enquiry site; no unrelated payment/shipping policies or compliance certification was added.

Owner brand/footer settings and homepage edit screens returned200 on the deployed app. A further protected manual off-server copy of the new-content snapshot20261103T225122Z was made and both SHA256 values matched; this does not configure recurring off-server transport or constitute a new restore test.
