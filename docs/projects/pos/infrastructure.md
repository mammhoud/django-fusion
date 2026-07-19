# 🔧 POS — Infrastructure

> Infrastructure specifics for the POS (Point of Sale) Tauri desktop application.

---

## Editions & Infrastructure

| Edition | Backend | Frontend | Database |
|---------|---------|----------|----------|
| **Minimal** | Embedded Rust | Vue 3 (Tauri) | SQLite (file) |
| **Solo** | Sidecar API (embedded) | Vue 3 (Tauri) | SQLite (file) |
| **Full** | Sidecar API (external) | Vue 3 (Tauri) | SQLite (file) |

---

## Sidecar Architecture

### Solo (Embedded)

```
┌──────────────────────────┐
│     Tauri App Window      │
│  ┌──────────────────────┐ │
│  │   Vue 3 Frontend     │ │
│  │   (TypeScript)        │ │
│  └──────┬───────────────┘ │
│         │ invoke()        │
│  ┌──────▼───────────────┐ │
│  │   Rust Core (lib.rs)  │ │
│  │   Tauri Commands      │ │
│  └──────┬───────────────┘ │
│         │ sidecar spawn   │
│  ┌──────▼───────────────┐ │
│  │   Sidecar Binary      │ │
│  │   (Rust HTTP API)     │ │
│  └──────────────────────┘ │
└──────────────────────────┘
```

### Full (External Server)

```
┌──────────────────┐     ┌──────────────────┐
│  Tauri App #1    │     │  Tauri App #2    │
│  (Terminal 1)    │     │  (Terminal 2)    │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         └──────────┬─────────────┘
                    │ HTTP API
         ┌──────────▼─────────────┐
         │   Sidecar Server       │
         │   (Rust HTTP + WS)     │
         │   :3000                │
         └──────────┬─────────────┘
                    │
         ┌──────────▼─────────────┐
         │   SQLite Database      │
         │   (shared pos.db)      │
         └────────────────────────┘
```

---

## Network Requirements

| Edition | Network |
|---------|---------|
| Minimal | None (embedded) |
| Solo | None (localhost sidecar) |
| Full | LAN/WiFi for multi-terminal |

### Full Edition Ports

| Service | Port | Protocol |
|---------|------|----------|
| Sidecar HTTP API | `3000` | HTTP REST |
| Sidecar WebSocket | `3001` | WS (real-time sync) |
| Tauri Dev Server | `1420` | HTTP (Vite) |

---

## Build

```bash
cd projects/pos/pos-full
cargo build --release          # Rust backend
cd ../pos-client
npm install && npm run build   # Vue frontend
cd ../pos-client/src-tauri
cargo tauri build              # Tauri desktop bundle
```

---

## Related

| Topic | Path |
|-------|------|
| POS editions | [`editions.md`](editions.md) |
| Rust backend | [`rust-backend.md`](backend/rust-backend.md) |
| TypeScript frontend | [`typescript-frontend.md`](frontend/typescript-frontend.md) |
| Sidecar API | [`sidecar-readme.md`](sidecar/README.md) |
