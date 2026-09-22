---
Object type: Architecture
Tags: architecture, sync, pos, offline, cloud
Status: Published
Related Products: formint-pos
Related Editions: Community, Formint Professional, POS Cloud
Related Plans: cloud
---

# Sync Data — Local, Branch, and Cloud Synchronization

> **Description:** Synchronization boundaries that preserve local service continuity while enabling branch coordination and hosted cloud operations.

## Current model

| Boundary | Product scope | Responsibility |
|---|---|---|
| Local store | Community and Formint Professional | Keep core catalog, orders, and operational work available locally where supported |
| Branch coordination | Formint Professional as released | Coordinate approved branch or device workflows without making the cloud a requirement for every sale |
| Cloud control plane | POS Cloud | Hosted tenants, branch aggregation, analytics, backups, billing, and managed integrations |

## Design principles

- Local service continuity is separated from cloud analytics and management.
- Synchronization is explicit, observable, retryable, and auditable.
- Conflicts require a documented policy and operator visibility.
- Cloud-only capabilities do not silently become local dependencies.

## Related

- → `editions.md` — Current edition boundaries
- → `../plans/cloud.md` — Cloud-only operating model
- → `../features/integrations.md` — Integration feature
- → `../README.md` — Anytype hub
