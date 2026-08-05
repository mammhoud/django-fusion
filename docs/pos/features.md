# 🎯 POS — Features

> Feature set specific to the POS (Point of Sale) desktop application.

---

## Feature Matrix by Edition

| Feature | Mini | Solo | Full |
|---------|:----:|:----:|:----:|
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
| Multi-terminal sync | ❌ | ✅ | ✅ |
| Real-time WebSocket | ❌ | ✅ | ✅ |
| Offline mode | ✅ | ✅ | ❌ |
| Cloud CRM sync | ❌ | ✅ | ✅ |
| **Bolt analytics dashboard** | ❌ | ❌ | ☁️ |
| **Sync event log viewer** | ❌ | ❌ | ☁️ |
| **WebSocket live sync events** | ❌ | ❌ | ☁️ |
| **DataToken sync tagging** | ❌ | 🔧 | 🔧 |
| Robyn admin settings | ❌ | ✅ | ✅ |
| Device peer sync | ❌ | ✅ | ❌ |
| .env config | ✅ | ✅ | ✅ |
| POS crest branding | ✅ | ✅ | ✅ |
| Auth pages (6 languages) | ✅ | ✅ | ✅ |
| Scroll cart preview | ✅ | ✅ | ✅ |

> 🔧 = Available in django-fusion library for integration  
> ☁️ = Available in pos-cloud server

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

## Cloud Server (pos-cloud)

| Feature | Description |
|---------|-------------|
| **Bolt analytics dashboard** | Self-contained HTML dashboard at `/apis/data/` — 6 KPI cards, WebSocket live updates, sync event log viewer, dark theme |
| **WebSocket sync events** | Django Channels `SyncEventConsumer` at `/ws/sync-events/` — broadcasts products/sales/inventory/heartbeat events in real-time |
| **Unfold admin** | Django Unfold admin with live sync activity badges, delta counters, WS status indicator |
| **REST sync API** | `/api/sync/push/{products,sales,inventory,heartbeats}` — receives branch data from pos-solo/pos-full |
| **Branch management** | Organizations → Branches → Leads → Deals → Reports hierarchy |
| **django-fusion viewsets** | ModelViewset + SearchableViewMixin for all sync entities |
| **Makefile cloud targets** | `make cloud-run`, `cloud-dev`, `cloud-check`, `cloud-test`, `cloud-clean` |

## DataToken Sync Tagging (django-fusion)

| Feature | Description |
|---------|-------------|
| **Generic FK tagging** | Tag ANY model row for sync via `token` field (supports int, UUID, slug PKs) |
| **Parent/child tree** | Invoice → items ordering via self-referential FK + `sync_order` |
| **Progress tracking** | `sync_status`, `retry_count`, `error_message`, `synced_at` per token |
| **Auto-untag** | Signal handler auto-marks synced tokens when SyncLog flips to success |
| **Batch sync** | `DataToken.objects.sync_batch(node_id, limit)` — indexed, ordered query |
| **Mixin** | `DataTokenMixin` — drop-in `tag_for_sync()`, `mark_synced()`, `untag_for_sync()` |

> 📖 Full docs: [`docs/features/data-token-sync-tagging.md`](../../features/data-token-sync-tagging.md)

---

## Related

| Topic | Path |
|-------|------|
| POS editions | [`editions.md`](editions.md) |
| Rust backend | [`rust-backend.md`](backend/rust-backend.md) |
| Feature matrix | [`../../features/`](../../features/) |
| DataToken docs | [`../../features/data-token-sync-tagging.md`](../../features/data-token-sync-tagging.md) |
| Cloud CRM | [`cloud/`](cloud/) |
