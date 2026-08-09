# Pro Edition — Design, Architecture & Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the Pro edition (`formint/`) as the reference tier: document its design, architecture, and data model (the schema Standard extends into), fix the remaining stale documentation (Robyn references), and land a green verification gate.

**Architecture:** Pro shares the `formint/` codebase with the Standard tier (gated by configuration) — Astro + Alpine + HTMX frontend (32 pages), full Django sidecar (`formint/sidecar/`, 48 models, Django Ninja + django-bolt + Channels WebSockets + django-fusion + Unfold admin), Tauri 2 shell. It is the most complete edition; the work here is reference documentation + hardening, not new features.

**Tech Stack:** Python (Django 5.2, ninja-extra, django-bolt, django-fusion, django-unfold), Astro 5, Rust (Tauri 2), pytest, Vitest.

## Global Constraints

- All changes live under `projects/formints/formint/` only.
- **No schema changes** — Pro's data model is the reference; the 48-model `full_*` schema is already canonical.
- No new dependencies. No Robyn.
- Test commands: `cd projects/formints/formint/sidecar && make check && make test` · frontend `cd projects/formints/formint/frontend && pnpm check` (Astro check).
- Ports unchanged: backend 8767, bolt 8766, frontend 4321.
- **Feature inheritance (hard):** Pro MUST include every Standard feature (`02-standard.md`) — including the new `Currency`/`TaxProfile` models, export endpoints, and permission enforcement — plus its own CRM/fusion surface. The parity sweep in Task P4 verifies it.

---

## Design

**Audience:** multi-terminal operators and their cloud master. Pro is the flagship: everything Community and Standard offer, plus cloud CRM, fusion render-mode, Unfold admin, and Channels WebSocket streams.

**Positioning in the extension chain:** Pro and Standard share one codebase and one schema. Standard is the same stack gated down (no CRM/fusion surface); Pro is the full surface. There is **no data-model delta between Standard and Pro** — Pro's plan therefore documents the reference architecture and closes the last accuracy gaps in its documentation, then gates on a fully green test suite.

**Completion criteria:** `formint/README.md` describes the current (Django-only) architecture with zero Robyn references; `make check`, `make test`, and the Astro check all pass.

## Architecture

```
Astro + Alpine + HTMX (frontend/, 32 pages)
  ├── /api/v1        Django Ninja — 45 paginated resources (fusion envelope)
  ├── /htmx          django-fusion tables + forms fragments
  ├── /fusion        render-mode / navigation / assets contract
  ├── /admin         Unfold dashboard (10 KPI cards · 5 charts · 3 tables)
  ├── /bolt          django-bolt REST (manage.py runbolt, :8766)
  └── ws/{nodes,entities,config}   Channels WebSocket streams
Tauri 2 shell (src-tauri/) — Django is the data authority
```

## Data model (reference tier)

The canonical 48-model Django schema (`app_label="pos_full"`, `full_*` tables), organized by domain:

| Domain | Models |
|--------|--------|
| POS core | `Category`, `Product`, `Customer`, `Sale`, `SaleItem`, `InventoryTransaction`, `Employee`, `DeliveryType`, `DeliveryZone` |
| Menu & kitchen | `MenuItem`, `Menu`, `MenuItemAssignment`, `KitchenTicket`, `SupportTicket` |
| Inventory & ops | `Supplier`, `PurchaseOrder`, `PurchaseOrderItem`, `Ingredient`, `Recipe`, `InventoryAdjustment`, `Coupon` |
| HR | `Payroll`, `EmployeeSchedule`, `Role`, `TaxReport` |
| Loyalty & settings | `ClientCategory`, `LoyaltyTransaction`, `UserSettings`, `ReceiptTemplate` |
| Node & sync | `Node`, `Heartbeat`, `NodeEvent`, `DeviceConfig`, `MasterDevice`, `CloudLink`, `SyncLog`, `SyncApproval`, `DeviceToken` |
| CRM | `Company`, `Pipeline`, `Stage`, `Contact`, `Deal`, `Activity`, `CRMNote` |
| Platform | `ApiKey`, `SignalEvent`, `Note` |

**Extension note:** Standard (02-standard.md) adds `Currency` + `TaxProfile` to this schema; Pro consumes the same schema unchanged. Cloud (04-cloud.md) re-expresses the sync concepts as a multi-tenant `pos_cloud` schema.

---

## Task P1: Fix stale Robyn references in the Pro README

**Files:**
- Modify: `projects/formints/formint/README.md`

- [ ] **Step 1: Read the current README and locate stale lines**

Run: `grep -n "server.py\|Robyn" projects/formints/formint/README.md`
Expected: matches at (at least) lines ~13, ~28, ~174, e.g.:
- `- \`sidecar/\` — merged Django boundary (… + Robyn/django-bolt APIs)`
- `│   ├── server.py                # Robyn sidecar server (API + WebSocket, :8766)`
- `The sidecar/desktop layer consumes the same Robyn/Django APIs`

- [ ] **Step 2: Rewrite the stale lines**

Replace each occurrence to describe the actual Django-only architecture:

