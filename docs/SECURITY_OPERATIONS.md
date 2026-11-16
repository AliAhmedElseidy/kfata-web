# KFATA security operations follow-up

## SSH and Fail2ban

The `kfata-ops` account was tested over an independent, public-key-only SSH connection, including `sudo -n id -u`. Root key access was also checked. The owner's independent recovery access still needs verification before applying the root password restriction. Validate the intended setting with `sshd -t` and `sshd -T`, keep an authenticated session and provider console open, use `PermitRootLogin prohibit-password`, and reload SSH only after owner validation. Confirm both a fresh operator login with sudo and root key recovery before closing the original session.

The only enabled Fail2ban jail is `kfata-ssh`. It uses the SSH journal and an nftables action restricted to TCP destination port 22. The known working administration source and loopback are exempt. Applying and removing a reserved test address verified the rule and its scope. To roll back this jail, stop Fail2ban and confirm its SSH chain was removed. Host mail and web firewall rules were left in place.

## Off-host recovery

A dedicated SSH identity runs only the root-owned `export-latest-backup.sh` exporter. It sends the latest complete, checksum-verified archive over SSH. The account's only sudo permission is that exporter without arguments. The Windows scheduled job invokes `pull-encrypted-backup.ps1` at 08:00 device time under the existing interactive profile. It verifies each DPAPI-encrypted copy, stores only encrypted payloads on disk, and records a failure status and raises a local desktop notification when available. A scheduled run completed successfully and simulated transport failure recorded an error. The PC must be available with that profile signed in. Independent key escrow and external alert delivery require an owner-managed destination.

The encrypted Windows archive was decrypted in memory and streamed back for an isolated restore on PostgreSQL 16.16. Both language routes opened and all 72 stored image and document files matched their database references. The restored snapshot contained no enquiry attachments. The drill used separate volumes and disabled outbound mail. It was stopped after verification.

## PostgreSQL maintenance

Production remains on 16.15. `compose.postgres-16.16.yaml` pins the tested 16.16 image. `postgres-16.16-preflight.sql` is read-only and reports role privileges and affected index types. The current KFATA connection has superuser, role/database creation, replication and RLS bypass privileges. PostgreSQL has no published host port.

A minimal role was rehearsed inside a transaction on the restored database. Wagtail reads and an enquiry insert and update worked, and schema creation was rejected. For cutover, keep the existing database owner for operations and migrations, provision a separate runtime login with schema usage, CRUD and sequence access, and set default privileges for future objects created by the owner. Test the runtime login in a second web instance before replacing the database connection secret.

1. Agree on the window and keep the known working SSH and provider recovery paths available. Verify healthy KFATA, ERPNext and Mailcow. Check the pinned image, old image rollback tag, free disk space and backup age.
2. Pause KFATA writes only. Take a current database/media backup with its protected recovery configuration, confirm the manifest and encrypted off-host copy, and preserve the pre-upgrade data volume or a verified snapshot.
3. Stop only the KFATA database while writes are paused, start it with the pinned override, and verify the version and health. Inspect the three application GIN indexes and rebuild any affected by the PostgreSQL release notes before reopening writes. The preflight found no invalid indexes, BRIN indexes, unconstrained `bpchar` btree indexes or trigram GiST indexes in the public schema.
4. Verify both languages, application authentication and a reversible write check. Resume KFATA writes after validation. If validation fails, keep writes paused and use the old tagged image with the preserved pre-upgrade state. Restore to a separate volume if a data restore is needed.

[PostgreSQL 16.16 release and migration notes](https://www.postgresql.org/docs/16/release-16-16.html)
