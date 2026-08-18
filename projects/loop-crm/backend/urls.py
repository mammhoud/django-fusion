"""Loop-CRM URL configuration.

The browser road is owned by the django-fusion Application registry. The
versioned JSON road remains explicit and domain-scoped under ``/api/v1/``.
Wagtail owns the /cms/ editor surface and a trailing preview-only catch-all;
public URLs stay on the Astro frontend.
"""
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images import urls as wagtailimages_urls

from apps.core import views as core_views
from apps.core.api import reports_api as core_views_reports
from apps.core.api import resource_api
from apps.core.bolt_api import bolt
from apps.core.fusion import loop_crm_module
from apps.core.realtime import workspace_events_sse
from apps.crm import views as crm_views
from apps.finance import views as finance_views
from apps.marketing import views as marketing_views
from apps.pages import api as pages_api

urlpatterns = [
    path("admin/", admin.site.urls),
    # Wagtail editor surface — /cms/ (admin) + /documents/ + /images/.
    # Django admin stays at /admin/ (no prefix collision).
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("images/", include(wagtailimages_urls)),
    path("accounts/", include("allauth.urls")),
    loop_crm_module.url_pattern,
    path("fragments/navigation/", core_views.navigation_fragment, name="navigation_fragment"),
    path("fragments/workflows/create/", core_views.workflow_create, name="workflow_create"),
    path("fragments/workflows/<int:pk>/toggle/", core_views.workflow_toggle, name="workflow_toggle"),
    path("fragments/workflows/<int:pk>/run/", core_views.workflow_run, name="workflow_run"),
    path("fragments/workflows/<int:pk>/steps/", core_views.workflow_steps_update, name="workflow_steps_update"),
    path("fragments/workflows/<int:pk>/graph/", core_views.workflow_graph_update, name="workflow_graph_update"),
    path("fragments/posts/create/", marketing_views.post_create, name="post_create"),
    path("fragments/crm/companies/create/", crm_views.company_create, name="company_create"),
    path("fragments/crm/contacts/create/", crm_views.contact_create, name="contact_create"),
    path("fragments/crm/deals/create/", crm_views.deal_create, name="deal_create"),
    path("fragments/finance/invoices/create/", finance_views.invoice_create, name="invoice_create"),
    path("fragments/finance/payments/create/", finance_views.payment_create, name="payment_create"),
    path("fragments/posts/<int:pk>/transition/", marketing_views.post_transition, name="post_transition"),
    path("fragments/marketing/channels/connect/", marketing_views.channel_connect, name="channel_connect"),
    path("fragments/marketing/channels/<int:pk>/disconnect/", marketing_views.channel_disconnect, name="channel_disconnect"),
    path("fragments/marketing/channels/<int:pk>/refresh/", marketing_views.channel_refresh, name="channel_refresh"),
    # Report catalog for the webapp /reports/ surface.
    path("apis/reports/", core_views_reports, name="reports_api"),
    # ── Public landing road — Wagtail-managed pages for the Astro frontend.
    # Astro fetches /apis/pages/<slug>/ and renders; the backend never serves
    # public HTML (the trailing Wagtail catch-all below is preview-only).
    path("apis/pages/", pages_api.page_list_api, name="page_list_api"),
    path("apis/pages/<slug:slug>/", pages_api.page_data_api, name="page_data_api"),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.crm.urls")),
    path("api/v1/", include("apps.marketing.urls")),
    path("api/v1/", include("apps.attribution.urls")),
    path("api/v1/", include("apps.finance.urls")),
    path("api/v1/", include("apps.pos.urls")),
    # SaaS billing roads — checkout/portal/webhook + public plan catalog.
    path("", include("apps.billing.urls")),
    # Generic detail road for every registered resource: GET/PATCH/DELETE
    # ``/api/v1/<resource>/<pk>/``. Declared after the explicit app URLs so the
    # specific routes (``deals/<pk>/stage/``, ``revenue/trend/``) win first.
    path("api/v1/<str:resource>/<int:pk>/", resource_api, name="resource_detail_api"),
    path("account/profile/", core_views.profile_view, name="profile"),
    path("connect/email/", include("apps.core.email_oauth_urls")),
    path("connect/", include("apps.marketing.oauth_urls")),
    path(
        "sse/workspace/<int:workspace_id>/events/",
        workspace_events_sse,
        name="workspace_events_sse",
    ),
]

# django-bolt owns the canonical high-throughput API road when its optional
# runtime is installed. Keep the Django JSON road above for compatibility.
if bolt is not None and getattr(bolt, "urls", None) is not None:
    urlpatterns.append(path("bolt/", bolt.urls))

# Wagtail preview road — intentionally LAST. Astro owns every public URL;
# this catch-all only serves live Wagtail pages so editor previews from
# /cms/ resolve (unknown paths fall through to Wagtail's 404). The
# /apis/pages/<slug>/ JSON road is the contract Astro actually consumes.
urlpatterns += [path("", include(wagtail_urls))]
