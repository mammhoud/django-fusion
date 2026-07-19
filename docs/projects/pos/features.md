# 🎯 POS — Features

> Feature set specific to the POS (Point of Sale) desktop application.

---

## Feature Matrix by Edition

| Feature | Minimal | Solo | Full |
|---------|:-------:|:----:|:----:|
| Product catalog | ✅ | ✅ | ✅ |
| Category management | ✅ | ✅ | ✅ |
| Barcode scanning | ❌ | ✅ | ✅ |
| Sales orders | ✅ | ✅ | ✅ |
| Customer management | ❌ | ✅ | ✅ |
| Inventory tracking | ❌ | ✅ | ✅ |
| Multi-warehouse | ❌ | ❌ | ✅ |
| Purchase orders | ❌ | ❌ | ✅ |
| Cash register | ✅ | ✅ | ✅ |
| Receipt printing | ✅ | ✅ | ✅ |
| Payment methods | ✅ | ✅ | ✅ |
| Discount rules | ❌ | ✅ | ✅ |
| Tax rates | ✅ | ✅ | ✅ |
| i18n / Translation | ✅ | ✅ | ✅ |
| Dark mode | ✅ | ✅ | ✅ |
| Multi-terminal sync | ❌ | ❌ | ✅ |
| Real-time WebSocket | ❌ | ❌ | ✅ |
| Offline mode | ✅ | ✅ | ❌ |

---

## Rust Backend Operations

| Module | Operations |
|--------|-----------|
| `products` | CRUD + soft delete + barcode lookup |
| `categories` | CRUD + nested category tree |
| `orders` | Create, update status, list by date/customer |
| `inventory` | Stock levels, movements, adjustments |
| `customers` | CRUD + order history |
| `payments` | Record, refund, payment method routing |
| `registers` | Open/close session, cash float |
| `settings` | Store config, currency, locale |

---

## Related

| Topic | Path |
|-------|------|
| POS editions | [`editions.md`](editions.md) |
| Rust backend | [`rust-backend.md`](backend/rust-backend.md) |
| Feature matrix | [`../../features/`](../../features/) |
