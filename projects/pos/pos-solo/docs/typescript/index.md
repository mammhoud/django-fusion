# TypeScript / React Docs — POS Solo + POS Mini

> **Directory:** `docs/typescript/`
> **Languages:** TypeScript, TSX
> **Framework:** React 18 + Vite + Tailwind CSS

---

POS Solo and POS Mini share the same TypeScript/React conventions as POS Full.

See **`../../pos-full/docs/typescript/index.md`** for the full conventions reference.

### Differences

| Feature | POS Full | POS Solo | POS Mini |
|---------|:--------:|:--------:|:--------:|
| Auth | Role-based (student/instructor/admin) | Single-user | Single-user |
| Sidecar | ✅ Python sidecar | ✅ Python sidecar | ❌ (Rust + Diesel direct) |
| Fusion | ✅ FusionDecoder + FusionStore | ✅ FusionDecoder + FusionStore | ❌ |
| Store | Redux + RTK Query + WebSocket | Redux + RTK Query | Redux + RTK Query |

See `../PROMPTS.md#typescript--react-prompts` for code generation templates.
