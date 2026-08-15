# POS × django-fusion — Enhancements Plan
> **Tags:** #pos #django-fusion #enhancement

> **Version:** 1.1.0  
> **Last Updated:** 2026-07-24 (audit revision)  
> **Scope:** POS Mini / Solo / Full / Cloud + django-fusion package  
> **Goal:** Increase django-fusion impact across POS apps, harden sync logic, and make both the package and the projects that use it more minimal. API transport remains project-owned; cloud transport is governed by [`cloud-plan.md`](cloud-plan.md).

---

## 1. Executive Summary

Today, django-fusion is used in the POS ecosystem in two narrow ways:

1. **Sidecars** (`pos-solo`, `pos-full`) use `DataToken` / `BaseDeviceToken` only for sync-tagging and device auth.
2. **POS Cloud** uses `django-fusion.routes.ModelViewset`, `SearchableViewMixin`, and `FragmentComponent` for CRM/reports.

> **Related:** The [django-fusion Tasks & MCP plan](django-fusion-tasks-mcp-plan.md) (2026-08-10)
> governs background task infrastructure, Celery removal, and MCP tooling — including
> the task primitives that sync engines and scheduled work will use.

This plan lays out how to:

- Turn django-fusion into the **primary data & UI layer** for the sidecars, not just a sync-token helper.
- Replace hand-written CRUD/scheduler code with reusable django-fusion components.
- Build POS Full pages and POS Cloud dashboards out of django-fusion fragments and routable components.
- Upstream the POS sync engine’s best ideas into django-fusion as a generic, minimal sync framework.
- Slim down django-fusion so POS-style deployments can depend on only the pieces they need.

---

## 2. Current State Assessment

### 2.1 POS Editions *(audited 2026-07-24)*

| Edition | Server | Django-Fusion Usage Today | Gaps / Opportunities |
|---------|--------|---------------------------|------------------------|
| **pos-mini** | Rust/Tauri, Diesel, no sidecar | None | Out of scope. |
| **pos-solo** | Robyn + Django ORM, port `8765` | `DataToken` tagging; `BaseDeviceToken`; **8 `FragmentComponent` classes**; Fusion health endpoint; `routes/fusion_fragments.py` | Hand-written CRUD in `routes/state.py`; no `ModelViewset` or `RobynAdapter`. |
| **pos-full** | Robyn + Django ORM + Django Unfold, port `8766` | `DataToken` tagging; `BaseDeviceToken`; **8 `FragmentComponent` classes**; Fusion health endpoint; `routes/fusion_fragments.py` | Hand-written CRUD in `routes/state.py`; no `ModelViewset` or `RobynAdapter`. |
| **pos-cloud** | Django + django-fusion, port `8082` | `ModelViewset`, `FragmentComponent`, `SearchableViewMixin` for CRM/reports/sync viewsets | API transport remains project-owned; sync receive endpoints are plain Django views. |

### 2.2 django-fusion Usage Matrix *(audited 2026-07-24)*

| Feature | Used in POS Cloud | Used in Sidecars | Notes |
|---------|-------------------|------------------|-------|
| `ModelViewset` / `ReadonlyModelViewset` | ✅ Yes | ❌ No | Sidecars use hand-written `_register_crud`. |
| `FragmentComponent` / `RoutableComponent` | ✅ Yes | 🟡 **Partial** (8 fragments) | Sidecars have 8 `FragmentComponent` subclasses (Dashboard, Suppliers, About, Customers, Inventory, Employees, ProductList, ProductDetail). Not yet routable via django-fusion URL system — served through custom `routes/fusion_fragments.py`. |
| `DataToken` / `BaseDeviceToken` | ⚠️ Partial (models exist) | ✅ Yes | Sidecars tag every CRUD change. |
| Fusion health endpoint (`/fusion/health`) | ❌ No | ✅ Yes | Both sidecars expose `GET /fusion/health` returning `{fusion_render_first, health}`. |
| Fusion frontend bridge (`FusionPage`, `FusionProxy`, `FusionMiddleware`) | ❌ No | ✅ Yes (React side) | pos-full: 13/24 pages wired; pos-solo: 11/24 pages wired. Full fusion lib stack: `fusion-types.ts`, `fusion-decoder.ts`, `fusion-store.ts`. |
| `SearchableViewMixin` | ✅ Yes | ❌ No | Could replace search helpers. |
| `Application` / `Site` routing | ️ Partial | ❌ No | Sidecars mount routes manually via Robyn decorators. |

