# 🎨 Vue Frontend — Overview

> The POS frontend is built with Vue 3 + TypeScript + Vite, running inside a Tauri desktop shell.

---

## Architecture

```
Tauri Desktop Shell
     │
     ▼
Vue 3 + TypeScript (Vite)
     ├── Views (Dashboard, Menu, Orders, Settings...)
     ├── Components (ProductCard, OrderList, Receipt...)
     ├── API Layer (Tauri invoke + HTTP to sidecar)
     ├── Contexts (Auth, Theme, Language)
     ├── Hooks (useAuth, useProducts, useOrders...)
     ├── Router (Vue Router)
     └── i18n (en/fr/ar)
```

---

## Files

| File | Purpose |
|------|---------|
| [`typescript-frontend.md`](typescript-frontend.md) | Frontend architecture: views, router, layouts |
| [`typescript-components.md`](typescript-components.md) | Reusable Vue components catalog |
| [`typescript-contexts-hooks.md`](typescript-contexts-hooks.md) | Auth context, theme provider, language provider |
| [`typescript-api.md`](typescript-api.md) | API client layer: Tauri invoke + HTTP calls |

---

## Related

| Topic | Path |
|-------|------|
| Sidecar overview | [`../sidecar/README.md`](../sidecar/README.md) |
| Rust backend | [`../backend/README.md`](../backend/README.md) |
| POS editions | [`../editions.md`](../editions.md) |
