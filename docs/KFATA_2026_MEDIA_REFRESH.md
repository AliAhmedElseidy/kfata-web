# KFATA 2026 source and gallery refresh

- The supplied 28-page company profile and 13-page brochure were checked against the archive manifest and the project images. The 13-page brochure covers company background and values (pp. 3–4), work categories (p. 5), repeated villa examples (pp. 6–7), Al Wadi offices (p. 8), the organization chart (p. 9), historic documents (pp. 10–12) and a mixed logo wall (p. 13).
- The previous bilingual reconciliation remains in place. This update adds six service topics, the organization chart in editable text, a page linking named organizations to documented portfolio work, and an Al Wadi case study connected to fit-out and the commercial sector. Construction and landscaping already have public service topics.
- 58 selected WebP photographs cover 14 project topics. The allowlist records the brochure, source page, SHA-256 and bilingual description for each derivative. Montage edges were trimmed. Existing ANB tower and villa photographs, repeated views, an ambiguous ATM sign, the mixed branch/landmark groups, identifying technical-room images, and unverified documents or isolated marks were excluded. Al Hizam remains unpublished. Certifications remain in Wagtail pending verification.
- Galleries are editable in each language. The image's alt text is independent from the optional visible caption. Mobile thumbnails use a compact WebP; click, touch and keyboard navigation use the existing accessible gallery dialog. The approved bilingual construction scene stays under Wagtail Brand settings.

## Apply to the existing KFATA project

Keep originals, ZIP files and the reviewed WebP directory outside Git. Supply only the derivatives matching the checked-in allowlist. The import rejects any extra recognized image name, changed checksum, invalid WebP or duplicate checksum. Preview reports preserve/create/attach counts and writes nothing. Application appends galleries to eligible projects, preserving existing covers, blocks, drafts and owner revisions. A repeated import skips applied galleries and existing pages.

After a consistent KFATA-only backup, run the state-only Wagtail migration and preview with the reviewed files mounted read-only into a one-shot Compose web container:

```sh
docker compose run --rm --no-deps -v /private/reviewed-photos:/reviewed-photos:ro web \
  python manage.py import_kfata_2026 --asset-dir /reviewed-photos
docker compose run --rm --no-deps -v /private/reviewed-photos:/reviewed-photos:ro web \
  python manage.py import_kfata_2026 --asset-dir /reviewed-photos --apply --publish
```

The public repository contains the source code and attribution manifest. The website serves the reviewed image derivatives through Wagtail media. Private documents and third-party brand assets stay out of both.
