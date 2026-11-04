# Backup and recovery

Run `bash deploy/backup.sh` in `/opt/kfata-web`. It locks against concurrent runs, briefly stops only KFATA web to freeze writers, dumps PostgreSQL custom format and archives public/private media, then restarts web via EXIT trap. A short 502 interval is possible. It records deployed commit/image ID, SHA256SUMS and .complete. Permissions are restrictive; completed local snapshots retain 14 days. Daily systemd schedule is 03:15 Riyadh +≤5min jitter. Existing stacks are unaffected.

Backups contain customer data. Keep them access-controlled and transfer to a chosen secure off-server destination. A manual owner-PC copy was verified, but recurring off-server transport is not configured. `.env`, initial owner password and SMTP encryption key are excluded: preserve recovery secrets separately. Saved SMTP passwords need the original key, or must be re-entered. Do not expose environment/config files in support output.

## Isolated drill

Use a fresh project name matching `kfata-restore-[a-z0-9-]+` and unused loopback port. The helper refuses existing containers, volumes or configuration and validates archive paths/types before extraction. It uses a separate database password and files under `operations/<project>.env` and `.yaml`. It waits for PostgreSQL TCP readiness, avoiding the entrypoint's temporary Unix-socket initialization server. It disables indexing and forces OUTBOUND_EMAIL_DISABLED=true even if restored panel SMTP was enabled.

```sh
KFATA_DRILL_PROJECT=kfata-restore-example KFATA_DRILL_PORT=8100 \
  bash deploy/restore-drill.sh backups/<UTC-snapshot>
```

Use the image matching saved image-id/commit; the helper selects `kfata-web-web:latest`, so verify/rebuild that tag against the snapshot before a later recovery. Never assume the current latest image matches old database migrations. Restore does not capture Docker images or secrets.

Verify counts/routes/content, compare archive to restored files with `tar --diff`, test protected attachment access, and stop only the isolated drill project after inspection. Do not use down -v or production volume paths. A recovered dataset may contain enquiries since deleted under retention; restrict access and reapply retention before any production cutover. Take a current backup and plan cutover separately; running this helper is not production rollback.

## Executed final drill

Snapshot `20261103T211956Z`, application `5d5bd9bf016c95581f08e375214cf3a312eb99fd`, restored as `kfata-restore-final2` on8099. 42 published ContentPages +2 homes, synthetic enquiry with 10×10 private JPEG recovered, file archive comparison passed, Arabic HTTP200, owner private download200 and anonymous302. Outbound kill switch verified true. Only that synthetic fixture/file was removed from production and drill afterward. Drill stopped, volumes retained. Earlier initialization attempt `kfata-restore-final` stopped after a readiness race; corrected helper passed on fresh volumes.

Manual PC copy `C:\Users\dell\.codex\backups\kfata-web\20261103T211956Z` is restricted to the current Windows owner, SYSTEM and Administrators. Verified hashes:

```text
72b27780153d73218acb20673bc8e7e044a0bfdcdf56075d912ffe596aad19f1  database.dump
5a8c6a75594884dc00cbf6467049acffef4e3a7bf570f42c9567415c615bd7b1  files.tar.gz
```

Older stopped `kfata-restore-check` also retains its separate volumes for inspection. No Mailcow/ERPNext services or volumes were removed.

## Redesign snapshots (2026-11-04 Riyadh)

`20261103T222742Z` precedes the0011 presentation migration/content update; `20261103T225122Z` captures the new content/media and owner pending English tower draft under f98e413 before a sitemap-only application patch. Snapshots and previous image were preserved. No new isolated restore was executed during this design phase; earlier recovery proof above remains for its original snapshot. Daily local backup/retention remain active; recurring off-server transfer is still not configured.

The new-content snapshot225122Z also has a manual restricted-access PC copy at `C:\Users\dell\.codex\backups\kfata-web\20261103T225122Z`. Matching SHA256: database `c995806f57331c57714deba12a0330933875462f8f49d13bb1a0c2b9f828b7fc`; files `705285849d7889e51dff58c2446f5ff9c9e6ab63c6793a6891a0b5149d8773ea`. No scheduled off-server transfer or new restore claim.
