"""
POS Full — Django URL Configuration (post-Robyn migration).

Comprehensive URLconf wiring all Django views, django-bolt API, NinjaExtra
API (/api/v1/), Django admin (Unfold), and static files into one router.

Route summary:
  * /admin/                    — Unfold Django admin
  * /bolt/                     — django-bolt high-performance CRUD API
  * /api/v1/                   — NinjaExtra + django-fusion contract
  * /, /health, /stats          — server info
  * /kds/*, /htmx/*, /fusion/* — KDS, HTMX fragments, fusion renders
  * /nodes/*, /events           — node registry CRUD
  * /sync/*, /sales/*           — sync + sales operations
  * /api-keys/*                 — scoped API key management
  * /transactions, /analytics   — data aggregation
  * /crm/*, /reports/*          — CRM + reports
  * /approvals/*, /webhooks/*   — approvals + webhooks
  * /config/*                   — device/master config
  * ws/nodes, ws/entities, ws/config — Django Channels WebSocket
"""

import importlib.util
from django.contrib import admin
from django.urls import include, path

from formint.export_views import export_resource

urlpatterns = [
    # ── Django admin (Unfold-themed) ──
    path("admin/", admin.site.urls),

    # ── Formint app (fusion render-mode contract, session-mode, etc.) ──
    path("", include("formint.urls")),
    # Read-only CSV/JSON exports shared with Standard clients.
    path("export/<str:resource>.<str:file_format>", export_resource, name="formint-export"),

    # ── django-bolt (high-performance API) ──
]
# Mount the POS Full django-bolt API when the real django-bolt runtime is
# installed. ``bolt_api`` raises ImportError on the stub package, so this
# stays optional and never breaks the Django-only stack.
try:
    from bolt_api import bolt  # noqa: F401
    if bolt is not None and getattr(bolt, "urls", None) is not None:
        urlpatterns.append(path("bolt/", bolt.urls))
except ImportError:
    bolt = None
if importlib.util.find_spec("django_bolt.urls"):
    urlpatterns.append(path("", include("django_bolt.urls")))

# ── All migrated Robyn routes → Django views ──
from views_django import (
    index, health, stats_endpoint,
    kds_list_tickets, kds_get_ticket, kds_update_ticket,
    kds_get_sale_items, kds_stats,
    kds_list_stations, kds_create_station,
    menu_list_published, menu_publish, menu_preview, menu_qr, menu_public,
    node_list, node_detail, node_register, node_heartbeat,
    node_update, node_delete,
    node_get_config, node_set_config, node_delete_config, node_history,
    list_events,
    sale_cashback, sale_return, create_sale_with_items, sale_checkout,
    sale_split, sale_merge, sale_group_list, sale_group_detail,
    sync_status, sync_config, sync_log, sync_trigger,
    sync_changes, sync_ack,
    offline_queue_list, offline_queue_enqueue, offline_queue_flush, offline_queue_requeue,
    barcode_resolve, barcode_label,
    gaming_stations, gaming_station_detail,
    gaming_tokens, gaming_sessions,
    gaming_session_start, gaming_session_pause, gaming_session_resume, gaming_session_stop,
    gaming_queue, gaming_queue_assign, gaming_queue_cancel,
    gift_cards, gift_card_detail, gift_card_transactions,
    gift_card_redeem, gift_card_reload, gift_card_disable,
    tables, table_detail, table_status, table_occupy, table_clear, tables_floor,
    reservations, reservation_action,
    delivery_providers, deliveries, delivery_detail,
    delivery_status, delivery_cancel, delivery_stats, delivery_webhook,
    forecast_demand, forecast_stock, forecast_waste,
    forecast_insights, forecast_report,
    forecast_inventory, forecast_reorder_orders,
    scheduling_shifts, scheduling_week, scheduling_coverage,
    scheduling_timeclock, scheduling_timeclock_action, scheduling_hours,
    customer_display_board, customer_display_order,
    kiosk_catalog, kiosk_sessions, kiosk_session_detail,
    kiosk_cart, kiosk_cart_line, kiosk_cart_clear,
    kiosk_checkout, kiosk_session_cancel, kiosk_stats,
    purchase_orders, purchase_order_detail, purchase_order_action,
    purchase_order_alerts, purchase_order_stats,
    cloud_push, receive_push,
    list_transactions, get_transaction_detail, get_analytics,
    approval_approve, approval_reject, approval_stats, approval_pending,
    webhook_receive, webhook_list, webhook_stats,
    config_cloud_link_test, config_master_sync,
    crm_dashboard, crm_contacts, crm_contact_detail, crm_contact_create,
    crm_companies, crm_company_detail, crm_deals, crm_deal_create,
    crm_deal_detail, crm_pipelines, crm_activities, crm_activity_detail,
    crm_notes, crm_note_detail,
    report_sales, report_inventory,
    list_coupons, list_delivery_types, list_delivery_zones, list_shifts,
    create_shift, shift_detail,
)

