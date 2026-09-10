---
Object type: Release
Tags: release, loop-crm, demo, preview
Status: Released
Related Features: crm-core-features
Related Milestones: demo-state-gap-fixing, formint-finance-integration
---

# Loop-CRM Demo Preview — crm.structa.cloud

> **Description:** Demo-ready preview of the Loop-CRM product: deterministic demo user, bare auth shell with demo panel, auto-seed on boot, all side-nav destinations resolve.

## What shipped

- `DEMO_MODE` setting + context processor, bare auth shell (no sidebar)
- Deterministic `seed_demo --superuser` (idempotent, password restored)
- Entrypoint auto-seed; `LOGIN_REDIRECT_URL=/overview/`
- Astro pages for all six previously-404 side-nav destinations
- Backend 255 tests + frontend 34 pages + node suite 50/50 green

## Pending

- Server-half end-to-end verification against the deployed stack (requires a real deploy)

## Related

- → `../../feature-tracking.md` § Loop-CRM — Demo state & auth gap fixing milestone
- → `../objects/release.md` — Release object type