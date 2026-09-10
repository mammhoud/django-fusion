---
Object type: Decision
Tags: adr, tauri, rust, pos, architecture
Status: Accepted
Category: Technology
Date: 2026-01-20
Decision Maker: mammhoud
Related Products: formint-pos
Related Editions: Community, Formint Professional, POS Cloud
---

# ADR-003: Tauri 2 + Rust for Desktop POS

## Context

The POS system needed desktop operations that could run offline on restaurant hardware, including kitchen display terminals, cashier stations, and back-office computers. The requirements were cross-platform delivery, local data access, native printing and file operations, a small runtime footprint, and reuse of the shared frontend.

## Options considered

1. **Electron** — mature ecosystem, but larger binaries and higher resource use.
2. **React Native Desktop** — shared React knowledge, but desktop support and abstraction costs.
3. **Flutter Desktop** — strong cross-platform UI, but a separate Dart stack and no direct fit for the existing backend boundary.
4. **Tauri 2 + Rust** — selected for the webview shell, native commands, security model, and low runtime overhead.

## Decision

Use Tauri 2 with Rust as the desktop shell for the Formint product workspace. The current product model is Community, Formint Professional, and POS Cloud.

The shared desktop boundary uses a web frontend, Rust native commands, local persistence where required, and an optional Django-backed service boundary for features that need server-side data or synchronization. The exact implementation is maintained in repository engineering plans rather than this knowledge-graph object.

## Consequences

**Positive:** cross-platform desktop delivery, native file and printer access, shared frontend reuse, and a smaller runtime boundary than Electron.

**Negative:** Rust learning curve, plugin ecosystem work, platform signing, sidecar lifecycle, and cross-platform test requirements.

**Guardrails:** pin supported Tauri versions, test release artifacts on supported platforms, document native permissions, and keep cloud-only concerns out of the local desktop boundary.

## Related

- → `../architecture/editions.md` — Current edition boundaries
- → `../architecture/sync-data.md` — Synchronization context
- → `../plans/tauri-desktop.md` — Desktop tools and use cases
- → `../plans/formint-pos-professional-plan.md` — Product contract
- → `../products/formint-pos.md` — Product description
- → `../objects/decision.md` — Decision object type
