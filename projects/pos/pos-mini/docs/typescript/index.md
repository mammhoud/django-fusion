# TypeScript / React Docs — POS Mini

> **Directory:** `docs/typescript/`
> **Languages:** TypeScript, TSX
> **Framework:** React 18 + Vite + Tailwind CSS (no sidecar, no Python)

---

POS Mini uses the same TypeScript/React conventions as POS Full but with a
simpler architecture (no sidecar, no Fusion, direct Rust/Diesel data access).

See **`../../pos-full/docs/typescript/index.md`** for the base conventions.

### POS Mini Specific

- **No Python sidecar** → no FusionDecoder, FusionStore, or fusion-types
- **Direct Tauri invoke** → all data goes through Rust commands
- **Simpler state** → no WebSocket, no multi-store sync
- **No role system** → all features available to the single user
- **`stores/` directory** (plural, not `store/`) — pre-existing convention

See `../PROMPTS.md#typescript--react-prompts` for code generation templates.
