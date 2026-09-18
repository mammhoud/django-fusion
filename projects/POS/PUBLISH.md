# POS — Marketplace Publish Kit

> **Related Names:** `publish`, `ThemeForest`, `CodeCanyon`, `Gumroad`, `marketplace`, `listing`, `screenshots`, `pricing`
> **Tags:** #publish #themeforest #marketplace #listing

Use this file when listing **Formints POS** on any digital marketplace.
The canonical edition family lives in `projects/formints/` — Community,
Standard, Pro, Cloud, and pos-client. **Pro** (Django-first) is the flagship
edition to list for enterprise buyers; statuses below follow the edition
finish board in [`docs/plans/editions/README.md`](../../docs/plans/editions/README.md).

---

## Editions Available

| Edition | Contents | Status |
|---------|----------|--------|
| **Community** | Tauri + Rust/Diesel + SQLite, offline-first desktop POS | ✅ done in code |
| **Standard** | Community + multi-currency, tax profiles, roles, CSV/JSON export, offline sync queue | ✅ done in code |
| **Pro** | Astro + Alpine + HTMX, Django ASGI + django-fusion + Unfold admin, KDS, CRM, gaming, gift cards, tables, delivery, kiosk, forecasting | ✅ done in code |
| **Cloud** | Hosted Django master: Organization → Branch, async sync, WebSocket, backups + monitoring, schema-per-tenant (Postgres flip-on pending) | 🟡 staging |
| **pos-client** | Vue 3 + Tauri register + Django shop backend + Astro storefront | 🔵 in development |

> **For marketplace listing**, lead with the **Pro** edition; every higher
> tier inherits the features of the tiers below it.

---

## Item Name

**POS — Restaurant Point of Sale Desktop App (Formint Edition)**

> Maximum 100 characters. No HTML or emoji.

---

## Short Description

Formints POS is a modern, cross-platform point-of-sale family for
restaurants and cafes. Built with Tauri, React 19, Rust, and SQLite, with a
Django (ASGI) backend for the Pro and Cloud editions. Works offline,
syncs between devices, and ships enterprise features — inventory, payroll,
kitchen display, suppliers, tax reports, loyalty, gift cards, and table
management.

---

<a id="visual-preview" aria-hidden="true"></a>

## Visual Preview

Screenshots captured via headless Chromium. Regenerate with `make screenshots`:

```bash
make -C formint-pos screenshots
```

### 1. Unfold Admin — Dashboard
![POS — Dashboard](../precis/landi/backend/assets/static/related/formints/pro-admin-dashboard.jpg)

### 2. Unfold Admin — Products
![POS — Products](../precis/landi/backend/assets/static/related/formints/pro-admin-products.jpg)

### 3. Unfold Admin — Customers
![POS — Customers](../precis/landi/backend/assets/static/related/formints/pro-admin-customers.jpg)

### 4. Unfold Admin — Sales
![POS — Sales](../precis/landi/backend/assets/static/related/formints/pro-admin-sales.jpg)

### 5. Unfold Admin — Loyalty (client categories)
![POS — Loyalty](../precis/landi/backend/assets/static/related/formints/pro-admin-loyalty.jpg)

### 6. Unfold Admin — Settings
![POS — Settings](../precis/landi/backend/assets/static/related/formints/pro-admin-settings.jpg)

---

## Key Features (for marketplace listing)

- Cross-platform desktop POS (Windows/macOS/Linux)
- Offline-first SQLite — no internet required
- Role-based user management with 2FA
- Inventory tracking with low-stock alerts
- Supplier and purchase order management
- Customer database with loyalty points
- Kitchen display system (pending → preparing → ready → delivered)
- Advanced receipt templates
- Automated tax reports
- Employee scheduling and payroll
- PDF and Excel report export
- Dark and light mode
- 3-language i18n (English, French, Arabic)
- Python/Sanic REST API (35+ endpoints)
- WebSocket real-time chat support
- Django ORM data models for sync
- Cross-device data synchronization

---

## Claim-Evidence Checklist (truth gate)

Every claim in a marketplace listing or public page must pass this gate
before publish. It is the lightweight gate from Phase 0 of the
[Formint audit plan](../../docs/plans/editions/10-formint-audit-and-reconciliation-2026-08-22.md).

- [ ] **Edition names and counts are canonical.** Use Community, Standard,
      Pro, Cloud, pos-client. Do not use retired names (Mini, Solo, Full,
      `formintA`, `formint-pos`) in public copy.
- [ ] **Status is accurate.** `done in code` (implemented + locally tested) ·
      `staging` (implemented, deployment pending) · `in development` (flows
      incomplete). Never use "live" or "shipped" for code that has not been
      deployed and verified.
- [ ] **Every feature claim cites a code path.** Link the feature to its
      edition directory or plan file
      ([`docs/plans/editions/`](../../docs/plans/editions/README.md)), or
      label it explicitly as roadmap/planned.
- [ ] **No external placeholder media.** Images come from the shared asset
      registry (`projects/formints/assets/`) or approved brand photography.
      No `picsum.photos` or other external placeholders.
- [ ] **Stack claims match the code.** Django ASGI for Pro/Cloud; Rust/Diesel
      + SQLite for Community/Standard; Vue 3 for pos-client. No Robyn, Sanic,
      RTK Query, or retired path references.

## Category & Attributes

| Field | Value |
|-------|-------|
| Category | Desktop Application / Software Template |
| High Resolution | Yes |
| Compatible Browsers | Chrome, Edge, Firefox, Safari |
| Compatible With | React 19, TypeScript, Tauri 2, Rust, SQLite, Python, Sanic, Django |
| Files Included | TSX, TS, RS, PY, JSON, SCSS, HTML, PNG, ICO |
| Layout | Responsive |
| Demo URL | https://structa.cloud |

---

## Tags (15 max for marketplace)

```
pos, restaurant, point of sale, desktop app, tauri, react, inventory, offline, reports, analytics, cross-platform, sqlite, typescript, rust, open source
```

---

## Pricing Guidance

| License | Suggested Price |
|---------|-----------------|
| Regular License | $17 – $21 |
| Extended License | $850 – $950 |

---

## Message to Reviewer

All images, sounds, video, code, and other assets included in this item are
either original work or appropriately licensed. This work is entirely my own
and I have full rights to sell it on ThemeForest/CodeCanyon.

The product family ships 5 editions:
- **Community**: offline-first desktop POS (Tauri + Rust + SQLite)
- **Standard**: Community + multi-currency, tax profiles, roles, exports, offline sync queue
- **Pro**: Django-first multi-terminal operation (KDS, CRM, gaming, gift cards, tables, delivery, kiosk, forecasting)
- **Cloud**: hosted master with Organization → Branch sync, backups, monitoring (staging)
- **pos-client**: Vue 3 register + Django shop + storefront (in development)

All source code is included, documented, and buildable from scratch.
