# Phase 1 — Tauri + Rust Desktop Architecture

**Status:** Planned  
**Scope:** `application/tools/PlanInc/`  
**Owner:** Desktop / Frontend  
**Depends on:** Phase 0 (submodule setup complete)

---

## Objective

Rewrite PlanInc as a pure Tauri v2 desktop application — a React/Vite frontend
communicating with embedded Rust commands — replacing the current Docker +
Node.js/Express + SurrealDB container stack entirely. No server process, no
containers, no network port at runtime.

---

## Background

The current `application/tools/PlanInc/` layout:

```
PlanInc/
├── planing/          ← Blinko upstream fork (Turbo monorepo, Prisma/PostgreSQL)
├── runtime/          ← Custom Node.js/Express server (SurrealDB via HTTP)
├── docker-compose.yml← Runs surrealdb container + planing container
└── verify-surrealdb.sh
```

The `planing/app/src-tauri/` already has Tauri v2 scaffolding with:
- `tauri-plugin-fs`, `tauri-plugin-dialog`, `tauri-plugin-http`
- `serde`, `serde_json`
- Two stub commands: `setcolor`, `open_app_settings`

The `runtime/` is the active backend — the `planing/` Blinko fork is the
upstream source used for UI patterns only.

---

## Target Architecture

```
application/tools/PlanInc/
├── src/                     # React/Vite frontend (TypeScript)
│   ├── components/
│   │   ├── NoteList/
│   │   ├── NoteCard/
│   │   ├── TagSidebar/
│   │   ├── SearchBar/
│   │   ├── ShareModal/
│   │   └── AppearanceSettings/
│   ├── store/               # Zustand stores
│   │   ├── noteStore.ts
│   │   ├── tagStore.ts
│   │   └── settingsStore.ts
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Settings.tsx
│   │   └── SharePreview.tsx
│   ├── lib/
│   │   ├── invoke.ts        # typed Tauri invoke wrappers
│   │   └── alpineAppearance.ts
│   └── main.tsx
├── src-tauri/               # Rust backend
│   ├── src/
│   │   ├── main.rs          # Tauri app bootstrap
│   │   ├── db.rs            # SurrealDB embedded init + State<Db>
│   │   ├── models.rs        # Serde data models (Note, Tag, etc.)
│   │   └── commands/
│   │       ├── notes.rs     # create_note, list_notes, update_note, delete_note
│   │       ├── tags.rs      # list_tags, create_tag, delete_tag
│   │       ├── search.rs    # search_notes (BM25 full-text)
│   │       ├── share.rs     # share_note, get_share_link
│   │       └── settings.rs  # get_settings, update_settings
│   ├── Cargo.toml
│   └── tauri.conf.json      # productName: PlanInc, id: cloud.structa.planinc
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── package.json             # frontend deps only — no server deps
├── LICENSE                  # AGPL-3.0
├── README.md
└── project.json
```

---

## Task Breakdown

### Task 1.1 — Scaffold clean Tauri v2 project

- Remove `runtime/`, `planing-data/`, `blinko-data/`, `docker-compose.yml`,
  `verify-surrealdb.sh` from the PlanInc root (keep `planing/` as archive).
- Scaffold Tauri v2 + Vite + React + TypeScript template.
- Set `productName = "PlanInc"`, `identifier = "cloud.structa.planinc"`.
- Remove all Blinko product name references.

**Acceptance:** `cargo check` passes. `bun run dev` opens a Tauri window titled
"PlanInc".

---

### Task 1.2 — SurrealDB embedded crate + State<Db>

- Add to `Cargo.toml`:
  ```toml
  surrealdb = { version = "2", features = ["kv-surrealkv"] }
  ```
