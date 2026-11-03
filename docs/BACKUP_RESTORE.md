# Backup and restore

`bash deploy/backup.sh` creates a PostgreSQL custom-format dump, media/private-media tarball and commit identifier with restrictive file permissions. It does not capture `.env`; keep secrets in a separate secure recovery system.

The dump and files contain customer data. Backups must be access-controlled and copied off-server to a selected secure destination. A daily 03:15 Asia/Riyadh systemd timer and 14-day completed-snapshot retention are configured. A manual access-controlled off-server copy was made on the owner PC; recurring off-server transport is not configured. See HANDOVER.md.

The script freezes writers by stopping only KFATA web briefly and restarts it with an EXIT trap. It records the deployed commit and image ID, and creates portable SHA-256 checksums. Do not interrupt Mailcow or ERPNext.

## Isolated restore drill (required before claiming operational readiness)

1. Create a separate Compose project name, database credentials, unused loopback port and volumes; do not reuse production volumes.
2. Start its db and restore with pg_restore using the target db/user environment.
3. Extract the file archive only after listing and validating its paths, then restore ownership for UID/GID 10001.
4. Start the exact saved application commit with indexing disabled and outbound SMTP disabled.
5. Check page content, images, private attachments and enquiry counts.
6. Record results. Delete only the explicitly identified drill resources afterward.

A full isolated drill was executed on the VPS on 2026-11-03 with deploy/restore-drill.sh. Database restore, page counts, HTTP routes and tar content comparison passed. See HANDOVER.md for the exact snapshot and retained drill volumes.
