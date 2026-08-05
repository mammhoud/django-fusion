# POS — Marketplace Publish Kit

> **Related Names:** `publish`, `ThemeForest`, `CodeCanyon`, `Gumroad`, `marketplace`, `listing`, `screenshots`, `pricing`
> **Tags:** #publish #themeforest #marketplace #listing

Use this file when listing **POS** on any digital marketplace.
The merged **Formint** package is the canonical edition to list.

---

## Editions Available

| Edition | Contents | Target |
|---------|----------|--------|
| **Mini** | Core POS app (Tauri + Rust + SQLite) | Offline-only deployments |
| **Formint (merged)** | Astro frontend + Django Ninja backend + Robyn sidecar + Unfold admin (consolidates former Solo + Full) | Enterprise multi-device |

> **For marketplace listing, always use `formint-pos/`** (the merged package).

---

## Item Name

**POS — Restaurant Point of Sale Desktop App (Formint Edition)**

> Maximum 100 characters. No HTML or emoji.

---

## Short Description

POS is a modern, cross-platform desktop POS app for restaurants and cafes.
Built with Tauri, React 19, Rust, and SQLite. Works offline. Includes a
Python/Sanic API sidecar with Django ORM, WebSocket chat, data sync between
devices, and full enterprise features — inventory, payroll, kitchen display,
suppliers, tax reports, loyalty program, and 29 database tables.

---

<a id="visual-preview" aria-hidden="true"></a>

## Visual Preview

Screenshots captured via headless Chromium. Regenerate with `make screenshots`:

```bash
make -C formint-pos screenshots
```

### 1. Unfold Admin — Dashboard
![POS — Dashboard](formint-pos/docs/screenshots/admin/01_admin_dashboard.jpg)

### 2. Unfold Admin — Products
![POS — Products](formint-pos/docs/screenshots/admin/02_admin_products.jpg)

### 3. Unfold Admin — Customers
![POS — Customers](formint-pos/docs/screenshots/admin/03_admin_customers.jpg)

### 4. Unfold Admin — Sales
![POS — Sales](formint-pos/docs/screenshots/admin/04_admin_sales.jpg)

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

The product ships in 3 editions:
- **Minimal**: Core desktop app only
- **Solo**: Core + REST API sidecar + Cloud CRM sync
- **Full**: Core + sidecar + Django ORM + WebSocket + data sync + Cloud CRM master (this listing)

All source code is included, documented, and buildable from scratch.
