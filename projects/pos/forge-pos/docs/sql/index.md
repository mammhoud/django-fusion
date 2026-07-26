# SQL / Migration Docs — POS Mini

> **Directory:** `docs/sql/`
> **Dialect:** SQLite 3.42+
> **ORM:** Diesel direct (no Django ORM)

---

POS Mini uses raw SQL migration files in `src-tauri/migrations/` — no Diesel
migration runner and no Django ORM.

See **`../../pos-full/docs/sql/index.md`** for the base SQL convention patterns.

### POS Mini Specific

- **Migrations are raw SQL files** (not Diesel `diesel migration generate`)
- **Filename format:** `YYYY-MM-DD-HHMMSS_description/up.sql`
- **No `down.sql` required** — migrations are additive (IF NOT EXISTS)
- **All tables managed by Diesel** — no Django ORM counterpart

### Migration File Example

```
src-tauri/migrations/
├── 2026-01-01-000000_create_all/
│   └── up.sql                       # Initial schema
└── 2026-07-25-000000_add_border_color/
    └── up.sql                       # Additive column
```

See `../PROMPTS.md#sql-prompts` for code generation templates.
