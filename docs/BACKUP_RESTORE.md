# Backup and restore

`bash deploy/backup.sh` creates a PostgreSQL custom-format dump, media/private-media tarball and commit identifier with restrictive file permissions. It does not capture `.env`; keep secrets in a separate secure recovery system.

The dump and files contain customer data. Backups must be access-controlled and copied off-server to a selected secure destination. No off-server destination, schedule or retention cleanup is configured yet.

For a consistent snapshot, prevent changes/uploads to this application while taking the database and file snapshots. Do not interrupt Mailcow or ERPNext.

## Isolated restore drill (required before claiming operational readiness)

1. Create a separate Compose project name, database credentials, unused loopback port and volumes; do not reuse production volumes.
2. Start its db and restore with pg_restore using the target db/user environment.
3. Extract the file archive only after listing and validating its paths, then restore ownership for UID/GID 10001.
4. Start the exact saved application commit with indexing disabled and outbound SMTP disabled.
5. Check page content, images, private attachments and enquiry counts.
6. Record results. Delete only the explicitly identified drill resources afterward.

No restore drill has been executed in the initial environment because Docker is unavailable.
