# POS Docs — Legacy / Archived

> These documents describe **retired** architecture and code paths (the
> pre-merge `pos-mini` / `pos-solo` / `pos-full` editions and the Robyn/Sanic
> sidecar). They are kept for history only — **do not follow their paths or
> commands**. The canonical, current documentation lives in the docs root
> (`projects/formints/docs/`) and the edition plans
> ([`docs/plans/editions/`](../../../../docs/plans/editions/README.md)).

## What is archived here

| File | Was | Replaced by |
|------|-----|-------------|
| `POS_ARCHITECTURE.md` | Pre-merge master design doc (pos-solo/pos-full) | [`FORMINT_ARCHITECTURE.md`](../FORMINT_ARCHITECTURE.md) |
| `SERVER_V2.md` | Robyn + Django ORM server v2 (70+ APIs, WS streams) | [`architecture/editions.md`](../architecture/editions.md) + Pro/Cloud plans |
| `SYNC_ARCHITECTURE.md` | Robyn-era sync design (LAN solo → cloud full) | [`architecture/pro-cloud-sync-contract.md`](../architecture/pro-cloud-sync-contract.md) |
| `BOLT_INTEGRATION.md` | django-bolt API integration plan (complete/removed) | [`architecture/editions.md`](../architecture/editions.md) |
| `RUST_INTEGRATION.md` | Rust ↔ Robyn server linking (planning phase) | [`architecture/pos-architecture.md`](../architecture/pos-architecture.md) |
| `PINIA_INTEGRATION.md` | Pinia ↔ Robyn API guide (merged from `PINIA_API.md` + `PINIA_INTEGRATION.md`) | Vue 3 client: [`formint-client`](../../formint-client/README.md) |
| `page-data-map.md` | Historical pos-mini/solo/full page data map | [`architecture/editions.md`](../architecture/editions.md) |
| `audit.md` | 2026-07-23 architecture audit (pos-mini/solo/full) | [`architecture/editions.md`](../architecture/editions.md) |
| `_sidebar.md` / `index.html` | Old docsify shell for this folder | [`../README.md`](../README.md) |

## Notes

- Robyn was removed from the Pro and Cloud editions; Django (daphne ASGI +
  django-fusion) serves their API surfaces. Do not reintroduce Robyn paths
  from these docs.
- `pos-mini` / `pos-solo` / `pos-full` / `forge-pos` were merged or retired;
  the current editions are `formint-community/`, `formint-standard/`,
  `formint-pro/`, `formint-cloud/`, and `formint-client/`.
