# SQL / Migration Docs — POS Solo

> **Directory:** `docs/sql/`
> **Dialect:** SQLite 3.42+
> **ORM:** Diesel (Rust) + Django ORM (Python sidecar)

---

POS Solo uses the same SQL conventions as POS Full.

See **`../../pos-full/docs/sql/index.md`** for the full conventions reference.

### POS Solo Tables

POS Solo uses a subset of POS Full tables — no employee, payroll, or role-system
tables. Core tables: `products`, `categories`, `customers`, `sales`, `sale_items`.

See `../PROMPTS.md#sql-prompts` for code generation templates.
