# PlanInc — Implementation Plans

Enterprise Planning & Incubation Platform  
License: AGPL-3.0 | Repo: `https://github.com/mammhoud/PlanInc` | Branch: `generic`  
Directory: `application/tools/PlanInc/`

---

## Overview

PlanInc started as a wrapper around the Blinko note-taking platform
(`planing/` subdirectory) with a custom SurrealDB-backed Express runtime
(`runtime/server.mjs`). These plans migrate it to a fully self-contained
desktop application with no containers, no PostgreSQL, and a premium brand
identity.

---

## Phase Index

| Phase | File | Status | Summary |
|---|---|---|---|
| 0 | [phase-0-git-submodules.md](./phase-0-git-submodules.md) | ✅ Complete | Git remotes, submodule setup, `.gitmodules` config |
| 1 | [phase-1-tauri-rust-architecture.md](./phase-1-tauri-rust-architecture.md) | 📋 Planned | Full Tauri v2 + Rust desktop rewrite; Zustand frontend |
| 2 | [phase-2-surrealdb-file-migration.md](./phase-2-surrealdb-file-migration.md) | 🔜 Next | SurrealDB embedded file mode; remove container |
| 3 | [phase-3-prisma-postgres-removal.md](./phase-3-prisma-postgres-removal.md) | 📋 Planned | Remove Prisma, pg-boss, PostgreSQL from Blinko fork |
| 4 | [phase-4-privacy-sharing-preview.md](./phase-4-privacy-sharing-preview.md) | 📋 Planned | Note privacy, share modal, session-guarded preview |
| 5 | [phase-5-tag-visibility-scroll-alpine.md](./phase-5-tag-visibility-scroll-alpine.md) | 📋 Planned | Tag visibility filter, scroll-to-note, Alpine.js appearance |
| 6 | [phase-6-brand-identity.md](./phase-6-brand-identity.md) | 📋 Planned | Brand identity, logo mark, CSS tokens, Tauri window identity |

---

## Execution Order

```
Phase 0 (done)
     │
     ├── Phase 2 ──────────────────── IMMEDIATE (unblocks 3,4,5)
     │       │
     │       ├── Phase 3 ──────────── parallel with 4 and 5
     │       ├── Phase 4 ──────────── parallel with 3 and 5
     │       └── Phase 5 ──────────── parallel with 3 and 4
     │                │
     │                └── Phase 6 ── after CSS token system in place
     │
     └── Phase 1 ────────────────── long-term; after runtime stabilised
```

**Priority order for immediate work:**
1. Phase 2 — SurrealDB file migration (eliminates the container dependency)
2. Phase 3 — Prisma/PostgreSQL removal (stops broken pg-boss startup)
3. Phase 4 — Privacy + sharing (user-facing correctness)
4. Phase 5 — Tag filter + Alpine.js (UI quality)
5. Phase 6 — Brand identity (polish)
6. Phase 1 — Tauri rewrite (architecture; planned for next major cycle)

---

## Current Architecture

```
application/tools/PlanInc/
├── planing/              ← Blinko upstream fork
│   ├── prisma/           ← PostgreSQL schema (to be removed in Phase 3)
│   ├── server/           ← Express + tRPC + pg-boss backend (Blinko original)
│   └── app/src/          ← React frontend (kept, enhanced in Phases 4-6)
├── runtime/              ← ACTIVE BACKEND: custom Express + SurrealDB
│   └── server.mjs        ← All routes, auth, schema bootstrap
├── docker-compose.yml    ← surrealdb container + planing container
└── verify-surrealdb.sh   ← Deployment validator
```

---

## Target Architecture (after all phases)

```
application/tools/PlanInc/
├── src/                  ← React/Vite frontend (Tauri app)
├── src-tauri/            ← Rust backend (SurrealDB embedded)
│   └── src/commands/     ← All data access via Tauri invoke
├── brandkit/             ← Brand assets
├── runtime/              ← Retired after Phase 1 completion
└── planing/              ← Archive reference only
```

---

## Repository Context from This Chat Session

### Submodules established (Phase 0)

| Submodule | GitHub URL | Branch |
|---|---|---|
| `libs/django-fusion` | `mammhoud/django-fusion` | `generic` |
| `projects/CRM` | `mammhoud/crm` | `generic` |
| `projects/CMS` | `mammhoud/cms` | `generic` |
| `projects/POS` | `mammhoud/pos` | `generic` |
| `projects/Clients/ctc-research` | `mammhoud/ctc-research` | `generic` |
| `application/tools/PlanInc` | `mammhoud/PlanInc` | `generic` |

Workspace root: `https://github.com/mammhoud/workspace.git` → branch `generic`

### Product directory renames committed (commit `c5571fd0`)

| Old path | New path |
|---|---|
| `projects/syntara/` | `projects/CMS/` |
| `projects/loop-crm/` | `projects/CRM/` |
| `projects/formints/` | `projects/POS/` |

### PlanInc files created this session

| File | Location | Notes |
|---|---|---|
| `LICENSE` | `application/tools/PlanInc/LICENSE` | AGPL-3.0 |
| `README.md` | `application/tools/PlanInc/README.md` | Updated with Blinko/Anytype resources, ideations |
| `project.json` | `application/tools/PlanInc/project.json` | AGPL-3.0, PlanInc identity |

---

## Key Technical Facts (from codebase analysis)

### `runtime/server.mjs` (active backend)
- Pure SurrealDB — no PostgreSQL (throws on boot if any PG env var found)
- Connects via HTTP to SurrealDB container at `SURREALDB_URL`
- Schema: ~25 SCHEMAFULL tables bootstrapped idempotently on every boot
- Auth: JWT (Bearer token), workspace-scoped via `workspace_member` edges
- ~50 REST endpoints: auth, settings, workspaces, members, notes, tags,
  categories, attachments, tickets, AI, chat, study, invitations, audit

### `planing/` Blinko fork
- Backend: Express + tRPC (18 sub-routers) + Prisma/PostgreSQL + pg-boss
- Frontend: React 18, MobX, tRPC client, Vite, TailwindCSS, Tauri v2 shell
- Tauri plugin: two stub commands (`setcolor`, `open_app_settings`)
- `blinkoStore.tsx`: all note/tag/share operations via `api.*` tRPC calls
- `BlinkoShareDialog`: has share toggle, password, expiry — no email panel yet
- `pages/share/[id].tsx`: no session check for private notes yet
- Tags: full tree with CRUD; no visibility filtering by note count yet

### Prisma schema (PostgreSQL — to be removed)
21 models: `accounts`, `notes`, `attachments`, `config`, `tag`, `tagsToNote`,
`noteReference`, `comments`, `follows`, `notifications`, `cache`, `plugin`,
`conversation`, `message`, `noteHistory`, `noteInternalShare`, `session`,
`aiProviders`, `aiModels`, `aiScheduledTask`, `mcpServers`

---

## Related Plans Elsewhere in `docs/plans/`

| Plan | Path | Relevance |
|---|---|---|
| Loop CRM SurrealDB migration | `loop-crm/surrealdb-migration-plan.md` | Same SurrealDB SDK migration pattern |
| Workspace CRM M1-M6 | `workspace-crm/` | Multi-tenant context for PlanInc workspace model |
| Precis render flow | `repository/precis-main-render-flow.md` | Dual-rendering pattern reference |
| Brand logo enhancement | `BRAND-LOGO-ENHANCEMENT-PLAN.md` | Branding precedent for PlanInc Phase 6 |
