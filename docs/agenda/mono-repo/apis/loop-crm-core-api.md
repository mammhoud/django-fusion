---
Object type: API
Tags: api, rest-api, loop-crm, core
Status: Active
Related Features: crm-core-features
Related Integrations: social-publishing
Related Products: loop-crm
---

# Loop-CRM Core API — `/apis/core/`

> **Description:** The canonical named API roads replacing the deprecated `/api/v1/` prefix — workspace identity, dashboard KPIs, reports, AI, employees, search, badges, locale, board, and deal stage moves.

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `workspace/current/` | GET | Tenant discovery for the WebSocket island |
| `dashboard/` | GET | RevOps KPIs (revenue trend, POS vs deal) |
| `reports/` | GET | Report catalog |
| `ai/` · `ai/consent/` · `ai/<op>/` | GET/POST | AI catalog, consent gate, operations |
| `employees/` · `employees/<pk>/report/` | GET | HR surface |
| `search/` | GET | Global search |
| `badges/` | GET | Sidebar badge counters |
| `locale/` | GET | i18n |
| `board/` | GET | Pipeline kanban payload |
| `deals/<pk>/stage/` | POST | Move deal between stages |

## Contract notes

- Tenant derived server-side from the authenticated user — never from client headers
- Auth: session cookie or `Authorization: Bearer`
- Legacy `/api/v1/` copies carry `Deprecation`/`Sunset` headers via `APIV1DeprecationMiddleware`

## Related

- → `loop-crm-pos-api.md` — POS road
- → `../../diagrams/api-request-flows.md` — Sequence diagrams for these endpoints
- → `../objects/api.md` — API object type