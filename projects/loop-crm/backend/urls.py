"""Loop-CRM URL configuration.

The browser road is owned by the django-fusion Application registry. The
versioned JSON road remains explicit and domain-scoped under ``/api/v1/``.
"""
from django.contrib import admin
from django.urls import include, path

from apps.core import views as core_views
from apps.core.bolt_api import bolt
from apps.core.fusion import loop_crm_module
from apps.crm import views as crm_views
from apps.finance import views as finance_views
from apps.marketing import views as marketing_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    loop_crm_module.url_pattern,
    path("fragments/navigation/", core_views.navigation_fragment, name="navigation_fragment"),
    path("fragments/workflows/create/", core_views.workflow_create, name="workflow_create"),
    path("fragments/workflows/<int:pk>/toggle/", core_views.workflow_toggle, name="workflow_toggle"),
    path("fragments/workflows/<int:pk>/run/", core_views.workflow_run, name="workflow_run"),
    path("fragments/posts/create/", marketing_views.post_create, name="post_create"),
    path("fragments/crm/companies/create/", crm_views.company_create, name="company_create"),
    path("fragments/crm/contacts/create/", crm_views.contact_create, name="contact_create"),
    path("fragments/crm/deals/create/", crm_views.deal_create, name="deal_create"),
    path("fragments/finance/invoices/create/", finance_views.invoice_create, name="invoice_create"),
    path("fragments/finance/payments/create/", finance_views.payment_create, name="payment_create"),
    path("fragments/posts/<int:pk>/transition/", marketing_views.post_transition, name="post_transition"),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.crm.urls")),
    path("api/v1/", include("apps.marketing.urls")),
    path("api/v1/", include("apps.attribution.urls")),
    path("api/v1/", include("apps.finance.urls")),
    path("account/profile/", core_views.profile_view, name="profile"),
    path("connect/", include("apps.marketing.oauth_urls")),
]

# django-bolt owns the canonical high-throughput API road when its optional
# runtime is installed. Keep the Django JSON road above for compatibility.
if bolt is not None and getattr(bolt, "urls", None) is not None:
    urlpatterns.append(path("bolt/", bolt.urls))