### 2.3 Sync Logic Today

The sync flow lives in:

- `projects/pos/pos-full/sidecar/services/scheduler.py` — scheduled sync loop, DataToken fast path, fallback table scan, cleanup.
- `projects/pos/pos-full/sidecar/services/sync.py` — `ProductSyncEngine` for master ↔ child pushes, sales/reports/inventory receipts, approvals.
- `projects/pos/pos-full/sidecar/handlers.py` — CRUD factory that auto-tags rows with `DataToken`.

Strengths:

- `DataToken.objects.sync_batch(node_id, limit=100)` gives an indexed fast path.
- `tag_row()` on create/update/delete creates an auditable sync trail.
- Cleanup prunes synced tokens and old logs.

Weaknesses:

- Sync engine is private POS code; other django-fusion projects cannot reuse it.
- Conflict resolution, retry/backoff, and idempotency are hand-rolled and sparse.
- Sidecars still carry a lot of boilerplate CRUD that `ModelViewset` already solves.

---

## 3. Objectives

1. **Amplify django-fusion in sidecars:** Replace the hand-written CRUD factory and route wiring with django-fusion viewsets / components.
2. **Make POS Full pages fragment-ready:** Convert admin dashboard widgets and report cards into `FragmentComponent`s that can be rendered from the sidecar or from POS Cloud.
3. **Unify POS Cloud sync:** Rewrite the receive endpoints in `core/sync_api.py` as django-fusion viewsets backed by `DataToken`-style sync tracking. Keep any cloud transport adapter within POS Cloud, never in local Formint or django-fusion.
4. **Upstream sync logic into django-fusion:** Extract a generic sync engine, conflict resolver, and scheduler utilities that any django-fusion project can use.
5. **Slim django-fusion for embedded deployments:** Allow POS-style sidecars to install only the core, sync, and Robyn integration packages without Wagtail/Unfold/DRF bloat.
6. **Improve correctness & observability:** Add sync metrics, idempotency keys, and deterministic ordering to the sync pipeline.

---

## 4. Phase 1 — Sidecar Data Layer with django-fusion

### 4.1 Replace `_register_crud` with `ModelViewset`

Current code (`projects/pos/pos-full/sidecar/server.py`):

```python
from routes.state import _register_crud

_register_crud(app, "products", Product, "Product", **_tag_sync)
_register_crud(app, "categories", Category, "Category", **_tag_sync)
# ... repeated for ~30 entities
```

Proposed change:

```python
from django_fusion.routes import ModelViewset, Application
from django_fusion.comp.robyn import register_viewset, RobynAdapter

class ProductViewSet(ModelViewset):
    model = Product
    url_prefix = "products"
    sync_tag = True          # new django-fusion flag
    sync_node_id = _DATA_TOKEN_NODE_ID
    sync_prefix = "pos_full"

pos_api = Application(prefix="", name="pos")
# auto-register all managed models
for viewset_cls in auto_discover_viewsets(__package__):
    pos_api.register(viewset_cls)

app = RobynAdapter.mount(app, pos_api)
```

Impact:

- Removes ~200 lines of `_register_crud` boilerplate.
- Standardizes list/create/get/update/delete on django-fusion’s battle-tested mixins.
- Keeps `DataToken` auto-tagging via a new `SyncTagMixin` / `sync_tag` class attribute.

### 4.2 Robyn Integration Helpers in django-fusion

Add a new sub-package: `django_fusion.comp.robyn`.

Responsibilities:

- `RobynAdapter`: maps django-fusion `Viewset` routes onto a Robyn app.
- `RobynRequest`: wraps Robyn’s `Request` to look like Django’s `HttpRequest` for django-fusion views.
- `run_django_setup(settings_module)`: idempotent Django bootstrap for sidecars.

This is the bridge that lets POS sidecars run django-fusion without a full Django server.

### 4.3 Sync-Tag Mixin for Viewsets

Introduce `django_fusion.sync.SyncTagMixin`:

```python
class ProductViewSet(SyncTagMixin, ModelViewset):
    model = Product
    sync_tag = True
    sync_node_id = "pos-full-auto"
    sync_prefix = "pos_full"
```

The mixin hooks `post_save`/`post_delete` and calls `DataToken.objects.tag_row(...)` with the viewset’s configured node and prefix. This removes the inline `tag_row()` calls in `handlers.py`.

