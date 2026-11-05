> Execution update: [CONTENT_DELIVERY.md](CONTENT_DELIVERY.md). Source text has been applied and publicly verified; earlier unreachable-host statements describe the authoring environment. The original construction scene now exists as a local review prototype/recording; it is not deployed.

# Company-content reconciliation — 2026-11-05

## Findings and scope

The supplied image-only PDFs were reread visually (profile: 28 pages; portfolio: 45 pages), with English OCR and enlarged review of relevant narrative/project pages. This is a source/code audit. The production site could not be fetched from the available web tool and SSH returned `Network is unreachable`; live database contents are not independently confirmed here.

Existing `import_profile_drafts` contains 15 additional project groups with short summaries and no project-body creation. Its `fill` method does not enrich an already populated body. Portfolio examples for the Jeddah headquarters, internal clinic, control room, tower cafe, garage finishes, road blockers and parking shades are not separate entries in that project list.

This follow-up adds 39 bilingual content records (24 project groups, 6 services, 7 sectors, About and Quality), traced to source pages. It preserves existing URLs, layouts, media selections, owner revisions, unpublished owner changes and the excluded ambiguous Golden Belt attribution. It adds no new source photographs, certificate scans, legal IDs or operational-security specifications.

Some project groups overlap as parts of a broader banking programme. They are portfolio case-study topics, not 24 distinct contracts or a company-wide project count.

The industrial page title previously implied a warehouse. The new copy uses the supported broader industrial-facility description and does not invent a precise facility subtype.

## Source matrix

| Page key | Kind | Profile pages | Portfolio pages |
| --- | --- | --- | --- |
| about | page | 2, 5 | 2, 3 |
| design-build | service | 5 | — |
| contracting | service | 5, 15, 18, 22 | 26, 27, 28 |
| renovation | service | 5, 6, 7, 9, 10, 11 | 6, 12, 13, 14, 22 |
| landscaping | service | 5, 14 | — |
| furnishing | service | 5, 16, 22 | 8, 9, 10, 11 |
| technology | service | 5 | 5, 12 |
| banking | sector | 6, 7, 9, 10, 11, 12, 13, 14 | 6, 12, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25 |
| commercial | sector | 15, 16, 17 | 10, 11, 15, 34, 35 |
| education | sector | 18 | 26 |
| industrial | sector | 21 | — |
| residential | sector | 22 | 36 |
| public-spaces | sector | 19, 20 | 29, 30, 31, 32, 33 |
| entertainment | sector | 5 | — |
| anb-new-tower | project | 6 | 6, 7, 8, 9 |
| anb-old-head-office | project | 7 | — |
| anb-al-awali | project | 9 | 13, 14 |
| anb-al-majmaah | project | 10 | 16, 17 |
| anb-southern-branches | project | 11 | 22 |
| anb-atm-sites | project | 12 | 24, 25 |
| telemoney-centres | project | 13 | 23 |
| anb-courtyard | project | 14 | — |
| amnco-cash-centre | project | 15 | 27, 28 |
| office-fitout | project | 16 | — |
| restaurant-fitout | project | 17 | 34, 35 |
| school-muzahmiyah | project | 18 | 26 |
| al-ghat-landmark | project | 19 | 32 |
| rumah-landmark | project | 19 | 33 |
| road-works | project | 20 | 30 |
| warehouse-finishing | project | 21 | — |
| residential-villas | project | 22 | 36 |
| anb-jeddah-head-office | project | — | 15 |
| anb-internal-clinic | project | — | 21 |
| anb-control-room | project | — | 12 |
| anb-tower-cafe | project | — | 10, 11 |
| garage-finishing | project | — | 29 |
| road-blocker-installations | project | — | 29, 30 |
| parking-shades | project | — | 31 |
| quality-safety | page | 4 | 3 |

## Deliberately unresolved

- Company-wide year/area/staff/project/repeat-client numbers are retained in review-only metadata, not promoted as verified current claims.
- Current legal name, certificate status, dates and detailed contract/security specifications are not inferred.
- Only the photographs separately approved earlier remain available; this update does not expand their publication permission.
- The owner-authored English tower draft remains protected and is reported as skipped.

## Apply on the existing server

Read the current host checkout and deployment marker; retrieve this reviewed follow-up without discarding local/editor changes. Run the application backup first. Build the new application image and run its management command in the same existing KFATA project/environment, not a stale running image.

```sh
python manage.py enrich_company_content
# Preview prints would-create, would-update and protected pages without writing.
python manage.py enrich_company_content --apply --publish
# Or use --apply alone to create editorial drafts without publication.
```

First application is recorded per page. Re-running does not restore a body cleared by the owner or recreate a renamed page. Draft-only application is not silently converted to automatic publication by a later rerun: publish those reviewed revisions deliberately in Wagtail. Missing parents/locales and protected pages are explicitly reported, never replaced or silently created at another location.

The command publishes only when explicitly invoked with --apply --publish. It does not modify homepages, BrandSettings, SMTP, customer records, accounts or source imagery. Check public project listings/relationships and language links after application. Do not claim live content changed merely because this code was pushed.

## Validation

Eight targeted SQLite tests passed (12.492s); migration drift check reported no changes. Targeted tests exercise dry run, complete source references and bilingual records, creating/publishing pages and relationships, preservation of owner drafts/homepages, repeat safety after rename/clearing, draft-only behavior and curated layout preservation. See the PR for the observed test result. PostgreSQL/runtime deployment is not claimed by this local audit.
