# Rust / Tauri Docs — POS Solo

> **Directory:** `docs/rust/`
> **Language:** Rust (2021 edition)
> **Framework:** Tauri 2.x + Diesel ORM

---

POS Solo uses the same Rust/Tauri conventions as POS Full.

See **`../../pos-full/docs/rust/index.md`** for the full conventions reference.

### POS Solo Differences

- No WebSocket sync — all data operations are local SQLite
- Tauri invoke commands are direct database operations
- Simplified command set (no multi-store, no employee, no role commands)

See `../PROMPTS.md#rust--tauri-prompts` for code generation templates.
