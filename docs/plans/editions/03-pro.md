# Pro Edition — Local Completion Record

> Tags: `#formints` `#pos` `#pro` `#django` `#django-fusion` `#unfold` `#astro` `#htmx` `#kds` `#sync` — status ✅ done (21 Aug 2026).

**Canonical product:** `projects/formints/formint-pro/`
**Legacy aliases:** `pos-full`, `pos-solo`, and `formint/` are compatibility names only.

**Status:** Local work complete (Standard-parity `Currency`/`TaxProfile` models
+ migration + Ninja CRUD, read-only CSV/JSON export, regression tests, scoped
API-key enforcement + sliding-window rate limits, the Kitchen Display System
station-routing pillar, the QR Menu versioning/publish core, the Loyalty
reversal + consent fields, the Mobile Waiter split/merge workflow, Multi-terminal
Sync, the Offline Queue, the Barcode Scanner, the POS-KO Gaming Center,the Gift Cards, the Table Management (floor layouts + order tracking), the
Delivery Integration (platform connectors), the AI Forecasting (advisory
read-only analytics), the Employee Scheduling (shift planning + time
clock), the Customer Display (read-only order-confirmation screens), the
Self-checkout Kiosk (self-service kiosk mode), the Inventory Forecasting
(reorder-point planning + draft purchase orders), and the Purchase Order
workflow (order → receive → stock-in with reorder alerts). The server is
Django-first (daphne ASGI + django-bolt + django-fusion; Robyn removed). Only
environment/operator-gated items remain; see
[Next phases / follow-ups](#next-phases--follow-ups).

## Kitchen Display System (KDS)

The Pro edition owns the KDS — one of the four P0 launch-scope features.
Scope per the feature roadmap: **station routing, ticket lifecycle, timers,
metrics**.

| Pillar | State | Implementation |
|---|---|---|
| Ticket lifecycle | ✅ | `pending → preparing → ready → delivered` + auto `completed_at` |
| Timers | ✅ | `prepare_time_minutes`, `started_at`/`ready_at`/`completed_at` lifecycle timestamps, elapsed/overdue + prep progress bar |
| Metrics | ✅ | `GET /kds/stats/` (counts by status + overdue + last-24h) |
| Station routing | ✅ (this change) | `KitchenStation` model + `station` FK, category-keyword auto-routing with expedite fallback |

**Station routing surface** (canonically the Django `views_django.py`; the
legacy Robyn `routes/kds.py` mirror is deprecated and no longer registered):

| Endpoint | Method | Purpose |
|---|---|---|
| `/kds/stations/` | GET/POST | List / create kitchen stations |
| `/kds/tickets/?station=<slug>` | GET | Filter tickets by station |
| `/kds/tickets/<id>` (PATCH `station_id`) | PATCH | Re-route a ticket |

Routing is automatic on ticket creation (`views_django.py`
`create_sale_with_items`): explicit `kitchen_station_id` wins, else
`route_station_for_sale()` matches sale-item product categories against each
station's comma-separated `category_keywords`, falling back to the first
active `expedite` station. Stations are seeded by `manage.py seed_demo`
(Expedite, Bar, Grill, Pantry, Prep).

## QR Menu

QR Menu is the second P0 launch-scope feature. Scope per the roadmap:
**versioned localized menu, preview/publish, branch/table QR**.

| Pillar | State | Implementation |
|---|---|---|
| Versioned menu | ✅ | `MenuVersion` — immutable (menu, version, locale) snapshot with draft/published/archived status |
| Preview / publish | ✅ | `publish_menu_version()` increments versions + archives prior published; token-gated draft preview |
| Localized | ✅ | per-locale versions (`locale` BCP 47 code) |
| Branch/table QR | ✅ | `GET /menu/<slug>/qr?branch=&table=&locale=` returns SVG QR (lazy `qrcode` dep) |

**Surface** (Django `views_django.py` + `configs/urls.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `/menu/published/?locale=` | GET | List published menu versions |
| `/menu/<id>/publish` | POST | Publish the next version (archives current) |
| `/menu/<id>/preview?token=` | GET | Preview draft (token-gated) |
| `/menu/<slug>/` | GET | Public slug-keyed menu (grouped by category) |
| `/menu/<slug>/qr` | GET | SVG QR for the public menu URL |

Public page: `frontend/src/pages/menu/[slug].astro`. Seeding publishes an
initial `en` version of `main-menu`. Note: QR image generation needs the
`qrcode` dependency (`uv sync`) — it is lazy-imported so the rest of the
server runs without it.

## Loyalty System (P1)

| Pillar | State | Implementation |
|---|---|---|
| Immutable points ledger | ✅ | `LoyaltyTransaction` (earn/redeem/adjust/expire/**reversal**) |
| Rewards | ✅ | `ClientCategory` perks + `discount_rate` |
| Consent | ✅ | `Customer.marketing_consent` + `consent_granted_at` (GDPR) |
| Reversals | ✅ | `reversal` transaction type (negative `points_change`) |

## API Access (P1)

| Pillar | State | Implementation |
|---|---|---|
| Versioned schemas | ✅ | `/api/v1/` Ninja contract (django-fusion encoder/decoder) |
| Scoped keys | ✅ | `ApiKey` (SHA-256 hash, `resource:action` scopes, revoke/rotate) |
| Rate limits | ✅ | `ApiKey.rate_limit_per_minute` + `ApiKeyRateLimitMiddleware` (sliding window, Redis-ready) |
| Webhooks | ✅ | `/webhooks/receive/<signal>` + stats |

Rate limiting is enforced on `/api/v1/` and `/api-keys/` via the
`X-API-Key` header; a key over budget receives `429` with `Retry-After` +
`X-RateLimit-*` headers. The limiter is in-memory (single-node) behind a
`SlidingWindowRateLimiter` interface that can be swapped for Redis.

## Mobile Waiter (P1)

| Pillar | State | Implementation |
|---|---|---|
| Tableside orders | ✅ | `sale_checkout` accepts `order_type` + `table_number` |
| Kitchen handoff | ✅ | KDS `KitchenTicket` auto-creation on checkout |
| Split / merge | ✅ | `SaleGroup` + `Sale.group`/`parent_sale`; `services.split_merge` (split/merge/merge-group) |
| Offline retry | ✅ | existing sync/offline queue contract |

Split/merge surface: `POST /sales/split`, `POST /sales/merge`,
`GET /sale-groups/`, `GET /sale-groups/<group_key>/`. Splitting moves the
selected `SaleItem`s into child sales under a new `SaleGroup` and recomputes
totals; merging returns them to the parent and closes the group.

## Multi-terminal Sync (P1)

Real-time sync between POS terminals: every sync-tracked model (all models
with an `is_synced` flag) is flagged `pending` on change by `sync_signals`,
broadcast to connected terminals over the entities WebSocket, and pullable
via a changeset endpoint.

| Surface | Method | Purpose |
|---|---|---|
| `/sync/changes?entity_type=&limit=` | GET | Pull pending (unsynced) rows across all sync-tracked models |
| `/sync/changes?types=1` | GET | List sync-tracked entity types |
| `/sync/ack` | POST | Mark rows synced after a peer confirms (`{entity_type, ids}`) |
| `/sync/trigger` | POST | Broadcast a `sync_request` over WS so peers pull now |
| `/ws/entities` | WS | Real-time `entity_change` + `sync_request` events |

The collector is `services/sync_changes.SyncChangeCollector` (canonical
`(entity_type, model)` ordering parents-before-children so FKs resolve on
apply). `POST /sync/trigger` is the push half; peers pull on demand.

## Offline Queue (P1)

Transactions recorded while the cloud master is unreachable are durably
queued in the `OutboxQueue` and flushed (with exponential backoff and
dead-lettering) once connectivity returns.

| Surface | Method | Purpose |
|---|---|---|
| `/offline-queue/` | GET | Queue health (`pending/failed/dead/…`) + recent entries |
| `/offline-queue/enqueue` | POST | Queue an outbound op (`{entity_type, entity_id, action, payload, node_id}`) |
| `/offline-queue/flush` | POST | Attempt to push due entries now (backoff/dead-letter on failure) |
| `/offline-queue/requeue` | POST | Re-arm dead-lettered entries |

The service is `services.outbox.OfflineQueueService`; ``push_one`` POSTs to
`{cloud_url}/api/sync/push/<entity_type>` (URL from `sync_state.json` then
`CLOUD_CRM_URL`). Offline = empty URL → entries stay `failed` and retry with
backoff `2**retry_count` (capped at 1h); `max_retries` dead-letters them.

`BranchSyncScheduler` wires its failure path into the same queue: a scheduled
cloud push that returns `status=failed` (or raises) is auto-enqueued via
`_enqueue_failed_push` (products/sales/inventory, one pending/failed entry per
`(node, entity_type)` so the periodic loop doesn't flood the queue).

## Barcode Scanner (P1)

A hardware/device scanner emits a barcode string; the POS resolves it to a
product and can render a printable Code128 label for the same value.

| Surface | Method | Purpose |
|---|---|---|
| `/barcode/<value>` | GET | Resolve a scanned code to a product (exact `barcode` match, then `sku` fallback) |
| `/barcode/<value>/label` | GET | Render a Code128 SVG label (`image/svg+xml`) for shelf/item printing |

The resolver is `services/barcode.resolve_product`; label rendering uses
`services/barcode.barcode_label_svg` (``python-barcode`` is lazy-imported so
the server boots without the optional dependency — a missing package returns
501 instead of crashing).

## POS-KO Gaming Center (P0)

Token-based gaming sessions for gaming cafes / LAN centers. Scope per the
roadmap: **token purchase, start/pause/resume per station, queue management,
station status, session billing (duration × rate)**.

| Pillar | State | Implementation |
|---|---|---|
| Token purchase | ✅ | `GamingToken` (`minutes` / `remaining_minutes` balance) |
| Session tracking | ✅ | `GamingSession` start/pause/resume/stop with accumulated `active_seconds` |
| Queue management | ✅ | `GamingQueueEntry` waitlist + estimated wait + auto-assign |
| Station status | ✅ | `GamingStation` available/occupied/maintenance |
| Session billing | ✅ | `cost = ceil(active_seconds/60) / 60 × hourly_rate`; token decrement on stop |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/gaming.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `/gaming/stations` · `/gaming/stations/<pk>` | GET/POST | List / create stations; detail + active session |
| `/gaming/tokens` | GET/POST | List / purchase time tokens |
| `/gaming/sessions` | GET | List sessions (filter `?status=`) |
| `/gaming/sessions/start` · `/pause` · `/resume` · `/stop` | POST | Session lifecycle (stop computes cost + frees station + auto-assigns next) |
| `/gaming/queue` · `/queue/assign` · `/queue/cancel` | GET/POST | Waitlist management |

## Gift Cards (P2, Professional+)

Digital gift cards with a spendable balance and an immutable transaction
ledger.


| Pillar | State | Implementation |
|---|---|---|
| Issue with balance | ✅ | `GiftCard` + `services.giftcard.issue` (unique `GC-XXXX` codes) |
| Balance check | ✅ | `GET /gift-cards/<code>` (case-insensitive) |
| Redeem against a sale | ✅ | `services.giftcard.redeem` (atomic, `used` at zero, expiry/disabled guards) |
| Ledger | ✅ | `GiftCardTransaction` (issue/redeem/reload/void, signed amounts) |
| Reload / disable | ✅ | `services.giftcard.reload` / `disable` |

**Surface** (`views_django.py` + `configs/urls.py`): `GET/POST /gift-cards`,
`GET /gift-cards/<code>` (+ `/transactions`), `POST /gift-cards/{redeem,reload,disable}`.

## Table Management (P2, Professional+)

Restaurant floor layouts and order tracking. Scope per the roadmap: **table
layouts, order tracking, reservations**.

| Pillar | State | Implementation |
|---|---|---|
| Table layouts | ✅ | `RestaurantTable` (name/section/capacity/shape, floor-plan `pos_x`/`pos_y`/size, `status` free/occupied/reserved/cleaning/closed) |
| Order tracking | ✅ | `current_sale` FK + `occupy_table`/`clear_table` (seats the open sale, syncs the sale's `SaleGroup.table_number`, optional `close_sale`) |
| Floor summary | ✅ | `floor_summary()` — status/section/capacity counts + occupied/free totals |
| Reservations | ✅ | `TableReservation` lifecycle: create (free tables only) → seat (occupies the table) → complete; cancel / no-show branches |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/tables.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `/tables` · `/tables/floor` | GET/POST · GET | List / create tables; floor occupancy summary |
| `/tables/<pk>` | GET | Table detail + recent reservations |
| `/tables/<pk>/status` | POST | Transition status (`free`/`cleaning`/`closed`) with sale-integrity guards |
| `/tables/<pk>/occupy` · `/clear` | POST | Seat a sale at the table / free it (optionally closing the sale) |
| `/reservations` | GET/POST | List (filter `?status=`) / book a table |
| `/reservations/<pk>/<action>` | POST | `cancel` · `seat` · `complete` · `no-show` |

Migration `0013` (`full_restaurant_tables`, `full_table_reservations`).

## Delivery Integration (P2, Professional+)

Delivery platform connectors and outbound order tracking. Scope per the
roadmap: **Talabat / HungerStation connectors**.

| Pillar | State | Implementation |
|---|---|---|
| Provider registry | ✅ | `DeliveryProvider` (talabat/hungerstation/careem/manual, base URL, API key, commission rate) |
| Order dispatch | ✅ | `DeliveryOrder` — links the `Sale`, snapshots customer/subtotal/total, computes the fee from the `DeliveryZone` (base + per-km, out-of-zone rejected) |
| Status lifecycle | ✅ | pending → accepted → preparing → out_for_delivery → delivered; cancelled/failed branches with timestamp tracking and transition guards |
| Provider webhooks | ✅ | `POST /deliveries/webhook/<provider>` — status callbacks matched on `provider_order_id` (POS state wins on illegal transitions) |
| Delivery KPIs | ✅ | `delivery_stats()` — per-status counts, delivered revenue, fee totals |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/delivery.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `/deliveries` | GET/POST | List orders (filter `?status=`) / dispatch one |
| `/deliveries/<pk>` | GET | Delivery order detail |
| `/deliveries/<pk>/status` · `/cancel` | POST | Advance the lifecycle / cancel before delivery |
| `/deliveries/providers` | GET/POST | List / register platform connectors |
| `/deliveries/stats` | GET | Delivery KPIs |
| `/deliveries/webhook/<provider>` | POST | Provider status callback (matched on `order_id`) |

Migration `0014` (`full_delivery_providers`, `full_delivery_orders`).

## AI Forecasting (P2, Professional/SaaS)

Advisory demand / stock / waste / sales analytics — **read-only**. Per the
django-fusion LLM/MCP enhancement plan, AI output is advisory by default:
`services/forecast.py` never writes POS records (no prices, stock, or sync
authority changes); it only reads history and returns recommendations a
human or an approved MCP workflow can act on.

| Pillar | State | Implementation |
|---|---|---|
| Demand forecast | ✅ | `demand_forecast()` — per-product units/day (moving average over the lookback window) with a clamped trend factor (0.5×–2×) from the recent 7 days |
| Stock advisory | ✅ | `stock_advisory()` — days-of-cover + suggested reorder quantity when projected demand over lead time exceeds stock or the product is below its low-stock threshold |
| Waste analysis | ✅ | `waste_analysis()` — waste/disposal transactions with estimated cost (product `cost_price`); excludes non-waste movements |
| Sales insights | ✅ | `sales_insights()` — top movers, revenue growth vs the previous period, rising products (>50% unit growth), plain-language recommendations |
| Combined report | ✅ | `full_report()` — one advisory envelope for the dashboard |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/forecast.py`):

| Endpoint | Query params | Purpose |
|---|---|---|
| `GET /forecast/demand` | `days` (14), `lookback` (28) | Per-product demand projection |
| `GET /forecast/stock` | `days` (14), `lead_time_days` (3) | Reorder recommendations |
| `GET /forecast/waste` | `days` (30) | Waste aggregation + cost |
| `GET /forecast/insights` | `days` (30) | Movers, growth, recommendations |
| `GET /forecast/report` | `days` (14) | Combined advisory envelope |

No new models — the service computes purely from `Sale` / `SaleItem` /
`Product` / `InventoryTransaction`. A future LLM/MCP pass can consume the
same envelope for natural-language advisory without changing POS authority.

## Employee Scheduling (P3, Professional)

Shift planning and time tracking. Scope per the roadmap: **shift planning
and time tracking**. The repeating weekly plan lives in the existing
`EmployeeSchedule` model; the new `TimeClockEntry` records actual punches.

| Pillar | State | Implementation |
|---|---|---|
| Shift planning | ✅ | `upsert_shift()` — create/update one employee's shift per day of week (`EmployeeSchedule`); `week_schedule()` materializes the repeating plan into a concrete week's roster with planned hours |
| Coverage | ✅ | `coverage()` — staff count + planned hours per day of the week |
| Time tracking | ✅ | `TimeClockEntry` — `clock_in`/`clock_out`/`toggle_break` with a single-active-punch guard; `worked_minutes` subtracts breaks |
| Hours + payroll input | ✅ | `worked_hours()` — total/regular/overtime (beyond 8 h/day) + pay estimate at `hourly_rate` (×1.5 overtime) |
| Live roster | ✅ | `timeclock_summary()` — currently active staff + recent punches |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/scheduling.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `/scheduling/shifts` | GET/POST | List / create-or-update a weekly shift |
| `/scheduling/week` | GET | Concrete week roster (`?week_start=YYYY-MM-DD`) |
| `/scheduling/coverage` | GET | Staffing coverage (`?day_of_week=`) |
| `/scheduling/timeclock` | GET/POST | Recent punches + active staff / clock in |
| `/scheduling/timeclock/<action>` | POST | `out` (close punch) · `break` (toggle start/end) |
| `/scheduling/hours` | GET | Worked hours + overtime + pay estimate (`?employee_id=&start=&end=`) |

Migration `0015` (`full_timeclock_entries`).

## Customer Display (P3, Professional)

Read-only, customer-facing order-confirmation display fed by `Sale` /
`SaleItem` / `KitchenTicket`. Scope per the roadmap: **customer-facing
display for order confirmation**. Like AI Forecasting, this is advisory and
read-only — the service never writes POS records; it only reads history and
returns display envelopes.

| Pillar | State | Implementation |
|---|---|---|
| Order confirmation | ✅ | `order_display()` — one sale's envelope: order number, table, order type, items (qty/name/line totals), totals, kitchen-ticket status + ETA |
| Order context | ✅ | `order_context()` — table/order type resolved from the linked `SaleGroup` first, then the sale's JSON meta, then defaults |
| Ticket enrichment | ✅ | elapsed/remaining minutes, overdue detection (`pending`/`preparing` past `prepare_time_minutes`), station + status label |
| Active board | ✅ | `active_board()` — live orders (pending/preparing/ready) + recent delivered, per-status summary strip |
| Wall screen | ✅ | `frontend/src/pages/customer-display/index.astro` — read-only page polling the board every 5s; `?sale=<id>` focuses one confirmation |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/customer_display.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /customer-display/<sale_id>` | GET | One order's display envelope (order-confirmation screen) |
| `GET /customer-display/board` | GET | Active orders feed + summary (`?limit=` 1–50, default 20) |

No new models or migration — the service computes purely from `Sale` /
`SaleItem` / `KitchenTicket` (matching the AI Forecasting precedent).

## Self-checkout Kiosk (P3, Professional/SaaS)

Self-service kiosk mode. Scope per the roadmap: **self-service kiosk mode**.
A guest browses the catalog, builds a cart on a `KioskSession`, and checks
out — and checkout **reuses the canonical `sale_checkout` surface** (the same
atomic Sale + SaleItem + KitchenTicket + stock-deduction path the cashier
screen uses), so the kiosk never reimplements sale creation.

| Pillar | State | Implementation |
|---|---|---|
| Catalog feed | ✅ | `catalog()` — active products grouped by category (`?category=<slug>` filter), each with price/stock availability for tile disabling |
| Session lifecycle | ✅ | `KioskSession` — `start_session` (reuses open keys, reopens closed), `cancel_session`, `kiosk_stats` |
| Cart ops | ✅ | `KioskCartItem` + `add_item`/`set_quantity`/`remove_item`/`clear_cart` with stock + availability guards |
| Totals | ✅ | `cart_summary()` — subtotal + 8% tax + total from unit prices |
| Checkout reuse | ✅ | `checkout()` — builds the exact `POST /sales/` payload and forwards through `sale_checkout`; on success links the sale + closes the session |
| Touchscreen UI | ✅ | `frontend/src/pages/kiosk/index.astro` — catalog grid + category rail, sticky cart with qty steppers, Pay button, order-complete state |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/kiosk.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /kiosk/catalog` | GET | Active products grouped by category (`?category=`) |
| `GET/POST /kiosk/sessions` | GET/POST | List sessions / start a new one |
| `GET /kiosk/sessions/<key>` | GET | Session detail + cart summary |
| `POST /kiosk/sessions/<key>/cart` | POST | Add a product to the cart |
| `PATCH/DELETE /kiosk/sessions/<key>/cart/<product_id>` | PATCH/DELETE | Set quantity (0 removes) / remove a line |
| `POST /kiosk/sessions/<key>/cart/clear` | POST | Empty the cart |
| `POST /kiosk/sessions/<key>/checkout` | POST | Check out through `sale_checkout` (sale linked, session closed) |
| `POST /kiosk/sessions/<key>/cancel` | POST | Abandon the session |
| `GET /kiosk/stats` | GET | Open/checked-out/cancelled counts + total sales |

Migration `0016` (`full_kiosk_sessions`, `full_kiosk_cart_items`).

## Inventory Forecasting (P3, Professional/SaaS)

Reorder-point planning and auto-reorder — the roadmap's final P3 feature and
a superset of the AI Forecasting stock advisory. Adds the operational layer
on top of ``stock_advisory`` while keeping the planning read-only:

| Pillar | State | Implementation |
|---|---|---|
| Reorder point | ✅ | `inventory_plan()` — per product: lead-time demand, safety stock (lead × `safety_factor`), reorder point (lead + safety), days of cover, projected stock-out date |
| Needs-reorder flags | ✅ | `needs_reorder` + reason (`out of stock` / `below low-stock threshold` / `at/below reorder point`), sorted by urgency |
| Suggested quantities | ✅ | `suggested_order_quantity` — restores stock to reorder point + one lead window |
| Draft purchase orders | ✅ | `generate_reorder_orders()` — explicit operator action materializing the plan into `PurchaseOrder` drafts (`RF-YYYYMMDD-###`, cost from product, no stock movement) |
| Advisory guard | ✅ | planning endpoints stay read-only; only the explicit `POST …/reorder` writes (and only drafts) |

**Surface** (`views_django.py` + `configs/urls.py`; service additions in `services/forecast.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /forecast/inventory` | GET | Reorder-point / safety-stock / stock-out plan (`?days=14`, `?lead_time_days=3`, `?safety_factor=0.5`) |
| `POST /forecast/inventory/reorder` | POST | Create draft purchase orders from the plan (`{supplier_id}` optional — falls back to first active supplier) |

No new models or migration — drafts reuse the existing `PurchaseOrder` /
`PurchaseOrderItem` models.

## Purchase Order Workflow (Reorder Workflow follow-up)

Completes the procurement loop that Inventory Forecasting starts: drafts are
ordered, received (stock-in), or cancelled, with reorder alerts driven by the
same forecast plan.

| Pillar | State | Implementation |
|---|---|---|
| Draft creation | ✅ | `create_purchase_order()` — manual draft PO (supplier + lines; cost defaults to `cost_price`, `PO-YYYYMMDD-###` reference) |
| Lifecycle | ✅ | `mark_ordered` (draft → ordered) · `cancel_purchase_order` (draft/ordered → cancelled) with transition guards |
| Receive → stock-in | ✅ | `receive_purchase_order()` — creates `in` `InventoryTransaction` rows, bumps product stock + `received_quantity`, recomputes total; supports partial receipt (defaults to remaining balance) and rejects over-receipt |
| Reorder alerts | ✅ | `reorder_alerts()` — products at/below reorder point (reuses the forecast plan) + open PO drafts surfaced |
| Stats | ✅ | `purchase_order_stats()` — counts by status + outstanding (`ordered`) value |

**Surface** (`views_django.py` + `configs/urls.py`; service `services/purchase_orders.py`):

| Endpoint | Method | Purpose |
|---|---|---|
| `GET/POST /purchase-orders` | GET/POST | List (filter `?status=`) / create a draft |
| `GET /purchase-orders/<pk>` | GET | Detail with line items |
| `POST /purchase-orders/<pk>/order` | POST | Mark a draft as ordered |
| `POST /purchase-orders/<pk>/receive` | POST | Receive → stock-in (`{quantities: {product_id: qty}}` for partial) |
| `POST /purchase-orders/<pk>/cancel` | POST | Cancel a draft/ordered PO |
| `GET /purchase-orders/alerts` | GET | Reorder alerts + open drafts |
| `GET /purchase-orders/stats` | GET | Status counts + outstanding value |

No new models or migration — reuses `PurchaseOrder` / `PurchaseOrderItem` /
`InventoryTransaction`.

## Next phases / follow-ups

Candidate follow-up work, not yet started. Each is additive and follows the
same Django service + `/…/*` surface + migration + test pattern above:

- **Customer Display media** — swap the board/confirmation screens to brand
  assets and add QR links from table cards to the per-sale confirmation.
- **Kiosk extras** — kiosk payment terminal hook (card reader callback),
  per-kiosk catalog subsets, and a `sale_checkout` refactor into a shared
  service so kiosk + cashier share one checkout core.
- **Procurement scheduling** — supplier reorder schedules and email/notification
  alerts when products cross their reorder point (the alert feed exists at
  `GET /purchase-orders/alerts`; delivery is a follow-up).
- **LLM/MCP enrichment** — feed `GET /forecast/report` into the django-fusion
  LLM/MCP plan for natural-language advisory; stays read-only.

## Remaining work

- [ ] Pro `make check` — BLOCKED: `server/.venv/bin/python3` is absent in this checkout (validated here via the cloud backend venv).
- [ ] Pro `make test` — BLOCKED: same missing local Python environment.

After the repository owner provisions the existing Pro environment, run:

```bash
cd projects/formints/formint-pro
make check
make test
```

External publishing, release tags, and git commits remain owner actions.