from htmx_views import (
    htmx_products, htmx_product_delete,
    htmx_customers, htmx_customer_delete,
    htmx_inventory, htmx_inventory_delete,
    htmx_sales, htmx_sale_delete,
)

from api_keys_views import (
    list_api_keys, create_api_key, known_scopes,
    revoke_api_key, rotate_api_key,
)

from fusion_views import (
    fusion_render_dashboard, fusion_render_suppliers, fusion_render_about,
)

from fusion_dual_views import (
    fusion_forecast_demand, fusion_forecast_stock, fusion_forecast_inventory,
    fusion_customer_board, fusion_customer_order,
    fusion_kiosk_catalog, fusion_kiosk_stats,
    fusion_purchase_alerts, fusion_purchase_stats,
    fusion_tables_floor, fusion_delivery_stats, fusion_gift_cards,
)

urlpatterns += [
    # Info
    path("", index, name="index"),
    path("health", health, name="health"),
    path("stats", stats_endpoint, name="stats"),

    # KDS
    path("kds/tickets/", kds_list_tickets, name="kds-list"),
    path("kds/tickets/<int:pk>", kds_get_ticket, name="kds-detail"),
    path("kds/tickets/<int:pk>/update", kds_update_ticket, name="kds-update"),
    path("kds/items/<int:sale_id>", kds_get_sale_items, name="kds-items"),
    path("kds/stats/", kds_stats, name="kds-stats"),
    path("kds/stations/", kds_list_stations, name="kds-stations"),
    path("kds/stations/create", kds_create_station, name="kds-station-create"),

    # QR Menu
    path("menu/published/", menu_list_published, name="menu-published"),
    path("menu/<int:menu_id>/publish", menu_publish, name="menu-publish"),
    path("menu/<int:menu_id>/preview", menu_preview, name="menu-preview"),
    path("menu/<slug:slug>/", menu_public, name="menu-public"),
    path("menu/<slug:slug>/qr", menu_qr, name="menu-qr"),

    # HTMX fragments
    path("htmx/products/", htmx_products, name="htmx-products"),
    path("htmx/products/<int:product_id>/", htmx_product_delete, name="htmx-product-delete"),
    path("htmx/customers/", htmx_customers, name="htmx-customers"),
    path("htmx/customers/<int:customer_id>/", htmx_customer_delete, name="htmx-customer-delete"),
    path("htmx/inventory/", htmx_inventory, name="htmx-inventory"),
    path("htmx/inventory/<int:tx_id>/", htmx_inventory_delete, name="htmx-inventory-delete"),
    path("htmx/sales/", htmx_sales, name="htmx-sales"),
    path("htmx/sales/<int:sale_id>/", htmx_sale_delete, name="htmx-sale-delete"),

    # Fusion fragment renders
    path("fusion/render/dashboard", fusion_render_dashboard, name="fusion-dashboard"),
    path("fusion/render/suppliers", fusion_render_suppliers, name="fusion-suppliers"),
    path("fusion/render/about", fusion_render_about, name="fusion-about"),

    # Fusion dual-mode views (component HTML or data API via fusion_view)
    path("fusion/views/forecast/demand", fusion_forecast_demand, name="fusion-view-forecast-demand"),
    path("fusion/views/forecast/stock", fusion_forecast_stock, name="fusion-view-forecast-stock"),
    path("fusion/views/forecast/inventory", fusion_forecast_inventory, name="fusion-view-forecast-inventory"),
    path("fusion/views/customer-display/board", fusion_customer_board, name="fusion-view-customer-board"),
    path("fusion/views/customer-display/<int:sale_id>", fusion_customer_order, name="fusion-view-customer-order"),
    path("fusion/views/kiosk/catalog", fusion_kiosk_catalog, name="fusion-view-kiosk-catalog"),
    path("fusion/views/kiosk/stats", fusion_kiosk_stats, name="fusion-view-kiosk-stats"),
    path("fusion/views/purchase-orders/alerts", fusion_purchase_alerts, name="fusion-view-purchase-alerts"),
    path("fusion/views/purchase-orders/stats", fusion_purchase_stats, name="fusion-view-purchase-stats"),
    path("fusion/views/tables/floor", fusion_tables_floor, name="fusion-view-tables-floor"),
    path("fusion/views/deliveries/stats", fusion_delivery_stats, name="fusion-view-delivery-stats"),
    path("fusion/views/gift-cards", fusion_gift_cards, name="fusion-view-gift-cards"),

    # API Keys
    path("api-keys/scopes", known_scopes, name="apikeys-scopes"),
    path("api-keys/<int:key_id>/revoke", revoke_api_key, name="apikeys-revoke"),
    path("api-keys/<int:key_id>/rotate", rotate_api_key, name="apikeys-rotate"),
    path("api-keys/", list_api_keys, name="apikeys-list"),
    path("api-keys/create", create_api_key, name="apikeys-create"),

    # Nodes (specific paths before wildcards)
    path("nodes/register", node_register, name="nodes-register"),
    path("nodes/heartbeat", node_heartbeat, name="nodes-heartbeat"),
    path("nodes/<str:node_id>/config/<str:config_key>/delete", node_delete_config, name="nodes-config-delete"),
    path("nodes/<str:node_id>/config/set", node_set_config, name="nodes-config-set"),
    path("nodes/<str:node_id>/config", node_get_config, name="nodes-config-get"),
    path("nodes/<str:node_id>/update", node_update, name="nodes-update"),
    path("nodes/<str:node_id>/delete", node_delete, name="nodes-delete"),
    path("nodes/<str:node_id>/history", node_history, name="nodes-history"),
    path("nodes/<str:node_id>", node_detail, name="nodes-detail"),
    path("nodes", node_list, name="nodes-list"),
    path("events", list_events, name="events-list"),

    # Sync & Sales ops
    path("sales/<int:pk>/cashback", sale_cashback, name="sale-cashback"),
    path("sales/<int:pk>/return", sale_return, name="sale-return"),
    path("sales/", sale_checkout, name="sale-checkout"),
    path("sales/with-items", create_sale_with_items, name="sale-with-items"),
    path("sales/split", sale_split, name="sale-split"),
    path("sales/merge", sale_merge, name="sale-merge"),
    path("sale-groups/", sale_group_list, name="sale-groups-list"),
    path("sale-groups/<str:group_key>/", sale_group_detail, name="sale-groups-detail"),
    path("sync/status", sync_status, name="sync-status"),
    path("sync/config", sync_config, name="sync-config"),
    path("sync/log", sync_log, name="sync-log"),
    path("sync/changes", sync_changes, name="sync-changes"),
    path("sync/ack", sync_ack, name="sync-ack"),
    path("sync/trigger", sync_trigger, name="sync-trigger"),
    path("offline-queue/", offline_queue_list, name="offline-queue-list"),
    path("offline-queue/enqueue", offline_queue_enqueue, name="offline-queue-enqueue"),
    path("offline-queue/flush", offline_queue_flush, name="offline-queue-flush"),
    path("offline-queue/requeue", offline_queue_requeue, name="offline-queue-requeue"),

    # Barcode Scanner
    path("barcode/<str:value>/label", barcode_label, name="barcode-label"),
    path("barcode/<str:value>", barcode_resolve, name="barcode-resolve"),

    # POS-KO Gaming Center
    path("gaming/stations", gaming_stations, name="gaming-stations"),
    path("gaming/stations/<int:pk>", gaming_station_detail, name="gaming-station-detail"),
    path("gaming/tokens", gaming_tokens, name="gaming-tokens"),
    path("gaming/sessions", gaming_sessions, name="gaming-sessions"),
    path("gaming/sessions/start", gaming_session_start, name="gaming-session-start"),
    path("gaming/sessions/pause", gaming_session_pause, name="gaming-session-pause"),
    path("gaming/sessions/resume", gaming_session_resume, name="gaming-session-resume"),
    path("gaming/sessions/stop", gaming_session_stop, name="gaming-session-stop"),
    path("gaming/queue", gaming_queue, name="gaming-queue"),
    path("gaming/queue/assign", gaming_queue_assign, name="gaming-queue-assign"),
    path("gaming/queue/cancel", gaming_queue_cancel, name="gaming-queue-cancel"),

    # Gift Cards
    path("gift-cards", gift_cards, name="gift-cards"),
    path("gift-cards/redeem", gift_card_redeem, name="gift-card-redeem"),
    path("gift-cards/reload", gift_card_reload, name="gift-card-reload"),
    path("gift-cards/disable", gift_card_disable, name="gift-card-disable"),
    path("gift-cards/<str:code>/transactions", gift_card_transactions, name="gift-card-transactions"),
    path("gift-cards/<str:code>", gift_card_detail, name="gift-card-detail"),

    # Table Management
    path("tables/floor", tables_floor, name="tables-floor"),
    path("tables", tables, name="tables-list"),
    path("tables/<int:pk>/status", table_status, name="table-status"),
    path("tables/<int:pk>/occupy", table_occupy, name="table-occupy"),
    path("tables/<int:pk>/clear", table_clear, name="table-clear"),
    path("tables/<int:pk>", table_detail, name="table-detail"),
    path("reservations/<int:pk>/<str:action>", reservation_action, name="reservation-action"),
    path("reservations", reservations, name="reservations-list"),

    # Delivery Integration
    path("deliveries/stats", delivery_stats, name="deliveries-stats"),
    path("deliveries/providers", delivery_providers, name="deliveries-providers"),
    path("deliveries/webhook/<str:provider>", delivery_webhook, name="deliveries-webhook"),
    path("deliveries/<int:pk>/status", delivery_status, name="delivery-status"),
    path("deliveries/<int:pk>/cancel", delivery_cancel, name="delivery-cancel"),
    path("deliveries/<int:pk>", delivery_detail, name="delivery-detail"),
    path("deliveries", deliveries, name="deliveries-list"),

    # AI Forecasting (advisory)
    path("forecast/demand", forecast_demand, name="forecast-demand"),
    path("forecast/stock", forecast_stock, name="forecast-stock"),
    path("forecast/waste", forecast_waste, name="forecast-waste"),
    path("forecast/insights", forecast_insights, name="forecast-insights"),
    path("forecast/report", forecast_report, name="forecast-report"),
    path("forecast/inventory", forecast_inventory, name="forecast-inventory"),
    path("forecast/inventory/reorder", forecast_reorder_orders, name="forecast-inventory-reorder"),

    # Employee Scheduling
    path("scheduling/shifts", scheduling_shifts, name="scheduling-shifts"),
    path("scheduling/week", scheduling_week, name="scheduling-week"),
    path("scheduling/coverage", scheduling_coverage, name="scheduling-coverage"),
    path("scheduling/timeclock/<str:action>", scheduling_timeclock_action, name="scheduling-timeclock-action"),
    path("scheduling/timeclock", scheduling_timeclock, name="scheduling-timeclock"),
    path("scheduling/hours", scheduling_hours, name="scheduling-hours"),

    path("cloud/push/<str:entity_type>", cloud_push, name="cloud-push"),
    path("api/sync/push/<str:entity_type>", receive_push, name="api-sync-push"),

    # Data / Analytics
    path("transactions", list_transactions, name="transactions-list"),
    path("transactions/<int:pk>", get_transaction_detail, name="transactions-detail"),
    path("analytics", get_analytics, name="analytics"),

    # Approvals
    path("approvals/<int:pk>/approve", approval_approve, name="approval-approve"),
    path("approvals/<int:pk>/reject", approval_reject, name="approval-reject"),
    path("approvals/stats", approval_stats, name="approval-stats"),
    path("approvals/pending", approval_pending, name="approval-pending"),

    # Webhooks
    path("webhooks/receive/<str:signal_name>", webhook_receive, name="webhook-receive"),
    path("webhooks/receive", webhook_list, name="webhook-list"),
    path("webhooks/receive/stats", webhook_stats, name="webhook-stats"),

    # Config
    path("config/cloud-links/<int:pk>/test", config_cloud_link_test, name="config-cloud-link-test"),
    path("config/master/<int:pk>/sync", config_master_sync, name="config-master-sync"),

    # CRM
    path("crm/dashboard", crm_dashboard, name="crm-dashboard"),
    path("crm/contacts", crm_contacts, name="crm-contacts"),
    path("crm/contacts/<int:contact_id>", crm_contact_detail, name="crm-contact-detail"),
    path("crm/companies", crm_companies, name="crm-companies"),
    path("crm/companies/<int:company_id>", crm_company_detail, name="crm-company-detail"),
    path("crm/deals", crm_deals, name="crm-deals"),
    path("crm/deals/<int:deal_id>", crm_deal_detail, name="crm-deal-detail"),
    path("crm/pipelines", crm_pipelines, name="crm-pipelines"),
    path("crm/activities", crm_activities, name="crm-activities"),
    path("crm/activities/<int:activity_id>", crm_activity_detail, name="crm-activity-detail"),
    path("crm/notes", crm_notes, name="crm-notes"),
    path("crm/notes/<int:note_id>", crm_note_detail, name="crm-note-detail"),

    # Reports
    path("reports/sales", report_sales, name="report-sales"),
    path("reports/inventory", report_inventory, name="report-inventory"),

    # forge-gaps (coupons, delivery, shifts)
    path("coupons/", list_coupons, name="coupons-list"),
    path("delivery-types/", list_delivery_types, name="delivery-types-list"),
    path("delivery-zones/", list_delivery_zones, name="delivery-zones-list"),
    path("shifts/", list_shifts, name="shifts-list"),
    path("shifts/<int:shift_id>", shift_detail, name="shifts-detail"),

    # ── Module-prefixed aliases (Operations: /ops/*) ─────────────────
    path("ops/coupons/", list_coupons, name="ops-coupons-list"),
    path("ops/delivery-types/", list_delivery_types, name="ops-delivery-types-list"),
    path("ops/delivery-zones/", list_delivery_zones, name="ops-delivery-zones-list"),
    path("ops/shifts/", list_shifts, name="ops-shifts-list"),
    path("ops/shifts/<int:shift_id>", shift_detail, name="ops-shifts-detail"),
    path("ops/sync/status", sync_status, name="ops-sync-status"),
    path("ops/sync/config", sync_config, name="ops-sync-config"),
    path("ops/sync/log", sync_log, name="ops-sync-log"),
    path("ops/sync/trigger", sync_trigger, name="ops-sync-trigger"),
    path("ops/nodes", node_list, name="ops-nodes-list"),
    path("ops/nodes/<str:node_id>", node_detail, name="ops-nodes-detail"),
    path("ops/nodes/register", node_register, name="ops-nodes-register"),
    path("ops/nodes/heartbeat", node_heartbeat, name="ops-nodes-heartbeat"),

    # Customer Display (P3)
    path("customer-display/board", customer_display_board, name="customer-display-board"),
    path("customer-display/<int:sale_id>", customer_display_order, name="customer-display-order"),

    # Self-checkout Kiosk (P3)
    path("kiosk/catalog", kiosk_catalog, name="kiosk-catalog"),
    path("kiosk/stats", kiosk_stats, name="kiosk-stats"),
    path("kiosk/sessions", kiosk_sessions, name="kiosk-sessions"),
    path("kiosk/sessions/<str:session_key>", kiosk_session_detail, name="kiosk-session-detail"),
    path("kiosk/sessions/<str:session_key>/cart", kiosk_cart, name="kiosk-cart"),
    path("kiosk/sessions/<str:session_key>/cart/clear", kiosk_cart_clear, name="kiosk-cart-clear"),
    path("kiosk/sessions/<str:session_key>/cart/<int:product_id>", kiosk_cart_line, name="kiosk-cart-line"),
    path("kiosk/sessions/<str:session_key>/checkout", kiosk_checkout, name="kiosk-checkout"),
    path("kiosk/sessions/<str:session_key>/cancel", kiosk_session_cancel, name="kiosk-session-cancel"),

    # Purchase Order workflow (Reorder Workflow follow-up)
    path("purchase-orders", purchase_orders, name="purchase-orders"),
    path("purchase-orders/stats", purchase_order_stats, name="purchase-orders-stats"),
    path("purchase-orders/alerts", purchase_order_alerts, name="purchase-orders-alerts"),
    path("purchase-orders/<int:pk>", purchase_order_detail, name="purchase-order-detail"),
    path("purchase-orders/<int:pk>/<str:action>", purchase_order_action, name="purchase-order-action"),
]