---

## 5. Phase 2 — POS Full Pages as django-fusion Components

> **Partial progress (unplanned Phase 0):** 8 `FragmentComponent` subclasses already exist
> in both sidecar `fragments/` packages (Dashboard, Suppliers, About, Customers, Inventory,
> Employees, ProductList, ProductDetail), and 13/24 pos-full + 11/24 pos-solo React pages
> are wired with `FusionPage`. See Section 10 roadmap for status of items 0.1–0.5.
>
> The remaining Phase 2 work (Unfold dashboard splitting, routable report components) is
> not yet started.

### 5.1 Admin Dashboard as Fragments

The Unfold dashboard (`configs/dashboard.py`) currently renders KPIs server-side in one big template. Split it into django-fusion fragments:

| Fragment | Responsibility | Route |
|------------|---------------|-------|
| `dashboard.kpi_sales_today` | Today’s sales KPI | `/fragments/dashboard/kpi-sales-today/` |
| `dashboard.kpi_customers` | Active customers KPI | `/fragments/dashboard/kpi-customers/` |
| `dashboard.chart_revenue_7d` | Revenue chart | `/fragments/dashboard/chart-revenue-7d/` |
| `dashboard.recent_sales` | Recent sales table | `/fragments/dashboard/recent-sales/` |
| `dashboard.node_status` | Node status table | `/fragments/dashboard/node-status/` |

Each fragment is a `FragmentComponent` that:

- Exposes a URL.
- Can be requested via HTMX for the Unfold admin.
- Can be embedded in POS Cloud or a future web POS client.

### 5.2 Reports as Routable Components

Convert static report endpoints to `RoutableComponent` classes:

```python
from django_fusion.routes import RoutableComponent

class InventoryReportComponent(RoutableComponent):
    route_name = "inventory-report"
    route_path = "reports/inventory/"
    title = "Inventory Report"
    fragment_name = "pos.inventory_report"
    template_name = "pos/reports/inventory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ingredients"] = Ingredient.objects.filter(is_active=True)
        return context
```

These components can serve:

- Full-page reports in the Unfold admin.
- HTMX fragments for the React frontend.
- SSE updates for real-time report refreshes.

### 5.3 React Integration Strategy

The React app currently talks directly to `/products`, `/sales`, etc. Add a thin fusion bridge:

- `/fragments/*` endpoints return pre-rendered HTML for heavy report widgets.
- React uses the existing JSON CRUD for data entry.
- Use `fusion_render_first` flag from `RoutableComponent.get_context_data()` to decide whether a widget should be server-rendered or React-rendered.

---

## 6. Phase 3 — POS Cloud Unification

### 6.1 Move Sync Receivers to Viewsets

Current (`projects/pos/pos-cloud/core/sync_api.py`):

```python
@csrf_exempt
@require_POST
def sync_receive_products(request):
    ...
```

Proposed:

```python
from django_fusion.routes import ModelViewset

class BranchSyncReceiverViewSet(ModelViewset):
    model = BranchSyncLog
    url_prefix = "sync/receive"
    url_namespace = "sync_receive"

    @viewprop
    def products(self, request, **kwargs):
        ...

    @viewprop
    def sales(self, request, **kwargs):
        ...
```

Benefits:

- Consistent JSON schema with other POS Cloud endpoints.
- Automatic pagination, search, and filtering for sync logs.
- Easier to add new entity types via subclassing.

### 6.2 Use `DataToken` for Branch Sync

Replace the ad-hoc `BranchSyncLog` status tracking with `DataToken`:

- Each received batch gets a `DataToken` tagged to `BranchProduct`, `BranchSale`, or `BranchInventory`.
- POS Cloud can use `DataToken.objects.sync_batch(node_id=branch.node_id, ...)` to push pending changes back to branches.
- Cleanup is handled by the same retention policy as the sidecars.

### 6.3 Fragment Dashboard for POS Cloud

POS Cloud already has `FragmentComponent` layouts. Add:

- `SyncStatusFragment` — live sync status for every branch.
- `BranchHealthFragment` — heartbeat / last-seen widget.
- `PendingApprovalsFragment` — cross-branch approval queue.

---

## 7. Phase 4 — Upstream Sync Improvements into django-fusion

### 7.1 Generic `SyncEngine`

Extract POS `ProductSyncEngine` into `django_fusion.sync.engine.SyncEngine`:

```python
from django_fusion.sync import SyncEngine

engine = SyncEngine(
    node_model=Node,
    token_model=DataToken,
    serializer=JSONSerializer,
    transport=HTTPSTransport,
)

await engine.push(node_id, queryset)
await engine.pull(node_id, since=datetime(...))
```

Responsibilities:

- Batch selection via `DataToken.sync_batch()`.
- Serialization / deserialization.
- Conflict detection.
- Calling registered `SyncAdapter`s per content type.

### 7.2 Conflict Resolution

Add a pluggable conflict resolver:

```python
from django_fusion.sync import LastWriteWinsResolver, TimestampVectorResolver

engine = SyncEngine(resolver=LastWriteWinsResolver())
```

Strategies:

- `LastWriteWinsResolver`
- `TimestampVectorResolver`
- `CustomResolver` (user-defined)

### 7.3 Retry, Backoff & Idempotency

Add transport-level reliability:

- Exponential backoff with jitter.
- Idempotency key header (`X-Sync-Idempotency-Key`).
- Dead-letter queue for unresolvable conflicts.

### 7.4 Sync Metrics & Cleanup

New model: `django_fusion.sync.SyncRun`.

Fields:

- `node_id`
- `started_at` / `finished_at`
- `pushed` / `pulled` / `failed`
- `conflicts`

Cleanup tasks move from POS scheduler into django-fusion:

```python
from django_fusion.sync.tasks import cleanup_sync_tokens, cleanup_sync_logs

cleanup_sync_tokens(retention_days=7)
cleanup_sync_logs(retention_days=30)
```

---

## 8. Phase 5 — Make django-fusion More Minimal

### 8.1 Optional App Split

Split django-fusion into optional sub-apps so POS sidecars can install only what they need:

| App | Purpose | POS Sidecar Needs |
|---------|---------|-------------------|
| `django_fusion.core` | Base models, DataToken, managers | ✅ Yes |
| `django_fusion.routes` | Viewsets, components, routing | ✅ Yes (after Phase 1) |
| `django_fusion.fragments` | HTMX/Unpoly fragment rendering | ✅ Yes (Phase 2) |
| `django_fusion.sync` | Generic sync engine | ✅ Yes (Phase 4) |
| `django_fusion.admin` | Unfold integration helpers | ️ Only pos-full admin |
| `django_fusion.wagtail` | Wagtail page mixins | ❌ Not needed for POS |

### 8.2 Remove Hard Wagtail Dependency

Currently, POS Cloud includes `wagtail` only because django-fusion core models import it. Options:

1. Move Wagtail-dependent mixins to `django_fusion.contrib.wagtail`.
2. Make Wagtail imports lazy inside the mixin.
3. Document that Wagtail is required only for CMS-style projects.

### 8.3 Robyn-First Packaging

Add an `extras_require`:

```toml
[project.optional-dependencies]
robyn = ["robyn>=0.29", "asgiref>=3.7"]
sync = ["django-fusion[robyn]"]
admin = ["django-unfold", "django-filter"]
```

POS sidecars can then install:

```bash
pip install "django-fusion[robyn,sync]"
```

without pulling Unfold, DRF, or Wagtail.

---

## 9. Cross-Cutting Concerns

### 9.1 Auth & RBAC

- Reuse `BaseDeviceToken` for device identity across all editions.
- Add `permission_classes` to sidecar viewsets so POS roles (viewer/cashier/manager/admin) map to django-fusion permissions.

### 9.2 Observability

- Emit sync metrics from `SyncEngine`.
- Add Prometheus-compatible endpoints in sidecars.
- Use django-fusion’s fragment middleware to log fragment render times.

### 9.3 Testing

- Add django-fusion test helpers for Robyn adapters.
- Port sidecar tests from hand-written CRUD to viewset tests.
- Add sync engine tests: conflict resolution, retry, idempotency, cleanup.

### 9.4 Documentation

- Document `django_fusion.comp.robyn` setup.
- Add migration guide from `_register_crud` to `ModelViewset`.
- Provide sample POS fragment templates.

---

## 10. Roadmap *(audited 2026-07-24)*

> **Note:** Items 0.1–0.5 were **not in the original v1.0.0 plan**. They were implemented as
> necessary prerequisites for fragment-rendering support and are now tracked here for completeness.

**Legend:** ✅ Complete &nbsp; 🟡 In Progress &nbsp; ⬜ Not Started &nbsp; 🔴 Blocked

