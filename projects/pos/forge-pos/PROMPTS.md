# POS Mini — Prompt Variations

> **Project:** `projects/pos/pos-mini/`
> **Purpose:** Reusable AI prompts for code generation, organized by language

---

## TypeScript / React Prompts

Same as POS Full — see `../pos-full/PROMPTS.md` for base catalog.

### POS Mini Specific

```
Add a new page at src/pages/NewFeature.tsx for POS Mini (lightweight edition):
- PageLayout wrapper (no auth — lightweight single-user)
- Tauri invoke calls (no sidecar — all data via Rust/Diesel)
- Loading, error, empty, and normal states
- CTC teal theme classes
- No Python imports or sidecar dependencies
```

### Add a new Tauri invoke call (no sidecar)
```
Add a new Tauri invoke for [feature]:
- Create the Rust command in src-tauri/src/commands/[feature].rs
- Register in src-tauri/src/main.rs
- Create TypeScript wrapper in src/utils/tauri.ts
- Call via: const result = await invoke('[command]', { args });
```

---

## Rust / Tauri Prompts

### Add a new Diesel model (POS Mini — direct DB access)
```
Add a new Rust struct to src-tauri/src/db/models.rs for [table]:
- Derive Queryable, Insertable, Serialize, Deserialize, Identifiable
- Add to schema.rs with diesel::table! macro
- Add CRUD command handlers in src-tauri/src/commands/[table].rs
- Create SQL migration in src-tauri/migrations/YYYY-MM-DD-[description]/up.sql
```

### Add a new SQL migration (native SQL files)
```
Create a new SQL migration for [change]:
- File: src-tauri/migrations/YYYY-MM-DD-HHMMSS_[description]/up.sql
- Use raw SQL (no Diesel migration runner)
- IF NOT EXISTS patterns for idempotent migrations
```

---

## Python Prompts

**POS Mini does not include a Python sidecar.** No Python prompts apply.
All backend logic is in Rust + Diesel + SQLite.

---

## SQL Prompts

Same as POS Full — see `../pos-full/PROMPTS.md`.

### POS Mini Specific
- Migrations are raw SQL files in `src-tauri/migrations/` (not Diesel migration runner)
- No Django ORM — write SQL directly
- SQLite-compatible syntax only (no PostgreSQL-specific features)
