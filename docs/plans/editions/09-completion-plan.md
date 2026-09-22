# Formints Completion Plan — Make Every Edition DONE

> **Purpose:** turn the [finish board](README.md#finish-board-status-per-edition--21-aug-2026)
> into a concrete, actionable plan. `done` = implemented + verified in the
> tree. `staging`/`dev`/`publish pending` rows below each have exact steps to
> close them out. Owner actions (commits, deploys, registry releases, GitHub
> publish) are explicitly marked — nothing here requires new product code that
> does not already exist.
>
> **Status (21 Aug 2026):** Community ✅ · Standard ✅ · Pro ✅ · Cloud 🟡 staging ·
> pos-client 🔵 dev · Community version 🟡 publish pending · JS/TS SDK ✅ ·
> Tenant schemas 🟡 Postgres flip-on pending.

## 1. Cloud — staging → done

All Cloud code is implemented and locally verified (`apps/test_backup.py`,
`apps/test_monitor.py`, `apps/test_dashboard_contract.py`, `apps/test_tenancy.py`,
`apps/test_ws_*`). Promote it:

1. [ ] **Commit** the staged Cloud work — `BackupRun` model + migration (C1),
      `backup_db` command (C2), `/monitor/status` (C3), docs/changelog (C4),
      monitor tile + admin (C5), SDK monitor wiring (C6), e2e + parity sweep (C7).
2. [ ] **Boot a staging master** — `just install && make migrate`, then
      `make dev-backend` (:8082) + `make dev-api` (:8767) + `make dev-frontend` (:4323).
3. [ ] **Live verify** — `make verify-stack` (real WebSocket connect → identify →
      sync push → frame-shape assertions) and confirm `/monitor/status` +
      `/api/dashboard/*` on the running instance.
4. [ ] **Postgres schema-per-tenant flip-on** — set `DB_ENGINE`,
      `migrate_schemas --shared` then `--tenant`, seed `public` Tenant +
      `localhost` Domain ([08-tenant-schemas.md](08-tenant-schemas.md) Tenant 6–7).
5. [ ] Mark `04-cloud.md` + the finish board **done** after staging is healthy.

## 2. pos-client — dev → done

1. [ ] **Finish the cart/checkout UI flows end-to-end** against the Django shop
      backend (the API contracts + `my_orders_fragment` exist; the browser-level
      flows are the gap).
2. [ ] **Browser/E2E suite** — Playwright `frontends.spec.ts` on :1433
      (`projects/formints/tests/pos-e2e/`).
3. [ ] **Feature-inheritance parity sweep** — verify the Vue client inherits the
      lower-tier surface it should (shop catalog, orders, employee, CMS).
4. [ ] Mark `05-pos-client.md` + the finish board **done** once the suite is green.

## 3. Community — publish the standalone repo (external owner action)

Code is done. Only the GitHub publish checklist remains
([07-community-version.md](07-community-version.md) Task C4 + re-run gates C6):

1. [ ] Create `mammhoud/formint-community` (AGPL-3.0).
2. [ ] `make community-bundle` → push the bundle (`git init/add/commit/push`).
3. [ ] Repo metadata (description, topics, website `https://structa.cloud`),
      health files (CONTRIBUTING/CODE_OF_CONDUCT/SECURITY), issue templates.
4. [ ] First release `v0.1.0` (release.yml builds dmg/msi/AppImage/deb/rpm);
      configure `TAURI_SIGNING_PRIVATE_KEY` secrets.
5. [ ] Re-verify bundle smoke (`pnpm install` + `pnpm test` + `cargo test`) and
      the landing seed (Formints Community card CTA + offline-first badge).

## 4. Standard — environment gate only

- [ ] Run the full browser/E2E suite when a desktop/browser runtime is available
      (not a missing product feature).
- [ ] Optional: Django sidecar sync endpoints + large-dataset async exports
      (additive, not required for Standard's local contract).

## 5. Pro — environment gate only

- [ ] `cd projects/formints/formint-pro && make check && make test` once the
      local `server/.venv` is provisioned (absent in this checkout; validated
      via the cloud backend venv in the meantime).

## 6. JS/TS SDK — registry release (external owner action)

- [ ] Publish `@formints/client` to the registry (build/typecheck/tests pass;
      ESM + `.d.ts` ready).

## 7. Tenant schemas — Postgres flip-on (part of Cloud #4)

- [ ] When a Postgres target is available: flip `DB_ENGINE`, run
      `migrate_schemas`, seed a tenant, run the gated
      `TenantSchemaIntegrationTest`, mark Tenant 6–7 executed.

## Definition of done

| Edition | Done when |
|---------|-----------|
| Community | code + bundle verified; standalone repo published (owner) |
| Standard | local suite green (done); browser E2E run once (env gate) |
| Pro | `make check` + `make test` green in the provisioned env (env gate) |
| Cloud | staging deployed, `verify-stack` + Postgres flip-on pass |
| pos-client | cart/checkout UI + browser E2E green |
| SDK | registry release live (owner) |
| Community version | GitHub repo + first release live (owner) |
| Tenant schemas | Postgres `migrate_schemas` + integration test pass |

## How to track

- Update this file's checkboxes as steps land, then flip the finish-board status
  rows in [`README.md`](README.md#finish-board-status-per-edition--21-aug-2026)
  and the per-edition plan headers (`01`–`08`) when a row turns done.
- Owner-action items (commits, deploys, registry/GitHub publishes) are not code
  gaps — they are the only reason the edition is not yet marked done.
