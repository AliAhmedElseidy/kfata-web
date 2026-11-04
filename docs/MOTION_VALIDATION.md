# Architectural motion delivery — 2026-11-05 (Asia/Riyadh)

Live: https://kfata.elsaidy.org/ar/ and https://kfata.elsaidy.org/en/ . Application image/deployment marker: `f5e2454a076f702a46f2e401f02b914f255d173d`. [Application CI passed](https://github.com/AliAhmedElseidy/kfata-web/actions/runs/41912567100). Later documentation commits do not change the application marker. [PR 1](https://github.com/AliAhmedElseidy/kfata-web/pull/1) remains open.

## Delivered behavior

- Original-logo architectural introduction: six fine geometric paths, logo reveal and fade; removed after 1,320ms, once per browser session using the existing session key. Noninteractive and hidden from assistive technology; content remains available underneath. No loading percentage, image-load wait or scroll lock.
- Hero title, description and actions enter in a bounded sequence. The heading remains fully opaque. Existing real project photograph and mobile crop are preserved. Responsive image preloads match the picture sources. Standard motion optionally settles the image once over 950ms.
- Unified once-only IntersectionObserver section entrances, small transforms, opacity starting at .96, stagger capped at 180ms. Quiet: 360ms/6px; standard: 560ms/12px. No heavy dependency, continuous motion or hidden-until-JS content.
- Architectural hero frame, refined buttons/arrows/underlines, sticky header with measured anchor offset, balanced mobile footer and corrected English mobile header/title. Content and actions remain accessible without hover.
- Mobile navigation retains native details disclosure. Escape closes and restores summary focus. Gallery uses native dialog, selected-image loading, thumbnail preview, short transition, language-aware arrows, explicit Tab wrapping, Escape and opener-focus restoration. Reserved scrollbar space prevents modal horizontal jumps.
- Existing Wagtail Brand settings are reused: animations, opening animation, and motion level (`subtle`/`full`, existing labels Subtle/Full). No duplicate fields, dependencies, database migrations or content import. Hero images/text/buttons, selected projects, block ordering/backgrounds and footer remain editable through the existing fields; see [content guide](CONTENT_GUIDE.md).
- CSS and JavaScript respect reduced motion. Changing the preference cancels active effects. Default HTML remains readable and navigable when scripting fails. Local PerformanceObserver diagnostics stay in the DOM; no analytics endpoint was added.

## Actual browser checks

Windows Codex in-app Chromium against production HTTPS. The prior phase's unidentified-Chrome interruption was resolved by establishing the known in-app browser tab and URL; the outstanding checks below were performed in this session.

| Area | Arabic and English | Widths | Result |
|---|---|---|---|
| Home and hero actions | both | 360/768/1440 | No horizontal overflow or broken loaded images; both mobile actions visible |
| Services index | both | 360/768/1440 | Layout and links reviewed, no horizontal overflow |
| Project detail | Arabic ANB tower / English residential villas | 360/768/1440 | Facts, images and gallery layout reviewed |
| Footer | both | 360/768/1440 | Balanced columns, sticky header remains at top, links available |
| Gallery | both | desktop and mobile | Direction-aware arrows, Tab/Shift+Tab confinement, Escape, focus restore and scroll unlock passed |
| Mobile menu | Arabic | 360 | Open, Tab to navigation, Escape, summary focus restore passed |
| Project filters | both | production | Keyboard Enter for Arabic banking and English residential click select the correct published project |

Fresh-session intro played once; reload did not replay. Gallery desktop header width was identical before/after opening (1424.800px). English mobile header is 135px and hero button bottoms are 640/709px within the 800px viewport. No sections had computed opacity zero.

Reduced motion was tested locally with the real Windows Animation effects preference switched Off: root reported reduced, no opening intro, sections opacity 1/transform none. The original On setting was restored and normal motion verified. Quiet, standard and animations-off settings were exercised on the local database and restored to their original values; production settings were not toggled.