| Phase | Deliverable | Status | Effort | Depends On |
|-------|-------------|--------|--------|------------|
| **0.1** | Sidecar `FragmentComponent` classes (8 per edition) | ✅ Done | — | — |
| **0.2** | Fusion health endpoint (`/fusion/health`) on sidecars | ✅ Done | — | — |
| **0.3** | React fusion bridge (`FusionPage`, `FusionProxy`, `FusionMiddleware`) | ✅ Done | — | — |
| **0.4** | E2E fusion tests (decoder, store, proxy, page, middleware) | ✅ Done | — | — |
| **0.5** | Wire `FusionPage` into POS pages | 🟡 13/24 pos-full, 11/24 pos-solo | Low | — |
| **1.1** | `django_fusion.comp.robyn` adapter + `RobynRequest` | ⬜ | Medium | django-fusion routing internals |
| **1.2** | Port sidecar CRUD to `ModelViewset` + `SyncTagMixin` | ⬜ | High | 1.1 |
| **2.1** | Split Unfold dashboard into fragments | ⬜ | Medium | django-fusion fragment templates |
| **2.2** | Add routable report components to POS Full | ⬜ | Medium | 2.1 |
| **3.1** | Rewrite POS Cloud sync receivers as viewsets | ⬜ | Low | — |
| **3.2** | Use `DataToken` for branch sync in POS Cloud | ⬜ | Medium | 3.1 |
| **4.1** | Extract generic `SyncEngine` into django-fusion | ⬜ | High | POS sync logic audit |
| **4.2** | Add conflict resolvers + retry/idempotency | ⬜ | High | 4.1 |
| **5.1** | Split django-fusion into optional sub-apps | ⬜ | High | Package refactor |
| **5.2** | Make Wagtail/Unfold optional | ⬜ | Medium | 5.1 |
| **6.0** | Update docs, tests, migration guides | 🟡 This audit | Medium | All above |

---

## 11. Risks & Recommendations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking existing sidecar routes** | High | Keep `_register_crud` as a deprecated shim; run full sidecar test suites before removing. |
| **Wagtail dependency removal breaks other projects** | Medium | Move Wagtail code to `django_fusion.contrib.wagtail`; keep import shims for one major release. |
| **Robyn adapter maintenance overhead** | Medium | Keep adapter minimal; delegate request/response wrapping to django-fusion’s existing view layer. |
| **Sync engine generalization loses POS-specific semantics** | Medium | Design `SyncAdapter` interface so POS keeps product/sale-specific rules in small adapter classes. |
| **Performance regression in sidecars** | Medium | Benchmark JSON throughput before/after; Robyn adapter should not add significant overhead. |

---

## 12. Immediate Next Steps *(revised after 2026-07-24 audit)*

### ✅ Completed (Unplanned Work)

These items were completed ahead of the original Phase 1–5 plan:

1. **8 `FragmentComponent` classes** in both sidecars (`fragments/` package): Dashboard, Suppliers, About, Customers, Inventory, Employees, ProductList, ProductDetail.
2. **Fusion health endpoint** (`GET /fusion/health`) on both sidecars, registered via `middleware/fusion.py` → `register_fusion_health_routes()`.
3. **React fusion bridge** in both frontends: `FusionMiddleware` (mode context), `FusionPage` (data/fragment switch), `FusionProxy` (HTML fetch & render).
4. **Fusion utility libraries**: `fusion-types.ts`, `fusion-decoder.ts`, `fusion-store.ts`.
5. **E2E fusion tests**: `fusion-e2e.test.tsx`, `FusionDecoder.test.ts`, `FusionMiddleware.test.tsx`, `FusionPage.test.tsx`, `FusionProxy.test.tsx`, `fusion-store.test.ts`.
6. **FusionPage wiring**: 13/24 pos-full pages, 11/24 pos-solo pages.
7. **Sidecar fusion tests**: `test_fragments.py`, `test_fusion.py`, `test_fusion_integration.py`.

### ⚠️ Known Issues

- **Backend tests broken**: `test_webhook_e2e.py` has collection errors (3 errors in pos-full, 3 in pos-solo). Test suites collect 75/74 tests but fail on import (`RuntimeError: Model...`, `AssertionError`).
- **10–12 pages not yet wired** with FusionPage (Analytics, Auth, InvoicePage, ProductManager, Recipes, Reports, Sale, Settings, SupportChat, Transactions; plus Employees and Inventory in pos-solo).

