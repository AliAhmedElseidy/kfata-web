# KFATA 2026 company-profile media refresh

## Sources and validation
- The 28-page `KFATA International Contracting Company Profile(1).pdf` is a **flattened-page/image** brochure. Project photographs are therefore cropped from pages, not independently embedded at original camera resolution.
- The supplied 13-page `kfata(1).pdf` is byte-identical to `kfata.pdf` (SHA-256 `c3e2a3c174f3db071659b13f4dc6e0e00f696cab2b4f8ffba885e149b8e27324`).
- The 13-page brochure includes additional operational subjects: civil works, infrastructure, electromechanical works, electrical, HVAC/plumbing and temporary fencing on p5; residential villa photographs on pp6–7 (the same photos repeated); Al Wadi company project photos p8; organization chart p9; letters/certificates pp10–12 and third-party logos p13.
- The old 28-page brochure adds distinct banking, commercial, retail, school, roads, industrial and residential photo groups, mainly pp6–22.
- The existing content enrichment remains untouched. Avoid claiming the source material demonstrates additional unique contracts, verified certificate validity or permission to use others' trademarks.

## Current repository state
The active application code is in `feat/kfata-source-enrichment`, **not** the minimal `main` branch. This enhancement branch is based on it. Existing Wagtail project structure, live case studies and hero/scene controls are preserved.

## What changed
- `home/content/kfata_2026_additions.json` adds **nine** traceable bilingual content topics (six services, the organization page, a review-only clients/partners page, and Al Wadi project). It maps 15 project photo group slugs conservatively.
- `home/management/commands/import_kfata_2026.py` imports only images from `assets/source-2026`, creates missing bilingual pages and appends project galleries without replacing any gallery or hero photo. Imported images use source IDs, and one-time gallery markers protect against duplicate insertion.
- Extra third-party logos, raw certificates, commercial-registration IDs, and ambiguous project group imagery remain outside the automatic public path. The partners page is deliberately kept draft.
- `home/test_kfata_2026.py` exercises dry-run, bilingual pages, gallery creation, idempotence, protected owner revisions and publication flags.

## Important: no automatic deployment
PDF files, certificate scans, raw partner marks and private materials must not be committed. The website currently runs a Docker-hosted Django/Wagtail service; merging this branch alone does **not** update the running Docker image, Wagtail database or media storage.

Before running any import:
1. Review **every** candidate crop from the separately delivered `KFATA_PDF_photo_assets_2026.zip`; the cropped images are candidate assets and may include headings/borders/background or represent overlapping contracts.
2. Select only photos eligible for publication, and copy the selected `.webp` files from ZIP's `assets/source-2026` directory to the corresponding folder in the private build checkout, or a reviewed media upload route. Avoid the ZIP's `review-only` directory entirely.
3. Take a consistent production backup, inspect the actual deployed commit and current Wagtail revisions. Preserve all owner changes, contact/SMTP settings, enquiry records, and other services.
4. Run a full test suite (including PostgreSQL integration), migration drift checks and representative page QA on a staging build. Do not run legacy `seed_content` on production.
5. Preview, then explicitly apply. **Keep publication off until photo/copy review is completed.**

```sh
python manage.py import_kfata_2026
python manage.py import_kfata_2026 --apply
# Only after editorial approval of the pages and photographs:
python manage.py import_kfata_2026 --apply --publish
```

**Publication caveat:** If the first import was draft-only, the one-time image marker prevents duplicate insertion. Publish approved draft revisions from Wagtail deliberately; rerunning `--publish` should not override an owner/editor revision.

## Project attribution
Photo-group mapping is curated, not an assertion that similarly branded pages are one contract. The **Al Wadi** photographs form a new topic with no invented location, area, date or monetary amount. The source lists no certified current year/size/team count in this new brochure. `anb-alhizam`, `anb-branches` and `landmarks` are marked review-only: they should be sorted into correctly attributed project pages before attaching.

## Runtime risk
The JPEG/WEBP extraction may produce unsuitable rectangular crops due to different montage layouts between source pages; check before public use. Uploading a ZIP to the chat is not the same as committing images to GitHub or uploading Wagtail media. No real production changes or performance improvements are claimed.
