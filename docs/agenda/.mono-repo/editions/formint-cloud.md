---
Object type: Edition
Tags: edition, formint, cloud, pos, saas, multitenant
Status: In Development
Related Features: pos-cloud-integrations, pos-documentation
Related Plans: cloud
---

# Formint Cloud — Hosted Multi-Tenant SaaS Master

> **Description:** The cloud-hosted SaaS control plane (`projects/formints/formint-cloud/`) — schema-per-tenant master serving the API from Django (the Robyn sidecar is retired).

## Scope

- Hosted multi-tenant SaaS master (apps/core + apps/domain + apps/handlers, Channels ASGI)
- Automatic backups (`BackupRun` model + `backup_db` management command)
- Monitoring (`/monitor/status` endpoint)
- Cross-branch transport and analytics, billing, managed integrations
- Tenant schemas (Postgres flip-on pending)

## Boundaries

- Cloud is the schema-per-tenant master; Community/Standard/Pro are offline-capable editions
- Cloud API serves from Django on the canonical formint-cloud path

## Evidence

- 🟡 Staging (per `docs/plans/editions/` chain status)
- Tenant schemas: 🟡 Postgres flip-on pending
- Plan: `../../../plans/editions/04-cloud.md`

## Related

- → `formint-pro.md` — Base tier
- → `../plans/cloud.md` — Cloud operating model
- → `../objects/edition.md` — Edition object type