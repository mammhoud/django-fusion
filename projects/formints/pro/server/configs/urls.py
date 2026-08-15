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
    sync_status, sync_config, sync_log, sync_trigger,
    cloud_push, receive_push,
    list_transactions, get_transaction_detail, get_analytics,
    approval_approve, approval_reject, approval_stats, approval_pending,
    webhook_receive, webhook_list, webhook_stats,
    config_cloud_link_test, config_master_sync,
    crm_dashboard, crm_contacts, crm_contact_detail, crm_contact_create,
    crm_companies, crm_deals, crm_deal_create, crm_pipelines,
    crm_activities, crm_notes,
    report_sales, report_inventory,
    list_coupons, list_delivery_types, list_delivery_zones, list_shifts,
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
    path("sync/status", sync_status, name="sync-status"),
    path("sync/config", sync_config, name="sync-config"),
    path("sync/log", sync_log, name="sync-log"),
    path("sync/trigger", sync_trigger, name="sync-trigger"),
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
    path("crm/deals", crm_deals, name="crm-deals"),
    path("crm/pipelines", crm_pipelines, name="crm-pipelines"),
    path("crm/activities", crm_activities, name="crm-activities"),
    path("crm/notes", crm_notes, name="crm-notes"),

    # Reports
    path("reports/sales", report_sales, name="report-sales"),
    path("reports/inventory", report_inventory, name="report-inventory"),

    # forge-gaps (coupons, delivery, shifts)
    path("coupons/", list_coupons, name="coupons-list"),
    path("delivery-types/", list_delivery_types, name="delivery-types-list"),
    path("delivery-zones/", list_delivery_zones, name="delivery-zones-list"),
    path("shifts/", list_shifts, name="shifts-list"),

    # ── Module-prefixed aliases (Operations: /ops/*) ─────────────────
    path("ops/coupons/", list_coupons, name="ops-coupons-list"),
    path("ops/delivery-types/", list_delivery_types, name="ops-delivery-types-list"),
    path("ops/delivery-zones/", list_delivery_zones, name="ops-delivery-zones-list"),
    path("ops/shifts/", list_shifts, name="ops-shifts-list"),
    path("ops/sync/status", sync_status, name="ops-sync-status"),
    path("ops/sync/config", sync_config, name="ops-sync-config"),
    path("ops/sync/log", sync_log, name="ops-sync-log"),
    path("ops/sync/trigger", sync_trigger, name="ops-sync-trigger"),
    path("ops/nodes", node_list, name="ops-nodes-list"),
    path("ops/nodes/<str:node_id>", node_detail, name="ops-nodes-detail"),
    path("ops/nodes/register", node_register, name="ops-nodes-register"),
    path("ops/nodes/heartbeat", node_heartbeat, name="ops-nodes-heartbeat"),
]
