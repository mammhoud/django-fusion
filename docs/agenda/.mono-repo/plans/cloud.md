---
Object type: Plan
Tags: pos-cloud, cloud, multi-tenant, sync, api, django-bolt, infrastructure
Status: Planned
Type: Architecture
Edition: POS Cloud
Related Plans: formint-pos-professional-plan
---

# POS Cloud

> **Description:** SaaS control plane for tenant, branch, sync, analytics, billing, backup, and managed integration services. Local Formint remains useful without this service.

## Cloud methods and use cases

| Method | Responsibility | Use case |
|---|---|---|
| Tenant and branch registry | Authenticate organizations, branches, devices, and scopes | A franchise owner sees only authorized branches |
| Sync broker | Accept versioned idempotent events, retry, reconcile, and expose conflicts | Offline branch sales arrive once after reconnection |
| Streaming events | Deliver approved configuration and status changes | A menu or approval reaches selected branches quickly |
| Central analytics | Aggregate sales, stock, waste, and preparation measures | Managers compare branch performance remotely |
| Backup and restore | Protect tenant data and verify recovery | A customer can recover after device or service failure |
| Billing and limits | Track subscription, branches, usage, and entitlement | SaaS plans remain commercially measurable |
| Webhooks and partner API | Expose scoped cloud events to external systems | Accounting, delivery, and reporting systems integrate safely |

## Cloud-only transport boundary

This is the only POS planning object that may define django-bolt. A cloud-side `BoltAPI` adapter may be evaluated for high-throughput sync, WebSocket streaming, authentication, and cloud OpenAPI exposure. It must not be added to Formint local dependencies, django-fusion, or the local Astro/HTMX path.

Keep standard Django handlers as the operational fallback for health, administration, migrations, and adapter failure. The portable contract is the versioned event envelope: stable ID, event version, idempotency key, request ID, tenant/branch scope, retry metadata, conflict record, and audit reference.

## Cloud boundary

- Local Formint owns checkout, local SQLite, printer state, offline drafts, and branch continuity.
- Cloud owns tenant identity, cross-branch coordination, hosted PostgreSQL, billing, backups, and central analytics.
- Cloud does not return local page shells, skeletons, or full UI components.
- Public cloud endpoints require scoped credentials, rate limits, audit logs, replay protection, and tenant isolation.

## Delivery gates

1. Define portable sync envelopes and ownership.
2. Register branches and devices with health/status visibility.
3. Implement queue, retry, conflict, and batch reconciliation.
4. Benchmark the cloud transport and complete security/operations review before selecting django-bolt.
5. Test restore, billing reconciliation, tenant isolation, and local operation when cloud is unavailable.

## Related

- → `formint-pos-professional-plan.md` — Local product boundary
- → `pos-market-research.md` — SaaS market research
- → `../../../plans/editions/04-cloud.md` — Detailed repository cloud plan
- → `../../../plans/editions/03-pro.md` — Local engineering contract
- → `../objects/api.md` — API object type
- → `../objects/integration.md` — Integration object type
