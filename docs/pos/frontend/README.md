# 🎨 POS Frontend — Overview

> The desktop POS frontend is React 19 + TypeScript + Vite (Community /
> Standard) or Vue 3 (pos-client), running inside a Tauri desktop shell. Pro
> and Cloud use an Astro 5 + Alpine/HTMX shell. This folder documents the
> desktop React/Vue layers.

---

## Architecture

```
Tauri Desktop Shell
     │
     ▼
React 19 / Vue 3 + TypeScript (Vite)
     ├── Views (Dashboard, Menu, Orders, Settings...)
     ├── Components (ProductCard, OrderList, Receipt...)
     ├── API Layer (Tauri invoke → Rust/Diesel)
     ├── Contexts (Auth, Theme, Language)
     ├── Hooks (useAuth, useProducts, useOrders...)
     ├── Router (React Router / Vue Router)
     └── i18n (en/fr/ar or en/zh-CN)
```

---

## Files

| File | Purpose |
|------|---------|
| [`typescript-frontend.md`](typescript-frontend.md) | Frontend architecture: views, router, layouts |
| [`typescript-components.md`](typescript-components.md) | Reusable Vue components catalog |
| [`typescript-contexts-hooks.md`](typescript-contexts-hooks.md) | Auth context, theme provider, language provider |
| [`typescript-api.md`](typescript-api.md) | API layer: Tauri invoke (Community/Standard) — sidecar client archived |

---

## Related

| Topic | Path |
|-------|------|
| Sidecar overview (archived) | [`../sidecar/README.md`](../sidecar/README.md) |
| Rust backend | [`../backend/README.md`](../backend/README.md) |
| POS editions | [`../editions.md`](../editions.md) |
