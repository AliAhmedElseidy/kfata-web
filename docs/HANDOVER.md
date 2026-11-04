# KFATA operational handover — 2026-11-05 (Asia/Riyadh)

## Live service

- [Arabic](https://kfata.elsaidy.org/ar/), [English](https://kfata.elsaidy.org/en/), [administration](https://kfata.elsaidy.org/admin/).
- [PR 1](https://github.com/AliAhmedElseidy/kfata-web/pull/1) stays open, without merge or force push.
- Running application: `f5e2454a076f702a46f2e401f02b914f255d173d`, recorded at `/opt/kfata-web/operations/deployed-commit`. Later delivery-documentation commits do not change that application image.
- 50 public page routes: two home pages and 48 ContentPages. Six services and seven sectors have source-based copy in both languages. Original wordmark is installed. Eight specifically approved source project photographs and one explicitly labeled generated engineering illustration are published; source/approval details are in assets/README.md.
- Contact details, Al Olaya address and 90-day enquiry retention were approved by the owner. Bilingual privacy is published; enquiry collection and search indexing are enabled. Search ownership verification/submissions were not performed and discovery/rankings are not guaranteed.
- Sixteen bilingual project groups remain drafts (15 additional groups plus the inconsistent Al Hizam/Golden Belt attribution). The approved quality/safety summary, terms and cookies pages are public. Certificates, news and careers remain drafts pending current approved material. Legal Arabic name, founding figures and certificate claims are withheld. See [source review](SOURCE_REVIEW.md).

## Owner account and SMTP

Account: `kfata-owner`. Retrieve its unique initial password through your own trusted SSH session from `/root/.config/kfata-web/owner-initial-password` (0600, parent 0700). Do not paste it into chat, GitHub or tickets. Change the application password after taking ownership. Tested SSH public-key access is available; the owner should also change the previously shared root password after preserving that working access. This session did not change the root password.

From Wagtail **Settings → SMTP** (owner-only), select panel delivery and enter host, port, STARTTLS/SSL, username, new password, sender and recipient, then save. Blank password preserves the saved credential; the explicit clear option removes it. The test button sends a configuration test using the **saved** settings only, without client data. Test acceptance is not proof of inbox delivery. No SMTP account exists yet: mode is **off**, no password is stored, and no real notification delivery is claimed. Enquiries still save and remain visible under Enquiries.

SMTP passwords are Fernet-encrypted in the database, never returned in the settings form. Independent root-only recovery key: `/root/.config/kfata-web/smtp-encryption-key`; Compose loads `SMTP_ENCRYPTION_KEY` from root-only `.env`. Preserve this key separately in the owner's secret store before using saved SMTP credentials. Database-only recovery cannot decrypt them without it; alternatively re-enter the SMTP password. Restored drill instances force `OUTBOUND_EMAIL_DISABLED=true` regardless of saved panel mode.

## Manage KFATA only

Checkout: `/opt/kfata-web`. Independent project `kfata-web`, PostgreSQL 16, private media volumes/network. Host Nginx routes this domain to `127.0.0.1:8097`; database has no host port. Web/database memory ceilings 768/512 MiB and CPU ceilings 1.0/0.75. No Docker socket or Mailcow/ERPNext databases/networks are shared.

```sh
cd /opt/kfata-web
docker compose -p kfata-web ps
docker compose -p kfata-web logs --tail=100 web
docker compose -p kfata-web restart web
bash deploy/backup.sh
cat operations/deployed-commit
```

Before updates: capture application SHA/image, back up, review migrations/rollback, build and test the exact commit, apply migrations once and update only this project. Git rollback alone does not restore data. Preserve edited pages, revisions and translations. `setup_roles` configures draft editors, publishers and brand/enquiry managers; SMTP/user administration stays owner-only unless explicitly delegated. See [content guide](CONTENT_GUIDE.md) and [deployment](DEPLOYMENT.md).

## TLS, retention and recovery

- Certbot uses existing host installation/webroot `/var/lib/letsencrypt`. `certbot.timer` is active; domain-specific deploy hook validates/reloads Nginx. Certificate expires **2027-02-01 17:24:44 UTC**. A real production renewal succeeded; staging dry runs failed with resets/timeouts and are not reported as successes.
- Proxy configuration before changes is preserved in `operations/nginx-before.tar.gz`. Existing vhosts and mail DNS were preserved. Mailcow returned 200 and ERPNext 302 before and after deployment.
- `kfata-retention.timer`: 03:05 Riyadh, purges enquiries/private attachments older than 90 days and expired sessions. Contract records belong in separate company systems; this form database is not the contract archive.
- `kfata-backup.timer`: 03:15 Riyadh plus up to five minutes jitter; retains completed local snapshots 14 days. The consistency freeze briefly stops only KFATA web, so a short 502 interval can occur. An EXIT trap restarts it.
- Earlier-phase tested recovery snapshot: `/opt/kfata-web/backups/20261103T211956Z` (UTC). Restore into `kfata-restore-final2`, independent credentials/network/volumes, loopback 8099, returned 42 ContentPages plus two home pages and one synthetic enquiry. Media archive comparison passed, private 10x10 JPEG restored, authorized download 200/anonymous 302. The fixture and private file were subsequently removed from production and drill. Drill containers are stopped; volumes remain for inspection. An earlier failed initialization attempt is stopped as `kfata-restore-final`; no production data was affected. The helper now waits for TCP PostgreSQL readiness to avoid the temporary initialization-server race.
- Manual off-server copy: `C:\Users\dell\.codex\backups\kfata-web\20261103T211956Z`, ACL restricted to current owner, SYSTEM and Administrators; both SHA-256 values match. Scheduled off-server transfer is **not configured**. Select an owner-controlled destination and credentials; local VPS copies alone do not cover host loss.
- Dumps/media contain private data; never commit them. `.env`, owner password and SMTP recovery key are excluded. Preserve recovery secrets separately. See [backup/restore](BACKUP_RESTORE.md).

## Remaining limits

The owner reported Saudi Arabia as the physical hosting country. RIPE network registration for the IP range reports DE/Contabo; registration is not proof of server location. Physical datacenter location has not been independently verified. Confirm it from the hosting contract/control panel and update both privacy pages before relying on the location claim. Current notice attributes the location to management-provided information.

No SMTP transport was tested against a real provider; configure it later from the panel as requested. Unapproved content stays draft. Customer PDF uploads remain unavailable pending scanning/sanitizing. Video content requires an approved asset; the video block exists, while the main hero currently supports an image. Slow-network/cold-cache, representative INP and exhaustive accessibility QA remain incomplete. Real script-blocked/reduced-motion browser sessions passed in the motion phase; see MOTION_VALIDATION.md. Recent LCP observations varied and do not establish that all performance targets pass. [Validation](VALIDATION.md) records the evidence and limits.

## 2026-11-04 redesign delivery

Read DESIGN_REVIEW.md and REDESIGN_VALIDATION.md for the new presentation, asset approvals, test evidence and incomplete browser work. Current source adds local Arabic/Latin fonts, curated project/service/sector blocks, editable footer columns and process/captions, source galleries and native-dialog enhancement. One owner-authored English ANB tower draft was deliberately skipped; merge it through Wagtail before publishing its gallery update.

Consistent pre-content snapshot: `backups/20261103T222742Z` (old application image retained as `kfata-web-web:before-redesign`). A further snapshot `backups/20261103T225122Z` captures the new content/media and pending owner draft before the final sitemap-only image update. These are UTC directory names. This phase did not repeat an isolated restore; the earlier real restore evidence above remains historical. Do not use an old image/schema snapshot interchangeably with the new0011 schema/content.

SMTP fingerprints and existing user/enquiry IDs matched across the content update. The phase did not configure or send real SMTP mail. Actual synthetic form/private-file retest succeeded and was cleaned up. Mailcow and ERPNext remained200/302. Footer WhatsApp publication was explicitly approved for +966504552257; the map is an address search, not a verified coordinate pin.

Historical redesign-phase interruption: browser automation stopped when it could not determine the native Chrome URL confidently. That interruption was resolved in the subsequent motion phase using the established in-app browser; the requested responsive, gallery/keyboard, script-blocked and reduced-motion checks and after measurements are now recorded in MOTION_VALIDATION.md.

The new-content snapshot225122Z also has a manual restricted-access PC copy at `C:\Users\dell\.codex\backups\kfata-web\20261103T225122Z`. Matching SHA256: database `c995806f57331c57714deba12a0330933875462f8f49d13bb1a0c2b9f828b7fc`; files `705285849d7889e51dff58c2446f5ff9c9e6ab63c6793a6891a0b5149d8773ea`. No scheduled off-server transfer or new restore claim.

## 2026-11-05 architectural motion delivery

Read [MOTION_VALIDATION.md](MOTION_VALIDATION.md) for current application behavior, actual browser matrix, before/after captures and performance limits. Original-logo intro lasts 1,320ms once/session; existing settings control animation, intro and quiet/standard levels. Native menu/gallery keyboard focus, both languages and 360/768/1440 were tested. Final cached LCP samples: 1,596/1,540/1,040ms respectively; observed CLS0, with slower intermediate samples retained. This is not controlled cold-cache or field certification.

Pre-motion consistent snapshot: `backups/20261104T204024Z`, previous image `kfata-web-web:before-motion`. Final page/content/brand/SMTP hashes match before, existing enquiries preserved, owner English tower draft untouched. No content import or migration ran. Current web/database healthy; Mailcow200 and ERPNext302. The older restore and manual PC-copy evidence above remain historical; no new restore/off-server-copy claim for this snapshot.