1. Line ~13: change `+ Robyn/django-bolt APIs)` → `+ django-bolt APIs)`.
2. The `server.py` tree line (~28): replace with `│   ├── asgi.py                # Django ASGI (HTTP + Channels WebSocket)`.
3. Line ~174: change `consumes the same Robyn/Django APIs` → `consumes the same Django APIs`.

- [ ] **Step 3: Verify no Robyn references remain**

Run: `grep -rn "Robyn\|server.py" projects/formints/formint/README.md`
Expected: no matches.

- [ ] **Step 4: Commit**

```bash
git add projects/formints/formint/README.md
git commit -m "docs(formint): remove stale Robyn references from the Pro README"
```

---

## Task P2: Pro verification gate

**Files:**
- No code changes unless a check fails.

- [ ] **Step 1: Run the Django checks + suite**

Run: `cd projects/formints/formint/sidecar && make check && make test`
Expected: `make check` passes (Django system checks); `make test` passes the sidecar pytest suite.

- [ ] **Step 2: Run the frontend check**

Run: `cd projects/formints/formint/frontend && pnpm check`
Expected: Astro/TypeScript check passes.

- [ ] **Step 3: Fix any failure found (only if a check fails)**

If a specific test fails, fix the smallest code change that makes it pass and add a regression test in `formint/sidecar/tests/` mirroring the failing test's module. Re-run `make test` until green.

- [ ] **Step 4: Commit**

```bash
git add projects/formints/formint/
git commit -m "test(formint): green verification gate for the Pro edition"
```

---

## Task P3: Pro reference doc parity

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md` (Pro section)
- Modify: `projects/formints/CHANGELOG.md`

- [ ] **Step 1: Confirm the Pro section is accurate**

In `projects/formints/docs/architecture/editions.md`, the Pro section must state: Astro + Alpine + HTMX frontend · Django Ninja backend (45 resources) · django-bolt · Channels WS · Unfold admin · Tauri v2 shell · 48 models · CRM + fusion render-mode. Fix any line that contradicts the code (e.g., port numbers, model counts).

- [ ] **Step 2: Add a CHANGELOG entry**

Under the `## Unreleased` section:

```markdown
### Changed (Pro — formint)
- README no longer references the removed Robyn server; architecture docs reflect the Django-only sidecar
- Verification gate green: django check + sidecar pytest + Astro check
```

- [ ] **Step 3: Commit**

```bash
git add projects/formints/docs/architecture/editions.md projects/formints/CHANGELOG.md
git commit -m "docs: Pro edition reference parity + changelog"
```

---

# Cross-cutting enhancements (Pro)

## Task P4: Standard-feature parity sweep

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md` (parity note) — only if a gap is found and fixed

**Interfaces:**
- Consumes: the Standard plan (`02-standard.md`) deliverables — `Currency`, `TaxProfile`, `/api/v1/currencies`, `/api/v1/tax-profiles`, `/export/*`, `require_permission`.
- Produces: verified parity between Standard and Pro (same codebase) — any missing surface wired and recorded.

- [ ] **Step 1: Verify the new API surfaces exist in Pro**

Run (backend up via `make env`):
```bash
curl -s http://127.0.0.1:8767/api/v1/currencies | head -c 200
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8767/api/v1/tax-profiles
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8767/export/products.csv
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8767/export/sales.csv?format=json
```
Expected: currencies returns JSON (200), tax-profiles 200, both export endpoints 200.

- [ ] **Step 2: Verify permission enforcement is active**

Run: `curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8767/api/v1/currencies` (unauthenticated)
Expected: 401 (auth) or 403 (permission) — never 201. If it returns 201, wire the `require_permission` decorator (02-standard.md, Task B3, Step 4) into the Pro controller registration and re-run.

- [ ] **Step 3: Verify the admin surfaces**

Log in to the Unfold admin (`http://127.0.0.1:8767/admin/`) and confirm `Currencies` and `Tax profiles` entries exist with seeded rows (USD/EUR/GBP/MAD; Standard/Reduced/Zero-rated). If missing, register the models in `admin.py` (same pattern as `02-standard.md` B1/B2 Step 4).

- [ ] **Step 4: Record parity in editions.md**

In the Pro section, add one line under Features:
```markdown
- **Standard parity:** full Community + Standard surface (refunds, offline-first, multi-currency, tax profiles, custom roles, CSV/JSON export) — verified 9 Aug 2026
```

- [ ] **Step 5: Commit**

```bash
git add projects/formints/formint/ projects/formints/docs/architecture/editions.md
git commit -m "test(formint): Pro parity sweep confirms Standard features inherited"
```

---

## Self-Review

1. **Spec coverage:** Pro's completion = documentation accuracy (P1, P3) + green verification gate (P2). No feature markers remain for Pro in `editions.md` — correct, since Pro is the reference tier.
2. **Placeholder scan:** P2 Step 3 is conditional ("only if a check fails") but names the exact action and file location; acceptable as a verification plan, not a code placeholder.
3. **Type consistency:** n/a — no new interfaces introduced.

## Execution Handoff

**Plan complete and maintained at `docs/plans/editions/03-pro.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
