# ☁️ Formint Cloud — Data Sync & Hosted Master

> **Superseded.** This page previously described the retired `pos-solo`
> terminal / `shared-portal` cloud server with a Robyn sidecar. The current
> cloud master is **formint-cloud**, a Django multi-tenant service (see the
> edition chain), and its API is served from Django — no Robyn sidecar.

## Canonical sources

| Topic | Canonical doc |
|-------|---------------|
| Cloud edition plan (Organization → Branch, sync pipeline) | [`docs/plans/editions/04-cloud.md`](../plans/editions/04-cloud.md) |
| Tenant schemas + `BranchSettings` | [`docs/plans/editions/08-tenant-schemas.md`](../plans/editions/08-tenant-schemas.md) |
| Sync contract (REST + WebSocket + SDK) | [`docs/plans/editions/README.md`](../plans/editions/README.md) (E2E & sync matrix) |
| Cloud product docs | [`projects/formints/docs/`](../../projects/formints/docs/) · [`projects/formints/formint-cloud/`](../../projects/formints/formint-cloud/) |

> The reader-facing docs site keeps this slim pointer so the `/docs/en/pos/cloud-edition`
> route stays alive with current information instead of the retired architecture.
