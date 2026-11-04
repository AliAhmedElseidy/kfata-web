# KFATA implementation instructions

Continue this project through production deployment when the environment can reach the VPS.
The user authorized a separate Docker project on a server already running Mailcow and ERPNext.
Target domain: kfata.elsaidy.org. Do not embed SSH passwords or other secrets in this repository.

Before any server mutation, run a read-only inventory using deploy/audit.sh and inspect the actual ingress.
Never stop the existing stacks, publish PostgreSQL, reserve occupied 80/443 ports, prune Docker globally,
change mail DNS records, remove volumes, or overwrite proxy configuration blindly.

Read docs/VALIDATION.md and docs/CONTENT_REVIEW.md before claiming completion.
Review the full original implementation brief in the conversation when available.
The site is now deployed; read docs/HANDOVER.md and the host's operations/deployed-commit for current state.

Preserve editor changes: seed_content is initial import only, not a content reset.
Use a branch and PR. Run checks and meaningful tests after changes.
Respect reduced motion, private enquiry attachments, unpublished pages, translation links and form CSRF.
Do not invent company facts, testimonials, clients, certificates or performance measurements.
Document blockers accurately. Repository visibility is public: only reviewed public material belongs here.