- Create `src-tauri/src/db.rs`:
  ```rust
  use surrealdb::{Surreal, engine::local::SurrealKv};
  use tauri::Manager;

  pub struct Db(pub Surreal<SurrealKv>);

  pub async fn init_db(app: &tauri::App) -> surrealdb::Result<Surreal<SurrealKv>> {
      let data_dir = app.path().app_data_dir()?.join("planinc.db");
      let db = Surreal::new::<SurrealKv>(data_dir).await?;
      db.use_ns("planinc").use_db("planinc").await?;
      Ok(db)
  }
  ```
- Register with `.manage(Db(db))` in `main.rs`.

**Acceptance:** App starts → `data/planinc.db` created → `ping_db` command
returns `Ok(())`.

---

### Task 1.3 — Data models and CRUD commands

Define in `models.rs`:
```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct Note {
    pub id: Option<Thing>,
    pub content: String,
    pub is_share: bool,
    pub created_by: Option<String>,
    pub tags: Vec<String>,
    pub created_at: Option<Datetime>,
    pub updated_at: Option<Datetime>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Tag {
    pub id: Option<Thing>,
    pub name: String,
    pub note_count: Option<u64>,
}
```

Commands in `commands/notes.rs`:
- `create_note(content, tags) → Note`
- `list_notes(filter, page, size) → Vec<Note>`
- `update_note(id, content, is_share, tags) → Note`
- `delete_note(id) → bool`
- `search_notes(query) → Vec<Note>`

Unit-test each with `Surreal::new::<Mem>()` in-process.

**Acceptance:** `cargo test` passes all CRUD round-trips.

---

### Task 1.4 — React frontend + Tauri invoke wrappers

- Install: `@tauri-apps/api`, `tailwindcss`, `zustand`, `alpinejs`.
- Create `lib/invoke.ts` with typed wrappers:
  ```ts
  import { invoke } from '@tauri-apps/api/core';
  export const createNote = (content: string, tags: string[]) =>
    invoke<Note>('create_note', { content, tags });
  ```
- Build `NoteList`, `NoteCard`, `TagSidebar`, `SearchBar` components.
- Vitest unit tests for stores with mocked `invoke`.
- Playwright smoke: create note → appears in list → delete.

**Acceptance:** Full CRUD flow works in running Tauri window, no server, no
container.

---

### Task 1.5 — Packaging and bundle

- Configure Tauri bundler: Linux/macOS/Windows targets.
- Update icons from `brandkit/icons/` (Phase 6).
- Remove Blinko updater endpoint.
- `Makefile` targets: `dev`, `build`, `test`.

**Acceptance:** `cargo tauri build` produces a working installer. App persists
data across restarts.

---

## Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| `tauri` | `^2` | Desktop shell |
| `surrealdb` | `^2` | Embedded DB |
| `serde` + `serde_json` | `^1` | Serialization |
| `tauri-plugin-fs` | `^2` | File access |
| `tauri-plugin-dialog` | `^2` | Native dialogs |
| `@tauri-apps/api` | `^2` | JS invoke bridge |
| `zustand` | `^4` | Frontend state |
| `alpinejs` | `^3` | Appearance reactivity |

---

## Migration Path from Current Stack

| Current | Replaces with |
|---|---|
| `runtime/server.mjs` Express routes | Tauri Rust commands |
| `planing/server/` tRPC routers | Tauri Rust commands |
| SurrealDB container (HTTP) | SurrealDB embedded file (`kv-surrealkv`) |
| `planing/app/src/store/` MobX | Zustand stores |
| `docker-compose.yml` | No container needed |
| `node runtime/server.mjs` | `cargo tauri dev` / installed binary |

---

## Notes

- This is the long-term target architecture. Phase 2 (SurrealDB file migration
  in `runtime/server.mjs`) is the intermediate step that removes the container
  while keeping the Node.js runtime — Phase 1 replaces Node.js with Rust.
- Phases 2–7 can land independently; Phase 1 is a larger undertaking and
  should be done after the runtime is stabilised.
- The `planing/` Blinko fork remains as a UI reference — component patterns,
  CSS tokens, and Alpine.js integrations from Phases 5–6 are forward-ported
  into the Tauri frontend.
