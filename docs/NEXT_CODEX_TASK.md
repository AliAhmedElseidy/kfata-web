# Continue in an SSH-enabled Codex environment

The user has authorized implementation and deployment to kfata.elsaidy.org on the existing VPS with Mailcow and ERPNext. SSH credentials must be provided through the execution environment's secure login mechanism, not this repository.

1. Review this branch, AGENTS.md, docs/VALIDATION.md and docs/CONTENT_REVIEW.md.
2. Connect to the authorized VPS, run deploy/audit.sh read-only and inspect the actual ingress without printing secrets.
3. Preserve existing ERPNext and Mailcow deployments. Use only the KFATA Compose project and its independent volumes/network.
4. Resolve the remaining scope in VALIDATION.md; do not substitute a static demo for the CMS.
5. Run tests and Docker/PostgreSQL/browser QA. Fix observed failures before deployment.
6. Configure the minimal domain-specific route and HTTPS using the existing ingress mechanism. Do not take over occupied ports 80/443.
7. Configure the account/contacts/SMTP and reviewed privacy notice, test backup and isolated restore, then verify the live site and existing-service baseline.
8. Push tested changes, open/update the PR, record the deployed commit, and report only verified outcomes.

No server changes have been made by the initial authoring session. Do not assume DNS, TLS or SMTP is already configured.
