# pos-client Edition — Design, Architecture & Implementation Plan

> Tags: `#formints` `#pos` `#client` `#vue` `#tauri` `#shop` `#django` — status 🔵 dev (21 Aug 2026).

> **Status (21 Aug 2026): 🔵 DEV.** The shop API contract suite
> (`backend/tests/test_orders_api.py` + `test_shop_api.py`) and the My Orders
> fragment (`my_orders_fragment`) are implemented and verified, but the edition
> is still in **active development** — the full client flows and the browser
> E2E suite remain before it can be marked done. The canonical directory is
> **`projects/formints/formint-client/`**.
>
> **Architecture:** Vue 3 + Pinia desktop client (`src/` + `src-tauri/`,
> Rust/Diesel), a plain-Django shop backend (`backend/`), and an Astro
> storefront (`frontend/`) over django-fusion.

## Verified so far (code-backed)

- **Shop API contract suite** — `backend/tests/test_orders_api.py` +
  `backend/tests/test_shop_api.py`: catalog, auth status, cart-count fragment
  (D1) plus orders/checkout/promo/editorial flows.
- **My Orders fragment** — `my_orders_fragment` HTMX fragment
  (`backend/shop/views.py` + `backend/shop/urls.py`, route
  `shop/fragments/my-orders/`) mirroring `products_fragment`; HTMX-gated with
  anonymous empty state.
- **Vue 3 + Pinia shell** — dashboard/menu/orders/settings views, i18n
  (en/zh-CN), themes, custom title bar, Tauri store/fs/opener/log plugins.
- **Django shop backend apps** — `shop`, `employee`, `cms` under `backend/`.

## Remaining work (dev → done)

- [ ] Complete the full client cart/checkout UI flows end-to-end against the
  shop backend (browser-level, not just API contracts).
- [ ] Browser/E2E suite for the Vue client (`frontends.spec.ts` on :1433).
- [ ] Close any gaps surfaced by the feature-inheritance parity sweep.
- [ ] Release packaging, signing, and publishing remain operator actions.
