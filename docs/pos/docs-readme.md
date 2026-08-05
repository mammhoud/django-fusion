# 🖥️ POS — Desktop Point-of-Sale Documentation

> **Canonical source:** `projects/pos/`  
> **Stack:** Tauri 2 + React 19 + Rust + SQLite + Python/Sanic sidecar

This directory contains POS-specific documentation that lives in the `docs/` site tree.

## POS Documentation Pages

| Page | Description |
|------|-------------|
| [`changelog.md`](changelog.md) | POS version history (mirror of project changelog) |
| [`network-architecture.md`](sidecar/network-architecture.md) | POS network and deployment architecture |

## POS Project Documentation

For the authoritative POS documentation, see the project README and internal docs:

| Document | Location |
|----------|----------|
| **POS README** | [`projects/pos/README.md`](../../projects/pos/README.md) |
| **POS CHANGELOG** | [`projects/pos/CHANGELOG.md`](https://github.com/mammhoud/structa.cloud/blob/generic/projects/pos/CHANGELOG.md) |
| **PUBLISH.md** | [`projects/pos/PUBLISH.md`](https://github.com/mammhoud/structa.cloud/blob/generic/projects/pos/PUBLISH.md) |
| **Editions Overview** | [`projects/pos/docs/README.md`](README.md) |
| **Screen captures** | *(see screenshot capture script in scripts/)* |

## POS Editions

| Edition | Directory | Key Differentiator |
|---------|-----------|-------------------|
| **Minimal** | `pos-minimal/` | Core POS only (React + Rust + SQLite) |
| **Solo** | `pos-solo/` | + Sidecar API + Cloud CRM sync |
| **Full** | `pos-full/` | + Django ORM + WebSocket + Cloud CRM master |

## Related Docs

| Area | Path |
|------|------|
| POS Site Docs | [`docs/sites/pos.md`](editions.md) |
| Rust Backend | [`docs/rust/`](../rust/) |
| TypeScript Frontend | [`docs/typescript/`](../typescript/) |
| Sidecar Server | [`docs/server/`](../server/) |
| POS Dev Guide | [`docs/guides/03-dev.md`](../../guides/03-dev.md) |
| Customization Guide | [`docs/guides/05-customize.md`](../../guides/05-customize.md) |
