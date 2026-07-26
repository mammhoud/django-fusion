---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Decision
Status: Accepted
Category: Technology
Date: 2026-01-20
Decision Maker: mammhoud
Tags: adr, tauri, rust, pos---

# ADR-003: Tauri 2 + Rust for Desktop POS

## Context

The POS system needed desktop editions that could run offline on restaurant hardware — kitchen display terminals, cashier stations, and back-office computers. These run on consumer-grade hardware where resource efficiency matters: older Windows machines, Raspberry Pi-based kiosks, and budget Android x86 tablets.

The requirements were:
- Cross-platform desktop app (macOS, Windows, Linux)
- Offline-first operation with local SQLite database
- Native file system access for receipts, exports, and backups
- Small binary size and low memory footprint
- Reuse of the existing React frontend codebase
- Ability to embed a Python sidecar for Django-based features (solo/full editions)

## Options Considered

1. **Electron**
   - Pros: Mature ecosystem, large community, full Node.js/npm access, Chromium DevTools
   - Cons: ~150MB+ binary, ~500MB+ RAM at idle, heavy resource usage, slow startup

2. **React Native Desktop (RNW + Electron)**
   - Pros: Shared React knowledge
   - Cons: Still Electron underneath, plus another abstraction layer, immature desktop support

3. **Flutter Desktop**
   - Pros: Single codebase for mobile + desktop, good performance
   - Cons: Dart ecosystem separate from existing Python/React stack, no Python sidecar integration

4. **Tauri 2 + Rust** — **Chosen**
   - Pros: ~5MB binary, low memory usage, Rust system access, security model, existing React frontend reuse
   - Cons: Younger ecosystem, Rust learning curve, fewer native plugins, macOS code-signing complexity

## Decision

We chose **Tauri 2 with Rust** for the desktop POS editions.

The architecture uses Tauri's webview-based shell for the React frontend (built with Vite + Tailwind CSS + shadcn/ui) and Rust commands for native operations (SQLite access, file I/O, printing, serial port communication for receipt printers).

Three editions share the same Tauri + Rust core:

| Edition | Database | Sync | Python Sidecar | Target |
|---------|----------|------|----------------|--------|
| **pos-mini** | Rust SQLite (diesel) | None (air-gapped) | No | Food truck, kiosk |
| **pos-solo** | SQLite via Django ORM | LAN master/slave | Yes (Robyn) | Single restaurant |
| **pos-full** | SQLite/PostgreSQL via Django | Cloud + LAN | Yes (Robyn) | Restaurant chain |

The sidecar pattern (used in solo and full editions) runs a Robyn Python HTTP server alongside the Tauri process. The React frontend communicates with the sidecar via `fetch()` for Django-backed features, and via `@tauri-apps/api` invoke for native Rust commands. This hybrid approach lets us keep Django's ORM and admin for data-heavy features while using Rust for performance-critical operations.

## Consequences

**Positive:**
- Binary sizes of ~5–15MB versus Electron's ~150MB+
- RAM usage typically under 200MB at idle (versus 500MB+ for Electron)
- Rust's memory safety prevents common desktop bugs (buffer overflows, use-after-free)
- React frontend is shared across all three desktop editions and the web cloud edition
- Security model prevents XSS from accessing native APIs
- Vite-based dev server provides fast hot-reload during development

**Negative:**
- Rust learning curve for the development team
- Fewer ready-made Tauri plugins compared to Electron's npm ecosystem
- macOS code signing requires specific CI configuration
- Sidecar management adds process lifecycle complexity
- Building for Windows requires MSVC toolchain setup

**Risks:**
- **Tauri ecosystem maturity** — mitigated by pinning to Tauri 2 stable releases and contributing upstream when needed
- **Rust compilation times** — mitigated by incremental compilation and CI caching
- **Sidecar distribution** — mitigated by bundling Python dependencies via `uv` during the build
- **Cross-platform testing** — mitigated by CI matrix builds on macOS, Ubuntu, and Windows runners

## Related Docs

- → `../architecture/editions.md` — POS editions architecture
- → `../architecture/sync-architecture.md` — Sync models per edition
- → `../features/pos-mini.md` — pos-mini features
- → `../features/pos-solo.md` — pos-solo features
- → `../features/pos-full.md` — pos-full features
- → `../objects/decision.md` — Decision object type