Without JavaScript: a private local QA settings module added CSP `script-src 'none'` on port 8034. Browser DOM confirmed no script diagnostics/navigation class, all sections visible, native mobile details functioning, and gallery image links opening the full image directly. This was an actual script-execution-blocked browser session, not a production CSP change or a claimed browser-settings toggle.

## Measured performance and limits

PerformanceObserver LCP and layout-shift entries were read in the real browser, separately from navigation TTFB. Current Windows network, no throttling, uncontrolled cache, one sample per viewport in each series. Final samples reported hero IMG as LCP and image transferSize 0 (cached). These are observations, not Lighthouse scores, controlled cold-cache comparisons or field Core Web Vitals.

| Viewport | Before application b4b98b3 LCP | Final f5e2454 LCP | Final observed CLS | Final TTFB |
|---|---:|---:|---:|---:|
| 360×800 | 1,344ms | 1,596ms | 0.0000 | 1,190ms |
| 768×1024 | 1,908ms | 1,540ms | 0.0000 | 1,080ms |
| 1440×1000 | 1,340ms | 1,040ms | 0.0000 | 739ms |

Before samples had no observed layout-shift entries. Intermediate after-build samples were slower: 2,660–2,864ms in the saved series, with an additional desktop observation at 3,220ms. The final implementation keeps the heading opaque and preloads the matching responsive hero, but varying server/network/cache conditions prevent attributing the difference solely to those changes. Mobile final LCP is slower than its before sample. Do not claim universal improvement or guaranteed sub-2.5s loading.

Raw evidence: [before measurements](validation/motion-performance.json), [intermediate/final measurements and service/footer checks](validation/motion-browser-results.json). TTFB is not LCP. Representative INP, controlled cold-cache/slow-network testing and exhaustive screen-reader/contrast auditing remain open. No short video was recorded; actual still screenshots are available.

## Regression, preservation and operations

- Final local SQLite suite: 31 passed in 80.698s ([raw log](validation/motion-sqlite.txt)). PostgreSQL 16 suite: 31 passed in 120.670s at commit 8843219 ([raw log](validation/motion-postgresql.txt)); subsequent changes concern frontend opacity/diagnostics and hero preload. Final application CI passed its complete suite/build. JavaScript syntax and no model drift checks passed.
- Read-only `deploy/audit.sh` and actual Nginx ingress inspection preceded server mutation. Consistent pre-motion snapshot: `/opt/kfata-web/backups/20261104T204024Z`; previous application retained as `kfata-web-web:before-motion`. Only KFATA web was briefly stopped by the consistent backup and restarted. This phase did not repeat a restore drill; prior restore evidence remains historical in HANDOVER.
- Final production SHA-256 comparisons against the pre-motion snapshot matched `home_homepage`, `home_contentpage`, `home_brandsettings`, `wagtailcore_page` and SMTP settings; all existing enquiry IDs remain. Private hash snapshots are in host `operations/motion-before.json` and `motion-final.json`, outside Git. No raw customer/credential data is committed. No seed, content refresh, migration or publication command was run this phase. Owner English ANB tower pending revision remains untouched.
- KFATA web and PostgreSQL healthy; web binds only 127.0.0.1:8097, PostgreSQL has no host port. Mailcow/ERPNext ingress, stacks and mail DNS were preserved. Final HTTP checks returned Mailcow 200 and ERPNext 302.
- SMTP transport, off-server scheduled backups, provider proof of physical location and unapproved content remain the previously documented owner/operations follow-ups. No real email or customer enquiry was sent during this frontend phase.

## Visual evidence

[Before desktop](preview/motion-before/home-ar-1440.jpg) → [After desktop](preview/motion-after/home-ar-1440.jpg); [before mobile](preview/motion-before/home-ar-360.jpg) → [after mobile](preview/motion-after/home-ar-360.jpg). [Full homepage](preview/motion-after/home-ar-full-1440.jpg).

The [after folder](preview/motion-after/) also contains Arabic/English home, services, project and footer at all three widths, mobile navigation, galleries, reduced-motion and script-blocked sessions. All are browser captures of actual pages, not design mockups. English tower publication remains owner-controlled; English project QA uses the published residential page.
