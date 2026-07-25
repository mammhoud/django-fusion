# POS Solo — Prompt Variations

> **Project:** `projects/pos/pos-solo/`
> **Purpose:** Reusable AI prompts for code generation, organized by language

---

## TypeScript / React Prompts

Same as POS Full — see `../pos-full/PROMPTS.md` for the full catalog.

### POS Solo Specific

```
Add a new page at src/pages/NewFeature.tsx for POS Solo (single-user edition):
- PageLayout wrapper (no role-based auth — all features available)
- RTK Query data fetching from the sidecar API on localhost:8766
- Loading, error, empty, and normal states
- CTC teal theme classes
- No employee/role/payroll features — solo operator only
```

---

## Python / Sidecar Prompts

Same as POS Full — see `../pos-full/PROMPTS.md`.

### POS Solo Specific
- Sidecar runs on port `8766` (vs `8765` for POS Full)
- No role-based auth middleware — simpler request handling
- No multi-store sync services

---

## Rust / Tauri Prompts

Same as POS Full — see `../pos-full/PROMPTS.md`.

### POS Solo Specific
- No WebSocket sync — all data is local to the SQLite database
- Tauri invoke commands are direct SQLite operations

---

## SQL Prompts

Same as POS Full — see `../pos-full/PROMPTS.md`.
