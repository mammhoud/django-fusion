# Pro Edition — Local Completion Record

**Canonical product:** `projects/formints/pro/`
**Legacy aliases:** `pos-full`, `pos-solo`, and `formint/` are compatibility names only.

**Status:** Local work complete (Standard-parity `Currency`/`TaxProfile` models
+ migration + Ninja CRUD, read-only CSV/JSON export, regression tests, scoped
API-key enforcement, the Kitchen Display System station-routing pillar, the
QR Menu versioning/publish core, and the Loyalty reversal + consent fields).
Only environment/operator-gated items remain.

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

**Station routing surface** (served by both the Robyn `routes/kds.py` and the
Django `views_django.py`):

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

## Remaining work

- [ ] Pro `make check` — BLOCKED: `server/.venv/bin/python3` is absent in this checkout.
- [ ] Pro `make test` — BLOCKED: same missing local Python environment.

After the repository owner provisions the existing Pro environment, run:

```bash
cd projects/formints/pro
make check
make test
```

External publishing, release tags, and git commits remain owner actions.