### 🎯 Recommended Next Steps

1. **Fix backend test collection errors** (`test_webhook_e2e.py`) so all 75+ tests pass in both editions.  
2. **Wire remaining 10–12 pages** with `FusionPage` for complete fragment coverage.  
3. **Create the `django_fusion.comp.robyn` adapter skeleton** so sidecars can mount viewsets without a full Django server (original Phase 1.1).  
4. **Pick one sidecar entity (e.g., `Product`) and migrate it to `ModelViewset`** as a proof-of-concept (original Phase 1.2).

---

## 13. Files Referenced *(updated audit)*

### Sidecar (Backend)
- `projects/pos/pos-full/sidecar/server.py`
- `projects/pos/pos-full/sidecar/handlers.py`
- `projects/pos/pos-full/sidecar/services/scheduler.py`
- `projects/pos/pos-full/sidecar/services/sync.py`
- `projects/pos/pos-full/sidecar/middleware/fusion.py` — `RobynFusionChecker`, `register_fusion_health_routes`
- `projects/pos/pos-full/sidecar/fragments/__init__.py` — `FragmentComponent` registry
- `projects/pos/pos-full/sidecar/fragments/dashboard.py`
- `projects/pos/pos-full/sidecar/fragments/products.py`
- `projects/pos/pos-full/sidecar/fragments/customers.py`
- `projects/pos/pos-full/sidecar/fragments/inventory.py`
- `projects/pos/pos-full/sidecar/fragments/employees.py`
- `projects/pos/pos-full/sidecar/fragments/suppliers.py`
- `projects/pos/pos-full/sidecar/fragments/about.py`
- `projects/pos/pos-full/sidecar/routes/fusion_fragments.py`
- `projects/pos/pos-solo/sidecar/` (mirrors above)

### POS Cloud
- `projects/pos/pos-cloud/core/views.py`
- `projects/pos/pos-cloud/core/sync_api.py`
- `projects/pos/pos-cloud/configs/__init__.py`
- `projects/pos/pos-cloud/core/fragments/layouts.py`
- `projects/pos/pos-cloud/core/fragments/reports.py`
- `projects/pos/pos-cloud/core/fragments/tables.py`

### Frontend (React/Tauri)
- `projects/pos/pos-full/src/components/FusionMiddleware.tsx`
- `projects/pos/pos-full/src/components/FusionPage.tsx`
- `projects/pos/pos-full/src/components/FusionProxy.tsx`
- `projects/pos/pos-full/src/lib/fusion-types.ts`
- `projects/pos/pos-full/src/lib/fusion-decoder.ts`
- `projects/pos/pos-full/src/lib/fusion-store.ts`
- `projects/pos/pos-full/src/test/fusion-e2e.test.tsx`
- `projects/pos/pos-full/src/test/FusionDecoder.test.ts`
- `projects/pos/pos-full/src/pages/` — 24 pages, 13 wired with `FusionPage`
- `projects/pos/pos-solo/src/` (mirrors above, 11/24 wired)

### django-fusion
- `libs/django-fusion/src/django_fusion/models/datatoken.py`
- `libs/django-fusion/src/django_fusion/routes/components.py`
- `libs/django-fusion/src/django_fusion/routes/fragments.py`
- `libs/django-fusion/src/django_fusion/core/managers.py`
- `libs/django-fusion/src/django_fusion/core/cache.py`

---

## 16. Related Plans

| Plan | Path |
|---|---|
| django-fusion Tasks & MCP | [`django-fusion-tasks-mcp-plan.md`](django-fusion-tasks-mcp-plan.md) |
| Worker Consolidation | [`../repository/worker-consolidation.md`](../repository/worker-consolidation.md) |
| Formint POS Professional | [`../editions/03-pro.md`](../editions/03-pro.md) |
| Formint Cloud | [`../editions/04-cloud.md`](../editions/04-cloud.md) |
| Tauri Plugin Migration | [`../editions/02-standard.md`](../editions/02-standard.md) |
| Codebase Audit & Migration | [`../CODEBASE_AUDIT_AND_MIGRATION_PLAN.md`](../CODEBASE_AUDIT_AND_MIGRATION_PLAN.md) |
| Canonical Plan Registry | [`../README.md`](../README.md) |

---

*This plan is intended as a living document. Prioritize phases based on the most pressing business need: sidecar simplification, POS Full page modernization, POS Cloud sync unification, or django-fusion package minimalization.*
