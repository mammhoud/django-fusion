# Feature Comparison Matrix

**Type:** Feature ✨
**Tags:** `#pos-mini` `#pos-solo` `#pos-full` `#pos-cloud`
**Status:** Published

---

## Feature Grid

| Feature | pos-mini | pos-solo | pos-full | pos-cloud |
|---------|----------|----------|----------|-----------|
| **Sales (POS)** | ✅ | ✅ | ✅ | ✅ |
| **Cart + Checkout** | ✅ | ✅ | ✅ | ✅ |
| **Product Manager** | ✅ | ✅ | ✅ | ✅ |
| **Categories** | ✅ | ✅ | ✅ | ✅ |
| **Inventory** | ✅ | ✅ | ✅ | ✅ |
| **Recipes** | ✅ | ✅ | ✅ | ✅ |
| **Analytics Dashboard** | ✅ | ✅ | ✅ | ✅ |
| **Transaction History** | ✅ | ✅ | ✅ | ✅ |
| **Invoices** | ✅ | ✅ | ✅ | ✅ |
| **Reports** | ✅ | ✅ | ✅ | ✅ |
| **Employee Manager** | ✅ | ✅ | ✅ | ✅ |
| **Payroll** | ✅ | ✅ | ✅ | ✅ |
| **Schedule** | ✅ | ✅ | ✅ | ✅ |
| **Kitchen Display** | ✅ | ✅ | ✅ | ✅ |
| **Customer Manager** | ✅ | ✅ | ✅ | ✅ |
| **Supplier Manager** | ✅ | ✅ | ✅ | ✅ |
| **Receipt Templates** | ✅ | ✅ | ✅ | — |
| **Tax Reports** | ✅ | ✅ | ✅ | ✅ |
| **Roles & Permissions** | ✅ (Rust) | ✅ (Django) | ✅ (Django) | ✅ (Admin) |
| **Auth** | ✅ (Local) | ✅ (Local) | ✅ (Local) | ✅ (SSO) |
| **i18n (5 languages)** | ✅ | ✅ | ✅ | ✅ |
| **Theme System** | ✅ (Bio) | ✅ (Bio) | ✅ (Bio) | — |
| **RTL Support** | ✅ | ✅ | ✅ | ✅ |
| **Offline Mode** | ✅ Always | ✅ Partial | ✅ Partial | ❌ |
| **LAN Sync** | ❌ | ✅ Branch | ✅ Branch | ❌ |
| **Cloud Sync** | ❌ | ❌ | ✅ | ✅ Native |
| **Multi-branch** | ❌ | Single | ✅ | ✅ |
| **Admin Dashboard** | ❌ | ✅ Sidecar | ✅ Sidecar+Cloud | ✅ Native |
| **Export (PDF/Excel)** | ✅ | ✅ | ✅ | ✅ |
| **Keyboard Shortcuts** | ✅ | ✅ | ✅ | ✅ |
| **PDF Receipts** | ✅ | ✅ | ✅ | ✅ |
| **Print Receipts** | ✅ | ✅ | ✅ | ✅ |

---

## Edition-Specific Strengths

```
pos-mini ──→ Lightest, fastest, fully offline, no dependencies
pos-solo ──→ Branch sync, sidecar dashboard, Django ORM
pos-full ──→ Cloud sync, enterprise features, admin panel
pos-cloud ─→ Multi-tenant, subscription, web-first
```

---

## Technology Stack

| Component | pos-mini | pos-solo | pos-full | pos-cloud |
|-----------|----------|----------|----------|-----------|
| **Frontend** | React 19 + TS | React 19 + TS | React 19 + TS | Next.js 15 |
| **Desktop** | Tauri v2 + Rust | Tauri v2 | Tauri v2 | — |
| **Backend** | Rust (Tauri) | Django + Robyn | Django + Robyn | Django + DRF |
| **Database** | SQLite | SQLite | SQLite | PostgreSQL |
| **Sync** | — | LAN (Robyn) | REST + WSS | REST + WSS |
| **State** | Zustand + React | Zustand + React | Zustand + React | Redux + React |

---

## Related Docs
- → `architecture/editions-overview.md` — High-level edition comparison
- → `features/pos-mini.md` — pos-mini feature details
- → `features/pos-solo.md` — pos-solo feature details
- → `features/pos-full.md` — pos-full feature details
