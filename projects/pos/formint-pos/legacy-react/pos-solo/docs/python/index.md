# Python / Sidecar Docs — POS Solo

> **Directory:** `docs/python/`
> **Language:** Python 3.11+
> **Framework:** Robyn + Django ORM

---

POS Solo uses the same Python/sidecar conventions as POS Full.

See **`../../pos-full/docs/python/index.md`** for the full conventions reference.

### POS Solo Differences

- Sidecar runs on port `8766` (vs `8765` for POS Full)
- No role-based auth middleware — simpler request handling
- No multi-store sync services
- Simpler model set (no employee, payroll, role models)

See `../PROMPTS.md#python--sidecar-prompts` for code generation templates.
